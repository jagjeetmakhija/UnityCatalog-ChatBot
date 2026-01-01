# Deploy to Hugging Face Spaces

This guide explains how to deploy the Unity Catalog Chatbot to Hugging Face Spaces.

## Prerequisites

1. **Hugging Face Account** - Create one at https://huggingface.co
2. **Git** - Installed and configured
3. **Databricks Credentials** - API key and workspace URL
4. **Anthropic API Key** - For Claude AI

## Step 1: Create a Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `unity-catalog-chatbot` (or your choice)
   - **License**: MIT (or your preference)
   - **Space SDK**: Docker
   - **Space hardware**: CPU (or GPU if needed)
4. Click **"Create Space"**

## Step 2: Clone the Space Repository

```bash
# Clone your newly created space
git clone https://huggingface.co/spaces/YOUR_USERNAME/unity-catalog-chatbot
cd unity-catalog-chatbot
```

## Step 3: Add Files

Copy these files from this repo to the cloned Space:

```bash
cp /path/to/UnityCatalog-ChatBot/{app.py,unity-catalog-chatbot.jsx,unity_catalog_service.py,index.html,requirements.txt,.env.example,config.py,conftest.py} .
cp /path/to/UnityCatalog-ChatBot/Dockerfile .
```

Or manually add the files to the Space repository.

## Step 4: Configure Environment Variables

In the Space settings on Hugging Face:

1. Go to **Settings → Variables and Secrets**
2. Add these secrets (HF will mask them):
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `DATABRICKS_HOST`: Your Databricks workspace URL
   - `DATABRICKS_TOKEN`: Your Databricks personal access token

## Step 5: Push to Hugging Face

```bash
# Add all files
git add .

# Commit
git commit -m "Initial deployment"

# Push to HF
git push
```

The Space will automatically build and deploy.

## Step 6: Access Your App

Once deployed, you can access it at:
```
https://huggingface.co/spaces/YOUR_USERNAME/unity-catalog-chatbot
```

## How It Works

- **Frontend**: React UI served from `index.html`
- **Backend**: Flask API at `/api/chat` and other endpoints
- **Port**: Automatically uses port 7860 (HF Spaces standard)
- **Static Files**: Served from the root directory

## Testing the Deployment

1. Open the Space URL
2. You'll see the setup screen asking for credentials
3. Enter your Databricks workspace details:
   - Host: `https://your-workspace.cloud.databricks.com`
   - Token: Your Databricks API token
   - Workspace ID: (optional)
4. Click "✓ Connect"
5. Type: "Create a catalog named test_catalog"
6. You should see the response and SQL preview

## Troubleshooting

### App doesn't start
- Check logs in Space settings → Logs
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies

### "Cannot reach /api/chat"
- The Flask app may not be running
- Check that port is correctly set to 7860
- Verify CORS is enabled

### Databricks connection fails
- Double-check credentials
- Ensure token hasn't expired
- Verify workspace has Unity Catalog enabled

### Frontend not loading
- Check browser console (F12) for errors
- Ensure `index.html` is in the root directory
- Clear browser cache and reload

## Security Notes

⚠️ **Important:**
- Never hardcode API keys in files
- Use Hugging Face Secrets for sensitive credentials
- Don't commit `.env` files with real credentials
- Token will be masked in HF logs

## File Structure

```
huggingface-space/
├── app.py                      ← Flask backend (serves frontend + API)
├── unity-catalog-chatbot.jsx   ← React UI component
├── unity_catalog_service.py    ← Databricks integration
├── index.html                  ← React entry point
├── requirements.txt            ← Python dependencies
├── config.py                   ← Configuration
├── Dockerfile                  ← Docker container config
└── [other config files]
```

## Next Steps

1. **Monitor**: Check Space logs for any errors
2. **Test**: Try creating a catalog, granting permissions, etc.
3. **Customize**: Modify the UI colors, add more features
4. **Share**: Share the Space URL with your team

## Support

For issues:
1. Check the Space logs
2. Review the troubleshooting section
3. Check Hugging Face documentation: https://huggingface.co/docs/hub/spaces
4. Review app logs locally first before deploying

---

**Deployment Date**: December 2025  
**Status**: Production Ready
