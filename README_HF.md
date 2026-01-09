---
title: Unity Catalog Chatbot
emoji: 🧠
colorFrom: purple
colorTo: green
sdk: docker
sdk_version: "1.0"
app_file: Dockerfile
pinned: false
license: mit
---

# Unity Catalog Chatbot 🧠

An intelligent AI-powered chatbot for managing Databricks Unity Catalog through natural language. Built with Flask, Claude AI (Anthropic), and the Databricks SDK.

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue" alt="Python 3.11"/>
  <img src="https://img.shields.io/badge/Flask-3.0-green" alt="Flask 3.0"/>
  <img src="https://img.shields.io/badge/Databricks-SDK-red" alt="Databricks SDK"/>
  <img src="https://img.shields.io/badge/Claude-AI-purple" alt="Claude AI"/>
</div>

## 🚀 Live Demo

Try it now at: [Your Hugging Face Space URL]

## ✨ Features

### 🤖 Natural Language Interface
- **Create** catalogs, schemas, and tables using plain English
- **Manage** permissions with simple commands
- **Query** and explore your Unity Catalog metadata
- AI-powered intent parsing using Claude Sonnet 4

### 🔒 Security & Governance
- Grant/revoke permissions to users and groups
- Set object ownership
- View current permissions on any object
- Full audit trail of all operations

### 📊 Comprehensive Management
- **Catalogs**: Create, list, delete, get details
- **Schemas**: Create within catalogs, list, delete
- **Tables**: Create with custom schemas, list, view details, delete
- **Permissions**: Grant, revoke, show grants for any object
- **Ownership**: Set and transfer ownership of catalogs, schemas, tables

### 💻 Modern UI
- Real-time chat interface with streaming responses
- Action log sidebar showing all executed operations
- SQL preview for every operation
- Quick action buttons for common tasks
- Responsive dark theme design

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ ← Natural language input
└────────┬────────┘
         │
         ├─> Claude API (Intent parsing)
         │
         ▼
┌─────────────────┐
│   Flask API     │ ← Request handling & routing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Unity Catalog   │ ← Business logic
│    Service      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Databricks SDK │ ← Unity Catalog operations
└─────────────────┘
```

## 🎯 Use Cases

### Quick Examples

1. **Catalog Management**
   - "Create a catalog called sales_data"
   - "List all catalogs"
   - "Delete the test_catalog"

2. **Schema Operations**
   - "Create a schema named bronze in sales_data catalog"
   - "Show me all schemas in production"

3. **Table Creation**
   - "Create table sales_data.bronze.orders with columns: order_id string, amount decimal"
   - "List all tables in sales_data.bronze"

4. **Permission Management**
   - "Grant SELECT on sales_data.bronze.orders to data_analysts"
   - "Show grants on sales_data.bronze.orders"
   - "Revoke SELECT from analysts on my_table"

5. **Ownership**
   - "Set ownership of sales_data to admin_team"
   - "Transfer ownership of production.gold to data_governance"

### Complete Workflow Example

```
1. Create catalog analytics_lakehouse
2. Create schemas bronze, silver, gold in analytics_lakehouse
3. Create table analytics_lakehouse.bronze.raw_events with columns: event_id string, timestamp timestamp, user_id string
4. Grant SELECT on analytics_lakehouse.bronze to data_engineers
5. Grant ALL PRIVILEGES on analytics_lakehouse.gold to analysts
6. Show grants on analytics_lakehouse.bronze.raw_events
```

## 🔧 Configuration

### Required Environment Variables

This Space requires three secrets to be configured:

1. **DATABRICKS_HOST**
   - Your Databricks workspace URL
   - Format: `https://your-workspace.cloud.databricks.com`

2. **DATABRICKS_TOKEN**
   - Databricks personal access token
   - Generate at: Settings → User Settings → Access Tokens

3. **ANTHROPIC_API_KEY**
   - Anthropic API key for Claude AI
   - Get yours at: https://console.anthropic.com

### Setting Up Secrets in Hugging Face Spaces

1. Go to your Space settings
2. Navigate to **Variables and secrets**
3. Add the three secrets above
4. Save and restart the Space

## 📊 Sample Queries

Check [`sample_queries.json`](sample_queries.json) for a comprehensive list of example queries organized by category:
- Catalog Management
- Schema Management
- Table Creation
- Permission Management
- Ownership Management
- Medallion Architecture Setup

## 🧪 Testing

The application includes a comprehensive test suite:
- ✅ 23 automated tests covering all features
- ✅ Unit tests for service layer
- ✅ Integration tests for API endpoints
- ✅ Performance tests for concurrent operations

Run tests locally:
```bash
pytest test_chatbot.py -v
```

## 🛡️ Security Features

- **Credential Protection**: All sensitive credentials stored as Hugging Face secrets
- **Token Validation**: Automatic validation of Databricks connections
- **Error Handling**: Comprehensive error messages without exposing sensitive data
- **Permission Checks**: Respects Unity Catalog's permission model
- **Audit Trail**: Complete logging of all operations

## 📖 Documentation

- [Quick Deployment Guide](HF_DEPLOYMENT.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Quickstart Guide](QUICKSTART.md)

## 🔗 Related Resources

- [Databricks Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Databricks SDK for Python](https://docs.databricks.com/dev-tools/sdk-python.html)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

## 📝 License

MIT License - feel free to use this project for your own Unity Catalog management needs!

## 🤝 Contributing

Contributions welcome! This is an open-source project designed to make Unity Catalog management more accessible through natural language.

## 💡 Tips for Best Results

1. **Be Specific**: Include full three-part names for tables (catalog.schema.table)
2. **Use Natural Language**: The AI understands conversational requests
3. **Check SQL Preview**: Review the SQL before executing sensitive operations
4. **Start Simple**: Test with list operations before making changes
5. **Use Quick Actions**: Click suggested actions for common tasks

## 🚨 Important Notes

- This chatbot performs **real operations** on your Unity Catalog
- Always review the SQL preview before executing
- Start with a test workspace to familiarize yourself
- Set up proper permissions in your Databricks workspace
- Use a dedicated service principal token for production deployments

## 🆘 Support

For issues or questions:
- Check the [Testing Guide](TESTING_GUIDE.md) for common scenarios
- Review [HF_DEPLOYMENT.md](HF_DEPLOYMENT.md) for deployment troubleshooting
- Open an issue on GitHub

---

**Built with ❤️ for the Databricks community**
