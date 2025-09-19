# ACI Dashboard Docker Setup Guide

This guide provides comprehensive instructions for setting up and running the ACI Dashboard using Docker.

## 🏗️ Architecture

The ACI Dashboard consists of the following services:

- **Frontend**: Next.js application (Port 8082)
- **Backend**: FastAPI application (Port 8001)  
- **Database**: PostgreSQL 15 (Port 5433)
- **Cache**: Redis 7 (Port 6379)
- **Proxy**: Nginx reverse proxy (Port 8083)

## 📋 Prerequisites

- Docker Desktop 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for Docker
- Ports 8001, 8082, 8083, 5433, 6379 available

## 🚀 Quick Start

### Windows
```bash
scripts\start.bat development
```

### Linux/Mac
```bash
chmod +x scripts/start.sh
./scripts/start.sh development
```

### Manual Setup

1. **Clone and navigate to the project**
   ```bash
   git clone <repository-url>
   cd "ACI DASHBOARD"
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**
   ```bash
   # Development
   docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
   
   # Production
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://postgres:secure_db_password@localhost:5433/aci_dashboard

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001
ALLOWED_ORIGINS=http://localhost:8082,http://localhost:8083

# Redis
REDIS_URL=redis://:redis_secure_password@localhost:6379/0
```

### Service Ports

| Service | Development | Production | Description |
|---------|------------|------------|-------------|
| Frontend | 8082 | 8082 | Next.js web application |
| Backend | 8001 | 8001 | FastAPI REST API |
| Nginx | 8083 | 80/443 | Reverse proxy |
| PostgreSQL | 5433 | 5433 | Database |
| Redis | 6379 | 6379 | Cache & sessions |

## 🏥 Health Checks

All services include comprehensive health checks:

- **Backend**: `GET /health`
- **Frontend**: `GET /api/health`
- **Nginx**: `GET /health`
- **Database**: `pg_isready` check
- **Redis**: Connection test

### Check Service Health

```bash
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs backend
docker-compose logs frontend

# Test endpoints
curl http://localhost:8001/health
curl http://localhost:8082/api/health
curl http://localhost:8083/health
```

## 🔄 Common Operations

### Start Services
```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Production  
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Rebuild Services
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Scale Services (Production)
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3 --scale frontend=2
```

## 📊 Monitoring

### Service Status
```bash
docker-compose ps
```

### Resource Usage
```bash
docker stats
```

### Disk Usage
```bash
docker system df
```

## 🔧 Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8001
   
   # Kill process using port (Linux/Mac)
   sudo fuser -k 8001/tcp
   ```

2. **Permission errors (Linux/Mac)**
   ```bash
   sudo chown -R $USER:$USER data/ logs/
   chmod -R 755 data/ logs/
   ```

3. **Database connection issues**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Connect to database manually
   docker-compose exec db psql -U postgres -d aci_dashboard
   ```

4. **Memory issues**
   ```bash
   # Clean up Docker
   docker system prune -a
   docker volume prune
   ```

### Service Dependencies

Services start in this order:
1. Database & Redis
2. Backend (waits for DB/Redis to be healthy)
3. Frontend (waits for Backend to be healthy)
4. Nginx (waits for Frontend/Backend to be healthy)

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v --remove-orphans

# Remove images
docker-compose down --rmi all

# Clean data directories
rm -rf data/ logs/

# Restart fresh
./scripts/start.sh development
```

## 🔐 Security Considerations

### Production Deployment

1. **Change default passwords**
   - Update `POSTGRES_PASSWORD` in docker-compose.yml
   - Update `Redis password` in docker-compose.yml
   - Generate new `SECRET_KEY` and `JWT_SECRET_KEY`

2. **Enable HTTPS**
   - Uncomment HTTPS server block in nginx/nginx.conf
   - Add SSL certificates to nginx/ssl/
   - Update ports in docker-compose.prod.yml

3. **Environment isolation**
   - Use secrets management (Docker secrets, HashiCorp Vault)
   - Run with non-root users
   - Enable security scanning

4. **Monitoring**
   - Set up log aggregation
   - Configure health check alerts
   - Monitor resource usage

## 📈 Performance Optimization

### Development
- Services use volume mounts for hot reloading
- Debug mode enabled
- Reduced resource limits

### Production
- Multi-stage builds for smaller images
- Read-only containers where possible
- Resource limits and reservations
- Service replication for high availability
- Connection pooling and caching

## 🛠️ Development Tips

1. **Live reload**: Code changes are automatically reflected
2. **Database access**: Connect to `localhost:5433`
3. **Redis access**: Connect to `localhost:6379`
4. **Logs**: Use `docker-compose logs -f service-name`
5. **Shell access**: `docker-compose exec service-name /bin/sh`

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

For additional help or questions, check the application logs or consult the development team.