#!/bin/bash
# Schema Validator Pro - Production Startup Script
# This script starts the FastAPI backend service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Schema Validator Pro - Starting Backend${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and configure it:${NC}"
    echo -e "  cp .env.example .env"
    echo -e "  nano .env"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r config/requirements.txt

# Check if running in production
if [ "${APP_ENV}" = "production" ]; then
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}WARNING: Running in PRODUCTION mode${NC}"
    echo -e "${YELLOW}========================================${NC}"
    
    # Validate critical environment variables
    if [ "${ALLOWED_ORIGINS}" = "*" ] || [ -z "${ALLOWED_ORIGINS}" ]; then
        echo -e "${RED}ERROR: ALLOWED_ORIGINS must be set to specific domains in production!${NC}"
        echo -e "${YELLOW}Current value: ${ALLOWED_ORIGINS}${NC}"
        exit 1
    fi
    
    if [ "${DEBUG}" = "true" ]; then
        echo -e "${RED}ERROR: DEBUG must be false in production!${NC}"
        exit 1
    fi
    
    # Use production settings
    WORKERS=${WORKERS:-4}
    LOG_LEVEL=${LOG_LEVEL:-info}
    RELOAD_FLAG=""
else
    echo -e "${GREEN}Running in DEVELOPMENT mode${NC}"
    WORKERS=1
    LOG_LEVEL=${LOG_LEVEL:-debug}
    RELOAD_FLAG="--reload"
fi

# Create logs directory
mkdir -p logs

# Start the server
echo -e "${GREEN}Starting FastAPI server...${NC}"
echo -e "  Host: ${API_HOST:-0.0.0.0}"
echo -e "  Port: ${API_PORT:-8000}"
echo -e "  Workers: ${WORKERS}"
echo -e "  Log Level: ${LOG_LEVEL}"
echo -e "  Allowed Origins: ${ALLOWED_ORIGINS}"
echo -e "${GREEN}========================================${NC}"

exec uvicorn backend.main:app \
    --host "${API_HOST:-0.0.0.0}" \
    --port "${API_PORT:-8000}" \
    --workers ${WORKERS} \
    --log-level ${LOG_LEVEL} \
    ${RELOAD_FLAG}

