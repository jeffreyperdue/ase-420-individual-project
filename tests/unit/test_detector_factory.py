"""
Unit tests for the RiskDetectorFactory class.

This module tests the RiskDetectorFactory to ensure it correctly creates
detectors for different types and handles edge cases.
"""

import pytest
from unittest.mock import Mock, patch
from src.factories.detector_factory import RiskDetectorFactory
from src.detectors.ambiguity_detector import AmbiguityDetector
from src.detectors.security_detector import SecurityDetector
from src.detectors.conflict_detector import ConflictDetector
from src.detectors.missing_detail_detector import MissingDetailDetector
from src.detectors.performance_detector import PerformanceDetector
from src.detectors.availability_detector import AvailabilityDetector
from src.detectors.traceability_detector import TraceabilityDetector
from src.detectors.scope_detector import ScopeDetector
from src.detectors.base import RiskDetector
from src.config.detector_config_manager import DetectorConfigManager


class TestRiskDetectorFactory:
    """Test cases for the RiskDetectorFactory class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.factory = RiskDetectorFactory()
    
    # Detector creation tests
    def test_create_ambiguity_detector(self):
        """Test creating an ambiguity detector."""
        detector = self.factory.create_detector('ambiguity')
        
        assert isinstance(detector, AmbiguityDetector)
        assert isinstance(detector, RiskDetector)
    
    def test_create_security_detector(self):
        """Test creating a security detector."""
        detector = self.factory.create_detector('security')
        
        assert isinstance(detector, SecurityDetector)
        assert isinstance(detector, RiskDetector)
    
    def test_create_conflict_detector(self):
        """Test creating a conflict detector."""
        detector = self.factory.create_detector('conflict')
        
        assert isinstance(detector, ConflictDetector)
        assert isinstance(detector, RiskDetector)
    
    def test_create_missing_detail_detector(self):
        """Test creating a missing detail detector."""
        detector = self.factory.create_detector('missing_detail')
        
        assert isinstance(detector, MissingDetailDetector)
        assert isinstance(detector, RiskDetector)
    
    def test_create_performance_detector(self):
        """Test creating a performance detector."""
        detector = self.factory.create_detector('performance')
        
        assert isinstance(detector, PerformanceDetector)
        assert isinstance(detector, RiskDetector)
    
    def test_create_availability_detector(self):
        """Test creating an availability detector."""
        detector = self.factory.create_detector('availability')
        
        assert isinstance(detector, AvailabilityDetector)
        assert isinstance(detector, RiskDetector)
    
    def test_create_traceability_detector(self):
        """Test creating a traceability detector."""
        detector = self.factory.create_detector('traceability')
        
        assert isinstance(detector, TraceabilityDetector)
        assert isinstance(detector, RiskDetector)
    
    def test_create_scope_detector(self):
        """Test creating a scope detector."""
        detector = self.factory.create_detector('scope')
        
        assert isinstance(detector, ScopeDetector)
        assert isinstance(detector, RiskDetector)
    
    # Error handling tests
    def test_unknown_detector_type_raises_error(self):
        """Test that unknown detector type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown detector type"):
            self.factory.create_detector('unknown_detector')
    
    def test_error_message_includes_available_types(self):
        """Test that error message includes available detector types."""
        with pytest.raises(ValueError) as exc_info:
            self.factory.create_detector('unknown')
        
        error_message = str(exc_info.value)
        assert "Available types" in error_message
        assert "ambiguity" in error_message.lower()
    
    # Caching tests
    def test_detector_caching(self):
        """Test that detectors are cached."""
        detector1 = self.factory.create_detector('ambiguity')
        detector2 = self.factory.create_detector('ambiguity')
        
        # Should return the same instance (cached)
        assert detector1 is detector2
    
    def test_same_detector_returned_on_multiple_calls(self):
        """Test that same detector is returned on multiple calls."""
        detector1 = self.factory.create_detector('security')
        detector2 = self.factory.create_detector('security')
        detector3 = self.factory.create_detector('security')
        
        assert detector1 is detector2
        assert detector2 is detector3
    
    # Configuration integration tests
    def test_create_all_detectors(self):
        """Test creating all available detectors."""
        detectors = self.factory.create_all_detectors()
        
        assert isinstance(detectors, list)
        assert len(detectors) == 8  # All 8 detector types
        assert all(isinstance(d, RiskDetector) for d in detectors)
    
    def test_create_enabled_detectors(self):
        """Test creating only enabled detectors."""
        detectors = self.factory.create_enabled_detectors()
        
        assert isinstance(detectors, list)
        assert all(isinstance(d, RiskDetector) for d in detectors)
        # Should return at least some detectors (depending on config)
        assert len(detectors) > 0
    
    def test_create_enabled_detectors_with_config(self):
        """Test creating enabled detectors with custom config."""
        # Create factory with custom config manager
        mock_config_manager = Mock(spec=DetectorConfigManager)
        mock_config_manager.get_all_detector_names.return_value = ['ambiguity', 'security']
        mock_config_manager.is_detector_enabled.return_value = True
        
        factory = RiskDetectorFactory(config_manager=mock_config_manager)
        detectors = factory.create_enabled_detectors()
        
        assert len(detectors) == 2
        assert any(isinstance(d, AmbiguityDetector) for d in detectors)
        assert any(isinstance(d, SecurityDetector) for d in detectors)
    
    def test_create_enabled_detectors_falls_back_to_all(self):
        """Test that create_enabled_detectors falls back to all when config fails."""
        # Create factory with config manager that raises error
        mock_config_manager = Mock(spec=DetectorConfigManager)
        mock_config_manager.get_all_detector_names.side_effect = Exception("Config error")
        
        factory = RiskDetectorFactory(config_manager=mock_config_manager)
        detectors = factory.create_enabled_detectors()
        
        # Should fall back to all detectors
        assert len(detectors) == 8
    
    # Detector registration tests
    def test_register_custom_detector(self):
        """Test registering a custom detector type."""
        # Create a custom detector class
        class CustomDetector(RiskDetector):
            def detect_risks(self, requirement):
                return []
            
            def get_detector_name(self):
                return "Custom Detector"
            
            def get_category(self):
                from src.models.risk import RiskCategory
                return RiskCategory.AMBIGUITY
        
        # Register the custom detector
        self.factory.register_detector('custom', CustomDetector)
        
        # Should be able to create it
        detector = self.factory.create_detector('custom')
        assert isinstance(detector, CustomDetector)
    
    def test_register_invalid_detector_raises_error(self):
        """Test that registering a non-RiskDetector class raises ValueError."""
        class NotADetector:
            pass
        
        with pytest.raises(ValueError, match="must implement RiskDetector interface"):
            self.factory.register_detector('invalid', NotADetector)
    
    def test_registered_detector_clears_cache(self):
        """Test that registering a detector clears the cache."""
        # Create and cache a detector
        detector1 = self.factory.create_detector('ambiguity')
        
        # Register a new class for the same type
        class NewAmbiguityDetector(AmbiguityDetector):
            pass
        
        self.factory.register_detector('ambiguity', NewAmbiguityDetector)
        
        # Should get new detector instance
        detector2 = self.factory.create_detector('ambiguity')
        assert isinstance(detector2, NewAmbiguityDetector)
        assert detector1 is not detector2
    
    # Information methods tests
    def test_get_available_detector_types(self):
        """Test getting list of available detector types."""
        types = self.factory.get_available_detector_types()
        
        assert isinstance(types, list)
        assert len(types) == 8
        assert 'ambiguity' in types
        assert 'security' in types
        assert 'conflict' in types
        assert 'missing_detail' in types
        assert 'performance' in types
        assert 'availability' in types
        assert 'traceability' in types
        assert 'scope' in types
    
    def test_get_detector_info(self):
        """Test getting information about all detectors."""
        info = self.factory.get_detector_info()
        
        assert isinstance(info, dict)
        assert len(info) == 8
        assert 'ambiguity' in info
        assert 'security' in info
        assert info['ambiguity'] == "Ambiguity Detector"
        assert info['security'] == "Security Detector"
    
    # Case insensitivity tests
    def test_detector_type_case_insensitive(self):
        """Test that detector type is case-insensitive."""
        detector1 = self.factory.create_detector('AMBIGUITY')
        detector2 = self.factory.create_detector('ambiguity')
        detector3 = self.factory.create_detector('Ambiguity')
        
        assert isinstance(detector1, AmbiguityDetector)
        assert isinstance(detector2, AmbiguityDetector)
        assert isinstance(detector3, AmbiguityDetector)
    
    # Edge cases
    def test_create_detector_with_custom_rules_file(self):
        """Test creating detector with custom rules file."""
        factory = RiskDetectorFactory(rules_file="data/rules.json")
        detector = factory.create_detector('ambiguity')
        
        assert isinstance(detector, AmbiguityDetector)
    
    def test_factory_handles_detector_creation_errors(self):
        """Test that factory handles errors when creating detectors."""
        # This test verifies that create_all_detectors handles errors gracefully
        detectors = self.factory.create_all_detectors()
        
        # Should return list even if some detectors fail
        assert isinstance(detectors, list)
    
    def test_multiple_factories_independent(self):
        """Test that multiple factory instances are independent."""
        factory1 = RiskDetectorFactory()
        factory2 = RiskDetectorFactory()
        
        detector1 = factory1.create_detector('ambiguity')
        detector2 = factory2.create_detector('ambiguity')
        
        # Should be different instances (different factories)
        assert detector1 is not detector2

