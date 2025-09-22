# ACI Dashboard API Documentation

## Overview
The ACI Dashboard API is a FastAPI-based backend service that provides comprehensive user management, authentication, and tool access control for the ACI Dashboard application.

## Base URL
```
http://localhost:8000
```

## Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Health & Status

#### GET `/`
Get API status
- **Response**: Basic API information and version

#### GET `/health`
Health check endpoint
- **Response**: Database connectivity status and timestamp

### Authentication Routes

#### POST `/api/auth/login`
User login endpoint
- **Request Body**: 
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: JWT token and user information
- **Access**: Public

#### POST `/api/auth/register`
Register new user (SuperUser only)
- **Request Body**:
  ```json
  {
    "full_name": "string",
    "username": "string",
    "email": "string",
    "password": "string",
    "role_ids": [1, 2],
    "tool_ids": [1, 2]
  }
  ```
- **Response**: Created user information
- **Access**: SuperUser only

#### GET `/api/auth/me`
Get current user information
- **Response**: Current user details with roles and tools
- **Access**: Authenticated users

### User Management Routes

#### GET `/api/users`
Get all users
- **Response**: List of all users with their roles and tools
- **Access**: SuperUser only

#### GET `/api/users/{user_id}`
Get specific user by ID
- **Parameters**: `user_id` (integer)
- **Response**: User details with roles and tools
- **Access**: SuperUser only

#### POST `/api/users`
Create new user
- **Request Body**: Same as register endpoint
- **Response**: Created user information
- **Access**: SuperUser only

#### PUT `/api/users/{user_id}`
Update user information
- **Parameters**: `user_id` (integer)
- **Request Body**:
  ```json
  {
    "full_name": "string",
    "username": "string", 
    "email": "string",
    "password": "string",
    "role_ids": [1, 2],
    "tool_ids": [1, 2],
    "is_active": true
  }
  ```
- **Response**: Updated user information
- **Access**: SuperUser only

#### DELETE `/api/users/{user_id}`
Delete user
- **Parameters**: `user_id` (integer)
- **Response**: Success message
- **Access**: SuperUser only

### Role Management Routes

#### GET `/api/roles`
Get all available roles
- **Response**: List of all roles
- **Access**: SuperUser only

### Tool Management Routes

#### GET `/api/tools`
Get all available tools
- **Response**: List of all tools
- **Access**: SuperUser only

#### POST `/api/tools`
Create new tool
- **Request Body**:
  ```json
  {
    "name": "string",
    "display_name": "string",
    "description": "string",
    "route": "string",
    "icon": "string",
    "is_active": true
  }
  ```
- **Response**: Created tool information
- **Access**: SuperUser only

#### PUT `/api/tools/{tool_id}`
Update tool information
- **Parameters**: `tool_id` (integer)
- **Request Body**: Same as create tool (all fields optional)
- **Response**: Updated tool information
- **Access**: SuperUser only

### Assignment Routes

#### POST `/api/assign-role`
Assign role to user
- **Request Body**:
  ```json
  {
    "user_id": 1,
    "role_id": 2
  }
  ```
- **Response**: Success message
- **Access**: SuperUser only

#### POST `/api/assign-tool`
Assign tool to user
- **Request Body**:
  ```json
  {
    "user_id": 1,
    "tool_id": 2
  }
  ```
- **Response**: Success message
- **Access**: SuperUser only

### Tool Access Routes

#### GET `/api/tools/compare`
Access Compare Tool
- **Response**: Success message with user info
- **Access**: Users with compare_tool access

#### GET `/api/tools/x-tool`
Access X Tool
- **Response**: Success message with user info
- **Access**: Users with x_tool access

#### GET `/api/tools/y-tool`
Access Y Tool
- **Response**: Success message with user info
- **Access**: Users with y_tool access

## Database Models

### User
- **id**: Integer (Primary Key)
- **full_name**: String
- **username**: String (Unique)
- **email**: String (Unique)
- **hashed_password**: String
- **is_active**: Boolean
- **created_at**: DateTime
- **roles**: Many-to-Many relationship with Role
- **tools**: Many-to-Many relationship with Tool

### Role
- **id**: Integer (Primary Key)
- **name**: String (Unique)
- **description**: String
- **created_at**: DateTime

### Tool
- **id**: Integer (Primary Key)
- **name**: String (Unique)
- **display_name**: String
- **description**: String
- **route**: String
- **icon**: String
- **is_active**: Boolean
- **created_at**: DateTime

## Available Roles
1. **superuser** - Full system access
2. **manager** - Management level access
3. **user** - Regular user access
4. **operator** - Operator level access
5. **itra** - ITRA specific access

## Available Tools
1. **compare_tool** - Data comparison functionality
2. **x_tool** - X analysis functionality  
3. **y_tool** - Y analysis functionality

## Security Features
- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: 30-minute expiration time
- **Role-Based Access Control**: Different permission levels
- **Tool-Based Access Control**: Granular tool access management
- **Input Validation**: Comprehensive validation for all inputs
- **SuperUser Privileges**: SuperUsers automatically get access to all tools

## Error Responses
The API returns standard HTTP status codes:
- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **422**: Validation Error
- **503**: Service Unavailable (health check failure)

## Sample Demo Users
- **SuperUser**: `tony967` / `AhFnrAASWN0a`
- **Manager**: `max463` / `CCiYxAAxyR0z`
- **User**: `pratiksha649` / `hUDcvxtL26I9` (Compare Tool only)