-- Insert all 15 users with their roles and tools
-- Passwords are bcrypt hashed versions of the original passwords

-- Insert users with correctly hashed passwords  
INSERT INTO users (full_name, username, email, password_hash, is_active) VALUES 
    ('Tony', 'tony967', 'tony@americancircuits.com', '$2b$12$no08BeKqCyMiNmSWLO.etu1SkcAEU0GruCz4wVPigu1vuuJ4PJSu.', true),
    ('Preet', 'preet858', 'preet@americancircuits.com', '$2b$12$4xR8WkVgsPtWzRWlQcaWYepNtFFfAwmuhmy8r/ngsDs679N7ajWQ.', true),
    ('Kanav', 'kanav651', 'kanav@americancircuits.com', '$2b$12$HS0BorUpijyI109.qtV9gOwU36QxXVaieXRf56wuMXP9voqwkpqrG', true),
    ('Khash', 'khash826', 'khash@americancircuits.com', '$2b$12$5SAu6nb.1cR4osDOaEqcIu.wHf.0ul0DBNr9jSBRciVs1QdiFmsNu', true),
    ('Max', 'max463', 'max@americancircuits.com', '$2b$12$T5N5U2dsjvfsSyO.q0Mv4eLgTovW75MgUxHE0d2IFGQUmkPzJvWJm', true),
    ('Ket', 'ket833', 'ket@americancircuits.com', '$2b$12$y9ePs7MxvRlefj0tnEwZv.kS.j3YHw033ECC/95owwxRM/WFW9eEW', true),
    ('Julia', 'julia509', 'julia@americancircuits.com', '$2b$12$9osOzn3QQ.ZLe8mkok6JuuKtp25pgHE5RKFaoQkSW0/OJ989rldtu', true),
    ('Praful', 'praful396', 'praful@americancircuits.com', '$2b$12$UnvUZkaVs2TH9tmThttKmON7xduPT4Mq/1jwbDda/hLhigDiTBPsW', true),
    ('Kris', 'kris500', 'kris@americancircuits.com', '$2b$12$df5zGdayjJ7ONqMzDmxGO.5kgXSqDL13VQEc0yuZMfv151JflPje.', true),
    ('Adam', 'adam585', 'adam@americancircuits.com', '$2b$12$4XCsCHWntiqeOf3nBdIOS.hlRKsrsQHy/r7BF1XMfdaUGka8rZPam', true),
    ('Alex', 'alex343', 'alex@americancircuits.com', '$2b$12$HJY7Mp.R1MzOPlArKOa.zOa31IvOG0ibzNUKJeb4bL8tAn6w9j48O', true),
    ('Pratiksha', 'pratiksha649', 'pratiksha@americancircuits.com', '$2b$12$8Am1PcOxyVb/UJ9bAsbBg.BXKvgQyIVnq0hagfdTYrEhJtn40SF8q', true),
    ('Cathy', 'cathy596', 'cathy@americancircuits.com', '$2b$12$ulkby7upSORtgMuscvhWme6UZqYTlcq0uwCKx0HmQ0imCIiWz4eHa', true),
    ('Bob', 'bob771', 'bob@americancircuits.com', '$2b$12$UGHWAWqQ5WCythna5NC0QuLM/xry9/y6bmwQtEoHxFgOm7BuHeQj6', true),
    ('Abhishek', 'abhishek878', 'abhi@americancircuits.com', '$2b$12$Xl/M07pE7wEIeWowf7Q2TeiWnbGrNTrrEoPxZV4ovo.xySEBZKDqG', true)
ON CONFLICT (username) DO NOTHING;

-- Get role and tool IDs for assignments
DO $$ 
DECLARE
    superuser_role_id INTEGER;
    manager_role_id INTEGER; 
    user_role_id INTEGER;
    operator_role_id INTEGER;
    compare_tool_id INTEGER;
    user_record RECORD;
BEGIN
    -- Get role IDs
    SELECT id INTO superuser_role_id FROM roles WHERE name = 'superuser';
    SELECT id INTO manager_role_id FROM roles WHERE name = 'manager';
    SELECT id INTO user_role_id FROM roles WHERE name = 'user';
    SELECT id INTO operator_role_id FROM roles WHERE name = 'operator';
    
    -- Get tool IDs
    SELECT id INTO compare_tool_id FROM tools WHERE name = 'compare_tool';

    -- Assign roles to users
    
    -- SuperUsers (Tony, Preet, Kanav, Khash)
    FOR user_record IN 
        SELECT id FROM users WHERE username IN ('tony967', 'preet858', 'kanav651', 'khash826')
    LOOP
        INSERT INTO user_roles (user_id, role_id) VALUES (user_record.id, superuser_role_id) ON CONFLICT DO NOTHING;
        -- SuperUsers get all tools
        INSERT INTO user_tools (user_id, tool_id) VALUES 
            (user_record.id, compare_tool_id) ON CONFLICT DO NOTHING;
    END LOOP;
    
    -- Tony also has manager role
    SELECT id INTO user_record FROM users WHERE username = 'tony967';
    INSERT INTO user_roles (user_id, role_id) VALUES (user_record.id, manager_role_id) ON CONFLICT DO NOTHING;
    
    -- Managers (Max, Ket, Julia, Praful)  
    FOR user_record IN 
        SELECT id FROM users WHERE username IN ('max463', 'ket833', 'julia509', 'praful396')
    LOOP
        INSERT INTO user_roles (user_id, role_id) VALUES (user_record.id, manager_role_id) ON CONFLICT DO NOTHING;
        -- Managers get compare_tool
        INSERT INTO user_tools (user_id, tool_id) VALUES 
            (user_record.id, compare_tool_id) ON CONFLICT DO NOTHING;
    END LOOP;
    
    -- Kris (manager + user + operator)
    SELECT id INTO user_record FROM users WHERE username = 'kris500';
    INSERT INTO user_roles (user_id, role_id) VALUES 
        (user_record.id, manager_role_id),
        (user_record.id, user_role_id),
        (user_record.id, operator_role_id) ON CONFLICT DO NOTHING;
    INSERT INTO user_tools (user_id, tool_id) VALUES 
        (user_record.id, compare_tool_id) ON CONFLICT DO NOTHING;
    
    -- Operators and Users (Adam, Alex, Pratiksha, Cathy, Abhishek)
    FOR user_record IN 
        SELECT id FROM users WHERE username IN ('adam585', 'alex343', 'pratiksha649', 'cathy596', 'abhishek878')
    LOOP
        INSERT INTO user_roles (user_id, role_id) VALUES 
            (user_record.id, operator_role_id),
            (user_record.id, user_role_id) ON CONFLICT DO NOTHING;
        -- These users get compare_tool only
        INSERT INTO user_tools (user_id, tool_id) VALUES 
            (user_record.id, compare_tool_id) ON CONFLICT DO NOTHING;
    END LOOP;
    
    -- Bob (user only)
    SELECT id INTO user_record FROM users WHERE username = 'bob771';
    INSERT INTO user_roles (user_id, role_id) VALUES (user_record.id, user_role_id) ON CONFLICT DO NOTHING;
    INSERT INTO user_tools (user_id, tool_id) VALUES (user_record.id, compare_tool_id) ON CONFLICT DO NOTHING;

END $$;