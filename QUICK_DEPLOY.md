# Quick Deployment to Hugging Face 🚀

**5-Minute Deployment Guide for Unity Catalog Chatbot**

## Option 1: Automated Script (Recommended)

### Windows
```cmd
cd c:\MyCode\UnityCatalog-ChatBot
deploy-to-huggingface.bat
```

### Linux/Mac
```bash
cd /path/to/UnityCatalog-ChatBot
chmod +x deploy-to-huggingface.sh
./deploy-to-huggingface.sh
```

The script will:
- ✅ Create a deployment package
- ✅ Initialize git repository
- ✅ Push to your Hugging Face Space
- ✅ Provide next steps for secrets configuration

## Option 2: Manual Deployment

### Step 1: Create Hugging Face Space (2 minutes)

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Configure:
   - **Name**: `unity-catalog-chatbot`
   - **License**: MIT
   - **Space SDK**: **Docker** ⚠️ Important!
   - **Hardware**: CPU basic (free)
4. Click **Create Space**

### Step 2: Clone and Push (2 minutes)

```bash
# Clone your new Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/unity-catalog-chatbot
cd unity-catalog-chatbot

# Copy these files from your project:
# - app.py
# - unity_catalog_service.py
# - unity-catalog-chatbot.jsx
# - index.html
# - requirements.txt
# - Dockerfile
# - config.py
# - conftest.py
# - sample_queries.json

# Copy README_HF.md as README.md
cp /path/to/README_HF.md README.md

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### Step 3: Configure Secrets (1 minute)

In your Space on Hugging Face:

1. Click **Settings** → **Variables and secrets**
2. Add these **Secrets**:

   | Name | Value | Where to Get |
   |------|-------|--------------|
   | `DATABRICKS_HOST` | `https://your-workspace.cloud.databricks.com` | Your Databricks workspace URL |
   | `DATABRICKS_TOKEN` | `dapi...` | Settings → User Settings → Access Tokens |
   | `ANTHROPIC_API_KEY` | `sk-ant-...` | https://console.anthropic.com |

3. Click **Save**

### Step 4: Wait for Build (2-3 minutes)

The Space will automatically build. You'll see:
- 📦 Building Docker image
- ⚙️ Installing dependencies
- ✅ Running application

### Step 5: Test Your Chatbot! 🎉

Once built, try these test queries:
1. "List all catalogs"
2. "Create a catalog called test_demo"
3. "Help - show me what you can do"

## Validation Checklist

Before deploying, verify:

- [x] All tests pass (23/23)
- [x] Python 3.11+ installed
- [x] Docker builds successfully
- [x] All required files present
- [x] Secrets configured in HF Space
- [x] Space SDK set to "Docker"

## Files Required for Deployment

```
unity-catalog-chatbot/
├── README.md (from README_HF.md)
├── Dockerfile
├── requirements.txt
├── app.py
├── unity_catalog_service.py
├── unity-catalog-chatbot.jsx
├── index.html
├── config.py
├── conftest.py
├── sample_queries.json
└── .env.example
```

## Common Issues

### Build Fails
- **Check**: SDK is set to "Docker" not "Streamlit" or "Gradio"
- **Check**: Dockerfile exists in root directory
- **Check**: Port 7860 is exposed in Dockerfile

### App Doesn't Load
- **Check**: All three secrets are configured
- **Check**: DATABRICKS_HOST starts with `https://`
- **Check**: Tokens are valid and not expired

### Can't Connect to Databricks
- **Check**: Token has proper permissions
- **Check**: Unity Catalog is enabled in workspace
- **Check**: Network/firewall settings allow connections

## Monitoring

After deployment:
1. Check **Logs** tab for any errors
2. Monitor **Settings** → **Analytics** for usage
3. Review error messages in the chat interface

## Updating Your Space

To update after deployment:

```bash
cd unity-catalog-chatbot
# Make changes to your files
git add .
git commit -m "Update: description of changes"
git push
```

The Space will automatically rebuild.

## Testing in HF Space

Use [sample_queries.json](sample_queries.json) for comprehensive testing:

### Quick Tests
```
1. List all catalogs
2. Create a catalog called test_space
3. Create schema bronze in test_space
4. Show grants on test_space
5. Delete catalog test_space
```

### Full Demo Workflow
Run the complete workflow from `sample_queries.json`:
- Create demo_lakehouse catalog
- Create bronze, silver, gold schemas
- Create sample tables
- Configure permissions
- Verify setup

## Support

- 📖 Full guide: [HF_DEPLOYMENT.md](HF_DEPLOYMENT.md)
- 🧪 Testing: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- 📚 Documentation: [README.md](README.md)

---

**Total Time**: ~5-10 minutes including build time

**Cost**: Free (uses HF free tier + your Databricks workspace)
