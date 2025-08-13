#!/bin/bash

echo "�� Starting Sentiment Analysis API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please copy env.example to .env and configure your settings."
    exit 1
fi

# Start services
echo "📦 Starting infrastructure services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Start API and workers
echo "🔥 Starting API and Celery workers..."
docker-compose up -d api celery-worker celery-beat

echo "✅ All services started!"
echo "🌐 API available at: http://localhost:5000"
echo "�� Monitor logs with: make logs"
echo "�� Stop services with: make down"