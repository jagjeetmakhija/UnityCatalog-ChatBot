"""
Test Suite for Unity Catalog Chatbot
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from unity_catalog_service import UnityCatalogService
from app import parse_with_claude, execute_intent


class TestUnityCatalogService:
    """Tests for Unity Catalog Service"""
    
    @pytest.fixture
    def mock_workspace_client(self):
        """Mock Databricks workspace client"""
        with patch('unity_catalog_service.WorkspaceClient') as mock:
            yield mock
    
    @pytest.fixture
    def service(self, mock_workspace_client):
        """Initialize service with mocked client"""
        return UnityCatalogService(
            workspace_url="https://test.databricks.com",
            token="test-token"
        )
    
    def test_parse_object_path_catalog(self, service):
        """Test parsing catalog path"""
        result = service.parse_object_path("my_catalog")
        assert result == {'catalog': 'my_catalog'}
    
    def test_parse_object_path_schema(self, service):
        """Test parsing schema path"""
        result = service.parse_object_path("my_catalog.my_schema")
        assert result == {
            'catalog': 'my_catalog',
            'schema': 'my_schema'
        }
    
    def test_parse_object_path_table(self, service):
        """Test parsing table path"""
        result = service.parse_object_path("my_catalog.my_schema.my_table")
        assert result == {
            'catalog': 'my_catalog',
            'schema': 'my_schema',
            'table': 'my_table'
        }
    
    def test_create_catalog_success(self, service, mock_workspace_client):
        """Test successful catalog creation"""
        mock_catalog = Mock()
        mock_catalog.name = "test_catalog"
        mock_catalog.owner = "test_user"
        mock_catalog.created_at = "2025-01-01T00:00:00Z"
        
        service.client.catalogs.create = Mock(return_value=mock_catalog)
        
        result = service.create_catalog("test_catalog")
        
        assert result['success'] is True
        assert result['catalog']['name'] == "test_catalog"
        assert "CREATE CATALOG" in result['sql']
    
    def test_create_catalog_error(self, service, mock_workspace_client):
        """Test catalog creation error handling"""
        service.client.catalogs.create = Mock(
            side_effect=Exception("Permission denied")
        )
        
        result = service.create_catalog("test_catalog")
        
        assert result['success'] is False
        assert "Permission denied" in result['message']
    
    def test_create_schema_success(self, service, mock_workspace_client):
        """Test successful schema creation"""
        mock_schema = Mock()
        mock_schema.name = "test_schema"
        mock_schema.catalog_name = "test_catalog"
        mock_schema.owner = "test_user"
        
        service.client.schemas.create = Mock(return_value=mock_schema)
        
        result = service.create_schema("test_catalog", "test_schema")
        
        assert result['success'] is True
        assert "CREATE SCHEMA" in result['sql']
    
    def test_validate_name_valid(self, service):
        """Test name validation with valid names"""
        assert service.validate_name("valid_name") is True
        assert service.validate_name("ValidName123") is True
    
    def test_validate_name_invalid(self, service):
        """Test name validation with invalid names"""
        assert service.validate_name("invalid-name") is False
        assert service.validate_name("invalid name") is False
        assert service.validate_name("invalid.name") is False


class TestIntentParsing:
    """Tests for intent parsing with Claude"""
    
    @patch('app.claude_client.messages.create')
    def test_parse_create_catalog(self, mock_create):
        """Test parsing create catalog intent"""
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text='{"intent": "createCatalog", "params": {"catalog": "sales"}, "explanation": "Creating catalog"}',
                type='text'
            )
        ]
        mock_create.return_value = mock_response
        
        result = parse_with_claude("Create a catalog named sales")
        
        assert result['intent'] == 'createCatalog'
        assert result['params']['catalog'] == 'sales'
    
    @patch('app.claude_client.messages.create')
    def test_parse_grant_permission(self, mock_create):
        """Test parsing grant permission intent"""
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text='{"intent": "grantPermission", "params": {"privilege": "SELECT", "object": "sales.customers", "principal": "analysts"}}',
                type='text'
            )
        ]
        mock_create.return_value = mock_response
        
        result = parse_with_claude("Grant SELECT on sales.customers to analysts")
        
        assert result['intent'] == 'grantPermission'
        assert result['params']['privilege'] == 'SELECT'
    
    @patch('app.claude_client.messages.create')
    def test_parse_error_handling(self, mock_create):
        """Test error handling in parsing"""
        mock_create.side_effect = Exception("API Error")
        
        result = parse_with_claude("Invalid request")
        
        assert result['intent'] == 'help'


class TestExecuteIntent:
    """Tests for intent execution"""
    
    @pytest.fixture
    def mock_uc_service(self):
        """Mock Unity Catalog service"""
        with patch('app.uc_service') as mock:
            yield mock
    
    def test_execute_create_catalog(self, mock_uc_service):
        """Test executing create catalog intent"""
        mock_uc_service.create_catalog.return_value = {
            'success': True,
            'message': 'Catalog created',
            'sql': 'CREATE CATALOG test'
        }
        
        intent_data = {
            'intent': 'createCatalog',
            'params': {'catalog': 'test'}
        }
        
        result = execute_intent(intent_data)
        
        assert result['success'] is True
        mock_uc_service.create_catalog.assert_called_once()
    
    def test_execute_grant_permission(self, mock_uc_service):
        """Test executing grant permission intent"""
        mock_uc_service.grant_permission.return_value = {
            'success': True,
            'message': 'Permission granted'
        }
        
        intent_data = {
            'intent': 'grantPermission',
            'params': {
                'privilege': 'SELECT',
                'object': 'catalog.schema.table',
                'principal': 'user'
            }
        }
        
        result = execute_intent(intent_data)
        
        assert result['success'] is True
        mock_uc_service.grant_permission.assert_called_once()
    
    def test_execute_help(self, mock_uc_service):
        """Test executing help intent"""
        intent_data = {'intent': 'help', 'params': {}}
        
        result = execute_intent(intent_data)
        
        assert result['success'] is True
        assert 'help' in result['message'].lower()


class TestAPIEndpoints:
    """Integration tests for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Flask test client"""
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'
    
    @patch('app.parse_with_claude')
    @patch('app.execute_intent')
    def test_chat_endpoint_success(self, mock_execute, mock_parse, client):
        """Test chat endpoint with successful response"""
        mock_parse.return_value = {
            'intent': 'createCatalog',
            'params': {'catalog': 'test'},
            'explanation': 'Creating catalog'
        }
        mock_execute.return_value = {
            'success': True,
            'message': 'Catalog created',
            'sql': 'CREATE CATALOG test'
        }
        
        response = client.post('/api/chat', json={
            'message': 'Create catalog test'
        })
        
        assert response.status_code == 200
        assert response.json['success'] is True
    
    def test_chat_endpoint_no_message(self, client):
        """Test chat endpoint without message"""
        response = client.post('/api/chat', json={})
        assert response.status_code == 400
    
    @patch('app.uc_service.list_catalogs')
    def test_get_catalogs(self, mock_list, client):
        """Test get catalogs endpoint"""
        mock_list.return_value = {
            'success': True,
            'catalogs': [{'name': 'test'}]
        }
        
        response = client.get('/api/catalogs')
        assert response.status_code == 200
        assert 'catalogs' in response.json


class TestComplexScenarios:
    """Integration tests for complex scenarios"""
    
    @pytest.fixture
    def service(self):
        """Service with mocked client"""
        with patch('unity_catalog_service.WorkspaceClient'):
            return UnityCatalogService()
    
    def test_medallion_architecture_setup(self, service):
        """Test setting up medallion architecture"""
        # This would be a comprehensive integration test
        # that tests creating multiple catalogs, schemas, and tables
        pass
    
    def test_permission_workflow(self, service):
        """Test complete permission management workflow"""
        # Test grant, show, and revoke permissions
        pass
    
    def test_error_recovery(self, service):
        """Test error recovery scenarios"""
        # Test handling of API errors, network issues, etc.
        pass


# Performance tests
class TestPerformance:
    """Performance tests"""
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        # Test with multiple simultaneous API calls
        pass
    
    def test_large_catalog_listing(self):
        """Test listing large number of catalogs"""
        # Test performance with hundreds of catalogs
        pass


# Configuration for pytest
@pytest.fixture(scope='session')
def test_config():
    """Test configuration"""
    return {
        'DATABRICKS_HOST': 'https://test.databricks.com',
        'DATABRICKS_TOKEN': 'test-token',
        'ANTHROPIC_API_KEY': 'test-key'
    }
