#!/bin/bash
# deploy/scripts/dev.sh - Quick development workflow

set -e

echo "🚀 Starting CBMS-Sim development stack..."

# Copy .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    
    # Generate random secrets
    JWT_SECRET=$(openssl rand -hex 32)
    POSTGRES_PASSWORD=$(openssl rand -hex 16)
    REDIS_PASSWORD=$(openssl rand -hex 16)
    MINIO_ROOT_PASSWORD=$(openssl rand -hex 16)
    
    sed -i "s|JWT_SECRET=.*|JWT_SECRET=${JWT_SECRET}|" .env
    sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${POSTGRES_PASSWORD}|" .env
    sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASSWORD}|" .env
    sed -i "s|MINIO_ROOT_PASSWORD=.*|MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}|" .env
    
    echo "🔑 Random secrets generated"
fi

# Build and start
echo "🏗️  Building images (first time may take 5-10 min)..."
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml build

echo "🚀 Starting services..."
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml up

echo ""
echo "✅ Stack is running! Access points:"
echo "   API:      http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Web:      http://localhost:3000"
echo "   Grafana:  http://localhost:3000 (admin/admin or your .env password)"
echo "   MinIO:    http://localhost:9001 (minioadmin/...)"
echo "   Postgres: localhost:5432"
echo "   Redis:    localhost:6379"
