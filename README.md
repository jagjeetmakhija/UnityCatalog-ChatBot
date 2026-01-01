# Unity Catalog Chatbot

An intelligent chatbot for managing Databricks Unity Catalog through natural language. Built with React, Flask, Claude AI, and the Databricks SDK.

## Features

### 🤖 Natural Language Interface
- Create catalogs, schemas, and tables using plain English
- Manage permissions with simple commands
- Query and explore your Unity Catalog metadata
- AI-powered intent parsing using Claude

### 🔒 Security & Governance
- Grant/revoke permissions to users and groups
- Set object ownership
- View current permissions on any object
- Full audit trail of all operations

### 📊 Comprehensive Management
- **Catalogs**: Create, list, delete
- **Schemas**: Create, list, delete  
- **Tables**: Create with custom schemas, list, view details
- **Permissions**: Grant, revoke, show grants
- **Ownership**: Set and transfer ownership

### 💻 Modern UI
- Real-time chat interface
- Action log sidebar showing all executed operations
- SQL preview for every operation
- Quick action buttons for common tasks
- Responsive design with dark theme

## Architecture

```
┌─────────────────┐
│  React Frontend │ (Natural language UI)
└────────┬────────┘
         │
         ├─> Claude API (Intent parsing)
         │
         ▼
┌─────────────────┐
│   Flask API     │ (Request handling)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Unity Catalog   │ (Databricks operations)
│    Service      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Databricks SDK │
└─────────────────┘
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+ (for React development)
- Databricks workspace with Unity Catalog enabled
- Databricks personal access token
- Anthropic API key

### Backend Setup

1. **Clone and navigate to the project**
```bash
cd unity-catalog-chatbot
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...
ANTHROPIC_API_KEY=sk-ant-...
```

4. **Run the Flask API server**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Frontend Setup

The React component can be:
1. Integrated into your existing React application
2. Used as a standalone artifact in Claude
3. Deployed as a static site

**For development:**
```bash
npm install react react-dom lucide-react
npm start
```

## Usage

### Quick Start Examples

**Creating a Catalog:**
```
User: Create a catalog named sales_data
Bot: Created catalog 'sales_data' successfully.
SQL: CREATE CATALOG IF NOT EXISTS sales_data
```

**Creating a Schema:**
```
User: Create schema analytics in sales_data
Bot: Created schema 'sales_data.analytics' successfully.
SQL: CREATE SCHEMA IF NOT EXISTS sales_data.analytics
```

**Creating a Table:**
```
User: Create table sales_data.analytics.customers with columns id BIGINT, name STRING, email STRING
Bot: Created table 'sales_data.analytics.customers' with specified schema.
SQL: CREATE TABLE IF NOT EXISTS sales_data.analytics.customers (
  id BIGINT,
  name STRING,
  email STRING
) USING DELTA
```

**Granting Permissions:**
```
User: Grant SELECT permission on sales_data.analytics.customers to data_analysts
Bot: Granted SELECT on 'sales_data.analytics.customers' to 'data_analysts'.
SQL: GRANT SELECT ON sales_data.analytics.customers TO `data_analysts`
```

**Listing Objects:**
```
User: List all catalogs
Bot: Here are the available catalogs...
SQL: SHOW CATALOGS
```

### Supported Commands

#### Catalog Operations
- `create a catalog named <name>`
- `list all catalogs`
- `delete catalog <name>`

#### Schema Operations
- `create schema <name> in <catalog>`
- `create schema <catalog>.<schema>`
- `list schemas in <catalog>`
- `delete schema <catalog>.<schema>`

#### Table Operations
- `create table <catalog>.<schema>.<table>`
- `create table <catalog>.<schema>.<table> with columns <spec>`
- `list tables in <catalog>.<schema>`
- `show details for <catalog>.<schema>.<table>`
- `delete table <catalog>.<schema>.<table>`

#### Permission Operations
- `grant <privilege> on <object> to <principal>`
- `revoke <privilege> on <object> from <principal>`
- `show permissions for <object>`
- `set owner of <object> to <user>`

**Supported Privileges:**
- SELECT
- MODIFY
- CREATE
- USAGE
- CREATE_TABLE
- CREATE_SCHEMA
- USE_CATALOG
- USE_SCHEMA
- ALL_PRIVILEGES

## API Endpoints

### POST /api/chat
Main chatbot endpoint for natural language requests.

**Request:**
```json
{
  "message": "Create a catalog named demo"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully created catalog 'demo'",
  "sql": "CREATE CATALOG IF NOT EXISTS demo",
  "catalog": {
    "name": "demo",
    "owner": "user@company.com",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

### GET /api/catalogs
List all catalogs.

### GET /api/schemas/<catalog>
List schemas in a catalog.

### GET /api/tables/<catalog>/<schema>
List tables in a schema.

### POST /api/execute
Execute raw SQL (for advanced users).

## Configuration

### Databricks Setup

1. **Create a Personal Access Token:**
   - Go to User Settings → Developer → Access Tokens
   - Generate new token
   - Copy and add to `.env`

2. **Verify Unity Catalog Access:**
   ```sql
   SHOW CATALOGS;
   ```

3. **Grant Necessary Permissions:**
   The user/service principal needs:
   - `CREATE CATALOG` on the metastore (for creating catalogs)
   - `USE CATALOG` on existing catalogs
   - `CREATE SCHEMA` on catalogs where schemas will be created
   - Admin permissions for granting/revoking privileges

### Security Best Practices

1. **Use Service Principals** for production deployments
2. **Implement authentication** on the Flask API
3. **Audit all operations** using the action log
4. **Limit permissions** to principle of least privilege
5. **Rotate tokens regularly**

## Advanced Features

### Custom Table Schemas
```
User: Create table products.inventory.items with columns:
- item_id BIGINT
- name STRING
- quantity INT
- price DECIMAL(10,2)
- last_updated TIMESTAMP
```

### Batch Operations
```
User: Create catalog ecommerce, then create schemas staging and production in it
```

### Complex Permission Scenarios
```
User: Grant SELECT and MODIFY on ecommerce.production to data_engineers, 
but only SELECT to data_analysts
```

## Troubleshooting

### Common Issues

**Authentication Error:**
```
Error: Invalid credentials
```
- Verify `DATABRICKS_TOKEN` is correct
- Check token hasn't expired
- Ensure workspace URL is correct

**Permission Denied:**
```
Error: User does not have CREATE privilege
```
- Check user has necessary Unity Catalog permissions
- Verify you're using correct catalog/schema names

**Claude API Error:**
```
Error: Anthropic API error
```
- Verify `ANTHROPIC_API_KEY` is set
- Check API key is valid
- Ensure you have API credits

### Debug Mode

Enable debug logging:
```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Structure
```
.
├── app.py                      # Flask API server
├── unity_catalog_service.py    # UC operations service
├── unity-catalog-chatbot.jsx   # React UI component
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

### Adding New Operations

1. **Add to UnityCatalogService:**
```python
def your_new_operation(self, params):
    # Implementation
    return {'success': True, 'message': '...', 'sql': '...'}
```

2. **Update intent parsing in app.py:**
```python
elif intent == "yourNewIntent":
    return uc_service.your_new_operation(params)
```

3. **Update Claude system prompt** to recognize new intent

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

### Production Considerations
- Use **gunicorn** or **uwsgi** instead of Flask dev server
- Implement **authentication & authorization**
- Add **rate limiting**
- Enable **HTTPS**
- Use **environment-specific configs**
- Set up **monitoring and alerting**

## Roadmap

- [ ] Multi-catalog operations in single command
- [ ] Table data preview
- [ ] Schema validation and suggestions
- [ ] Integration with Databricks notebooks
- [ ] Permission templates
- [ ] Export configurations as Terraform
- [ ] WebSocket support for real-time updates
- [ ] Multi-user support with sessions

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: [Databricks Unity Catalog Docs](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- Anthropic Claude: [Claude Documentation](https://docs.anthropic.com/)

## Acknowledgments

Built with:
- [Databricks SDK](https://github.com/databricks/databricks-sdk-py)
- [Anthropic Claude](https://www.anthropic.com/)
- [React](https://react.dev/)
- [Flask](https://flask.palletsprojects.com/)
