#!/bin/bash
# Schema Validator Pro - Installation Script for Production
# This script installs the backend service on a Linux server

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Schema Validator Pro - Installation${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERROR: Please run as root (use sudo)${NC}"
    exit 1
fi

# Installation directory
INSTALL_DIR="/opt/schema-validator-pro"

# Check if Python 3.9+ is installed
echo -e "${GREEN}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "  Found Python ${PYTHON_VERSION}"

# Create installation directory
echo -e "${GREEN}Creating installation directory...${NC}"
mkdir -p ${INSTALL_DIR}
cd ${INSTALL_DIR}

# Copy files (assuming script is run from project root)
echo -e "${GREEN}Copying files...${NC}"
cp -r backend ${INSTALL_DIR}/
cp -r config ${INSTALL_DIR}/
cp -r scripts ${INSTALL_DIR}/
cp .env.example ${INSTALL_DIR}/

# Create virtual environment
echo -e "${GREEN}Creating virtual environment...${NC}"
python3 -m venv ${INSTALL_DIR}/venv

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
${INSTALL_DIR}/venv/bin/pip install --upgrade pip
${INSTALL_DIR}/venv/bin/pip install -r ${INSTALL_DIR}/config/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ${INSTALL_DIR}/.env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp ${INSTALL_DIR}/.env.example ${INSTALL_DIR}/.env
    echo -e "${RED}IMPORTANT: Edit ${INSTALL_DIR}/.env and configure for production!${NC}"
fi

# Set permissions
echo -e "${GREEN}Setting permissions...${NC}"
chown -R www-data:www-data ${INSTALL_DIR}
chmod 600 ${INSTALL_DIR}/.env
chmod +x ${INSTALL_DIR}/scripts/*.sh

# Create logs directory
mkdir -p ${INSTALL_DIR}/logs
chown www-data:www-data ${INSTALL_DIR}/logs

# Install systemd service
echo -e "${GREEN}Installing systemd service...${NC}"
cp ${INSTALL_DIR}/config/schema-validator-pro.service /etc/systemd/system/
systemctl daemon-reload

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Edit configuration: nano ${INSTALL_DIR}/.env"
echo -e "  2. Enable service: systemctl enable schema-validator-pro"
echo -e "  3. Start service: systemctl start schema-validator-pro"
echo -e "  4. Check status: systemctl status schema-validator-pro"
echo -e "  5. View logs: journalctl -u schema-validator-pro -f"
echo ""
echo -e "${RED}SECURITY CHECKLIST:${NC}"
echo -e "  [ ] Configure ALLOWED_ORIGINS in .env"
echo -e "  [ ] Set DEBUG=false in .env"
echo -e "  [ ] Generate and set API_KEY in .env"
echo -e "  [ ] Configure firewall (allow port 8000)"
echo -e "  [ ] Set up SSL/TLS (use nginx reverse proxy)"
echo ""

