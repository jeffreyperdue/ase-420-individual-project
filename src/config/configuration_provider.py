"""
Configuration provider interface for StressSpec.

This module defines the abstraction for configuration providers, allowing
different sources of configuration (JSON files, databases, environment variables, etc.)
to be used interchangeably.

BEGINNER NOTES:
- This follows the Strategy pattern and Dependency Inversion Principle
- It allows swapping configuration sources without changing code that uses configuration
- It makes testing easier by allowing mock configuration providers
- It follows the "program to interfaces, not implementations" principle
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ConfigurationProvider(ABC):
    """
    Abstract interface for configuration providers.
    
    BEGINNER NOTES:
    - This is the "contract" that all configuration providers must follow
    - It's like a "job description" - any provider must implement these methods
    - It allows different configuration sources (file, database, API, etc.)
    - It makes the code more flexible and testable
    
    This interface defines:
    - get_configuration(): Load configuration from source
    - get_detector_config(): Get detector-specific configuration
    - is_detector_enabled(): Check if detector is enabled
    - get_global_setting(): Get global setting value
    - get_severity_mapping(): Get severity mapping
    """
    
    @abstractmethod
    def get_configuration(self) -> Dict[str, Any]:
        """
        Load and return the complete configuration.
        
        Returns:
            Dictionary containing the complete configuration
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        pass
    
    @abstractmethod
    def get_detector_config(self, detector_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific detector.
        
        Args:
            detector_name: Name of the detector
            
        Returns:
            Dictionary containing detector configuration
        """
        pass
    
    @abstractmethod
    def is_detector_enabled(self, detector_name: str) -> bool:
        """
        Check if a detector is enabled.
        
        Args:
            detector_name: Name of the detector
            
        Returns:
            True if detector is enabled, False otherwise
        """
        pass
    
    @abstractmethod
    def get_global_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a global setting value.
        
        Args:
            key: Setting key name
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        pass
    
    @abstractmethod
    def get_severity_mapping(self) -> Dict[str, Any]:
        """
        Get severity mapping configuration.
        
        Returns:
            Dictionary containing severity mappings
        """
        pass


class JsonFileConfigurationProvider(ConfigurationProvider):
    """
    Configuration provider that loads configuration from a JSON file.
    
    BEGINNER NOTES:
    - This is the default implementation that reads from rules.json
    - It implements the ConfigurationProvider interface
    - It's like a "file-based librarian" that reads from a book
    - Other providers could read from databases, APIs, environment variables, etc.
    """
    
    def __init__(self, rules_file: str = "data/rules.json"):
        """
        Initialize JSON file configuration provider.
        
        Args:
            rules_file: Path to the JSON configuration file
        """
        self.rules_file = rules_file
        self._config: Optional[Dict[str, Any]] = None
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Returns:
            Dictionary containing configuration
            
        Raises:
            ConfigurationError: If file cannot be loaded or is invalid
        """
        if self._config is None:
            self._config = self._load_from_file()
        return self._config
    
    def _load_from_file(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Returns:
            Dictionary containing configuration
            
        Raises:
            ConfigurationError: If file cannot be loaded or is invalid
        """
        import json
        from pathlib import Path
        from src.exceptions import ConfigurationError
        
        try:
            rules_path = Path(self.rules_file)
            if not rules_path.exists():
                raise ConfigurationError(
                    f"Rules file not found: {self.rules_file}",
                    config_file=self.rules_file
                )
            
            with open(rules_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return config
            
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in rules file: {e}",
                config_file=self.rules_file,
                details={'json_error': str(e)}
            )
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Error loading rules file: {e}",
                config_file=self.rules_file,
                details={'error': str(e)}
            )
    
    def get_detector_config(self, detector_name: str) -> Dict[str, Any]:
        """Get configuration for a specific detector."""
        config = self.get_configuration()
        return config.get('detectors', {}).get(detector_name, {})
    
    def is_detector_enabled(self, detector_name: str) -> bool:
        """Check if detector is enabled."""
        detector_config = self.get_detector_config(detector_name)
        return detector_config.get('enabled', False)
    
    def get_global_setting(self, key: str, default: Any = None) -> Any:
        """Get global setting value."""
        config = self.get_configuration()
        return config.get('global_settings', {}).get(key, default)
    
    def get_severity_mapping(self) -> Dict[str, Any]:
        """Get severity mapping configuration."""
        config = self.get_configuration()
        return config.get('severity_mapping', {})
    
    def reload(self) -> None:
        """
        Reload configuration from file.
        
        BEGINNER NOTES:
        - This clears the cached configuration
        - Next call to get_configuration() will reload from file
        - Useful for testing or dynamic configuration updates
        """
        self._config = None

