#!/bin/bash
# ACI Dashboard Startup Script

set -e

# Configuration
PROJECT_NAME="ACI Dashboard"
COMPOSE_FILE="docker-compose.yml"
ENVIRONMENT=${1:-development}

echo "🚀 Starting $PROJECT_NAME in $ENVIRONMENT mode..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data/postgres data/redis logs/nginx nginx/conf.d nginx/ssl database/init

# Set appropriate permissions for data directories
if [[ "$OSTYPE" != "msys"* ]] && [[ "$OSTYPE" != "win32"* ]]; then
    chmod 755 data/postgres data/redis logs/nginx
fi

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your configuration before proceeding."
fi

# Choose compose file based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_CMD="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"
    echo "🏭 Using production configuration"
elif [ "$ENVIRONMENT" = "development" ]; then
    COMPOSE_CMD="docker-compose -f docker-compose.yml -f docker-compose.override.yml"
    echo "🛠️  Using development configuration"
else
    COMPOSE_CMD="docker-compose"
    echo "📋 Using default configuration"
fi

# Build and start services
echo "🏗️  Building and starting services..."
$COMPOSE_CMD build --no-cache
$COMPOSE_CMD up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
$COMPOSE_CMD ps

# Show service URLs
echo ""
echo "✅ $PROJECT_NAME is starting up!"
echo "📊 Services will be available at:"
echo "   🌐 Frontend: http://localhost:8082"
echo "   🔌 Backend API: http://localhost:8001"
echo "   🌉 Nginx Proxy: http://localhost:8083"
echo "   🗄️  Database: localhost:5433"
echo "   🔴 Redis: localhost:6379"
echo ""
echo "🔍 View logs with: $COMPOSE_CMD logs -f"
echo "⏹️  Stop services with: $COMPOSE_CMD down"
echo "🔄 Restart services with: $COMPOSE_CMD restart"
echo ""

# Show health check
echo "🏥 Performing health checks..."
sleep 5

# Check if services are responding
check_service() {
    local url=$1
    local name=$2
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo "✅ $name: Healthy"
    else
        echo "❌ $name: Not responding"
    fi
}

check_service "http://localhost:8001/health" "Backend API"
check_service "http://localhost:8082/api/health" "Frontend"
check_service "http://localhost:8083/health" "Nginx Proxy"

echo ""
echo "🎉 Startup complete! Check the logs if any services are not responding."