provider "aws" {
  region = var.aws_region
}

# ==========================================
# 1. NETWORKING (VPC, Subnets, Gateways)
# ==========================================

data "aws_availability_zones" "available" {}

resource "aws_vpc" "uawos_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "uawos-vpc"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.uawos_vpc.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "uawos-public-subnet-${count.index}"
    Environment = var.environment
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.uawos_vpc.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "uawos-private-subnet-${count.index}"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "uawos_igw" {
  vpc_id = aws_vpc.uawos_vpc.id

  tags = {
    Name = "uawos-igw"
  }
}

resource "aws_eip" "nat" {
  vpc = true
}

resource "aws_nat_gateway" "uawos_nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "uawos-nat-gateway"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.uawos_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.uawos_igw.id
  }

  tags = {
    Name = "uawos-public-route-table"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.uawos_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.uawos_nat.id
  }

  tags = {
    Name = "uawos-private-route-table"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# ==========================================
# 2. SECURITY GROUPS
# ==========================================

resource "aws_security_group" "alb" {
  name        = "uawos-alb-sg"
  description = "Allow inbound web traffic to ALB"
  vpc_id      = aws_vpc.uawos_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "uawos-ecs-tasks-sg"
  description = "Control traffic to ECS tasks"
  vpc_id      = aws_vpc.uawos_vpc.id

  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow all internal communications within ECS security group
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name   = "uawos-rds-sg"
  vpc_id = aws_vpc.uawos_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ==========================================
# 3. RELATIONAL STATE DATABASE (RDS)
# ==========================================

resource "aws_db_subnet_group" "rds" {
  name       = "uawos-rds-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_db_instance" "postgres" {
  identifier             = "uawos-postgres-db"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "14"
  instance_class         = "db.t3.micro"
  db_name                = var.db_name
  username               = var.db_user
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = true

  tags = {
    Environment = var.environment
  }
}

# ==========================================
# 4. ECS CLUSTER & IAM ROLES
# ==========================================

resource "aws_ecs_cluster" "uawos_cluster" {
  name = "uawos-cluster-${var.environment}"
}

resource "aws_iam_role" "ecs_execution_role" {
  name = "uawos-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "uawos-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "uawos_logs" {
  name              = "/ecs/uawos-logs"
  retention_in_days = 7
}

# ==========================================
# 5. ECS TASK DEFINITION (BFF Core Daemon)
# ==========================================

resource "aws_ecs_task_definition" "uawos_bff" {
  family                   = "uawos-bff"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "uawos-bff"
      image     = "uawos-bff-image:${var.container_image_tag}"
      essential = true
      portMappings = [
        {
          containerPort = 8099
          hostPort      = 8099
        }
      ]
      environment = [
        { name = "POSTGRES_HOST", value = element(split(":", aws_db_instance.postgres.endpoint), 0) },
        { name = "POSTGRES_PORT", value = "5432" },
        { name = "POSTGRES_DB", value = var.db_name },
        { name = "POSTGRES_USER", value = var.db_user },
        { name = "POSTGRES_PASSWORD", value = var.db_password },
        { name = "QDRANT_HOST", value = "qdrant.local" },
        { name = "QDRANT_PORT", value = "6333" },
        { name = "OLLAMA_BASE_URL", value = "http://ollama-gateway.local:11434" },
        { name = "MARKER_BASE_URL", value = "http://marker-service.local:8000" },
        { name = "MOCK_SERVICES_BASE_URL", value = "http://mocks-service.local:5001" },
        { name = "OPA_HOST", value = "opa.local" },
        { name = "OPA_PORT", value = "8181" },
        { name = "OPENFGA_HOST", value = "openfga.local" },
        { name = "OPENFGA_PORT", value = "8083" }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.uawos_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "bff"
        }
      }
    }
  ])
}

# ==========================================
# 6. ECS SERVICE & ALB SETUP
# ==========================================

resource "aws_lb" "uawos_alb" {
  name               = "uawos-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "uawos_target" {
  name        = "uawos-target-group"
  port        = 8099
  protocol    = "HTTP"
  vpc_id      = aws_vpc.uawos_vpc.id
  target_type = "ip"

  health_check {
    path                = "/api/status"
    port                = "8099"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.uawos_alb.load_balancer_arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.uawos_target.arn
  }
}

resource "aws_ecs_service" "uawos_bff_service" {
  name            = "uawos-bff-service"
  cluster         = aws_ecs_cluster.uawos_cluster.id
  task_definition = aws_ecs_task_definition.uawos_bff.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.uawos_target.arn
    container_name   = "uawos-bff"
    container_port   = 8099
  }

  depends_on = [aws_lb_listener.http]
}
