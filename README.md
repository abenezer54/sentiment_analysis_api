# Sentiment Analysis API

A scalable, asynchronous API service that analyzes the sentiment of recent social media posts about a given topic. Built with Flask, Celery, Redis, PostgreSQL, and Hugging Face transformers following Clean Architecture principles.

## Features

- **Asynchronous Processing**: Non-blocking API that queues background jobs for sentiment analysis
- **Twitter Integration**: Fetches recent tweets about specified topics using Twitter API v2
- **ML-Powered Sentiment Analysis**: Uses state-of-the-art transformer models for accurate sentiment classification
- **Scalable Architecture**: Built with Celery for distributed task processing and scheduled tasks
- **Clean Architecture**: Well-structured codebase with clear separation of concerns
- **Production Ready**: Includes proper error handling, logging, and configuration management
- **Docker Support**: Complete containerization with Docker Compose for easy deployment
- **Cross-Platform**: Windows and Unix/Linux support with dedicated startup scripts

## Architecture

The application follows Clean Architecture principles with the following layers:

```
/sentiment_analysis_api
├── app/
│   ├── api/                  # Presentation Layer (Flask)
│   │   ├── routes.py         # API endpoints
│   │   └── schemas.py        # Request/response validation
│   ├── use_cases/            # Application Business Logic
│   │   └── analyze_topic.py  # Use case orchestration
│   ├── domain/               # Enterprise Business Logic
│   │   ├── models.py         # Core domain models
│   │   ├── services.py       # Business logic services
│   │   └── interfaces.py     # Abstract contracts
│   └── infrastructure/       # Frameworks & Drivers
│       ├── repositories/     # Data access implementations
│       ├── services/         # External service integrations
│       └── task_queue/       # Celery task definitions
├── config.py                 # Configuration management
├── main.py                   # Application entry point
├── docker-compose.yml        # Docker services orchestration
├── Dockerfile                # Application containerization
├── start.sh                  # Unix/Linux startup script
├── start.bat                 # Windows startup script
├── Makefile                  # Development and deployment commands
└── requirements.txt          # Dependencies
```

## Prerequisites

- **Docker & Docker Compose** (Recommended)
- Python 3.8+ (for local development)
- PostgreSQL (if running locally)
- Redis (if running locally)
- Twitter API credentials

## Quick Start with Docker (Recommended)

### 1. Clone and Setup

```bash
git clone https://github.com/abenezer54/sentiment_analysis_api.git
cd sentiment_analysis_api
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your Twitter API credentials
# Required: TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET,
#          TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
```

### 3. Start All Services

**Windows:**

```cmd
start.bat
```

**Unix/Linux/macOS:**

```bash
chmod +x start.sh
./start.sh
```

**Or use Make:**

```bash
make up
```

### 4. Access the API

- **API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/v1/health

## Manual Installation (Alternative)

### 1. Clone the repository

```bash
git clone https://github.com/abenezer54/sentiment_analysis_api.git
cd sentiment_analysis_api
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp env.example .env
# Edit .env with your configuration
```

### 5. Set up database and Redis

```bash
# Create PostgreSQL database
createdb sentiment_analysis

# Start Redis
redis-server
```

## Configuration

Copy `env.example` to `.env` and configure the following variables:

### Required Environment Variables

- `TWITTER_BEARER_TOKEN`: Twitter API v2 Bearer Token
- `TWITTER_API_KEY`: Twitter API Key
- `TWITTER_API_SECRET`: Twitter API Secret
- `TWITTER_ACCESS_TOKEN`: Twitter Access Token
- `TWITTER_ACCESS_TOKEN_SECRET`: Twitter Access Token Secret

### Optional Environment Variables

- `FLASK_ENV`: Environment (development/production)
- `FLASK_DEBUG`: Debug mode (True/False)
- `MAX_TWEETS_PER_ANALYSIS`: Maximum tweets to analyze (default: 100)
- `SENTIMENT_MODEL_NAME`: Hugging Face model name (default: cardiffnlp/twitter-roberta-base-sentiment-latest)

## Running the Application

### Docker (Recommended)

**Start all services:**

```bash
make up
# or
docker-compose up -d
```

**Stop all services:**

```bash
make down
# or
docker-compose down
```

**View logs:**

```bash
make logs          # All services
make logs-api      # API only
make logs-worker   # Celery worker only
make logs-beat     # Celery beat only
```

**Other useful commands:**

```bash
make help          # Show all available commands
make build         # Rebuild Docker images
make restart       # Restart all services
make status        # Show service status
make shell         # Open shell in API container
make test          # Run tests in container
```

### Local Development

1. **Start the Flask application**

   ```bash
   python main.py
   ```

2. **Start Celery worker** (in a separate terminal)

   ```bash
   celery -A app.infrastructure.task_queue.tasks worker --loglevel=info
   ```

3. **Start Celery beat** (optional, for scheduled tasks)
   ```bash
   celery -A app.infrastructure.task_queue.tasks beat --loglevel=info
   ```

### Production Mode

1. **Start with Gunicorn**

   ```bash
   gunicorn -c gunicorn.conf.py main:app
   ```

2. **Start Celery worker**
   ```bash
   celery -A app.infrastructure.task_queue.tasks worker --loglevel=info
   ```

## API Documentation

### Base URL

```
http://localhost:5000/api/v1
```

### Endpoints

#### 1. Start Analysis

**POST** `/analyze`

Start a new sentiment analysis job for a topic.

**Request Body:**

```json
{
  "topic": "MLH Fellowship",
  "max_tweets": 100
}
```

**Response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Analysis job created successfully"
}
```

#### 2. Get Results

**GET** `/results/{job_id}`

Retrieve analysis results by job ID.

**Response (Pending):**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "topic": "MLH Fellowship",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": null
}
```

**Response (Completed):**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "topic": "MLH Fellowship",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:15Z",
  "positive_percentage": 65.5,
  "negative_percentage": 12.3,
  "neutral_percentage": 22.2,
  "average_polarity": 0.78,
  "total_tweets": 100,
  "analyzed_tweets": 95
}
```

**Response (Failed):**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "topic": "MLH Fellowship",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:30:05Z",
  "error_message": "Twitter API rate limit exceeded"
}
```

#### 3. Health Check

**GET** `/health`

Check API health status.

**Response:**

```json
{
  "status": "healthy",
  "service": "sentiment-analysis-api"
}
```

## Usage Examples

### Python Client Example

```python
import requests
import time

# Start analysis
response = requests.post('http://localhost:5000/api/v1/analyze', json={
    'topic': 'Python programming',
    'max_tweets': 50
})
job_id = response.json()['job_id']

# Poll for results
while True:
    response = requests.get(f'http://localhost:5000/api/v1/results/{job_id}')
    data = response.json()

    if data['status'] == 'completed':
        print(f"Analysis completed!")
        print(f"Positive: {data['positive_percentage']}%")
        print(f"Negative: {data['negative_percentage']}%")
        print(f"Neutral: {data['neutral_percentage']}%")
        break
    elif data['status'] == 'failed':
        print(f"Analysis failed: {data['error_message']}")
        break

    time.sleep(5)  # Wait 5 seconds before polling again
```

### cURL Examples

```bash
# Start analysis
curl -X POST http://localhost:5000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"topic": "Machine Learning", "max_tweets": 100}'

# Get results
curl http://localhost:5000/api/v1/results/550e8400-e29b-41d4-a716-446655440000

# Health check
curl http://localhost:5000/api/v1/health
```

## Development

### Docker Development Workflow

```bash
# Start development environment
make up

# View logs
make logs

# Run tests
make test

# Open shell in container
make shell

# Restart services after code changes
make restart
```

### Local Development

```bash
# Run tests
pytest

# Code formatting
black .

# Linting
flake8
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Deployment

### Docker (Recommended)

The project includes production-ready Docker configuration:

1. **Production Docker Compose**

   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Custom Override**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
   ```

### Manual Deployment

1. **Set up production environment**

   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@host/db
   export REDIS_URL=redis://host:6379/0
   ```

2. **Start services**

   ```bash
   # Start Gunicorn
   gunicorn -c gunicorn.conf.py main:app

   # Start Celery worker
   celery -A app.infrastructure.task_queue.tasks worker --loglevel=info
   ```

## Monitoring and Logging

The application includes comprehensive logging and monitoring:

- **Application Logs**: Structured logging for all operations
- **Error Tracking**: Detailed error messages and stack traces
- **Performance Metrics**: Request timing and resource usage
- **Health Checks**: Built-in health check endpoints
- **Docker Logs**: Easy log access with `make logs` commands

## Troubleshooting

### Common Issues

1. **Services won't start**: Check if ports 5000, 5432, and 6379 are available
2. **Twitter API errors**: Verify your Twitter API credentials in `.env`
3. **Database connection issues**: Ensure PostgreSQL is running and accessible
4. **Celery worker issues**: Check Redis connection and worker logs

### Useful Commands

```bash
# Check service status
make status

# View specific service logs
make logs-api
make logs-worker

# Restart problematic services
make restart

# Clean up and start fresh
make clean
make up
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.
