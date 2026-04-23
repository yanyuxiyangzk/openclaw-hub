#!/bin/bash
# OpenClawHub Deploy Script (Unix/macOS/Linux)
# Usage: ./deploy.sh [--production]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}=== OpenClawHub Deploy Script ===${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

# Parse arguments
ENV=${1:-staging}
if [ "$1" == "--production" ]; then
    ENV=production
fi

echo -e "${YELLOW}Deploying in $ENV mode${NC}"

# Load environment variables
if [ -f ".env.$ENV" ]; then
    echo "Loading .env.$ENV"
    export $(grep -v '^#' .env.$ENV | xargs)
elif [ -f ".env" ]; then
    echo "Loading .env"
    export $(grep -v '^#' .env | xargs)
fi

# Build and deploy
echo -e "${GREEN}Building Docker images...${NC}"
docker-compose -f docker/docker-compose.prod.yml build

echo -e "${GREEN}Starting services...${NC}"
docker-compose -f docker/docker-compose.prod.yml up -d

# Wait for services
echo -e "${GREEN}Waiting for services to be healthy...${NC}"
sleep 10

# Check health
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health || echo "000")
if [ "$HEALTH" == "200" ]; then
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    echo -e "Frontend: http://localhost:8080"
    echo -e "API: http://localhost:8080/api"
    echo -e "Health: http://localhost:8080/health"
else
    echo -e "${RED}✗ Health check failed (HTTP $HEALTH)${NC}"
    docker-compose -f docker/docker-compose.prod.yml logs
    exit 1
fi

echo -e "${GREEN}=== Deploy Complete ===${NC}"
