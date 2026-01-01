"""Shared pytest fixtures for offline testing."""

import os
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import app as app_module
import unity_catalog_service as uc_module


@pytest.fixture(scope="function", autouse=True)
def dummy_env(monkeypatch):
    """Set safe defaults to satisfy config validation without real secrets."""
    env_defaults = {
        "DATABRICKS_HOST": "https://dummy",
        "DATABRICKS_TOKEN": "dummytoken123",
        "ANTHROPIC_API_KEY": "sk-ant-dummy",
    }
    for key, value in env_defaults.items():
        monkeypatch.setenv(key, value)
    yield


@pytest.fixture
def workspace_client():
    """Provide a mocked Databricks WorkspaceClient surface."""
    catalogs = MagicMock()
    catalogs.create = MagicMock()
    catalogs.list = MagicMock(return_value=[])
    catalogs.get = MagicMock()
    catalogs.delete = MagicMock()

    schemas = MagicMock()
    schemas.create = MagicMock()
    schemas.list = MagicMock(return_value=[])
    schemas.delete = MagicMock()

    tables = MagicMock()
    tables.create = MagicMock()
    tables.list = MagicMock(return_value=[])
    tables.get = MagicMock()

    grants = MagicMock()
    grants.update = MagicMock()
    grants.get = MagicMock()

    sql = MagicMock()
    sql.execute = MagicMock(return_value=[])

    return SimpleNamespace(
        catalogs=catalogs,
        schemas=schemas,
        tables=tables,
        grants=grants,
        sql=sql,
    )


@pytest.fixture(autouse=True)
def patch_workspace_client(monkeypatch, workspace_client):
    """Force UnityCatalogService to use the shared workspace client mock."""
    monkeypatch.setattr(uc_module, "WorkspaceClient", MagicMock(return_value=workspace_client))
    yield


@pytest.fixture
def uc_service(workspace_client):
    """Real UnityCatalogService instance bound to the mocked workspace client."""
    service = uc_module.UnityCatalogService(
        workspace_url="https://dummy",
        token="dummytoken123",
    )
    service.client = workspace_client
    return service


@pytest.fixture
def claude_client_mock():
    """Mock Anthropics client matching the methods used in app.py."""
    messages = MagicMock()
    messages.create = MagicMock()
    return SimpleNamespace(messages=messages)


@pytest.fixture(autouse=True)
def patch_app_init(monkeypatch, uc_service, claude_client_mock):
    """Override app._init_services to return mocked services for tests."""
    def mock_init_services():
        return uc_service, claude_client_mock
    
    monkeypatch.setattr(app_module, "_init_services", mock_init_services)
    yield

