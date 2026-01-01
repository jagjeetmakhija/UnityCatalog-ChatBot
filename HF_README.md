---
title: Unity Catalog Chatbot
emoji: 💬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Unity Catalog Chatbot

A natural language chatbot for managing Databricks Unity Catalog powered by Claude AI.

## Features

✨ **Natural Language Interface**
- Ask questions in plain English
- Get instant responses from Claude AI
- No SQL knowledge required

🗂️ **Catalog Management**
- Create catalogs, schemas, and tables
- List objects across your workspace
- View table details and metadata

🔐 **Permission Management**
- Grant and revoke permissions
- Manage access control via chat
- Support for users and groups

🚀 **REST API**
- Full JSON API for integrations
- Health checks and monitoring
- Easy to embed in other apps

## Quick Start

### 1. Add Secrets

Go to **Settings → Secrets** and add:

```
DATABRICKS_HOST = https://your-workspace.databricks.com
DATABRICKS_TOKEN = dapi...your-token...
ANTHROPIC_API_KEY = sk-ant-...your-key...
```

### 2. Wait for Build

Space will auto-build (~2 min). Check **Settings → Build logs**.

### 3. Start Using

Once running, the app will be available at the Space URL.

### 4. API Endpoints

#### Health Check
```bash
GET /api/health
```

#### List Catalogs
```bash
GET /api/catalogs
```

#### List Schemas
```bash
GET /api/schemas/{catalog}
```

#### List Tables
```bash
GET /api/tables/{catalog}/{schema}
```

#### Chat (Main Endpoint)
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Create a catalog named sales_data"
}
```

## Example Requests

### Create a Catalog
```bash
curl -X POST https://your-space-url/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a catalog named sales_data"}'
```

### Grant Permissions
```bash
curl -X POST https://your-space-url/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Grant SELECT on sales_data.customers to data_analysts"
  }'
```

### List Objects
```bash
curl https://your-space-url/api/catalogs
curl https://your-space-url/api/schemas/sales_data
curl https://your-space-url/api/tables/sales_data/analytics
```

## Supported Operations

- ✅ Create catalogs
- ✅ Create schemas
- ✅ Create tables
- ✅ Grant permissions
- ✅ Revoke permissions
- ✅ List catalogs/schemas/tables
- ✅ Show permissions
- ✅ Set object owner
- ✅ Get table details
- ✅ Execute SQL (when enabled)

## Requirements

- **Databricks** workspace with Unity Catalog enabled
- **Personal Access Token** (generate in Databricks)
- **Anthropic API Key** (get from https://console.anthropic.com)

## Architecture

```
┌─────────────────────┐
│   User / Client     │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│   Flask API Server  │
│   (Port 5000)       │
└──────────┬──────────┘
           │
      ┌────┴──────┬────────────┐
      v           v            v
  Claude AI  UC Service  Config Manager
      │           │            │
      └────┬──────┴────────────┘
           v
   Databricks Unity Catalog
   + Anthropic API
```

## Local Development

```bash
# Clone repo
git clone <repo-url>
cd UnityCatalog-ChatBot

# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run tests
pytest test_chatbot.py -v

# Run server
python app.py
```

## Docker

```bash
# Build
docker build -t unitycatalog-chatbot .

# Run
docker run -p 5000:5000 \
  -e DATABRICKS_HOST="https://..." \
  -e DATABRICKS_TOKEN="..." \
  -e ANTHROPIC_API_KEY="..." \
  unitycatalog-chatbot
```

## Troubleshooting

### Build Fails
- Check **Settings → Build logs**
- Ensure `Dockerfile` exists
- Verify `requirements.txt` syntax

### App Crashes
- Check **Settings → Runtime logs**
- Verify secrets are set correctly
- Test credentials locally first

### API Returns Error
- Confirm Databricks host URL is correct
- Check token hasn't expired
- Verify Anthropic API key is valid

### Slow Responses
- Databricks API latency
- Large catalog size (many objects)
- Network connectivity

## Security Notes

⚠️ **Never commit secrets to Git**
- Use Hugging Face Secrets feature
- Rotate tokens regularly
- Use IAM roles when possible

## Performance

- **Requests**: Up to 60/min (configurable)
- **Response time**: 2-5 seconds typical
- **Catalog size**: Tested with 1000+ objects
- **Concurrent users**: Limited by Space tier

## License

MIT

## Support

- GitHub Issues: [Link to repo]
- Documentation: See `/docs`
- Discord: [Link to community]

---

**Built with ❤️ using Flask, Claude, and Databricks**

*Hugging Face Spaces - Free hosting for ML apps*
