"""
Detector configuration manager for StressSpec.

This module provides functionality for loading and accessing detector configuration
using a configuration provider abstraction.

BEGINNER NOTES:
- This class handles all configuration loading and access
- It follows the Single Responsibility Principle - only handles configuration
- It uses a ConfigurationProvider (Strategy pattern) for flexibility
- It can be reused by detectors and factories
- It makes configuration easier to test and mock
"""

from typing import Dict, Any, Optional
from src.exceptions import ConfigurationError
from src.config.configuration_provider import ConfigurationProvider, JsonFileConfigurationProvider


class DetectorConfigManager:
    """
    Manages detector configuration loading and access.
    
    BEGINNER NOTES:
    - This class is like a "configuration librarian" that knows how to read and find config
    - It uses a ConfigurationProvider to get configuration (Strategy pattern)
    - It can be used by detectors, factories, or any component that needs configuration
    - It makes it easy to test with mock configurations
    - It follows Dependency Inversion Principle - depends on ConfigurationProvider abstraction
    
    This class provides:
    - Configuration loading via ConfigurationProvider
    - Access to detector-specific configuration
    - Access to global settings
    - Access to severity mappings
    - Methods to check if detectors are enabled
    """
    
    def __init__(self, 
                 rules_file: str = "data/rules.json",
                 provider: Optional[ConfigurationProvider] = None):
        """
        Initialize the configuration manager.
        
        Args:
            rules_file: Path to the rules configuration file (used if provider is None)
            provider: Optional ConfigurationProvider instance (for dependency injection/testing)
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        self.provider = provider or JsonFileConfigurationProvider(rules_file)
        self.rules_file = rules_file
    
    @property
    def config(self) -> Dict[str, Any]:
        """
        Get the complete configuration (delegates to provider).
        
        Returns:
            Dictionary containing complete configuration
        """
        return self.provider.get_configuration()
    
    def get_detector_config(self, detector_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific detector.
        
        Args:
            detector_name: Name of the detector (e.g., "ambiguity", "security")
            
        Returns:
            Dictionary containing detector configuration (empty dict if not found)
        """
        return self.provider.get_detector_config(detector_name)
    
    def is_detector_enabled(self, detector_name: str) -> bool:
        """
        Check if a detector is enabled in the configuration.
        
        Args:
            detector_name: Name of the detector
            
        Returns:
            True if detector is enabled, False otherwise
        """
        return self.provider.is_detector_enabled(detector_name)
    
    def get_global_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a global setting value.
        
        Args:
            key: Setting key name
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        return self.provider.get_global_setting(key, default)
    
    def get_severity_mapping(self) -> Dict[str, Any]:
        """
        Get severity mapping configuration.
        
        Returns:
            Dictionary containing severity mappings
        """
        return self.provider.get_severity_mapping()
    
    def get_all_detector_names(self) -> list[str]:
        """
        Get list of all detector names in configuration.
        
        Returns:
            List of detector names
        """
        return list(self.config.get('detectors', {}).keys())
    
    def reload(self) -> None:
        """
        Reload configuration from provider (useful for testing or dynamic updates).
        
        BEGINNER NOTES:
        - This allows you to reload config without creating a new manager
        - Useful if the config changes during runtime
        - Mainly used in tests or for dynamic configuration updates
        - Delegates to provider's reload method if available
        """
        if hasattr(self.provider, 'reload'):
            self.provider.reload()

