"""
Tests for ConfigurationProvider abstraction.

This module tests the configuration provider interface and implementations.
"""

import pytest
import json
import tempfile
import os
from src.config.configuration_provider import (
    ConfigurationProvider,
    JsonFileConfigurationProvider
)
from src.exceptions import ConfigurationError


class TestJsonFileConfigurationProvider:
    """Test cases for JSON file configuration provider."""
    
    def test_load_valid_configuration(self):
        """Test loading valid JSON configuration."""
        config_data = {
            'detectors': {
                'ambiguity': {'enabled': True, 'rules': {}},
                'security': {'enabled': False, 'rules': {}}
            },
            'global_settings': {'setting1': 'value1'},
            'severity_mapping': {'high': 3}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            provider = JsonFileConfigurationProvider(temp_path)
            config = provider.get_configuration()
            
            assert config == config_data
        finally:
            os.unlink(temp_path)
    
    def test_get_detector_config(self):
        """Test getting detector-specific configuration."""
        config_data = {
            'detectors': {
                'ambiguity': {'enabled': True, 'rules': {'rule1': {}}}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            provider = JsonFileConfigurationProvider(temp_path)
            detector_config = provider.get_detector_config('ambiguity')
            
            assert detector_config == {'enabled': True, 'rules': {'rule1': {}}}
        finally:
            os.unlink(temp_path)
    
    def test_is_detector_enabled(self):
        """Test checking if detector is enabled."""
        config_data = {
            'detectors': {
                'ambiguity': {'enabled': True},
                'security': {'enabled': False}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            provider = JsonFileConfigurationProvider(temp_path)
            
            assert provider.is_detector_enabled('ambiguity') is True
            assert provider.is_detector_enabled('security') is False
            assert provider.is_detector_enabled('nonexistent') is False
        finally:
            os.unlink(temp_path)
    
    def test_get_global_setting(self):
        """Test getting global settings."""
        config_data = {
            'global_settings': {'setting1': 'value1', 'setting2': 42}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            provider = JsonFileConfigurationProvider(temp_path)
            
            assert provider.get_global_setting('setting1') == 'value1'
            assert provider.get_global_setting('setting2') == 42
            assert provider.get_global_setting('nonexistent') is None
            assert provider.get_global_setting('nonexistent', 'default') == 'default'
        finally:
            os.unlink(temp_path)
    
    def test_get_severity_mapping(self):
        """Test getting severity mapping."""
        config_data = {
            'severity_mapping': {'high': 3, 'medium': 2, 'low': 1}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            provider = JsonFileConfigurationProvider(temp_path)
            mapping = provider.get_severity_mapping()
            
            assert mapping == {'high': 3, 'medium': 2, 'low': 1}
        finally:
            os.unlink(temp_path)
    
    def test_file_not_found_raises_error(self):
        """Test that missing file raises ConfigurationError."""
        provider = JsonFileConfigurationProvider("nonexistent.json")
        
        with pytest.raises(ConfigurationError) as exc_info:
            provider.get_configuration()
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ConfigurationError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            temp_path = f.name
        
        try:
            provider = JsonFileConfigurationProvider(temp_path)
            
            with pytest.raises(ConfigurationError) as exc_info:
                provider.get_configuration()
            
            assert "invalid json" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)
    
    def test_reload_configuration(self):
        """Test reloading configuration."""
        config_data1 = {'detectors': {'test': {'enabled': True}}}
        config_data2 = {'detectors': {'test': {'enabled': False}}}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data1, f)
            temp_path = f.name
        
        try:
            provider = JsonFileConfigurationProvider(temp_path)
            
            # Load first config
            assert provider.is_detector_enabled('test') is True
            
            # Update file
            with open(temp_path, 'w') as f:
                json.dump(config_data2, f)
            
            # Reload
            provider.reload()
            
            # Should have new config
            assert provider.is_detector_enabled('test') is False
        finally:
            os.unlink(temp_path)

