# UnityCatalog-ChatBot: Step-by-Step Deployment Guide

## Overview
This guide covers deploying the Unity Catalog ChatBot locally, in Docker, and to cloud platforms (AWS ECS, Kubernetes, Azure, etc.).

---

## Part 1: Local Development Setup

### Prerequisites
- **Python 3.9+** (3.11+ recommended)
- **pip** (Python package manager)
- **Git**
- **Databricks workspace** with:
  - Host URL (e.g., `https://your-workspace.databricks.com`)
  - Personal Access Token (PAT)
  - Warehouse ID (optional, for SQL execution)
- **Anthropic API key** (Claude access)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd UnityCatalog-ChatBot
```

### Step 2: Create Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```env
# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.databricks.com
DATABRICKS_TOKEN=your-personal-access-token
DATABRICKS_WAREHOUSE_ID=your-warehouse-id  # Optional

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-your-api-key

# Server Configuration (Optional)
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
SERVER_WORKERS=4
FLASK_ENV=development

# Feature Flags (Optional)
ENABLE_AUTH=false
ENABLE_SQL_EXECUTION=false
LOG_LEVEL=INFO
```

**Important:** Never commit `.env` to version control. Add it to `.gitignore`:
```
.env
*.pyc
__pycache__/
venv/
```

### Step 5: Run Tests (Mock-Only, No Credentials Required)
```bash
# Run all tests
pytest test_chatbot.py -v

# Run specific test class
pytest test_chatbot.py::TestUnityCatalogService -v

# Run with coverage
pytest test_chatbot.py --cov=. --cov-report=html
```

Expected output:
```
======================== 23 passed in 0.52s =======================
```

### Step 6: Run Development Server
```bash
python app.py
```

Server starts on `http://localhost:5000`

### Step 7: Test API Endpoints
```bash
# Health check
curl http://localhost:5000/api/health

# List catalogs
curl http://localhost:5000/api/catalogs

# Chat endpoint
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a catalog named sales_data"}'
```

---

## Part 2: Docker Deployment

### Step 1: Build Docker Image
```bash
docker build -t unitycatalog-chatbot:latest .
```

### Step 2: Run Container (Development)
```bash
docker run -p 5000:5000 \
  -e DATABRICKS_HOST="https://your-workspace.databricks.com" \
  -e DATABRICKS_TOKEN="your-token" \
  -e ANTHROPIC_API_KEY="sk-ant-your-key" \
  unitycatalog-chatbot:latest
```

### Step 3: Run with Docker Compose
```bash
docker-compose up -d
```

Check logs:
```bash
docker-compose logs -f app
```

Stop containers:
```bash
docker-compose down
```

### Step 4: Verify Container Health
```bash
curl http://localhost:5000/api/health
```

---

## Part 3: Cloud Deployment

### AWS ECS (Elastic Container Service)

#### Prerequisites
- AWS account with ECS access
- ECR (Elastic Container Registry) repository created
- IAM role for ECS task execution

#### Steps
1. **Push image to ECR:**
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag unitycatalog-chatbot:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/unitycatalog-chatbot:latest

# Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/unitycatalog-chatbot:latest
```

2. **Create ECS Task Definition** (JSON):
```json
{
  "family": "unitycatalog-chatbot",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/unitycatalog-chatbot:latest",
      "portMappings": [{"containerPort": 5000, "hostPort": 5000}],
      "environment": [
        {"name": "DATABRICKS_HOST", "value": "https://your-workspace.databricks.com"},
        {"name": "SERVER_HOST", "value": "0.0.0.0"},
        {"name": "SERVER_PORT", "value": "5000"}
      ],
      "secrets": [
        {"name": "DATABRICKS_TOKEN", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/unitycatalog-chatbot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512"
}
```

3. **Create ECS Service** using AWS Console or CLI:
```bash
aws ecs create-service \
  --cluster my-cluster \
  --service-name unitycatalog-chatbot \
  --task-definition unitycatalog-chatbot:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

4. **Monitor service:**
```bash
aws ecs describe-services \
  --cluster my-cluster \
  --services unitycatalog-chatbot
```

### Kubernetes Deployment

#### Prerequisites
- Kubernetes cluster (EKS, AKS, GKE, or local)
- `kubectl` CLI configured
- Docker image pushed to container registry

#### Steps

1. **Create Kubernetes Secrets:**
```bash
kubectl create secret generic unitycatalog-secrets \
  --from-literal=DATABRICKS_TOKEN='your-token' \
  --from-literal=ANTHROPIC_API_KEY='sk-ant-your-key'
```

2. **Create Deployment (deployment.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unitycatalog-chatbot
  labels:
    app: unitycatalog-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: unitycatalog-chatbot
  template:
    metadata:
      labels:
        app: unitycatalog-chatbot
    spec:
      containers:
      - name: app
        image: your-registry/unitycatalog-chatbot:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABRICKS_HOST
          value: "https://your-workspace.databricks.com"
        - name: SERVER_HOST
          value: "0.0.0.0"
        - name: SERVER_PORT
          value: "5000"
        envFrom:
        - secretRef:
            name: unitycatalog-secrets
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
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: unitycatalog-chatbot-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 5000
  selector:
    app: unitycatalog-chatbot
```

3. **Deploy to Kubernetes:**
```bash
kubectl apply -f deployment.yaml
```

4. **Monitor deployment:**
```bash
# Check status
kubectl get pods -l app=unitycatalog-chatbot

# Check logs
kubectl logs -f deployment/unitycatalog-chatbot

# Get service endpoint
kubectl get service unitycatalog-chatbot-service
```

### Azure Container Instances (ACI)

1. **Push image to Azure Container Registry:**
```bash
az acr build --registry your-acr-name \
  --image unitycatalog-chatbot:latest .
```

2. **Deploy to ACI:**
```bash
az container create \
  --resource-group your-rg \
  --name unitycatalog-chatbot \
  --image your-acr-name.azurecr.io/unitycatalog-chatbot:latest \
  --cpu 1 --memory 1 \
  --ports 5000 \
  --environment-variables \
    DATABRICKS_HOST="https://your-workspace.databricks.com" \
    SERVER_HOST="0.0.0.0" \
    SERVER_PORT="5000" \
  --secure-environment-variables \
    DATABRICKS_TOKEN="your-token" \
    ANTHROPIC_API_KEY="sk-ant-your-key"
```

### Hugging Face Spaces (Docker)

#### Prerequisites
- Hugging Face account (free at https://huggingface.co/join)
- Repository on Hugging Face Hub (create at https://huggingface.co/new)

#### Step 1: Create Hugging Face Repository
1. Go to https://huggingface.co/new
2. Enter repository name: `unitycatalog-chatbot`
3. Select **Space** type
4. Choose **Docker** runtime
5. Click **Create repository**

#### Step 2: Clone Space Repository
```bash
git clone https://huggingface.co/spaces/your-username/unitycatalog-chatbot
cd unitycatalog-chatbot
```

#### Step 3: Copy Project Files
```bash
# Copy source files
cp -r ../UnityCatalog-ChatBot/* .

# Ensure key files are present:
# - app.py
# - unity_catalog_service.py
# - config.py
# - requirements.txt
# - Dockerfile
# - test_chatbot.py (optional)
```

#### Step 4: Create `README.md` for Space
```markdown
---
title: Unity Catalog Chatbot
emoji: 💬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Unity Catalog Chatbot

Natural language interface for Databricks Unity Catalog operations powered by Claude AI.

## Features
- Create catalogs, schemas, and tables via natural language
- Grant and revoke permissions
- List objects across Unity Catalog
- Execute SQL queries

## API Endpoints
- `GET /api/health` - Health check
- `POST /api/chat` - Chat with Claude to manage Unity Catalog
- `GET /api/catalogs` - List all catalogs
- `GET /api/schemas/<catalog>` - List schemas
- `GET /api/tables/<catalog>/<schema>` - List tables

## Environment Variables
Required:
- `DATABRICKS_HOST` - Databricks workspace URL
- `DATABRICKS_TOKEN` - Personal access token
- `ANTHROPIC_API_KEY` - Claude API key

Optional:
- `SERVER_PORT` - Port to run on (default: 5000)
- `LOG_LEVEL` - Logging level (default: INFO)
```

#### Step 5: Create `secrets.toml` for Credentials
Create `.streamlit/secrets.toml` (Hugging Face Spaces will hide these):

**⚠️ IMPORTANT: Never commit secrets to git**

Instead, use Hugging Face Secrets management:

1. Go to your Space Settings → Secrets
2. Add secrets:
   - `DATABRICKS_HOST` = `https://your-workspace.databricks.com`
   - `DATABRICKS_TOKEN` = your token
   - `ANTHROPIC_API_KEY` = your API key

Or set via UI environment variables in Space settings.

#### Step 6: Update Dockerfile for Space (if needed)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

CMD ["python", "app.py"]
```

#### Step 7: Push to Hugging Face
```bash
# Configure git with HF credentials
git config user.name "Your Name"
git config user.email "your-email@example.com"

# Add files
git add .

# Commit
git commit -m "Initial deployment"

# Push (triggers auto-build and deployment)
git push
```

**Space will automatically:**
- Build Docker image
- Deploy to Hugging Face infrastructure
- Provide public URL: `https://huggingface.co/spaces/your-username/unitycatalog-chatbot`

#### Step 8: Verify Deployment
```bash
# Once Space is running, test the endpoint:
curl https://your-username-unitycatalog-chatbot.hf.space/api/health

# Chat endpoint
curl -X POST https://your-username-unitycatalog-chatbot.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all catalogs"}'
```

#### Step 9: Set Secrets in Hugging Face UI
1. Go to Space → Settings → Secrets
2. Add environment variables:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
   - `ANTHROPIC_API_KEY`

3. Space will restart automatically with secrets loaded

#### Troubleshooting Hugging Face Spaces

**Issue: "Build failed"**
- Check **Build logs** in Space settings
- Ensure `Dockerfile` is present
- Verify `requirements.txt` has all dependencies

**Issue: "Application won't start"**
- Check **Runtime logs** in Space
- Verify environment variables are set in Secrets
- Test locally: `docker build -t test . && docker run -p 5000:5000 test`

**Issue: "Port already in use"**
- Hugging Face assigns a port automatically
- Ensure `app.py` uses environment variable for port:
```python
if __name__ == '__main__':
    port = int(os.getenv("SERVER_PORT", 5000))
    app.run(host='0.0.0.0', port=port)
```

**Issue: "API calls timeout"**
- Databricks/Anthropic credentials invalid
- Network connectivity issue
- Test locally first with real credentials

#### Hugging Face Space Features

- **Public URL:** `https://huggingface.co/spaces/your-username/unitycatalog-chatbot`
- **Auto-scaling:** Handles traffic spikes
- **Free tier:** Up to 2 CPU cores (enough for light use)
- **Persistent storage:** `/tmp` directory available (ephemeral)
- **Custom domain:** Upgrade to pro for custom domains

#### Sharing Your Space

1. Go to Space page
2. Click **Share** button
3. Copy shareable link or embed code:
```html
<iframe
  src="https://huggingface.co/spaces/your-username/unitycatalog-chatbot?embed=true"
  frameborder="0"
  width="800"
  height="600"
></iframe>
```

---

## Part 4: Production Configuration

### Security Best Practices

1. **Enable Authentication:**
```env
ENABLE_AUTH=true
API_KEY_HEADER=X-API-Key
```

Add API key header to requests:
```bash
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/health
```

2. **Rate Limiting:**
```env
RATE_LIMIT_PER_MINUTE=60
```

3. **HTTPS/TLS:**
Use reverse proxy (Nginx, HAProxy) to terminate TLS:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
}
```

4. **Environment Variables:**
Use secret management (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault):
```bash
# AWS
aws secretsmanager get-secret-value --secret-id unitycatalog-secrets

# Azure
az keyvault secret show --vault-name your-vault --name DATABRICKS_TOKEN
```

### Logging & Monitoring

1. **Enable comprehensive logging:**
```env
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE_PATH=/var/log/chatbot.log
```

2. **Application Insights / DataDog / CloudWatch:**
Logs are automatically captured by container orchestration platforms.

### Performance Tuning

1. **Gunicorn workers** (production):
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

2. **Caching:**
```env
ENABLE_CACHING=true
CACHE_TTL=300
```

---

## Part 5: Health Checks & Validation

### Pre-Deployment Checklist

- [ ] All tests pass: `pytest test_chatbot.py -v`
- [ ] `.env` file configured with valid credentials
- [ ] Docker image builds successfully
- [ ] Health endpoint responds: `curl /api/health`
- [ ] Sample requests succeed (catalog listing, chat)
- [ ] Logs show no errors

### Post-Deployment Validation

```bash
# Health check
curl https://your-api-endpoint/api/health

# Test chat endpoint
curl -X POST https://your-api-endpoint/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"message": "List all catalogs"}'

# Check logs
kubectl logs deployment/unitycatalog-chatbot  # K8s
docker logs <container-id>  # Docker
aws logs tail /ecs/unitycatalog-chatbot --follow  # ECS
```

---

## Part 6: Troubleshooting

### Common Issues

**1. "Cannot configure default credentials"**
- Ensure `.env` file has valid `DATABRICKS_HOST` and `DATABRICKS_TOKEN`
- Verify token format (starts with `dapi`)

**2. "Invalid Anthropic API key"**
- Confirm key starts with `sk-ant-`
- Check key has not expired

**3. "Port 5000 already in use"**
```bash
# Kill process using port
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000 & taskkill /PID <PID> /F  # Windows
```

**4. Docker build fails**
```bash
docker build --no-cache -t unitycatalog-chatbot:latest .
```

**5. Tests fail in CI/CD**
- Tests use mocks and don't require credentials
- If failing, check Python version (3.9+) and pytest version

### Get Help

Check logs for detailed error messages:
```bash
# Local
python app.py  # stdout

# Docker
docker logs <container-name>

# Kubernetes
kubectl logs <pod-name> -c app
```

---

## Part 7: Scaling & Maintenance

### Horizontal Scaling

- **Docker Compose:** Increase `replicas` in docker-compose.yml
- **Kubernetes:** `kubectl scale deployment unitycatalog-chatbot --replicas=5`
- **ECS:** Update desired task count in AWS Console

### Updates & Rollbacks

1. **Build new image:**
```bash
docker build -t unitycatalog-chatbot:v1.1.0 .
```

2. **Push to registry:**
```bash
docker push your-registry/unitycatalog-chatbot:v1.1.0
```

3. **Update deployment:**
```bash
# Kubernetes
kubectl set image deployment/unitycatalog-chatbot \
  app=your-registry/unitycatalog-chatbot:v1.1.0

# ECS (update task definition version)
aws ecs update-service \
  --cluster my-cluster \
  --service unitycatalog-chatbot \
  --task-definition unitycatalog-chatbot:2
```

4. **Rollback if needed:**
```bash
# Kubernetes
kubectl rollout undo deployment/unitycatalog-chatbot

# ECS
aws ecs update-service \
  --cluster my-cluster \
  --service unitycatalog-chatbot \
  --task-definition unitycatalog-chatbot:1
```

---

## Summary

| Deployment Type | Complexity | Best For |
|---|---|---|
| **Local** | Easy | Development, testing |
| **Docker** | Medium | Single machine, CI/CD |
| **Kubernetes** | Hard | Enterprise, multi-region, auto-scaling |
| **ECS** | Medium | AWS-only deployments |
| **ACI** | Medium | Quick Azure deployments |

Choose based on your infrastructure and scaling needs.
