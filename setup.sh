#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Yura Demo Setup Pipeline...${NC}"

# 1. Build Containers
echo -e "\n${BLUE}📦 Building Docker containers...${NC}"
docker compose build

# 2. Start Database
echo -e "\n${BLUE}🗄️  Starting Database...${NC}"
docker compose up -d db

# Wait for DB to be ready
echo -e "${BLUE}⏳ Waiting for Database to initialize (10s)...${NC}"
sleep 10

# 3. Enable pgvector Extension
echo -e "\n${BLUE}🔌 Enabling pgvector extension...${NC}"
# We try to enable it; if it fails, it might already be enabled or permissions issue, but usually yura_user is superuser
docker compose exec -T db psql -U yura_user -d yura_db -c "CREATE EXTENSION IF NOT EXISTS vector;" || echo -e "${RED}⚠️  Warning: Could not enable vector extension. It might already be enabled or require manual intervention.${NC}"

# 4. Start Backend
echo -e "\n${BLUE}🔥 Starting Backend...${NC}"
docker compose up -d backend

# Wait for Backend to be ready
echo -e "${BLUE}⏳ Waiting for Backend to initialize (5s)...${NC}"
sleep 5

# 5. Run Migrations
echo -e "\n${BLUE}🔄 Running Migrations...${NC}"
docker compose exec -T backend python manage.py migrate

# 6. Create Admin User
echo -e "\n${BLUE}👤 Creating Admin User...${NC}"
docker compose exec -T backend python create_admin.py

# 7. Run Tests
echo -e "\n${BLUE}🧪 Running Unit Tests...${NC}"
echo -e "${BLUE}   Targeting apps: users, ideas, content, conversations, resumes${NC}"
if docker compose exec -T backend python manage.py test users ideas content conversations resumes; then
    echo -e "\n${GREEN}✅ All Tests Passed!${NC}"
else
    echo -e "\n${RED}❌ Tests Failed! Stopping pipeline.${NC}"
    exit 1
fi

# 8. Success Summary
echo -e "\n${GREEN}🎉 Setup Complete! The application is running.${NC}"
echo "------------------------------------------------"
echo -e "🌍 ${GREEN}API:${NC}       http://localhost:8000/api/v1/"
echo -e "🛡️  ${GREEN}Admin:${NC}     http://localhost:8000/admin/"
echo "------------------------------------------------"
echo "🔑 Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "------------------------------------------------"
