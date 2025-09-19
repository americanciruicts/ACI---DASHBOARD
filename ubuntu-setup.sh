#!/bin/bash

# ACI Dashboard Ubuntu Server Setup Script
# This script prepares an Ubuntu server for running the ACI Dashboard

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ACI Dashboard"
DOCKER_COMPOSE_VERSION="2.21.0"
MIN_MEMORY_GB=4
MIN_DISK_GB=10

echo -e "${BLUE}🚀 $PROJECT_NAME Ubuntu Server Setup${NC}"
echo "=================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

# Check sudo privileges
if ! sudo -v; then
    echo -e "${RED}❌ This script requires sudo privileges${NC}"
    exit 1
fi

# System requirements check
echo -e "${BLUE}🔍 Checking system requirements...${NC}"

# Check Ubuntu version
ubuntu_version=$(lsb_release -rs)
echo "Ubuntu version: $ubuntu_version"

if (( $(echo "$ubuntu_version >= 20.04" | bc -l) )); then
    echo -e "${GREEN}✅ Ubuntu version is compatible${NC}"
else
    echo -e "${RED}❌ Ubuntu 20.04 LTS or later is required${NC}"
    exit 1
fi

# Check available memory
memory_gb=$(free -g | awk 'NR==2{print $2}')
echo "Available memory: ${memory_gb}GB"

if [ "$memory_gb" -ge "$MIN_MEMORY_GB" ]; then
    echo -e "${GREEN}✅ Memory requirement met${NC}"
else
    echo -e "${YELLOW}⚠️ Warning: Less than ${MIN_MEMORY_GB}GB RAM available. Performance may be affected.${NC}"
fi

# Check available disk space
disk_gb=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
echo "Available disk space: ${disk_gb}GB"

if [ "$disk_gb" -ge "$MIN_DISK_GB" ]; then
    echo -e "${GREEN}✅ Disk space requirement met${NC}"
else
    echo -e "${RED}❌ At least ${MIN_DISK_GB}GB free disk space is required${NC}"
    exit 1
fi

# Update system
echo -e "${BLUE}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install required packages
echo -e "${BLUE}📦 Installing required packages...${NC}"
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    htop \
    nano \
    unzip \
    wget \
    bc

# Install Docker
echo -e "${BLUE}🐳 Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    # Remove old Docker versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    echo -e "${GREEN}✅ Docker installed successfully${NC}"
else
    echo -e "${GREEN}✅ Docker is already installed${NC}"
fi

# Install Docker Compose
echo -e "${BLUE}🔧 Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed successfully${NC}"
else
    echo -e "${GREEN}✅ Docker Compose is already installed${NC}"
fi

# Start and enable Docker service
echo -e "${BLUE}🚀 Starting Docker service...${NC}"
sudo systemctl start docker
sudo systemctl enable docker

# Configure Docker daemon for production
echo -e "${BLUE}⚙️ Configuring Docker daemon...${NC}"
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "userland-proxy": false,
  "experimental": false,
  "live-restore": true
}
EOF

# Restart Docker to apply configuration
sudo systemctl restart docker

# Set up firewall rules (if UFW is enabled)
if sudo ufw status | grep -q "Status: active"; then
    echo -e "${BLUE}🔥 Configuring firewall rules...${NC}"
    sudo ufw allow 8001/tcp comment "ACI Dashboard Backend"
    sudo ufw allow 8082/tcp comment "ACI Dashboard Frontend"
    sudo ufw allow 8083/tcp comment "ACI Dashboard Nginx"
    sudo ufw allow 22/tcp comment "SSH"
    echo -e "${GREEN}✅ Firewall rules configured${NC}"
fi

# Create project structure
echo -e "${BLUE}📁 Creating project directories...${NC}"
mkdir -p data/{postgres,redis} logs/{nginx,backend,frontend} cache/{nginx,frontend} database/init nginx/{conf.d,ssl} scripts

# Set proper permissions
chmod 755 data/ logs/ cache/
chmod 600 .env.example 2>/dev/null || true

# Create systemd service for auto-start (optional)
read -p "Do you want to create a systemd service for auto-start? (y/N): " create_service
if [[ $create_service =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}⚙️ Creating systemd service...${NC}"
    
    sudo tee /etc/systemd/system/aci-dashboard.service > /dev/null <<EOF
[Unit]
Description=ACI Dashboard Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=$USER
Group=docker

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable aci-dashboard.service
    echo -e "${GREEN}✅ Systemd service created and enabled${NC}"
fi

# Check ports availability
echo -e "${BLUE}🔍 Checking port availability...${NC}"
ports=(5433 6379 8001 8082 8083)
for port in "${ports[@]}"; do
    if ss -tuln | grep -q ":$port "; then
        echo -e "${YELLOW}⚠️ Warning: Port $port is already in use${NC}"
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
    fi
done

# Final instructions
echo ""
echo -e "${GREEN}🎉 Ubuntu server setup completed successfully!${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Log out and log back in to apply docker group membership"
echo "2. Copy your project files to: $(pwd)"
echo "3. Copy .env.example to .env and configure your settings"
echo "4. Run: docker-compose up -d"
echo ""
echo -e "${BLUE}Verify installation:${NC}"
echo "• Docker version: $(docker --version)"
echo "• Docker Compose version: $(docker-compose --version)"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "• Start services: docker-compose up -d"
echo "• View logs: docker-compose logs -f"
echo "• Stop services: docker-compose down"
echo "• Check status: docker-compose ps"
echo ""
echo -e "${BLUE}Service URLs (after deployment):${NC}"
echo "• Frontend: http://$(hostname -I | awk '{print $1}'):8082"
echo "• Backend API: http://$(hostname -I | awk '{print $1}'):8001"
echo "• Nginx Proxy: http://$(hostname -I | awk '{print $1}'):8083"
echo ""
echo -e "${YELLOW}⚠️ Remember to configure your firewall and security settings for production use!${NC}"