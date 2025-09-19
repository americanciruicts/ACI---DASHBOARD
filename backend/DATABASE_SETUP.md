# Database Setup Guide

## Overview
The ACI Dashboard uses PostgreSQL as the primary database with Alembic for database migrations and schema management.

## Database Configuration

### Environment Variables
- **POSTGRES_USER**: `postgres`
- **POSTGRES_PASSWORD**: `postgres` 
- **POSTGRES_DB**: `aci_dashboard`
- **DATABASE_URL**: `postgresql://postgres:postgres@db:5432/aci_dashboard`

## Database Structure

### Tables Created
1. **users** - User account information
2. **roles** - Available system roles
3. **tools** - Available system tools
4. **user_roles** - Many-to-many relationship between users and roles
5. **user_tools** - Many-to-many relationship between users and tools

### Initial Data Seeded

#### Roles
- `superuser` - Super User with full access
- `user` - Regular user
- `operator` - Operator role
- `itra` - ITRA role

#### Tools
- `compare_tool` - Compare Tool for data comparison
- `x_tool` - X Tool for advanced functionality
- `y_tool` - Y Tool for analysis

#### Sample Users
- **Tony** (`tony967`) - SuperUser
- **Preet** (`preet858`) - SuperUser  
- **Kanav** (`kanav651`) - SuperUser
- **Khash** (`khash826`) - SuperUser
- **Max** (`max463`) - User with Compare Tool and X Tool
- **Pratiksha** (`pratiksha649`) - User/Operator with Compare Tool only
- **Cathy** (`cathy596`) - User/Operator with Compare Tool only

## Migration System

### Alembic Configuration
- Configuration file: `alembic.ini`
- Migrations directory: `alembic/versions/`
- Environment setup: `alembic/env.py`

### Available Migrations
1. **001_initial_migration.py** - Creates all database tables
2. **002_seed_data.py** - Inserts initial roles, tools, and users

### Running Migrations Manually

```bash
# Navigate to backend directory
cd backend/

# Run all pending migrations
alembic upgrade head

# Check current migration status
alembic current

# Create new migration (if needed)
alembic revision --autogenerate -m "description"
```

## Database Startup Process

The database setup follows this sequence:

1. **PostgreSQL Container Start**: Docker starts the PostgreSQL container
2. **Health Check**: System waits for database to be ready
3. **Migration Run**: Alembic runs all pending migrations
4. **Data Seeding**: Initial data is inserted via migrations
5. **FastAPI Start**: Backend application starts

### Startup Script
The `startup.py` script handles:
- Database connectivity verification
- Migration execution
- Seed data insertion (if needed)
- Error handling and logging

## Manual Database Operations

### Connect to Database
```bash
# Via Docker container
docker exec -it <container_name> psql -U postgres -d aci_dashboard

# Via local psql (if PostgreSQL client installed)
psql -h localhost -U postgres -d aci_dashboard
```

### Reset Database
```bash
# Drop and recreate database
docker exec -it <db_container> psql -U postgres -c "DROP DATABASE IF EXISTS aci_dashboard;"
docker exec -it <db_container> psql -U postgres -c "CREATE DATABASE aci_dashboard;"

# Run migrations again
alembic upgrade head
```

### Backup Database
```bash
# Create backup
docker exec <db_container> pg_dump -U postgres aci_dashboard > backup.sql

# Restore backup
docker exec -i <db_container> psql -U postgres aci_dashboard < backup.sql
```

## Testing Database Setup

Run the test script to verify everything is working:

```bash
cd backend/
python test_setup.py
```

This will verify:
- Database connectivity
- Table existence
- Seed data integrity
- User authentication data

## Troubleshooting

### Common Issues

1. **Database Connection Refused**
   - Ensure PostgreSQL container is running
   - Check network connectivity between containers
   - Verify environment variables

2. **Migration Failures**
   - Check Alembic configuration
   - Verify database permissions
   - Review migration logs

3. **Seed Data Missing**
   - Check if migrations ran successfully
   - Verify seed data migration (002_seed_data.py)
   - Run seed_data.py script manually if needed

### Logs and Debugging

```bash
# View database container logs
docker logs <db_container_name>

# View backend container logs
docker logs <backend_container_name>

# Check database tables
docker exec <db_container> psql -U postgres -d aci_dashboard -c "\dt"
```

## Security Considerations

1. **Password Hashing**: All user passwords are hashed using bcrypt
2. **Environment Variables**: Database credentials are configurable via environment
3. **Connection Security**: Use SSL in production environments
4. **Access Control**: Database access is restricted to application containers

## Production Deployment

For production environments:

1. **Change Default Passwords**: Update POSTGRES_PASSWORD
2. **Enable SSL**: Configure SSL connections
3. **Backup Strategy**: Implement regular database backups
4. **Monitoring**: Set up database monitoring and alerts
5. **Resource Limits**: Configure appropriate memory and CPU limits