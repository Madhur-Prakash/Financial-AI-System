# Setup & Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- Groq API key

### Backend Setup

1. **Clone and navigate to project**
```bash
git clone <repository>
cd financial_ai_system
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

5. **Start backend server**
```bash
python main.py
```

Server runs on `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Start development server**
```bash
npm start
```

Frontend runs on `http://localhost:3000`

## Production Deployment

### Docker Deployment

**Dockerfile (Backend)**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY main.py .
COPY .env .

EXPOSE 8000

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
```

### Cloud Deployment Options

#### 1. AWS Deployment

**Using AWS Lambda + API Gateway**
```bash
# Install serverless framework
npm install -g serverless

# Deploy backend
serverless deploy --stage prod

# Deploy frontend to S3 + CloudFront
aws s3 sync frontend/build s3://your-bucket-name
```

**serverless.yml**
```yaml
service: financial-ai-api

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  environment:
    GROQ_API_KEY: ${env:GROQ_API_KEY}

functions:
  api:
    handler: backend.app.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

#### 2. Heroku Deployment

**Procfile**
```
web: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```

**Deploy commands**
```bash
# Create Heroku app
heroku create financial-ai-system

# Set environment variables
heroku config:set GROQ_API_KEY=your_api_key

# Deploy
git push heroku main
```

#### 3. DigitalOcean App Platform

**app.yaml**
```yaml
name: financial-ai-system
services:
- name: api
  source_dir: /
  github:
    repo: your-username/financial-ai-system
    branch: main
  run_command: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: GROQ_API_KEY
    value: your_api_key
    type: SECRET
```

### Environment Variables

#### Required
```bash
GROQ_API_KEY=your_groq_api_key_here
```

#### Optional
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Production Configuration

#### Enhanced FastAPI Configuration
```python
# backend/app.py (production additions)
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

# Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limited endpoint
@app.post("/chat")
@limiter.limit("30/minute")
async def chat(request: Request, chat_request: ChatRequest):
    # ... existing code
```

### Monitoring & Logging

#### Application Logging
```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Usage in endpoints
@app.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"Chat request: {request.message[:50]}...")
    try:
        response = master_agent.process_user_input(request)
        logger.info(f"Response type: {response.query_type}")
        return response
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing failed")
```

#### Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

### Performance Optimization

#### Caching with Redis
```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_response(expiration=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_response(expiration=1800)  # 30 minutes
async def get_insights(analysis_data):
    # ... expensive operation
```

### Security Best Practices

#### API Key Management
```python
import os
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self):
        self.cipher = Fernet(os.environ.get('ENCRYPTION_KEY'))
    
    def get_api_key(self):
        encrypted_key = os.environ.get('ENCRYPTED_GROQ_KEY')
        return self.cipher.decrypt(encrypted_key.encode()).decode()
```

#### Input Validation
```python
from pydantic import validator, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    user_context: str = Field("", max_length=500)
    
    @validator('message')
    def validate_message(cls, v):
        # Sanitize input
        import re
        return re.sub(r'[<>]', '', v)
```

### Backup & Recovery

#### Database Backup (if using database)
```bash
# PostgreSQL backup
pg_dump financial_ai_db > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump financial_ai_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### Troubleshooting

#### Common Issues

1. **Groq API Rate Limits**
```python
import time
from functools import wraps

def retry_on_rate_limit(max_retries=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
                        continue
                    raise e
            return wrapper
    return decorator
```

2. **Memory Management**
```python
import gc
import psutil

@app.middleware("http")
async def monitor_memory(request: Request, call_next):
    # Monitor memory usage
    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024 / 1024  # MB
    
    response = await call_next(request)
    
    memory_after = process.memory_info().rss / 1024 / 1024  # MB
    if memory_after > 500:  # 500MB threshold
        gc.collect()  # Force garbage collection
    
    return response
```

### Scaling Considerations

#### Horizontal Scaling
- Use load balancer (nginx, AWS ALB)
- Stateless design (no session storage)
- Database connection pooling
- Redis for shared caching

#### Vertical Scaling
- Monitor CPU/memory usage
- Optimize database queries
- Use async/await properly
- Profile code for bottlenecks