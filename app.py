"""
Unity Catalog Chatbot API Server
Flask API to handle natural language requests and execute Unity Catalog operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
from typing import Dict, List, Optional
import anthropic
from unity_catalog_service import UnityCatalogService

app = Flask(__name__)
CORS(app)

# Initialize services
uc_service = UnityCatalogService()
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# System prompt for Claude to parse Unity Catalog requests
SYSTEM_PROMPT = """You are an expert Unity Catalog assistant. Your role is to:

1. Parse natural language requests about Databricks Unity Catalog operations
2. Extract the intent and parameters from user messages
3. Return structured JSON responses

Available intents:
- createCatalog: Create a new catalog
- createSchema: Create a new schema  
- createTable: Create a new table
- grantPermission: Grant permissions to users/groups
- revokePermission: Revoke permissions from users/groups
- listCatalogs: List all catalogs
- listSchemas: List schemas in a catalog
- listTables: List tables in a schema
- showPermissions: Show permissions for an object
- setOwner: Set the owner of an object
- getTableDetails: Get detailed information about a table
- help: Provide help information
- complex: Multi-step operation requiring clarification

For each request, analyze the user's intent and return a JSON object with:
{
  "intent": "string",
  "params": {
    "catalog": "string (optional)",
    "schema": "string (optional)", 
    "table": "string (optional)",
    "principal": "string (optional)",
    "privilege": "string (optional)",
    "comment": "string (optional)",
    "columns": [{"name": "string", "type_name": "string"}] (optional)
  },
  "explanation": "Brief explanation of what will be done"
}

Examples:
User: "Create a catalog called sales_data"
Response: {"intent": "createCatalog", "params": {"catalog": "sales_data"}, "explanation": "Will create a new catalog named sales_data"}

User: "Grant SELECT permission on sales.customers to data_analysts group"
Response: {"intent": "grantPermission", "params": {"privilege": "SELECT", "object": "sales.customers", "principal": "data_analysts"}, "explanation": "Will grant SELECT privileges on sales.customers table to data_analysts group"}

Always return valid JSON only, no additional text."""


def parse_with_claude(user_message: str) -> Dict:
    """Use Claude to parse complex natural language requests"""
    try:
        message = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": user_message
            }]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        
        # Try to find JSON in the response
        import json
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*|\s*```', '', response_text)
        
        parsed = json.loads(response_text.strip())
        return parsed
        
    except Exception as e:
        print(f"Error parsing with Claude: {e}")
        return {
            "intent": "help",
            "params": {},
            "explanation": "I couldn't understand that request. Please rephrase."
        }


def execute_intent(intent_data: Dict) -> Dict:
    """Execute the parsed intent using Unity Catalog service"""
    intent = intent_data.get("intent")
    params = intent_data.get("params", {})
    
    try:
        if intent == "createCatalog":
            return uc_service.create_catalog(
                name=params.get("catalog"),
                comment=params.get("comment")
            )
        
        elif intent == "createSchema":
            catalog, schema = params.get("catalog"), params.get("schema")
            # If full path provided (e.g., "catalog.schema")
            if not schema and catalog and '.' in catalog:
                catalog, schema = catalog.split('.', 1)
            return uc_service.create_schema(
                catalog=catalog,
                schema=schema,
                comment=params.get("comment")
            )
        
        elif intent == "createTable":
            catalog = params.get("catalog")
            schema = params.get("schema")
            table = params.get("table")
            
            # Parse full table path if needed
            if table and '.' in table:
                parts = table.split('.')
                if len(parts) == 3:
                    catalog, schema, table = parts
                elif len(parts) == 2 and catalog:
                    schema, table = parts
            
            return uc_service.create_table(
                catalog=catalog,
                schema=schema,
                table=table,
                columns=params.get("columns"),
                comment=params.get("comment")
            )
        
        elif intent == "grantPermission":
            # Determine securable type from object path
            obj = params.get("object", "")
            parts = obj.split('.')
            
            if len(parts) == 1:
                securable_type = "CATALOG"
            elif len(parts) == 2:
                securable_type = "SCHEMA"
            else:
                securable_type = "TABLE"
            
            return uc_service.grant_permission(
                principal=params.get("principal"),
                privilege=params.get("privilege"),
                securable_type=securable_type,
                securable_name=obj
            )
        
        elif intent == "revokePermission":
            obj = params.get("object", "")
            parts = obj.split('.')
            
            if len(parts) == 1:
                securable_type = "CATALOG"
            elif len(parts) == 2:
                securable_type = "SCHEMA"
            else:
                securable_type = "TABLE"
            
            return uc_service.revoke_permission(
                principal=params.get("principal"),
                privilege=params.get("privilege"),
                securable_type=securable_type,
                securable_name=obj
            )
        
        elif intent == "listCatalogs":
            return uc_service.list_catalogs()
        
        elif intent == "listSchemas":
            return uc_service.list_schemas(params.get("catalog"))
        
        elif intent == "listTables":
            return uc_service.list_tables(
                params.get("catalog"),
                params.get("schema")
            )
        
        elif intent == "showPermissions":
            obj = params.get("object", "")
            parts = obj.split('.')
            
            if len(parts) == 1:
                securable_type = "CATALOG"
            elif len(parts) == 2:
                securable_type = "SCHEMA"
            else:
                securable_type = "TABLE"
            
            return uc_service.show_grants(securable_type, obj)
        
        elif intent == "setOwner":
            obj = params.get("object", "")
            parts = obj.split('.')
            
            if len(parts) == 1:
                securable_type = "CATALOG"
            elif len(parts) == 2:
                securable_type = "SCHEMA"
            else:
                securable_type = "TABLE"
            
            return uc_service.set_owner(
                securable_type=securable_type,
                securable_name=obj,
                owner=params.get("owner")
            )
        
        elif intent == "getTableDetails":
            parts = params.get("table", "").split('.')
            if len(parts) == 3:
                return uc_service.get_table(parts[0], parts[1], parts[2])
            else:
                return {
                    "success": False,
                    "message": "Invalid table path. Use format: catalog.schema.table"
                }
        
        elif intent == "help":
            return {
                "success": True,
                "message": """I can help you with Unity Catalog operations:

**Creating Objects:**
• Create a catalog: "Create a catalog named sales_catalog"
• Create a schema: "Create schema analytics in sales_catalog"
• Create a table: "Create table sales_catalog.analytics.customers"

**Managing Permissions:**
• Grant access: "Grant SELECT on sales_catalog.analytics to data_analysts"
• Revoke access: "Revoke MODIFY on sales_catalog.analytics.customers from john_doe"
• Show permissions: "Show permissions for sales_catalog.analytics"
• Set owner: "Set owner of sales_catalog to admin_user"

**Listing Objects:**
• List catalogs: "List all catalogs" or "Show catalogs"
• List schemas: "List schemas in sales_catalog"
• List tables: "Show tables in sales_catalog.analytics"

**Table Details:**
• Get table info: "Show details for sales_catalog.analytics.customers"

Just describe what you want to do in natural language!""",
                "sql": None
            }
        
        else:
            return {
                "success": False,
                "message": f"Unknown intent: {intent}. Type 'help' for available commands."
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error executing operation: {str(e)}"
        }


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                'error': 'No message provided'
            }), 400
        
        # Parse intent with Claude
        intent_data = parse_with_claude(user_message)
        
        # Execute the operation
        result = execute_intent(intent_data)
        
        # Add explanation to response
        result['explanation'] = intent_data.get('explanation', '')
        result['intent'] = intent_data.get('intent')
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Unity Catalog Chatbot API'
    })


@app.route('/api/catalogs', methods=['GET'])
def get_catalogs():
    """Get all catalogs"""
    result = uc_service.list_catalogs()
    return jsonify(result)


@app.route('/api/schemas/<catalog>', methods=['GET'])
def get_schemas(catalog):
    """Get schemas in a catalog"""
    result = uc_service.list_schemas(catalog)
    return jsonify(result)


@app.route('/api/tables/<catalog>/<schema>', methods=['GET'])
def get_tables(catalog, schema):
    """Get tables in a schema"""
    result = uc_service.list_tables(catalog, schema)
    return jsonify(result)


@app.route('/api/execute', methods=['POST'])
def execute_sql():
    """Execute a SQL statement"""
    try:
        data = request.json
        sql = data.get('sql', '')
        warehouse_id = data.get('warehouse_id')
        
        result = uc_service.execute_sql(sql, warehouse_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
