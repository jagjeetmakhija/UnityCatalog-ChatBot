"""
Unity Catalog Chatbot Backend Service
Handles authentication and execution of Unity Catalog operations
"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import *
from typing import Dict, List, Optional, Any
import os
import re
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnityCatalogService:
    """Service for managing Unity Catalog operations through natural language"""
    
    def __init__(self, workspace_url: str = None, token: str = None):
        """
        Initialize Databricks workspace client
        
        Args:
            workspace_url: Databricks workspace URL
            token: Personal access token
        """
        self.workspace_url = workspace_url or os.getenv("DATABRICKS_HOST")
        self.token = token or os.getenv("DATABRICKS_TOKEN")
        
        self.client = WorkspaceClient(
            host=self.workspace_url,
            token=self.token
        )
        
        # Cache for frequently accessed data
        self._catalog_cache = {}
        self._schema_cache = {}
        
    def parse_object_path(self, path: str) -> Dict[str, str]:
        """Parse a Unity Catalog object path into components"""
        parts = path.split('.')
        
        if len(parts) == 1:
            return {'catalog': parts[0]}
        elif len(parts) == 2:
            return {'catalog': parts[0], 'schema': parts[1]}
        elif len(parts) == 3:
            return {'catalog': parts[0], 'schema': parts[1], 'table': parts[2]}
        else:
            raise ValueError(f"Invalid object path: {path}")
    
    # ==================== CATALOG OPERATIONS ====================
    
    def create_catalog(self, name: str, comment: str = None, properties: Dict = None) -> Dict:
        """Create a new catalog"""
        try:
            catalog = self.client.catalogs.create(
                name=name,
                comment=comment or f"Catalog created via chatbot on {datetime.now().isoformat()}",
                properties=properties or {}
            )
            
            logger.info(f"Created catalog: {name}")
            
            return {
                'success': True,
                'message': f"Successfully created catalog '{name}'",
                'catalog': {
                    'name': catalog.name,
                    'owner': catalog.owner,
                    'created_at': catalog.created_at
                },
                'sql': f"CREATE CATALOG IF NOT EXISTS {name}"
            }
        except Exception as e:
            logger.error(f"Error creating catalog {name}: {e}")
            return {
                'success': False,
                'message': f"Failed to create catalog: {str(e)}"
            }
    
    def list_catalogs(self) -> Dict:
        """List all available catalogs"""
        try:
            catalogs = list(self.client.catalogs.list())
            
            return {
                'success': True,
                'message': f"Found {len(catalogs)} catalog(s)",
                'catalogs': [
                    {
                        'name': cat.name,
                        'owner': cat.owner,
                        'comment': cat.comment
                    }
                    for cat in catalogs
                ],
                'sql': "SHOW CATALOGS"
            }
        except Exception as e:
            logger.error(f"Error listing catalogs: {e}")
            return {
                'success': False,
                'message': f"Failed to list catalogs: {str(e)}"
            }
    
    def get_catalog(self, name: str) -> Dict:
        """Get catalog details"""
        try:
            catalog = self.client.catalogs.get(name)
            
            return {
                'success': True,
                'catalog': {
                    'name': catalog.name,
                    'owner': catalog.owner,
                    'comment': catalog.comment,
                    'created_at': catalog.created_at,
                    'updated_at': catalog.updated_at,
                    'properties': catalog.properties
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Catalog not found: {str(e)}"
            }
    
    def delete_catalog(self, name: str, force: bool = False) -> Dict:
        """Delete a catalog"""
        try:
            self.client.catalogs.delete(name, force=force)
            
            return {
                'success': True,
                'message': f"Successfully deleted catalog '{name}'",
                'sql': f"DROP CATALOG {name} {'CASCADE' if force else ''}"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to delete catalog: {str(e)}"
            }
    
    # ==================== SCHEMA OPERATIONS ====================
    
    def create_schema(self, catalog: str, schema: str, comment: str = None) -> Dict:
        """Create a new schema"""
        try:
            full_name = f"{catalog}.{schema}"
            
            schema_obj = self.client.schemas.create(
                name=schema,
                catalog_name=catalog,
                comment=comment or f"Schema created via chatbot on {datetime.now().isoformat()}"
            )
            
            logger.info(f"Created schema: {full_name}")
            
            return {
                'success': True,
                'message': f"Successfully created schema '{full_name}'",
                'schema': {
                    'name': schema_obj.name,
                    'catalog': schema_obj.catalog_name,
                    'owner': schema_obj.owner
                },
                'sql': f"CREATE SCHEMA IF NOT EXISTS {full_name}"
            }
        except Exception as e:
            logger.error(f"Error creating schema {catalog}.{schema}: {e}")
            return {
                'success': False,
                'message': f"Failed to create schema: {str(e)}"
            }
    
    def list_schemas(self, catalog: str) -> Dict:
        """List all schemas in a catalog"""
        try:
            schemas = list(self.client.schemas.list(catalog_name=catalog))
            
            return {
                'success': True,
                'message': f"Found {len(schemas)} schema(s) in catalog '{catalog}'",
                'schemas': [
                    {
                        'name': sch.name,
                        'full_name': sch.full_name,
                        'owner': sch.owner,
                        'comment': sch.comment
                    }
                    for sch in schemas
                ],
                'sql': f"SHOW SCHEMAS IN {catalog}"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to list schemas: {str(e)}"
            }
    
    def delete_schema(self, catalog: str, schema: str, force: bool = False) -> Dict:
        """Delete a schema"""
        try:
            full_name = f"{catalog}.{schema}"
            self.client.schemas.delete(full_name)
            
            return {
                'success': True,
                'message': f"Successfully deleted schema '{full_name}'",
                'sql': f"DROP SCHEMA {full_name} {'CASCADE' if force else ''}"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to delete schema: {str(e)}"
            }
    
    # ==================== TABLE OPERATIONS ====================
    
    def create_table(
        self,
        catalog: str,
        schema: str,
        table: str,
        columns: List[Dict[str, str]] = None,
        comment: str = None,
        table_type: str = "MANAGED"
    ) -> Dict:
        """Create a new table"""
        try:
            full_name = f"{catalog}.{schema}.{table}"
            
            # Default columns if none provided
            if not columns:
                columns = [
                    {"name": "id", "type_name": "BIGINT", "comment": "Primary key"},
                    {"name": "created_at", "type_name": "TIMESTAMP", "comment": "Creation timestamp"},
                    {"name": "data", "type_name": "STRING", "comment": "Data field"}
                ]
            
            # Build column definitions
            column_defs = [
                ColumnInfo(
                    name=col['name'],
                    type_name=ColumnTypeName[col.get('type_name', 'STRING')],
                    comment=col.get('comment')
                )
                for col in columns
            ]
            
            table_obj = self.client.tables.create(
                name=table,
                catalog_name=catalog,
                schema_name=schema,
                columns=column_defs,
                table_type=TableType[table_type],
                data_source_format=DataSourceFormat.DELTA,
                comment=comment or f"Table created via chatbot on {datetime.now().isoformat()}"
            )
            
            logger.info(f"Created table: {full_name}")
            
            # Generate SQL
            col_sql = ",\n  ".join([
                f"{col['name']} {col.get('type_name', 'STRING')}"
                for col in columns
            ])
            
            return {
                'success': True,
                'message': f"Successfully created table '{full_name}'",
                'table': {
                    'name': table_obj.name,
                    'full_name': full_name,
                    'owner': table_obj.owner,
                    'table_type': str(table_obj.table_type)
                },
                'sql': f"CREATE TABLE IF NOT EXISTS {full_name} (\n  {col_sql}\n) USING DELTA"
            }
        except Exception as e:
            logger.error(f"Error creating table {catalog}.{schema}.{table}: {e}")
            return {
                'success': False,
                'message': f"Failed to create table: {str(e)}"
            }
    
    def list_tables(self, catalog: str, schema: str) -> Dict:
        """List all tables in a schema"""
        try:
            tables = list(self.client.tables.list(
                catalog_name=catalog,
                schema_name=schema
            ))
            
            return {
                'success': True,
                'message': f"Found {len(tables)} table(s) in {catalog}.{schema}",
                'tables': [
                    {
                        'name': tbl.name,
                        'full_name': tbl.full_name,
                        'owner': tbl.owner,
                        'table_type': str(tbl.table_type),
                        'data_source_format': str(tbl.data_source_format)
                    }
                    for tbl in tables
                ],
                'sql': f"SHOW TABLES IN {catalog}.{schema}"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to list tables: {str(e)}"
            }
    
    def get_table(self, catalog: str, schema: str, table: str) -> Dict:
        """Get table details including columns"""
        try:
            full_name = f"{catalog}.{schema}.{table}"
            table_obj = self.client.tables.get(full_name)
            
            return {
                'success': True,
                'table': {
                    'name': table_obj.name,
                    'full_name': full_name,
                    'owner': table_obj.owner,
                    'table_type': str(table_obj.table_type),
                    'data_source_format': str(table_obj.data_source_format),
                    'columns': [
                        {
                            'name': col.name,
                            'type': str(col.type_name),
                            'comment': col.comment
                        }
                        for col in (table_obj.columns or [])
                    ],
                    'comment': table_obj.comment
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to get table details: {str(e)}"
            }
    
    # ==================== PERMISSION OPERATIONS ====================
    
    def grant_permission(
        self,
        principal: str,
        privilege: str,
        securable_type: str,
        securable_name: str
    ) -> Dict:
        """Grant permission to a user or group"""
        try:
            # Map privilege strings to enum
            privilege_map = {
                'SELECT': Privilege.SELECT,
                'MODIFY': Privilege.MODIFY,
                'CREATE': Privilege.CREATE,
                'USAGE': Privilege.USAGE,
                'READ_METADATA': Privilege.READ_METADATA,
                'CREATE_TABLE': Privilege.CREATE_TABLE,
                'CREATE_SCHEMA': Privilege.CREATE_SCHEMA,
                'USE_CATALOG': Privilege.USE_CATALOG,
                'USE_SCHEMA': Privilege.USE_SCHEMA,
                'ALL_PRIVILEGES': Privilege.ALL_PRIVILEGES
            }
            
            privilege_enum = privilege_map.get(privilege.upper())
            if not privilege_enum:
                return {
                    'success': False,
                    'message': f"Invalid privilege: {privilege}"
                }
            
            # Map securable type
            securable_type_map = {
                'CATALOG': SecurableType.CATALOG,
                'SCHEMA': SecurableType.SCHEMA,
                'TABLE': SecurableType.TABLE,
                'VOLUME': SecurableType.VOLUME,
                'FUNCTION': SecurableType.FUNCTION
            }
            
            securable_enum = securable_type_map.get(securable_type.upper())
            
            self.client.grants.update(
                securable_type=securable_enum,
                full_name=securable_name,
                changes=[
                    PermissionsChange(
                        add=[privilege_enum],
                        principal=principal
                    )
                ]
            )
            
            logger.info(f"Granted {privilege} on {securable_name} to {principal}")
            
            return {
                'success': True,
                'message': f"Granted {privilege} on '{securable_name}' to '{principal}'",
                'sql': f"GRANT {privilege.upper()} ON {securable_name} TO `{principal}`"
            }
        except Exception as e:
            logger.error(f"Error granting permission: {e}")
            return {
                'success': False,
                'message': f"Failed to grant permission: {str(e)}"
            }
    
    def revoke_permission(
        self,
        principal: str,
        privilege: str,
        securable_type: str,
        securable_name: str
    ) -> Dict:
        """Revoke permission from a user or group"""
        try:
            privilege_map = {
                'SELECT': Privilege.SELECT,
                'MODIFY': Privilege.MODIFY,
                'CREATE': Privilege.CREATE,
                'USAGE': Privilege.USAGE,
                'ALL_PRIVILEGES': Privilege.ALL_PRIVILEGES
            }
            
            privilege_enum = privilege_map.get(privilege.upper())
            
            securable_type_map = {
                'CATALOG': SecurableType.CATALOG,
                'SCHEMA': SecurableType.SCHEMA,
                'TABLE': SecurableType.TABLE
            }
            
            securable_enum = securable_type_map.get(securable_type.upper())
            
            self.client.grants.update(
                securable_type=securable_enum,
                full_name=securable_name,
                changes=[
                    PermissionsChange(
                        remove=[privilege_enum],
                        principal=principal
                    )
                ]
            )
            
            logger.info(f"Revoked {privilege} on {securable_name} from {principal}")
            
            return {
                'success': True,
                'message': f"Revoked {privilege} on '{securable_name}' from '{principal}'",
                'sql': f"REVOKE {privilege.upper()} ON {securable_name} FROM `{principal}`"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to revoke permission: {str(e)}"
            }
    
    def show_grants(self, securable_type: str, securable_name: str) -> Dict:
        """Show all grants on a securable object"""
        try:
            securable_type_map = {
                'CATALOG': SecurableType.CATALOG,
                'SCHEMA': SecurableType.SCHEMA,
                'TABLE': SecurableType.TABLE
            }
            
            securable_enum = securable_type_map.get(securable_type.upper())
            
            grants = self.client.grants.get(
                securable_type=securable_enum,
                full_name=securable_name
            )
            
            permissions = []
            if grants.privilege_assignments:
                for assignment in grants.privilege_assignments:
                    permissions.append({
                        'principal': assignment.principal,
                        'privileges': [str(p) for p in (assignment.privileges or [])]
                    })
            
            return {
                'success': True,
                'message': f"Permissions for '{securable_name}'",
                'permissions': permissions,
                'sql': f"SHOW GRANTS ON {securable_name}"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to show grants: {str(e)}"
            }
    
    def set_owner(self, securable_type: str, securable_name: str, owner: str) -> Dict:
        """Set the owner of a securable object"""
        try:
            if securable_type.upper() == 'CATALOG':
                self.client.catalogs.update(securable_name, owner=owner)
            elif securable_type.upper() == 'SCHEMA':
                self.client.schemas.update(securable_name, owner=owner)
            elif securable_type.upper() == 'TABLE':
                self.client.tables.update(securable_name, owner=owner)
            else:
                return {
                    'success': False,
                    'message': f"Invalid securable type: {securable_type}"
                }
            
            return {
                'success': True,
                'message': f"Set owner of '{securable_name}' to '{owner}'",
                'sql': f"ALTER {securable_type.upper()} {securable_name} OWNER TO `{owner}`"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to set owner: {str(e)}"
            }
    
    # ==================== HELPER METHODS ====================
    
    def execute_sql(self, sql: str, warehouse_id: str = None) -> Dict:
        """Execute a SQL statement"""
        try:
            # This would require SQL execution API
            # For now, return the SQL that should be executed
            return {
                'success': True,
                'message': "SQL statement prepared",
                'sql': sql,
                'note': "Execute this SQL in a Databricks SQL Warehouse or notebook"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to execute SQL: {str(e)}"
            }
    
    def validate_name(self, name: str) -> bool:
        """Validate a catalog/schema/table name"""
        # Unity Catalog naming rules
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, name))


# ==================== USAGE EXAMPLES ====================

if __name__ == "__main__":
    # Initialize service
    service = UnityCatalogService()
    
    # Example operations
    print("=== Unity Catalog Chatbot Service ===\n")
    
    # Create catalog
    result = service.create_catalog(
        name="demo_catalog",
        comment="Demo catalog created by chatbot"
    )
    print(f"Create Catalog: {result}\n")
    
    # Create schema
    result = service.create_schema(
        catalog="demo_catalog",
        schema="analytics",
        comment="Analytics schema"
    )
    print(f"Create Schema: {result}\n")
    
    # Create table
    result = service.create_table(
        catalog="demo_catalog",
        schema="analytics",
        table="customers",
        columns=[
            {"name": "customer_id", "type_name": "BIGINT"},
            {"name": "name", "type_name": "STRING"},
            {"name": "email", "type_name": "STRING"},
            {"name": "created_at", "type_name": "TIMESTAMP"}
        ]
    )
    print(f"Create Table: {result}\n")
    
    # Grant permission
    result = service.grant_permission(
        principal="data_analysts",
        privilege="SELECT",
        securable_type="TABLE",
        securable_name="demo_catalog.analytics.customers"
    )
    print(f"Grant Permission: {result}\n")
    
    # Show grants
    result = service.show_grants(
        securable_type="TABLE",
        securable_name="demo_catalog.analytics.customers"
    )
    print(f"Show Grants: {result}\n")
