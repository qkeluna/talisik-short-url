"""Configuration management for Talisik Short URL service"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class TalisikConfig:
    """Configuration class for Talisik Short URL service"""
    
    # Xata Database Configuration
    xata_api_key: str
    xata_database_url: str
    
    # Application Configuration
    base_url: str = "http://localhost:8000"
    storage_backend: str = "memory"  # "memory" or "xata"
    default_code_length: int = 7
    max_custom_code_length: int = 50
    
    # Feature flags
    enable_analytics: bool = True
    enable_expiration: bool = True
    
    # Development settings
    debug: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'TalisikConfig':
        """Create configuration from environment variables"""
        xata_api_key = os.getenv('XATA_API_KEY')
        xata_database_url = os.getenv('XATA_DATABASE_URL')
        
        if not xata_api_key:
            raise ValueError("XATA_API_KEY environment variable is required")
        if not xata_database_url:
            raise ValueError("XATA_DATABASE_URL environment variable is required")
        
        return cls(
            xata_api_key=xata_api_key,
            xata_database_url=xata_database_url,
            base_url=os.getenv('BASE_URL', cls.base_url),
            storage_backend=os.getenv('STORAGE_BACKEND', cls.storage_backend),
            default_code_length=int(os.getenv('DEFAULT_CODE_LENGTH', cls.default_code_length)),
            max_custom_code_length=int(os.getenv('MAX_CUSTOM_CODE_LENGTH', cls.max_custom_code_length)),
            enable_analytics=os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true',
            enable_expiration=os.getenv('ENABLE_EXPIRATION', 'true').lower() == 'true',
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', cls.log_level),
        )
    
    def validate(self) -> None:
        """Validate configuration settings"""
        if self.default_code_length < 1 or self.default_code_length > 50:
            raise ValueError("default_code_length must be between 1 and 50")
        
        if self.max_custom_code_length < 1 or self.max_custom_code_length > 100:
            raise ValueError("max_custom_code_length must be between 1 and 100")
        
        if self.storage_backend not in ["memory", "xata"]:
            raise ValueError("storage_backend must be 'memory' or 'xata'")


# Global configuration instance
config: Optional[TalisikConfig] = None


def get_config() -> TalisikConfig:
    """Get the global configuration instance"""
    global config
    if config is None:
        config = TalisikConfig.from_env()
        config.validate()
    return config


def set_config(new_config: TalisikConfig) -> None:
    """Set the global configuration instance (useful for testing)"""
    global config
    config = new_config 