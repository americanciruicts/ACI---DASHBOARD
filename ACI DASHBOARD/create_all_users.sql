-- Complete User Creation Script for ACI Dashboard
-- This script adds all 15 users with proper role assignments

-- First ensure we have all necessary roles
INSERT INTO roles (name, description) VALUES 
('super_user', 'Super User with full system access'),
('manager', 'Manager with advanced tool access'),
('user', 'Regular user with basic permissions'),
('operator', 'Operator with limited tool access')
ON CONFLICT (name) DO NOTHING;


-- Ensure all basic tools exist
INSERT INTO tools (name, display_name, description, route, icon, is_active) VALUES 
('compare', 'Compare Tool', 'Compare and analyze data', '/dashboard/tools/compare', 'GitCompare', true),
('analytics', 'Analytics', 'View system analytics', '/dashboard/tools/analytics', 'BarChart3', true),
('monitoring', 'Monitoring', 'System monitoring dashboard', '/dashboard/tools/monitoring', 'Activity', true)
ON CONFLICT (name) DO NOTHING;

-- Create all 15 users
INSERT INTO users (full_name, username, email, password_hash, is_active) VALUES 
-- SUPERUSERS (Full Access - All Tools)
('Tony Manager', 'tony967', 'tony967@aci.local', '$2b$12$PExJlnbjRGjeWB7uA/OXLOA9TGGfhuaooAvNBaccFfMNUklKgzyse', true),
('Preet Super', 'preet858', 'preet858@aci.local', '$2b$12$DDLeVfQef47v2Zg1JvzSxeNfadynoyN0drmTcXyyXcLZWg/g7HkPO', true),
('Kanav Super', 'kanav651', 'kanav651@aci.local', '$2b$12$iwHnaQfUoySDAXiOCT4.EOSohQIEPrSYrpU5e7o..d387HvxebWNa', true),
('Khash Super', 'khash826', 'khash826@aci.local', '$2b$12$WlCm4bhlFUpa0aZjV2qGW.jN86Tq8muzq.wudVm.WXSFqb5kANVzK', true),

-- MANAGERS (All Tools)
('Max Manager', 'max463', 'max463@aci.local', '$2b$12$4pQbF5t/JpqFoy5dYnB5JeHJGAEQcjvXNctEXMl7oJfuNzNUZsceK', true),
('Ket Manager', 'ket833', 'ket833@aci.local', '$2b$12$LamO3jOFijzS1D1ULTnQKO1ja7mMBz7ZUCAzQtTz33VMw.70.2D/m', true),
('Julia Manager', 'julia509', 'julia509@aci.local', '$2b$12$mhSHuvja4YE4CsaQ2140ye/mb7S0npgWnFBVWyCG6Yl8Uo92JnZoK', true),
('Praful Manager', 'praful396', 'praful396@aci.local', '$2b$12$2NhyE9ZhR.B7UFU8osRfNOf3koqUYydqxx8xV7jYq5wnNvJRhEOuy', true),
('Kris Multi-Role', 'kris500', 'kris500@aci.local', '$2b$12$1Pt5rzfU.aBc7yfH.e6qVuTQeDfZ4uDe6/qHyslvF1q29W1zhfr.m', true),

-- USERS & OPERATORS (Compare Tool Only)
('Adam User', 'adam585', 'adam585@aci.local', '$2b$12$upDu2lrv4/257BkHJrW1..kWQoyrgsa6ljbQxEBgFQaToXwXu40ri', true),
('Alex User', 'alex343', 'alex343@aci.local', '$2b$12$owrCGq6h32ifIlT2e88mTujhjMMrOc/hH1EDfGiFte/CY1E2FGeNa', true),
('Pratiksha User', 'pratiksha649', 'pratiksha649@aci.local', '$2b$12$eYIle16mkjOZkGQ21XLh4OE3X.L8/D3V.SWlgcbIu7ULxRyQaZo5O', true),
('Cathy User', 'cathy596', 'cathy596@aci.local', '$2b$12$f7nY9bwiJYP/DtXqZNHDe.Hm6gp6JRzmxTl.r5RkMR7OA37kp.O72', true),
('Abhishek Operator', 'abhishek878', 'abhi@americancircuits.com', '$2b$12$Hb64naBqh3jR2lZzVEx7Uesu6ggMTn8lMlb5xRnjhYUz6Z7tEW25C', true),
('Bob User', 'bob771', 'bob771@aci.local', '$2b$12$qpBNkOeE8LZYr3tHfBA0M.qd3kdqc7qDRGYyEOlGEA63a2JUNKY/C', true)
ON CONFLICT (username) DO NOTHING;

-- Assign SUPERUSER roles (Full Access - All Tools)
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username IN ('tony967', 'preet858', 'kanav651', 'khash826') AND r.name = 'super_user'
ON CONFLICT DO NOTHING;

-- Tony is also a manager (dual role)
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username = 'tony967' AND r.name = 'manager'
ON CONFLICT DO NOTHING;

-- Assign MANAGER roles (All Tools)
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username IN ('max463', 'ket833', 'julia509', 'praful396', 'kris500') AND r.name = 'manager'
ON CONFLICT DO NOTHING;

-- Assign USER roles (Compare Tool Only)
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username IN ('adam585', 'alex343', 'pratiksha649', 'cathy596', 'bob771') AND r.name = 'user'
ON CONFLICT DO NOTHING;

-- Assign OPERATOR role to Abhishek
INSERT INTO user_roles (user_id, role_id) 
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username = 'abhishek878' AND r.name = 'operator'
ON CONFLICT DO NOTHING;

-- Assign ALL TOOLS to SUPERUSERS
INSERT INTO user_tools (user_id, tool_id)
SELECT u.id, t.id 
FROM users u, tools t 
WHERE u.username IN ('tony967', 'preet858', 'kanav651', 'khash826')
ON CONFLICT DO NOTHING;

-- Assign ALL TOOLS to MANAGERS
INSERT INTO user_tools (user_id, tool_id)
SELECT u.id, t.id 
FROM users u, tools t 
WHERE u.username IN ('max463', 'ket833', 'julia509', 'praful396', 'kris500')
ON CONFLICT DO NOTHING;

-- Assign COMPARE TOOL ONLY to USERS & OPERATORS
INSERT INTO user_tools (user_id, tool_id)
SELECT u.id, t.id 
FROM users u, tools t 
WHERE u.username IN ('adam585', 'alex343', 'pratiksha649', 'cathy596', 'abhishek878', 'bob771') 
AND t.name = 'compare'
ON CONFLICT DO NOTHING;

-- Display final user count
SELECT 'Total Users Created:' as status, COUNT(*) as count FROM users;
SELECT 'User Role Assignments:' as status, COUNT(*) as count FROM user_roles;
SELECT 'User Tool Assignments:' as status, COUNT(*) as count FROM user_tools;

-- Show all users with their roles
SELECT 
    u.username,
    u.full_name,
    STRING_AGG(DISTINCT r.name, ', ') as roles,
    COUNT(DISTINCT ut.tool_id) as tool_count
FROM users u
LEFT JOIN user_roles ur ON u.id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.id
LEFT JOIN user_tools ut ON u.id = ut.user_id
GROUP BY u.id, u.username, u.full_name
ORDER BY u.username;