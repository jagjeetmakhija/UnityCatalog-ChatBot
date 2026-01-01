# ⚡ Quick Deploy to Hugging Face - 5 Minutes

## Your Deployment Package is Ready! 📦

Everything you need is prepared. Just follow these 7 steps:

---

## Step 1: Get Your Credentials (1 min)

### Databricks
1. Go to your Databricks workspace
2. Click your user icon → Settings
3. Go to **Personal Access Tokens** → **Generate new token**
4. Copy the token (format: `dapi...`)
5. Note your workspace URL (e.g., `https://your-workspace.databricks.com`)

### Anthropic
1. Visit https://console.anthropic.com
2. Click **API Keys** in sidebar
3. Click **Create Key**
4. Copy the key (format: `sk-ant-...`)

---

## Step 2: Create Hugging Face Space (2 min)

1. **Go to:** https://huggingface.co/new
2. **Fill in:**
   - **Owner:** Your username
   - **Repository name:** `unitycatalog-chatbot`
   - **Type:** Space
   - **Space SDK:** Docker
   - **License:** MIT (or your choice)
3. **Click:** Create Space

**Result:** You'll get a Space at `https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot`

---

## Step 3: Run Local Tests (1 min)

```bash
cd UnityCatalog-ChatBot

# Run tests (no credentials needed - they're mocked)
python -m pytest test_chatbot.py -v

# Expected: 23 passed ✅
```

---

## Step 4: Push Code (1 min)

```bash
# Add HF remote
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot

# Push code
git push -u huggingface main

# If main doesn't exist, try master:
# git push -u huggingface master
```

**HF will start building automatically** ⏳

---

## Step 5: Add Secrets (1 min)

1. **Go to:** Your Space Settings
   - URL: `https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot/settings`

2. **Click:** Repository Secrets

3. **Add three secrets:**

   | Name | Value |
   |------|-------|
   | `DATABRICKS_HOST` | `https://your-workspace.databricks.com` |
   | `DATABRICKS_TOKEN` | `dapi...` |
   | `ANTHROPIC_API_KEY` | `sk-ant-...` |

4. **Click:** Save after each

**Result:** Space rebuilds with secrets loaded ✅

---

## Step 6: Wait for Build (3-5 min)

- Go to Space Settings → Build logs
- Watch the Docker build happen
- Status changes to **"Running"** when ready
- Check Runtime logs for any errors

---

## Step 7: Test Your Deployment (1 min)

Once **"Running"**, test the API:

```bash
# Replace YOUR_USERNAME and check health
curl https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/health

# Response should be:
# {"status": "healthy", "service": "Unity Catalog Chatbot API"}

# List catalogs
curl https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/catalogs

# Chat
curl -X POST https://YOUR_USERNAME-unitycatalog-chatbot.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List all catalogs"}'
```

---

## 🎉 You're Done!

Your chatbot is now live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/unitycatalog-chatbot
```

**Share it:** Just send the URL to anyone - they can use it immediately!

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Check build logs. Ensure `Dockerfile` exists. |
| App crashes | Check runtime logs. Verify secrets are set. |
| API returns error | Double-check credentials. Test locally first. |
| "Port already in use" | HF assigns port automatically, should work. |

---

## Common Commands

```bash
# View logs
# Go to: Space Settings → Build logs or Runtime logs

# Update code
git add .
git commit -m "Update"
git push huggingface main

# Revert to previous version
git log --oneline
git revert <commit-hash>
git push huggingface main

# Delete Space (if needed)
# Go to Space Settings → Delete
```

---

## Next Steps

- ✅ Share the Space URL with your team
- ✅ Monitor logs in Settings
- ✅ Iterate on features (push code updates)
- ✅ Upgrade to Pro tier for custom domain ($50/mo)

---

## Files You Have

```
UnityCatalog-ChatBot/
├── HF_DEPLOYMENT.md           ← Detailed HF guide
├── HF_DEPLOYMENT_SUMMARY.md   ← Complete reference
├── DEPLOYMENT_GUIDE.md        ← All deployment options
├── deploy-to-huggingface.sh   ← Automated script (Linux/Mac)
├── deploy-to-huggingface.bat  ← Automated script (Windows)
├── .env.example               ← Environment template
├── Dockerfile                 ← Ready for HF
├── app.py                     ← Your API
├── requirements.txt           ← Dependencies
└── [other project files]
```

---

**That's it! You're deploying in 5 minutes.** ⚡

If you have questions, check the detailed guides in your repo!
