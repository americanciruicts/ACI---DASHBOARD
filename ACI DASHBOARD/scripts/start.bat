@echo off
REM ACI Dashboard Startup Script for Windows

setlocal EnableDelayedExpansion

set PROJECT_NAME=ACI Dashboard
set COMPOSE_FILE=docker-compose.yml
set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development

echo 🚀 Starting %PROJECT_NAME% in %ENVIRONMENT% mode...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running. Please start Docker Desktop first.
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directory structure...
if not exist "data\postgres" mkdir "data\postgres"
if not exist "data\redis" mkdir "data\redis"
if not exist "logs\nginx" mkdir "logs\nginx"
if not exist "nginx\conf.d" mkdir "nginx\conf.d"
if not exist "nginx\ssl" mkdir "nginx\ssl"
if not exist "database\init" mkdir "database\init"

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy ".env.example" ".env"
    echo ⚠️  Please update the .env file with your configuration before proceeding.
)

REM Choose compose command based on environment
if "%ENVIRONMENT%"=="production" (
    set "COMPOSE_CMD=docker-compose -f docker-compose.yml -f docker-compose.prod.yml"
    echo 🏭 Using production configuration
) else if "%ENVIRONMENT%"=="development" (
    set "COMPOSE_CMD=docker-compose -f docker-compose.yml -f docker-compose.override.yml"
    echo 🛠️  Using development configuration
) else (
    set "COMPOSE_CMD=docker-compose"
    echo 📋 Using default configuration
)

REM Build and start services
echo 🏗️  Building and starting services...
%COMPOSE_CMD% build --no-cache
%COMPOSE_CMD% up -d

REM Wait for services to be healthy
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...
%COMPOSE_CMD% ps

REM Show service URLs
echo.
echo ✅ %PROJECT_NAME% is starting up!
echo 📊 Services will be available at:
echo    🌐 Frontend: http://localhost:8082
echo    🔌 Backend API: http://localhost:8001
echo    🌉 Nginx Proxy: http://localhost:8083
echo    🗄️  Database: localhost:5433
echo    🔴 Redis: localhost:6379
echo.
echo 🔍 View logs with: %COMPOSE_CMD% logs -f
echo ⏹️  Stop services with: %COMPOSE_CMD% down
echo 🔄 Restart services with: %COMPOSE_CMD% restart
echo.

REM Show health check
echo 🏥 Performing health checks...
timeout /t 5 /nobreak >nul

REM Check if services are responding (Windows version using PowerShell)
echo ✅ Backend API: Testing...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8001/health' -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host '✅ Backend API: Healthy' } catch { Write-Host '❌ Backend API: Not responding' }"

echo ✅ Frontend: Testing...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8082/api/health' -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host '✅ Frontend: Healthy' } catch { Write-Host '❌ Frontend: Not responding' }"

echo ✅ Nginx Proxy: Testing...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8083/health' -UseBasicParsing -TimeoutSec 5 | Out-Null; Write-Host '✅ Nginx Proxy: Healthy' } catch { Write-Host '❌ Nginx Proxy: Not responding' }"

echo.
echo 🎉 Startup complete! Check the logs if any services are not responding.
pause