# Database Migration Planner

Source: https://www.claudedirectory.org/skills/migrate-db

## System Prompt / Instructions

```markdown
# Database Migration Planner

Plan and generate safe database migrations with built-in safety checks.

## Overview

This skill helps you:

- **Plan Migrations** - Analyze schema changes and generate migration files
- **Safety Analysis** - Identify potentially dangerous operations (column drops, type changes)
- **Rollback Strategy** - Generate matching rollback migrations
- **Zero-Downtime** - Suggest multi-step migration strategies for production

## Safety Checks

Before generating migrations, the skill checks for:

- Destructive column/table drops
- Lock-heavy operations on large tables
- Missing indexes on foreign keys
- Data type changes that could lose data
- Default value additions on large tables

## Supported ORMs

- Prisma (schema.prisma)
- Drizzle ORM
- Knex.js
- TypeORM
- Django migrations
- Rails ActiveRecord
- Alembic (SQLAlchemy)

## Usage

Invoke with: "Plan a migration to add user preferences"

Options:
- "Generate a migration to add an email column to users"
- "Plan a safe migration to rename the orders table"
- "Create a rollback migration for the latest change"
```
