# Deploy UnityCatalog-ChatBot on Hugging Face Spaces

Quick 5-minute deployment guide for Hugging Face Spaces.

## Prerequisites
- Hugging Face account (free signup: https://huggingface.co/join)
- Databricks credentials (host + token)
- Anthropic API key

## Quick Start

### 1️⃣ Create Space on Hugging Face
```bash
# Go to: https://huggingface.co/new
# - Name: unitycatalog-chatbot
# - Type: Space
# - Runtime: Docker
# - Click "Create Space"
```

### 2️⃣ Clone the Space
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot
cd unitycatalog-chatbot
```

### 3️⃣ Copy Project Files
```bash
# Copy all files from UnityCatalog-ChatBot to your Space
cp -r ../UnityCatalog-ChatBot/* .

# Required files:
# - app.py
# - unity_catalog_service.py
# - config.py
# - requirements.txt
# - Dockerfile
# - README.md (already created)
```

### 4️⃣ Add README for Space
Create `README.md`:
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

Chat interface for Databricks Unity Catalog management.

## Setup
Add secrets in Space settings:
- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `ANTHROPIC_API_KEY`

Visit https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot
```

### 5️⃣ Push to Hugging Face
```bash
git add .
git commit -m "Deploy to HF Spaces"
git push
```

### 6️⃣ Add Secrets
1. Go to Space → **Settings** → **Secrets**
2. Add three secrets:
   - `DATABRICKS_HOST` = `https://your-workspace.databricks.com`
   - `DATABRICKS_TOKEN` = your PAT
   - `ANTHROPIC_API_KEY` = your key

3. Space rebuilds automatically ✅

### 7️⃣ Access Your App
- URL: `https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot`
- API: `https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/`

## Test Endpoints

```bash
# Health check
curl https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/health

# List catalogs
curl https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/catalogs

# Chat
curl -X POST https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a catalog named demo"}'
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check build logs in Settings. Verify Dockerfile exists. |
| App crashes | Check runtime logs. Ensure secrets are set. |
| API returns 500 | Credentials invalid. Test locally first. |
| "Port already in use" | App should auto-detect port. Check `app.py`. |

## Monitoring

View logs in Space:
1. **Settings** → **Build logs** (deployment)
2. **Settings** → **Runtime logs** (application)

## Upgrade Options

- **Free**: 2 CPU, shared GPU, variable uptime
- **Pro**: $50/month, dedicated resources, custom domain

---

## File Checklist

Before pushing, ensure you have:

- [ ] `app.py` - Flask server
- [ ] `unity_catalog_service.py` - UC operations
- [ ] `config.py` - Configuration management
- [ ] `requirements.txt` - Python dependencies
- [ ] `Dockerfile` - Container definition
- [ ] `README.md` - Space description (with metadata)
- [ ] `.gitignore` - Exclude `.env` and `__pycache__`

## Commands Quick Reference

```bash
# Clone space
git clone https://huggingface.co/spaces/username/unitycatalog-chatbot

# Push updates
git add . && git commit -m "Update" && git push

# View logs
# Go to: https://huggingface.co/spaces/username/unitycatalog-chatbot/settings

# Delete space (if needed)
# Go to: https://huggingface.co/spaces/username/unitycatalog-chatbot/settings → Delete
```

---

**Your app will be live in 2-5 minutes!** 🚀
