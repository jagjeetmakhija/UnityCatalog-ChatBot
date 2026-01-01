"""
Test Suite for Unity Catalog Chatbot
"""

import pytest
from unittest.mock import Mock, patch
from unity_catalog_service import UnityCatalogService
from app import parse_with_claude, execute_intent


class TestUnityCatalogService:
    """Tests for Unity Catalog Service"""
    
    def test_parse_object_path_catalog(self, uc_service):
        """Test parsing catalog path"""
        result = uc_service.parse_object_path("my_catalog")
        assert result == {'catalog': 'my_catalog'}
    
    def test_parse_object_path_schema(self, uc_service):
        """Test parsing schema path"""
        result = uc_service.parse_object_path("my_catalog.my_schema")
        assert result == {
            'catalog': 'my_catalog',
            'schema': 'my_schema'
        }
    
    def test_parse_object_path_table(self, uc_service):
        """Test parsing table path"""
        result = uc_service.parse_object_path("my_catalog.my_schema.my_table")
        assert result == {
            'catalog': 'my_catalog',
            'schema': 'my_schema',
            'table': 'my_table'
        }
    
    def test_create_catalog_success(self, uc_service):
        """Test successful catalog creation"""
        mock_catalog = Mock()
        mock_catalog.name = "test_catalog"
        mock_catalog.owner = "test_user"
        mock_catalog.created_at = "2025-01-01T00:00:00Z"
        
        uc_service.client.catalogs.create = Mock(return_value=mock_catalog)
        
        result = uc_service.create_catalog("test_catalog")
        
        assert result['success'] is True
        assert result['catalog']['name'] == "test_catalog"
        assert "CREATE CATALOG" in result['sql']
    
    def test_create_catalog_error(self, uc_service):
        """Test catalog creation error handling"""
        uc_service.client.catalogs.create = Mock(
            side_effect=Exception("Permission denied")
        )
        
        result = uc_service.create_catalog("test_catalog")
        
        assert result['success'] is False
        assert "Permission denied" in result['message']
    
    def test_create_schema_success(self, uc_service):
        """Test successful schema creation"""
        mock_schema = Mock()
        mock_schema.name = "test_schema"
        mock_schema.catalog_name = "test_catalog"
        mock_schema.owner = "test_user"
        
        uc_service.client.schemas.create = Mock(return_value=mock_schema)
        
        result = uc_service.create_schema("test_catalog", "test_schema")
        
        assert result['success'] is True
        assert "CREATE SCHEMA" in result['sql']
    
    def test_validate_name_valid(self, uc_service):
        """Test name validation with valid names"""
        assert uc_service.validate_name("valid_name") is True
        assert uc_service.validate_name("ValidName123") is True
    
    def test_validate_name_invalid(self, uc_service):
        """Test name validation with invalid names"""
        assert uc_service.validate_name("invalid-name") is False
        assert uc_service.validate_name("invalid name") is False
        assert uc_service.validate_name("invalid.name") is False


class TestIntentParsing:
    """Tests for intent parsing with Claude"""
    
    def test_parse_create_catalog(self, claude_client_mock):
        """Test parsing create catalog intent"""
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text='{"intent": "createCatalog", "params": {"catalog": "sales"}, "explanation": "Creating catalog"}',
                type='text'
            )
        ]
        claude_client_mock.messages.create.return_value = mock_response
        
        result = parse_with_claude("Create a catalog named sales")
        
        assert result['intent'] == 'createCatalog'
        assert result['params']['catalog'] == 'sales'
    
    def test_parse_grant_permission(self, claude_client_mock):
        """Test parsing grant permission intent"""
        mock_response = Mock()
        mock_response.content = [
            Mock(
                text='{"intent": "grantPermission", "params": {"privilege": "SELECT", "object": "sales.customers", "principal": "analysts"}}',
                type='text'
            )
        ]
        claude_client_mock.messages.create.return_value = mock_response
        
        result = parse_with_claude("Grant SELECT on sales.customers to analysts")
        
        assert result['intent'] == 'grantPermission'
        assert result['params']['privilege'] == 'SELECT'
    
    def test_parse_error_handling(self, claude_client_mock):
        """Test error handling in parsing"""
        claude_client_mock.messages.create.side_effect = Exception("API Error")
        
        result = parse_with_claude("Invalid request")
        
        assert result['intent'] == 'help'


class TestExecuteIntent:
    """Tests for intent execution"""

    def test_execute_create_catalog(self):
        """Test executing create catalog intent"""
        mock_uc = Mock()
        mock_uc.create_catalog.return_value = {
            'success': True,
            'message': 'Catalog created',
            'sql': 'CREATE CATALOG test'
        }

        with patch('app._init_services', return_value=(mock_uc, Mock())):
            intent_data = {
                'intent': 'createCatalog',
                'params': {'catalog': 'test'}
            }

            result = execute_intent(intent_data)

        assert result['success'] is True
        mock_uc.create_catalog.assert_called_once()
    
    def test_execute_grant_permission(self):
        """Test executing grant permission intent"""
        mock_uc = Mock()
        mock_uc.grant_permission.return_value = {
            'success': True,
            'message': 'Permission granted'
        }

        with patch('app._init_services', return_value=(mock_uc, Mock())):
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
        mock_uc.grant_permission.assert_called_once()
    
    def test_execute_help(self, uc_service):
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
    
    def test_get_catalogs(self, client):
        """Test get catalogs endpoint"""
        mock_uc = Mock()
        mock_uc.list_catalogs.return_value = {
            'success': True,
            'catalogs': [{'name': 'test'}]
        }

        with patch('app._init_services', return_value=(mock_uc, Mock())):
            response = client.get('/api/catalogs')

        assert response.status_code == 200
        assert 'catalogs' in response.json


class TestComplexScenarios:
    """Integration tests for complex scenarios"""

    @pytest.fixture
    def service(self, uc_service):
        """Service with mocked client"""
        return uc_service

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
