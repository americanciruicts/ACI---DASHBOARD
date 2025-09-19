-- Create the acidashboard database tables and data
-- This script will be executed when the PostgreSQL container starts for the first time

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tools table  
CREATE TABLE IF NOT EXISTS tools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    route VARCHAR(100) NOT NULL,
    icon VARCHAR(50) DEFAULT 'tool',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_roles junction table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Create user_tools junction table  
CREATE TABLE IF NOT EXISTS user_tools (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tool_id INTEGER REFERENCES tools(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, tool_id)
);

-- Insert roles
INSERT INTO roles (name, description) VALUES 
    ('superuser', 'Super User with full access to all features'),
    ('manager', 'Manager role with elevated permissions'), 
    ('user', 'Regular user with standard access'),
    ('operator', 'Operator role with operational permissions')
ON CONFLICT (name) DO NOTHING;

-- Insert tools
INSERT INTO tools (name, display_name, description, route, icon, is_active) VALUES
    ('compare_tool', 'Compare Tool', 'Tool for comparing data and analyzing differences', '/dashboard/tools/compare', 'compare', true)
ON CONFLICT (name) DO NOTHING;