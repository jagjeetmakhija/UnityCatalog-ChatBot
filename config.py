"""
Configuration Management for Unity Catalog Chatbot
Handles environment-specific settings and validation
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabricksConfig:
    """Databricks connection configuration"""
    host: str
    token: str
    warehouse_id: Optional[str] = None
    cluster_id: Optional[str] = None
    
    def validate(self) -> bool:
        """Validate Databricks configuration"""
        if not self.host or not self.host.startswith('https://'):
            raise ValueError("Invalid Databricks host URL")
        
        if not self.token or len(self.token) < 10:
            raise ValueError("Invalid Databricks token")
        
        return True


@dataclass
class AnthropicConfig:
    """Anthropic API configuration"""
    api_key: str
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 1000
    
    def validate(self) -> bool:
        """Validate Anthropic configuration"""
        if not self.api_key or not self.api_key.startswith('sk-ant-'):
            raise ValueError("Invalid Anthropic API key")
        
        if self.max_tokens < 100 or self.max_tokens > 200000:
            raise ValueError("Invalid max_tokens value")
        
        return True


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    workers: int = 4
    timeout: int = 120
    
    def validate(self) -> bool:
        """Validate server configuration"""
        if self.port < 1024 or self.port > 65535:
            raise ValueError("Invalid port number")
        
        if self.workers < 1 or self.workers > 32:
            raise ValueError("Invalid number of workers")
        
        return True


@dataclass
class SecurityConfig:
    """Security and rate limiting configuration"""
    enable_auth: bool = False
    api_key_header: str = "X-API-Key"
    rate_limit_per_minute: int = 60
    enable_cors: bool = True
    allowed_origins: list = None
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["*"]
    
    def validate(self) -> bool:
        """Validate security configuration"""
        if self.rate_limit_per_minute < 1 or self.rate_limit_per_minute > 1000:
            raise ValueError("Invalid rate limit")
        
        return True


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_to_file: bool = False
    log_file_path: str = "logs/chatbot.log"
    
    def validate(self) -> bool:
        """Validate logging configuration"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        
        return True


class Config:
    """Main configuration class"""
    
    def __init__(self, environment: Environment = None):
        """Initialize configuration from environment variables"""
        
        self.environment = environment or self._detect_environment()
        
        # Databricks configuration
        self.databricks = DatabricksConfig(
            host=os.getenv("DATABRICKS_HOST", ""),
            token=os.getenv("DATABRICKS_TOKEN", ""),
            warehouse_id=os.getenv("DATABRICKS_WAREHOUSE_ID"),
            cluster_id=os.getenv("DATABRICKS_CLUSTER_ID")
        )
        
        # Anthropic configuration
        self.anthropic = AnthropicConfig(
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "1000"))
        )
        
        # Server configuration
        self.server = ServerConfig(
            host=os.getenv("SERVER_HOST", "0.0.0.0"),
            port=int(os.getenv("SERVER_PORT", "5000")),
            debug=os.getenv("FLASK_ENV") == "development",
            workers=int(os.getenv("SERVER_WORKERS", "4")),
            timeout=int(os.getenv("SERVER_TIMEOUT", "120"))
        )
        
        # Security configuration
        self.security = SecurityConfig(
            enable_auth=os.getenv("ENABLE_AUTH", "false").lower() == "true",
            api_key_header=os.getenv("API_KEY_HEADER", "X-API-Key"),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
            enable_cors=os.getenv("ENABLE_CORS", "true").lower() == "true",
            allowed_origins=self._parse_list(os.getenv("ALLOWED_ORIGINS", "*"))
        )
        
        # Logging configuration
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            log_to_file=os.getenv("LOG_TO_FILE", "false").lower() == "true",
            log_file_path=os.getenv("LOG_FILE_PATH", "logs/chatbot.log")
        )
        
        # Feature flags
        self.features = {
            'sql_execution': os.getenv("ENABLE_SQL_EXECUTION", "false").lower() == "true",
            'batch_operations': os.getenv("ENABLE_BATCH_OPS", "true").lower() == "true",
            'audit_logging': os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true",
            'caching': os.getenv("ENABLE_CACHING", "false").lower() == "true",
        }
        
        # Cache configuration (if enabled)
        self.cache = {
            'redis_host': os.getenv("REDIS_HOST", "localhost"),
            'redis_port': int(os.getenv("REDIS_PORT", "6379")),
            'redis_db': int(os.getenv("REDIS_DB", "0")),
            'cache_ttl': int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
        }
    
    def _detect_environment(self) -> Environment:
        """Detect current environment"""
        env_str = os.getenv("ENVIRONMENT", "development").lower()
        
        env_map = {
            'dev': Environment.DEVELOPMENT,
            'development': Environment.DEVELOPMENT,
            'staging': Environment.STAGING,
            'prod': Environment.PRODUCTION,
            'production': Environment.PRODUCTION,
            'test': Environment.TESTING,
            'testing': Environment.TESTING
        }
        
        return env_map.get(env_str, Environment.DEVELOPMENT)
    
    def _parse_list(self, value: str) -> list:
        """Parse comma-separated list from environment variable"""
        if not value:
            return []
        return [item.strip() for item in value.split(',')]
    
    def validate_all(self) -> bool:
        """Validate all configuration sections"""
        try:
            self.databricks.validate()
            self.anthropic.validate()
            self.server.validate()
            self.security.validate()
            self.logging.validate()
            return True
        except ValueError as e:
            raise ValueError(f"Configuration validation failed: {str(e)}")
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary (for logging, excluding secrets)"""
        return {
            'environment': self.environment.value,
            'databricks': {
                'host': self.databricks.host,
                'warehouse_id': self.databricks.warehouse_id,
                'cluster_id': self.databricks.cluster_id,
                # Exclude token
            },
            'anthropic': {
                'model': self.anthropic.model,
                'max_tokens': self.anthropic.max_tokens,
                # Exclude API key
            },
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'debug': self.server.debug,
                'workers': self.server.workers,
                'timeout': self.server.timeout
            },
            'security': {
                'enable_auth': self.security.enable_auth,
                'rate_limit_per_minute': self.security.rate_limit_per_minute,
                'enable_cors': self.security.enable_cors
            },
            'features': self.features
        }
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT


# Singleton instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get configuration singleton instance"""
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config()
        _config_instance.validate_all()
    
    return _config_instance


def reset_config():
    """Reset configuration (useful for testing)"""
    global _config_instance
    _config_instance = None


# Example usage and testing
if __name__ == "__main__":
    # Load configuration
    config = get_config()
    
    print("Configuration loaded successfully!")
    print(f"Environment: {config.environment.value}")
    print(f"Databricks Host: {config.databricks.host}")
    print(f"Server Port: {config.server.port}")
    print(f"Features enabled: {config.features}")
    
    # Validate
    try:
        config.validate_all()
        print("\n✓ All configuration validated successfully!")
    except ValueError as e:
        print(f"\n✗ Configuration error: {e}")
    
    # Print configuration (safe for logging)
    import json
    print("\nConfiguration (sanitized):")
    print(json.dumps(config.to_dict(), indent=2))
