@echo off
echo �� Starting Sentiment Analysis API...

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Please copy env.example to .env and configure your settings.
    pause
    exit /b 1
)

REM Start services
echo 📦 Starting infrastructure services...
docker-compose up -d postgres redis

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Start API and workers
echo 🔥 Starting API and Celery workers...
docker-compose up -d api celery-worker celery-beat

echo ✅ All services started!
echo 🌐 API available at: http://localhost:5000
echo �� Monitor logs with: make logs
echo �� Stop services with: make down
pause