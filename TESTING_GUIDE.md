# Manual Testing Guide - Unity Catalog Chatbot

## Prerequisites Checklist

Before starting, ensure you have:
- [ ] Databricks workspace access
- [ ] Databricks personal access token (PAT)
- [ ] Anthropic API key
- [ ] Python 3.9+ installed OR Docker installed
- [ ] All project files downloaded

---

## Quick Start - Local Deployment

### Step 1: Setup Environment

```bash
# Navigate to project directory
cd unity-catalog-chatbot

# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

**Edit `.env` file:**
```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.net
DATABRICKS_TOKEN=dapi1234567890abcdef
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### Step 2: Run Automated Deployment

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

The script will:
1. Check prerequisites
2. Configure environment
3. Install dependencies
4. Start the application
5. Run health checks
6. Perform basic tests

### Step 3: Verify Deployment

**Check if application is running:**
```bash
curl http://localhost:5000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "Unity Catalog Chatbot API",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## Manual Testing Scenarios

### Test 1: Help Command

**Objective:** Verify chatbot responds to help requests

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "help"}'
```

**Expected Response:**
- `success: true`
- Message contains: "Creating Objects", "Managing Permissions", "Listing Objects"

**Pass Criteria:** ✅ Chatbot returns helpful information about available commands

---

### Test 2: List All Catalogs

**Objective:** Verify chatbot can list existing Unity Catalog catalogs

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "list all catalogs"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Found X catalog(s)",
  "sql": "SHOW CATALOGS",
  "data": {
    "catalogs": [...]
  }
}
```

**Pass Criteria:** ✅ Returns list of catalogs from your Databricks workspace

---

### Test 3: Create a Catalog

**Objective:** Test catalog creation

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create a catalog named test_chatbot_catalog"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully created catalog 'test_chatbot_catalog'",
  "sql": "CREATE CATALOG IF NOT EXISTS test_chatbot_catalog",
  "catalog": {
    "name": "test_chatbot_catalog",
    "owner": "your@email.com"
  }
}
```

**Verify in Databricks:**
```sql
-- Run this in Databricks SQL editor
SHOW CATALOGS;
-- Should see test_chatbot_catalog
```

**Pass Criteria:** ✅ Catalog appears in Databricks Unity Catalog

---

### Test 4: Create a Schema

**Objective:** Test schema creation

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create schema analytics in test_chatbot_catalog"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully created schema 'test_chatbot_catalog.analytics'",
  "sql": "CREATE SCHEMA IF NOT EXISTS test_chatbot_catalog.analytics"
}
```

**Verify in Databricks:**
```sql
SHOW SCHEMAS IN test_chatbot_catalog;
-- Should see analytics schema
```

**Pass Criteria:** ✅ Schema appears in the catalog

---

### Test 5: Create a Table

**Objective:** Test table creation

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create table test_chatbot_catalog.analytics.customers"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Successfully created table 'test_chatbot_catalog.analytics.customers'",
  "sql": "CREATE TABLE IF NOT EXISTS test_chatbot_catalog.analytics.customers (...) USING DELTA"
}
```

**Verify in Databricks:**
```sql
SHOW TABLES IN test_chatbot_catalog.analytics;
-- Should see customers table

DESCRIBE TABLE test_chatbot_catalog.analytics.customers;
-- Should show default columns: id, created_at, data
```

**Pass Criteria:** ✅ Table is created with default schema

---

### Test 6: Grant Permissions

**Objective:** Test permission granting

**Setup:** Replace `test_user@example.com` with a real user in your workspace

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "grant SELECT on test_chatbot_catalog.analytics to test_user@example.com"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Granted SELECT on 'test_chatbot_catalog.analytics' to 'test_user@example.com'",
  "sql": "GRANT SELECT ON test_chatbot_catalog.analytics TO `test_user@example.com`"
}
```

**Verify in Databricks:**
```sql
SHOW GRANTS ON SCHEMA test_chatbot_catalog.analytics;
-- Should show SELECT permission for test_user@example.com
```

**Pass Criteria:** ✅ Permission is granted successfully

---

### Test 7: Show Permissions

**Objective:** Verify permission listing

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show permissions for test_chatbot_catalog.analytics"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Permissions for 'test_chatbot_catalog.analytics'",
  "sql": "SHOW GRANTS ON test_chatbot_catalog.analytics",
  "data": {
    "permissions": [
      {
        "principal": "test_user@example.com",
        "privileges": ["SELECT"]
      }
    ]
  }
}
```

**Pass Criteria:** ✅ Returns list of permissions

---

### Test 8: Revoke Permissions

**Objective:** Test permission revocation

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "revoke SELECT on test_chatbot_catalog.analytics from test_user@example.com"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Revoked SELECT on 'test_chatbot_catalog.analytics' from 'test_user@example.com'",
  "sql": "REVOKE SELECT ON test_chatbot_catalog.analytics FROM `test_user@example.com`"
}
```

**Verify in Databricks:**
```sql
SHOW GRANTS ON SCHEMA test_chatbot_catalog.analytics;
-- Should NOT show SELECT permission for test_user@example.com
```

**Pass Criteria:** ✅ Permission is revoked successfully

---

### Test 9: Complex Query

**Objective:** Test multi-part natural language query

**Request:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need to create a new catalog for our sales team called sales_data, then create a schema called staging in it"}'
```

**Expected Response:**
- Should recognize intent to create catalog
- May ask for clarification or execute first step

**Pass Criteria:** ✅ Chatbot understands complex intent

---

### Test 10: Error Handling

**Objective:** Test invalid requests

**Request (Invalid catalog name):**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "create a catalog named invalid-name-with-dashes"}'
```

**Expected Behavior:**
- May attempt creation and get error from Databricks
- Should return error message to user

**Pass Criteria:** ✅ Errors are handled gracefully

---

## Automated Testing

### Run Full Test Suite

```bash
# Make test script executable
chmod +x test.sh

# Run all automated tests
./test.sh
```

**The test script will:**
1. Test basic connectivity
2. Test help commands
3. Test catalog operations
4. Test schema operations
5. Test table operations
6. Test permissions
7. Test complex queries
8. Test error handling
9. Run performance tests
10. Generate test report

**View Test Report:**
```bash
cat test_report.txt
```

---

## Performance Testing

### Response Time Test

```bash
# Measure response time
time curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "help"}'
```

**Expected:** Response < 3 seconds

### Load Test (Optional)

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Ubuntu/Debian

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 -T 'application/json' \
  -p <(echo '{"message":"help"}') \
  http://localhost:5000/api/chat
```

---

## Frontend Testing (React Component)

### Test in Browser

1. **Create a simple HTML file:**

```html
<!DOCTYPE html>
<html>
<head>
  <title>Unity Catalog Chatbot</title>
</head>
<body>
  <div id="root"></div>
  
  <!-- Include React and dependencies -->
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  
  <!-- Include your compiled chatbot component -->
  <script src="unity-catalog-chatbot.js"></script>
</body>
</html>
```

2. **Test interactions:**
- Type messages in chat input
- Click quick action buttons
- Verify messages appear
- Check action log updates
- Verify SQL commands display

---

## Cleanup After Testing

```bash
# Delete test catalog and all contents
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "delete catalog test_chatbot_catalog"}'

# Or manually in Databricks SQL:
DROP CATALOG IF EXISTS test_chatbot_catalog CASCADE;
```

---

## Troubleshooting

### Issue: Application won't start

**Check logs:**
```bash
# For local deployment
tail -f app.log

# For Docker
docker logs unity-catalog-chatbot

# For Docker Compose
docker-compose logs -f
```

**Common fixes:**
- Verify .env credentials are correct
- Check port 5000 is not in use: `lsof -i :5000`
- Ensure dependencies are installed

---

### Issue: Databricks connection failed

**Test Databricks connectivity:**
```bash
curl -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  $DATABRICKS_HOST/api/2.0/clusters/list
```

**Common fixes:**
- Verify DATABRICKS_HOST has https://
- Check token hasn't expired
- Ensure network allows connection to Databricks

---

### Issue: Claude API errors

**Test Anthropic API:**
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":100,"messages":[{"role":"user","content":"test"}]}'
```

**Common fixes:**
- Verify API key is correct (starts with sk-ant-)
- Check API credits/billing
- Ensure internet connectivity

---

## Success Criteria

Your deployment is successful when:
- [x] Health check returns 200 OK
- [x] Help command returns useful information
- [x] Can list existing catalogs
- [x] Can create a new catalog
- [x] Can create schemas and tables
- [x] Can grant and revoke permissions
- [x] SQL commands are generated correctly
- [x] Action log tracks operations
- [x] Error messages are clear and helpful

---

## Next Steps

After successful testing:
1. Review logs for any warnings
2. Customize chatbot prompts if needed
3. Add user authentication for production
4. Set up monitoring and alerts
5. Deploy to production environment
6. Document custom workflows
7. Train team on usage

---

## Support

If you encounter issues:
1. Check logs first
2. Review DEPLOYMENT.md for detailed guides
3. Test individual components separately
4. Verify all credentials are valid
5. Check network connectivity

**Happy Testing! 🚀**
