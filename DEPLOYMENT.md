# Unity Catalog Chatbot - Deployment & Operations Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Deployment Options](#deployment-options)
3. [Configuration](#configuration)
4. [Monitoring & Observability](#monitoring--observability)
5. [Security Hardening](#security-hardening)
6. [Troubleshooting](#troubleshooting)
7. [Performance Tuning](#performance-tuning)
8. [Backup & Recovery](#backup--recovery)

## Quick Start

### Local Development

```bash
# 1. Clone repository
git clone <repository-url>
cd unity-catalog-chatbot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Run the application
python app.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f unity-catalog-chatbot

# Stop services
docker-compose down
```

## Deployment Options

### Option 1: Docker on AWS ECS

```bash
# Build and tag image
docker build -t unity-catalog-chatbot:latest .
docker tag unity-catalog-chatbot:latest <aws-account-id>.dkr.ecr.<region>.amazonaws.com/unity-catalog-chatbot:latest

# Push to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.<region>.amazonaws.com
docker push <aws-account-id>.dkr.ecr.<region>.amazonaws.com/unity-catalog-chatbot:latest

# Deploy to ECS using terraform or console
```

**ECS Task Definition:**
```json
{
  "family": "unity-catalog-chatbot",
  "containerDefinitions": [
    {
      "name": "chatbot",
      "image": "<ecr-image>",
      "memory": 2048,
      "cpu": 1024,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABRICKS_TOKEN",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:databricks-token"
        },
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:anthropic-key"
        }
      ]
    }
  ]
}
```

### Option 2: Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unity-catalog-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: unity-catalog-chatbot
  template:
    metadata:
      labels:
        app: unity-catalog-chatbot
    spec:
      containers:
      - name: chatbot
        image: unity-catalog-chatbot:latest
        ports:
        - containerPort: 5000
        env:
        - name: ENVIRONMENT
          value: "production"
        envFrom:
        - secretRef:
            name: chatbot-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: unity-catalog-chatbot
spec:
  selector:
    app: unity-catalog-chatbot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

**secrets.yaml:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: chatbot-secrets
type: Opaque
stringData:
  DATABRICKS_HOST: "https://your-workspace.cloud.databricks.com"
  DATABRICKS_TOKEN: "your-token"
  ANTHROPIC_API_KEY: "your-key"
```

Deploy:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f secrets.yaml
```

### Option 3: Serverless (AWS Lambda)

**serverless.yml:**
```yaml
service: unity-catalog-chatbot

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  environment:
    DATABRICKS_HOST: ${env:DATABRICKS_HOST}
    DATABRICKS_TOKEN: ${env:DATABRICKS_TOKEN}
    ANTHROPIC_API_KEY: ${env:ANTHROPIC_API_KEY}

functions:
  chat:
    handler: lambda_handler.chat_handler
    timeout: 30
    events:
      - http:
          path: api/chat
          method: post
          cors: true
  
  health:
    handler: lambda_handler.health_handler
    events:
      - http:
          path: api/health
          method: get

plugins:
  - serverless-python-requirements
```

## Configuration

### Environment Variables

**Required:**
- `DATABRICKS_HOST`: Your Databricks workspace URL
- `DATABRICKS_TOKEN`: Personal access token or service principal token
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude

**Optional:**
- `DATABRICKS_WAREHOUSE_ID`: SQL Warehouse for executing queries
- `ENVIRONMENT`: development|staging|production (default: development)
- `SERVER_PORT`: API server port (default: 5000)
- `SERVER_WORKERS`: Number of worker processes (default: 4)
- `LOG_LEVEL`: DEBUG|INFO|WARNING|ERROR (default: INFO)
- `ENABLE_AUTH`: Enable API key authentication (default: false)
- `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 60)

### Configuration File

Create `config.yaml` for advanced configuration:

```yaml
environment: production

databricks:
  host: https://your-workspace.cloud.databricks.com
  warehouse_id: abc123

server:
  host: 0.0.0.0
  port: 5000
  workers: 4
  timeout: 120

security:
  enable_auth: true
  rate_limit: 100
  allowed_origins:
    - https://yourapp.com
    - https://admin.yourapp.com

features:
  sql_execution: true
  batch_operations: true
  audit_logging: true
  caching: true

logging:
  level: INFO
  log_to_file: true
  log_file: /var/log/chatbot/app.log
```

## Monitoring & Observability

### Health Checks

```bash
# Basic health check
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "service": "Unity Catalog Chatbot API"
}
```

### Metrics Collection

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
request_count = Counter('chatbot_requests_total', 'Total requests')
request_duration = Histogram('chatbot_request_duration_seconds', 'Request duration')
error_count = Counter('chatbot_errors_total', 'Total errors')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Logging

**Structured logging with JSON:**

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName
        }
        return json.dumps(log_data)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Application Performance Monitoring (APM)

**With DataDog:**

```python
from ddtrace import tracer

@app.before_request
def before_request():
    tracer.trace('http.request')

@app.after_request
def after_request(response):
    return response
```

## Security Hardening

### 1. API Key Authentication

```python
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key != os.getenv('API_SECRET_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/chat', methods=['POST'])
@require_api_key
def chat():
    # ... implementation
```

### 2. Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    # ... implementation
```

### 3. Input Validation

```python
from jsonschema import validate, ValidationError

chat_schema = {
    "type": "object",
    "properties": {
        "message": {"type": "string", "minLength": 1, "maxLength": 1000}
    },
    "required": ["message"]
}

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        validate(request.json, chat_schema)
    except ValidationError as e:
        return jsonify({'error': 'Invalid input'}), 400
```

### 4. Secrets Management

**AWS Secrets Manager:**

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('unity-catalog-chatbot/prod')
databricks_token = secrets['databricks_token']
```

### 5. HTTPS Enforcement

```python
@app.before_request
def before_request():
    if not request.is_secure and app.config.get('FORCE_HTTPS'):
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
```

## Troubleshooting

### Common Issues

**1. Authentication Errors**

```
Error: 401 Unauthorized
```

**Solutions:**
- Verify Databricks token is valid and not expired
- Check token has necessary permissions
- Ensure workspace URL is correct

**2. Rate Limiting**

```
Error: 429 Too Many Requests
```

**Solutions:**
- Increase rate limits in configuration
- Implement request queuing
- Use caching for repeated queries

**3. Timeout Errors**

```
Error: Request timeout
```

**Solutions:**
- Increase `SERVER_TIMEOUT` setting
- Optimize database queries
- Use async processing for long operations

**4. Memory Issues**

```
Error: Out of memory
```

**Solutions:**
- Increase container memory limits
- Reduce number of workers
- Implement pagination for large result sets

### Debug Mode

Enable detailed debugging:

```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
python app.py
```

## Performance Tuning

### 1. Caching

Implement Redis caching:

```python
import redis
from functools import wraps

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0
)

def cache_result(ttl=300):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
            
            # Execute and cache
            result = f(*args, **kwargs)
            redis_client.setex(key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_result(ttl=600)
def list_catalogs():
    # ... implementation
```

### 2. Connection Pooling

```python
from databricks.sdk import WorkspaceClient

class ConnectionPool:
    def __init__(self, size=10):
        self.pool = []
        self.size = size
        
    def get_client(self):
        # Implement connection pooling
        pass
```

### 3. Async Processing

For long-running operations:

```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def process_batch_operation(operations):
    # Process in background
    pass
```

## Backup & Recovery

### Configuration Backup

```bash
# Backup environment configuration
cp .env .env.backup.$(date +%Y%m%d)

# Backup custom configurations
tar -czf config-backup-$(date +%Y%m%d).tar.gz config.yaml *.yml
```

### Disaster Recovery Plan

1. **Database Backups**: Unity Catalog is backed up by Databricks
2. **Configuration**: Store in version control (Git)
3. **Secrets**: Use managed secret services (AWS Secrets Manager, HashiCorp Vault)
4. **Application State**: Stateless design - no local state to backup

### Recovery Procedure

```bash
# 1. Restore configuration
cp .env.backup.YYYYMMDD .env

# 2. Rebuild and redeploy
docker-compose build
docker-compose up -d

# 3. Verify health
curl http://localhost:5000/api/health

# 4. Run smoke tests
pytest tests/smoke_tests.py
```

## Production Checklist

- [ ] Environment variables configured in secrets manager
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Rate limiting configured
- [ ] Authentication enabled
- [ ] Logging configured and centralized
- [ ] Monitoring and alerting set up
- [ ] Health checks configured
- [ ] Auto-scaling policies defined
- [ ] Backup procedures documented
- [ ] Disaster recovery plan tested
- [ ] Security audit completed
- [ ] Load testing performed
- [ ] Documentation updated

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check API response times
- Verify health check status

**Weekly:**
- Review performance metrics
- Check for security updates
- Analyze usage patterns

**Monthly:**
- Rotate credentials
- Review and update dependencies
- Performance optimization review
- Security audit

### Upgrade Procedure

```bash
# 1. Test in staging
git checkout develop
docker-compose -f docker-compose.staging.yml up -d

# 2. Run tests
pytest tests/

# 3. Deploy to production
git checkout main
git merge develop
docker-compose build
docker-compose up -d --no-deps chatbot

# 4. Verify deployment
curl http://localhost:5000/api/health
```

## Support

For production issues:
1. Check logs: `docker-compose logs chatbot`
2. Verify configuration: Review .env file
3. Test connectivity: `curl http://localhost:5000/api/health`
4. Review documentation: README.md
5. Contact support: [Your support channel]
