# ACI Dashboard API - Comprehensive Documentation

## 🚀 Overview

The ACI Dashboard API is a production-ready FastAPI backend with enterprise-grade authentication, authorization, and user management capabilities.

### Key Features
- **OAuth2 + JWT Authentication** with access and refresh tokens
- **Role-Based Access Control (RBAC)** with 5 distinct roles
- **Tool-Based Access Control** with granular permissions
- **PostgreSQL Database** with SQLAlchemy ORM
- **Alembic Migrations** for schema management
- **Docker Containerization** for easy deployment
- **Comprehensive Seed Data** with real user accounts

## 🏗️ Architecture

### Project Structure
```
backend/
├── app/
│   ├── core/           # Configuration and security
│   ├── db/             # Database configuration
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── routers/        # API endpoints
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── seed_comprehensive.py # Database seeding
└── test_backend.py     # Comprehensive tests
```

## 🔐 Authentication System

### OAuth2 Flow
1. **Login**: POST `/api/v1/auth/login` with username/password
2. **Receive Tokens**: Get access token (30min) + refresh token (7 days)
3. **Access APIs**: Include `Authorization: Bearer <access_token>` header
4. **Refresh**: Use refresh token to get new access token when expired

### JWT Token Structure
- **Access Token**: Short-lived (30 minutes), used for API access
- **Refresh Token**: Long-lived (7 days), used to refresh access tokens
- **Security**: Different secret keys for access vs refresh tokens

## 👥 User Roles & Permissions

### Available Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **SuperUser** | Full system access | All endpoints, all tools, user management |
| **Manager** | Management level | Most endpoints, assigned tools |
| **User** | Regular user | Basic endpoints, assigned tools |
| **Operator** | Operational access | Operational endpoints, assigned tools |
| **ITRA** | Specialized access | ITRA-specific functionality |

### Role-Based Endpoints

```python
# SuperUser only
GET  /api/v1/admin/users
POST /api/v1/admin/users
PUT  /api/v1/admin/users/{id}
DELETE /api/v1/admin/users/{id}
GET  /api/v1/admin/roles
GET  /api/v1/admin/tools

# All authenticated users
GET  /api/v1/users/me
GET  /api/v1/tools/
```

## 🔧 Tool-Based Access Control

### Available Tools

| Tool | Route | Description | Access Control |
|------|-------|-------------|----------------|
| **Compare Tool** | `/dashboard/tools/compare` | Data comparison | User assignment or SuperUser |
| **X Tool** | `/dashboard/tools/x-tool` | Advanced X functionality | User assignment or SuperUser |
| **Y Tool** | `/dashboard/tools/y-tool` | Y analysis | User assignment or SuperUser |

### Tool Access Logic
- **SuperUsers**: Automatically get access to all tools
- **Regular Users**: Only get access to explicitly assigned tools
- **Dynamic Assignment**: Admins can assign/remove tool access

## 📊 Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Roles Table
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Tools Table
```sql
CREATE TABLE tools (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    display_name VARCHAR NOT NULL,
    description VARCHAR,
    route VARCHAR NOT NULL,
    icon VARCHAR DEFAULT 'tool',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Many-to-Many Relations
```sql
-- User-Role relationships
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- User-Tool relationships
CREATE TABLE user_tools (
    user_id INTEGER REFERENCES users(id),
    tool_id INTEGER REFERENCES tools(id),
    PRIMARY KEY (user_id, tool_id)
);
```

## 🛠️ API Endpoints

### Base URL: `http://localhost:8000/api/v1`

### Authentication Endpoints

#### POST `/auth/login`
Login with username/password and receive JWT tokens.

**Request:**
```json
{
    "username": "tony967",
    "password": "AhFnrAASWN0a"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "full_name": "Tony",
        "username": "tony967",
        "email": "tony@americancircuits.com",
        "is_active": true,
        "roles": [
            {
                "id": 1,
                "name": "superuser",
                "description": "Super User with full access to all features"
            }
        ],
        "tools": [...]
    }
}
```

#### POST `/auth/refresh`
Refresh access token using refresh token.

**Request:**
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### User Management Endpoints

#### GET `/users/me`
Get current user profile with roles and tools.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
    "id": 1,
    "full_name": "Tony",
    "username": "tony967",
    "email": "tony@americancircuits.com",
    "is_active": true,
    "roles": [...],
    "tools": [...],
    "created_at": "2024-01-01T12:00:00Z"
}
```

#### GET `/users/me/tools`
Get tools available to current user.

**Response:**
```json
{
    "user": "tony967",
    "tools": [
        {
            "id": 1,
            "name": "compare_tool",
            "display_name": "Compare Tool",
            "description": "Tool for comparing data and analyzing differences",
            "route": "/dashboard/tools/compare",
            "icon": "compare"
        }
    ]
}
```

### Admin Endpoints (SuperUser Only)

#### GET `/admin/users`
Get all users with their roles and tools.

**Response:** Array of user objects with full details.

#### POST `/admin/users`
Create new user.

**Request:**
```json
{
    "full_name": "New User",
    "username": "newuser",
    "email": "newuser@company.com",
    "password": "securepassword",
    "role_ids": [2, 3],
    "tool_ids": [1, 2],
    "is_active": true
}
```

#### PUT `/admin/users/{user_id}`
Update existing user.

#### DELETE `/admin/users/{user_id}`
Delete user (cannot delete self).

### Tool Access Endpoints

#### GET `/tools/`
Get tools assigned to current user.

#### GET `/tools/{tool_id}`
Get specific tool if user has access.

#### GET `/tools/compare/access`
Test access to Compare Tool.

#### POST `/tools/compare/execute`
Execute Compare Tool functionality.

## 👤 Seed Data - Demo Users

### SuperUsers
- **Tony** (`tony967` / `AhFnrAASWN0a`) - All tools
- **Preet** (`preet858` / `AaWtgE1hRECG`) - All tools
- **Kanav** (`kanav651` / `XCSkRBUbQKdY`) - All tools
- **Khash** (`khash826` / `9OHRzT69Y3AZ`) - All tools

### Managers
- **Max** (`max463` / `CCiYxAAxyR0z`) - Compare + X Tool
- **Ket** (`ket833` / `jzsNCHDdFGJv`) - Compare + Y Tool
- **Julia** (`julia509` / `SkqtODKmrLjW`) - X + Y Tool
- **Praful** (`praful396` / `F1Cur8klq4pe`) - Compare Tool only

### Regular Users
- **Pratiksha** (`pratiksha649` / `hUDcvxtL26I9`) - Compare Tool only ⭐
- **Cathy** (`cathy596` / `KOLCsB4kTzow`) - Compare Tool only ⭐
- **Bob** (`bob771` / `n6mTWAOhVDda`) - Compare Tool only
- **Abhishek** (`abhishek878` / `2umk93LcQ5cX`) - Y Tool only

### Operators
- **Adam** (`adam585` / `5AdsYCEqrrIg`) - Compare Tool
- **Alex** (`alex343` / `zQE3SqCV5zAE`) - X Tool

### ITRA Users
- **Sarah ITRA** (`sarah_itra` / `ITRA2024Secure!`) - Compare + X Tool
- **Mike ITRA** (`mike_itra` / `ITRAAccess2024!`) - Compare + Y Tool

⭐ *As specifically requested in requirements*

## 🐳 Docker Deployment

### Environment Variables
```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/acidashboard
JWT_SECRET_KEY=aSK1LtZz7jqianX3Xz1AEcSjHQRbnY30tNlDptwu6T2DOxDuKyzcjOriZYWNNCoM
JWT_REFRESH_SECRET_KEY=SxYjdAjtiJo4jDC1CW8zZ/0NFV55Qeje4WevX5yDOcn9dwujUoQ6EMeWYvfLzNEb
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Quick Start
```bash
# Clone and navigate to project
cd "ACI DASHBOARD"

# Start all services
docker-compose up --build

# Backend will be available at:
# http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Service Architecture
- **Backend**: FastAPI on port 8000
- **Database**: PostgreSQL on port 5432
- **Frontend**: Next.js on port 3000
- **Reverse Proxy**: Nginx on port 80/443

## 🧪 Testing

### Run Comprehensive Tests
```bash
# Make sure backend is running
docker-compose up -d backend db

# Run test suite
python backend/test_backend.py
```

### Test Coverage
- ✅ Health checks and connectivity
- ✅ Authentication and JWT tokens
- ✅ Role-based access control
- ✅ Tool-based permissions
- ✅ Admin functionality
- ✅ Security boundaries
- ✅ Error handling

## 🔒 Security Features

### Password Security
- **Bcrypt hashing** with 12 rounds
- **Secure password storage** - never store plaintext
- **Password validation** - minimum length requirements

### JWT Security
- **Separate secrets** for access vs refresh tokens
- **Short token expiry** (30 minutes for access)
- **Token type validation** prevents token misuse
- **Secure algorithm** (HS256)

### Access Control
- **Role-based permissions** with strict enforcement
- **Tool-based access control** with granular permissions
- **Input validation** with Pydantic schemas
- **SQL injection protection** with SQLAlchemy ORM

### API Security
- **CORS configuration** for frontend integration
- **Error handling** without information leakage
- **Request validation** with automatic OpenAPI docs
- **Rate limiting ready** (can be added with middleware)

## 🚀 Production Readiness

### SaaS-Ready Architecture
- ✅ Multi-tenant ready (easy to extend)
- ✅ Role-based access control
- ✅ Tool-based permissions
- ✅ Scalable database design
- ✅ Docker containerization
- ✅ Environment-based configuration
- ✅ Comprehensive logging ready
- ✅ Health checks and monitoring

### Scaling Considerations
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis can be added for session/token caching
- **Load Balancing**: Nginx ready for multiple backend instances
- **Monitoring**: Health checks and metrics endpoints available
- **Logging**: Structured logging can be added

## 📝 Next Steps for Production

1. **Add Monitoring**: Integrate Prometheus/Grafana
2. **Add Logging**: Structured logging with ELK stack
3. **Add Caching**: Redis for improved performance
4. **Add Rate Limiting**: Protect against abuse
5. **SSL/TLS**: Enable HTTPS in production
6. **Backup Strategy**: Automated database backups
7. **CI/CD Pipeline**: Automated testing and deployment

## 🤝 Frontend Integration

The backend is designed to work seamlessly with the Next.js frontend:

- **CORS configured** for frontend origin
- **JWT tokens** compatible with frontend auth
- **User data structure** matches frontend expectations
- **Tool assignments** drive frontend navigation
- **Role-based UI** controlled by backend permissions

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/health
- **Database Admin**: Can connect with pgAdmin or similar tools

---

**🎉 The ACI Dashboard backend is production-ready with enterprise-grade security, comprehensive user management, and scalable architecture!**