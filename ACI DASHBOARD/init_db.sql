-- Initialize ACI Dashboard Database Schema
-- Drop existing tables if they exist (in correct order due to foreign keys)
DROP TABLE IF EXISTS user_tools;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS tools;
DROP TABLE IF EXISTS roles;

-- Create roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create tools table
CREATE TABLE tools (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    display_name VARCHAR NOT NULL,
    description VARCHAR,
    route VARCHAR NOT NULL,
    icon VARCHAR,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR NOT NULL,
    username VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create user_roles association table
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Create user_tools association table
CREATE TABLE user_tools (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tool_id INTEGER REFERENCES tools(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, tool_id)
);

-- Insert default roles
INSERT INTO roles (name, description) VALUES 
('super_user', 'Super User with full system access'),
('admin', 'Administrator with advanced permissions'),
('user', 'Regular user with basic permissions')
ON CONFLICT (name) DO NOTHING;

-- Insert default tools
INSERT INTO tools (name, display_name, description, route, icon, is_active) VALUES 
('compare', 'Compare Tool', 'Compare and analyze data', '/dashboard/tools/compare', 'GitCompare', true),
('analytics', 'Analytics', 'View system analytics', '/dashboard/tools/analytics', 'BarChart3', true),
('monitoring', 'Monitoring', 'System monitoring dashboard', '/dashboard/tools/monitoring', 'Activity', true)
ON CONFLICT (name) DO NOTHING;

-- Insert default super user (password: admin123)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (full_name, username, email, password_hash, is_active) VALUES 
('Super Admin', 'admin', 'admin@aci.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewtsUphIJGdQP5zu', true)
ON CONFLICT (username) DO NOTHING;

-- Assign super_user role to admin
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username = 'admin' AND r.name = 'super_user'
ON CONFLICT DO NOTHING;

-- Assign all tools to admin user
INSERT INTO user_tools (user_id, tool_id)
SELECT u.id, t.id 
FROM users u, tools t 
WHERE u.username = 'admin'
ON CONFLICT DO NOTHING;

-- Create additional test user (password: test123)
INSERT INTO users (full_name, username, email, password_hash, is_active) VALUES 
('Test User', 'test', 'test@aci.local', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', true)
ON CONFLICT (username) DO NOTHING;

-- Assign user role to test user
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username = 'test' AND r.name = 'user'
ON CONFLICT DO NOTHING;

-- Assign compare tool to test user
INSERT INTO user_tools (user_id, tool_id)
SELECT u.id, t.id 
FROM users u, tools t 
WHERE u.username = 'test' AND t.name = 'compare'
ON CONFLICT DO NOTHING;