# 🚀 Quick Start Guide - Unity Catalog Chatbot

## ⚡ 5-Minute Deployment

### Step 1: Get Your Credentials (2 minutes)

#### Databricks:
1. Login to your Databricks workspace
2. Click profile → Settings → Developer → Access Tokens
3. Generate new token → **Copy it immediately**
4. Copy your workspace URL from browser (e.g., `https://adb-xxxx.azuredatabricks.net`)

#### Anthropic:
1. Go to https://console.anthropic.com
2. Sign up/Login → API Keys
3. Create key → **Copy it immediately**

---

### Step 2: Configure Environment (1 minute)

```bash
# Create .env file
cat > .env << 'EOF'
DATABRICKS_HOST=https://your-workspace.cloud.databricks.net
DATABRICKS_TOKEN=dapi_your_token_here
ANTHROPIC_API_KEY=sk-ant-api03-your_key_here
EOF
```

**Replace with your actual credentials!**

---

### Step 3: Deploy (2 minutes)

**Option A: Automated Deployment (Recommended)**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Option B: Manual Deployment**
```bash
# Install dependencies
pip install -r requirements.txt

# Start application
python app.py
```

**Option C: Docker**
```bash
docker-compose up -d
```

---

### Step 4: Test (30 seconds)

```bash
# Health check
curl http://localhost:5000/api/health

# Test chatbot
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "list all catalogs"}'
```

---

## ✅ You're Done!

**API is running at:** http://localhost:5000

**Try these commands:**
- `"help"` - See all available commands
- `"list all catalogs"` - List Unity Catalog catalogs
- `"create a catalog named test_demo"` - Create a catalog
- `"grant SELECT on main to user@example.com"` - Grant permissions

---

## 🧪 Run Full Tests

```bash
chmod +x test.sh
./test.sh
```

---

## 📊 Example Usage

### List Catalogs
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "list all catalogs"}'
```

### Create Catalog
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create a catalog named sales_data"}'
```

### Create Schema
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create schema analytics in sales_data"}'
```

### Grant Permission
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "grant SELECT on sales_data to analysts@company.com"}'
```

---

## 🛠️ Troubleshooting

### App won't start?
```bash
# Check logs
tail -f app.log

# Verify credentials
cat .env

# Test Databricks connection
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  $DATABRICKS_HOST/api/2.0/clusters/list
```

### Port already in use?
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>
```

### Dependencies error?
```bash
# Upgrade pip
pip install --upgrade pip

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Documentation

- **Full Documentation:** README.md
- **Testing Guide:** TESTING_GUIDE.md
- **Deployment Guide:** DEPLOYMENT.md

---

## 🎯 What You Have

✅ **Backend API** - Flask server with Claude AI integration
✅ **Natural Language Processing** - Talk to Unity Catalog in plain English
✅ **Complete UC Operations** - Catalogs, schemas, tables, permissions
✅ **React Frontend** - Beautiful UI component
✅ **Docker Support** - Containerized deployment
✅ **Automated Tests** - Comprehensive test suite
✅ **Production Ready** - Monitoring, logging, error handling

---

## 💡 Quick Tips

1. **Start Simple:** Test with "help" and "list all catalogs" first
2. **Use Natural Language:** "create a catalog" works just as well as exact commands
3. **Check SQL:** Every operation shows the SQL it will execute
4. **Review Logs:** app.log has detailed information
5. **Interactive Mode:** Run `./deploy.sh` and choose interactive testing

---

## 🔒 Security Note

**For Production:**
- Enable authentication (set `ENABLE_AUTH=true` in .env)
- Use Azure Key Vault for secrets
- Enable HTTPS
- Set up monitoring

---

## 📞 Need Help?

1. Check TESTING_GUIDE.md for detailed test scenarios
2. Review logs: `tail -f app.log`
3. Run diagnostics: `./test.sh`
4. Check Databricks connectivity
5. Verify API keys are valid

---

**🎉 Happy Chatting with Unity Catalog!**
