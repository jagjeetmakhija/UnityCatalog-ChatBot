# Hugging Face Spaces Deployment Summary

## What Was Created

### 📄 Files for HF Deployment

1. **[HF_DEPLOYMENT.md](HF_DEPLOYMENT.md)** - Quick 5-minute setup guide
2. **[HF_README.md](HF_README.md)** - Hugging Face Space metadata & documentation
3. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Updated with HF Spaces section

## Step-by-Step Deployment

### Phase 1: Create Space (2 minutes)
```bash
# 1. Visit https://huggingface.co/new
# 2. Fill in:
#    - Name: unitycatalog-chatbot
#    - Type: Space
#    - Runtime: Docker
# 3. Click "Create Space"
```

### Phase 2: Setup Files (3 minutes)
```bash
# 1. Clone the space
git clone https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot
cd unitycatalog-chatbot

# 2. Copy project files
cp -r ../UnityCatalog-ChatBot/* .

# 3. Verify files:
# ✅ app.py
# ✅ unity_catalog_service.py
# ✅ config.py
# ✅ requirements.txt
# ✅ Dockerfile
# ✅ README.md (use HF_README.md content)
```

### Phase 3: Add Secrets (2 minutes)
```
Go to Space Settings → Secrets → Add three:

1. DATABRICKS_HOST
   Value: https://your-workspace.databricks.com

2. DATABRICKS_TOKEN
   Value: dapi... (your personal access token)

3. ANTHROPIC_API_KEY
   Value: sk-ant-... (your API key)
```

### Phase 4: Deploy (3 minutes)
```bash
# 1. Push to HF
git add .
git commit -m "Initial deployment"
git push

# 2. Space auto-builds and deploys
# 3. Check build logs in Settings
# 4. App goes live! 🚀
```

## Total Time: ~10 minutes ⏱️

---

## Access Your App

**Live URL:** `https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot`

**API Base:** `https://YOUR_USERNAME-unitycatalog-chatbot.hf.space`

### Test Endpoints

```bash
# Health
curl https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/health

# Catalogs
curl https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/catalogs

# Chat
curl -X POST https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all catalogs"}'
```

---

## Key Features on HF Spaces

| Feature | Details |
|---------|---------|
| **Hosting** | Free (or Pro for $50/mo) |
| **Runtime** | Docker container |
| **CPU** | 2 vCPU (free) / dedicated (pro) |
| **Uptime** | Best effort / 99.9% (pro) |
| **Scaling** | Auto-scales with traffic |
| **Secrets** | Environment variables (hidden) |
| **Custom Domain** | Pro tier only |
| **Logs** | Real-time in Settings |

---

## What Happens When You Push

```
git push
   ↓
HF receives commit
   ↓
Triggers build
   ↓
- Reads Dockerfile
- Installs dependencies from requirements.txt
- Builds Docker image (~2-3 min)
   ↓
Loads secrets from Space Settings
   ↓
Starts container on public URL
   ↓
App is live! 🎉
```

---

## Updates & Rollbacks

### Push Updates
```bash
# Make changes to code
# e.g., edit app.py

git add .
git commit -m "Fix bug in chat endpoint"
git push
# Space rebuilds automatically
```

### Revert Changes
```bash
# View git history
git log --oneline

# Revert to previous commit
git revert HEAD
git push
# Space rebuilds with old code
```

---

## Monitoring

### View Logs
1. Go to Space → **Settings**
2. **Build logs** - Shows Docker build output
3. **Runtime logs** - Shows running application output
4. Logs updated in real-time

### Common Errors

**"ModuleNotFoundError: No module named 'X'"**
- Add to `requirements.txt`
- Push changes
- Space rebuilds

**"Connection refused to Databricks"**
- Check `DATABRICKS_HOST` in Secrets
- Verify it includes `https://`
- Ensure token hasn't expired

**"Port already in use"**
- HF Spaces assigns port automatically
- Check your `app.py` respects `SERVER_PORT` env var

**"Build timeout"**
- If build takes >30 min, it's canceled
- Check requirements.txt for slow installs
- Try Docker layer caching

---

## File Reference

### What Gets Deployed

```
unitycatalog-chatbot/
├── app.py                      # Flask server
├── unity_catalog_service.py    # Databricks operations
├── config.py                   # Configuration
├── conftest.py                 # Test fixtures
├── test_chatbot.py            # Tests (optional)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── README.md                  # HF Space description
├── .gitignore                # Exclude secrets & cache
└── (other supporting files)
```

### Don't Include
- ❌ `.env` file (use Secrets instead)
- ❌ `__pycache__/`
- ❌ `.git` directory (create fresh)
- ❌ Virtual environments
- ❌ Build artifacts

---

## Scaling & Costs

### Free Tier
- 2 vCPU, 16GB RAM
- Shared infrastructure
- Best-effort uptime
- Rate limited (but sufficient for testing)

### Pro Tier
- Dedicated infrastructure
- 99.9% SLA
- Custom domain
- $50/month

### When to Upgrade
- ✅ Production workloads
- ✅ High traffic (100+ requests/min)
- ✅ Custom domain needed
- ✅ SLA requirements

---

## Sharing Your Space

### Public Link
Just share the Space URL:
```
https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot
```

### Embed in Website
```html
<iframe
  src="https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot?embed=true"
  frameborder="0"
  width="800"
  height="600"
></iframe>
```

### Add to Collections
- Create collection on HF Hub
- Add Space to it
- Share collection link

---

## Integration Examples

### Use as Backend API

```python
import requests

API_URL = "https://YOUR_USERNAME-unitycatalog-chatbot.hf.space"

# Chat
response = requests.post(
    f"{API_URL}/api/chat",
    json={"message": "Create a catalog named demo"}
)
print(response.json())

# List catalogs
catalogs = requests.get(f"{API_URL}/api/catalogs").json()
print(catalogs)
```

### Embed in Slack Bot

```python
from slack_bolt import App

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.message("catalog")
def handle_catalog(message, say):
    response = requests.post(
        "https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/chat",
        json={"message": message["text"]}
    )
    say(response.json()["message"])

app.start(port=int(os.environ.get("PORT", 3000)))
```

### Use in Streamlit App

```python
import streamlit as st
import requests

st.title("Unity Catalog Manager")

message = st.text_input("Ask me anything about your catalog...")

if st.button("Send"):
    response = requests.post(
        "https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/chat",
        json={"message": message}
    )
    st.write(response.json())
```

---

## Troubleshooting Checklist

Before contacting support:

- [ ] Secrets are set in Space Settings
- [ ] Databricks token is valid (not expired)
- [ ] Anthropic API key is correct
- [ ] `Dockerfile` exists in repo root
- [ ] `requirements.txt` is valid Python
- [ ] Build logs show no errors
- [ ] Runtime logs show app started
- [ ] Test `/api/health` endpoint first
- [ ] Try locally with same credentials

---

## Next Steps

1. ✅ Create Space on HF
2. ✅ Push code
3. ✅ Add secrets
4. ✅ Wait for build
5. ✅ Test endpoints
6. ✅ Share with team
7. ✅ Monitor logs
8. ✅ Iterate on features

---

## Resources

- **Hugging Face Docs:** https://huggingface.co/docs/hub/spaces
- **Docker Guide:** https://docs.docker.com/
- **Flask Docs:** https://flask.palletsprojects.com/
- **Databricks API:** https://docs.databricks.com/api/workspace
- **Claude API:** https://docs.anthropic.com/

---

**Your chatbot is now live on Hugging Face Spaces! 🚀**

Questions? Check the logs, review error messages, or visit HF community.
