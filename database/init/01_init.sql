-- ACI Dashboard Database Initialization Script
-- This script will run when the PostgreSQL container starts for the first time

-- Create additional database configurations if needed
ALTER DATABASE aci_dashboard SET timezone TO 'UTC';

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE aci_dashboard TO postgres;

-- Create logging table first
CREATE TABLE IF NOT EXISTS public.system_log (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Log initialization
INSERT INTO public.system_log (message, created_at) 
VALUES ('Database initialized successfully', NOW())
ON CONFLICT DO NOTHING;