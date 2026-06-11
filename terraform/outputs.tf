output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer"
  value       = "aws_lb.uawos_alb.dns_name"
}

output "rds_endpoint" {
  description = "The database connection endpoint"
  value       = "aws_db_instance.postgres.endpoint"
}

output "ecs_cluster_name" {
  description = "The name of the ECS Cluster"
  value       = "aws_ecs_cluster.uawos_cluster.name"
}
