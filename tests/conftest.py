"""
Pytest configuration and shared fixtures for StressSpec tests.

This module provides common test fixtures and utilities that can be used
across all test files. It follows pytest best practices for fixture organization.

BEGINNER NOTES:
- Fixtures are reusable test components (like test data, mock objects, etc.)
- They're defined here so all tests can use them
- They reduce code duplication and make tests more maintainable
- They're automatically discovered by pytest
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any

from src.models.requirement import Requirement
from src.models.risk import Risk, RiskCategory, SeverityLevel
from src.file_loader import FileLoader
from src.requirement_parser import RequirementParser
from src.factories.detector_factory import RiskDetectorFactory
from src.factories.reporter_factory import ReporterFactory
from src.reporting import ReportFormat
from src.config.configuration_provider import ConfigurationProvider, JsonFileConfigurationProvider
from src.config.detector_config_manager import DetectorConfigManager


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_requirement_text() -> str:
    """
    Sample requirement text for testing.
    
    BEGINNER NOTES:
    - This fixture provides a simple requirement text
    - Tests can use this to create Requirement objects
    - It's like a "template" for test data
    """
    return "The system shall process user requests within 2 seconds."


@pytest.fixture
def sample_requirement() -> Requirement:
    """
    Sample Requirement object for testing.
    
    BEGINNER NOTES:
    - This fixture creates a ready-to-use Requirement object
    - Tests can use this without creating their own
    - It's like a "pre-made test object"
    """
    return Requirement(
        id="R001",
        text="The system shall process user requests within 2 seconds.",
        line_number=1
    )


@pytest.fixture
def sample_requirements() -> List[Requirement]:
    """
    List of sample Requirement objects for testing.
    
    BEGINNER NOTES:
    - This fixture provides multiple requirements
    - Useful for testing operations that work on multiple requirements
    - It's like a "test dataset"
    """
    return [
        Requirement(id="R001", text="The system shall process user requests.", line_number=1),
        Requirement(id="R002", text="The system shall validate user input.", line_number=2),
        Requirement(id="R003", text="The system shall log all errors.", line_number=3),
    ]


@pytest.fixture
def sample_risk() -> Risk:
    """
    Sample Risk object for testing.
    
    BEGINNER NOTES:
    - This fixture creates a ready-to-use Risk object
    - Tests can use this to test risk-related functionality
    - It's like a "pre-made risk object"
    """
    return Risk(
        id="R001-AMB-001",
        category=RiskCategory.AMBIGUITY,
        severity=SeverityLevel.HIGH,
        description="Ambiguous requirement",
        requirement_id="R001",
        line_number=1,
        evidence="The requirement uses vague terms",
        suggestion="Use specific, measurable terms"
    )


@pytest.fixture
def sample_risks() -> List[Risk]:
    """
    List of sample Risk objects for testing.
    
    BEGINNER NOTES:
    - This fixture provides multiple risks
    - Useful for testing operations that work on multiple risks
    - It's like a "test risk dataset"
    """
    return [
        Risk(
            id="R001-AMB-001",
            category=RiskCategory.AMBIGUITY,
            severity=SeverityLevel.HIGH,
            description="Ambiguous requirement",
            requirement_id="R001",
            line_number=1,
            evidence="Vague terms",
            suggestion="Be specific"
        ),
        Risk(
            id="R002-SEC-001",
            category=RiskCategory.SECURITY,
            severity=SeverityLevel.MEDIUM,
            description="Security concern",
            requirement_id="R002",
            line_number=2,
            evidence="No security specification",
            suggestion="Add security requirements"
        ),
    ]


# ============================================================================
# Component Fixtures
# ============================================================================

@pytest.fixture
def file_loader() -> FileLoader:
    """
    FileLoader instance for testing.
    
    BEGINNER NOTES:
    - This fixture creates a FileLoader instance
    - Tests can use this to test file loading functionality
    - It's like a "test component factory"
    """
    return FileLoader()


@pytest.fixture
def requirement_parser() -> RequirementParser:
    """
    RequirementParser instance for testing.
    
    BEGINNER NOTES:
    - This fixture creates a RequirementParser instance
    - Tests can use this to test parsing functionality
    """
    return RequirementParser()


@pytest.fixture
def detector_factory() -> RiskDetectorFactory:
    """
    RiskDetectorFactory instance for testing.
    
    BEGINNER NOTES:
    - This fixture creates a RiskDetectorFactory instance
    - Tests can use this to test detector creation
    """
    return RiskDetectorFactory()


@pytest.fixture
def reporter_factory() -> ReporterFactory:
    """
    ReporterFactory instance for testing.
    
    BEGINNER NOTES:
    - This fixture creates a ReporterFactory instance
    - Tests can use this to test reporter creation
    """
    return ReporterFactory()


@pytest.fixture
def config_provider() -> ConfigurationProvider:
    """
    ConfigurationProvider instance for testing.
    
    BEGINNER NOTES:
    - This fixture creates a ConfigurationProvider instance
    - Uses the default JSON file provider
    - Can be overridden in tests for custom configurations
    """
    return JsonFileConfigurationProvider("data/rules.json")


@pytest.fixture
def config_manager(config_provider: ConfigurationProvider) -> DetectorConfigManager:
    """
    DetectorConfigManager instance for testing.
    
    BEGINNER NOTES:
    - This fixture creates a DetectorConfigManager instance
    - Uses the config_provider fixture
    - Tests can inject custom providers if needed
    """
    return DetectorConfigManager(provider=config_provider)


# ============================================================================
# File Fixtures
# ============================================================================

@pytest.fixture
def temp_file() -> str:
    """
    Temporary file path for testing.
    
    BEGINNER NOTES:
    - This fixture creates a temporary file
    - The file is automatically cleaned up after the test
    - Useful for testing file operations without creating real files
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name
        f.write("Requirement 1\n")
        f.write("Requirement 2\n")
        f.write("Requirement 3\n")
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_file_with_content() -> callable:
    """
    Factory fixture for creating temporary files with custom content.
    
    BEGINNER NOTES:
    - This fixture returns a function that creates temp files
    - You can specify the content when calling it
    - It's like a "file factory" for tests
    
    Usage:
        temp_file = temp_file_with_content("Line 1\nLine 2\n")
    """
    def _create_temp_file(content: str, suffix: str = '.txt') -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            temp_path = f.name
            f.write(content)
        return temp_path
    
    created_files = []
    
    def _factory(content: str, suffix: str = '.txt') -> str:
        path = _create_temp_file(content, suffix)
        created_files.append(path)
        return path
    
    yield _factory
    
    # Cleanup all created files
    for path in created_files:
        if os.path.exists(path):
            os.unlink(path)


# ============================================================================
# Mock Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_config_provider() -> ConfigurationProvider:
    """
    Mock ConfigurationProvider for testing.
    
    BEGINNER NOTES:
    - This fixture creates a mock configuration provider
    - It returns a simple, predictable configuration
    - Useful for testing without needing real config files
    """
    from unittest.mock import Mock
    
    mock_provider = Mock(spec=ConfigurationProvider)
    mock_provider.get_configuration.return_value = {
        'detectors': {
            'ambiguity': {
                'enabled': True,
                'rules': {}
            },
            'security': {
                'enabled': True,
                'rules': {}
            }
        },
        'global_settings': {},
        'severity_mapping': {}
    }
    mock_provider.get_detector_config.return_value = {'enabled': True, 'rules': {}}
    mock_provider.is_detector_enabled.return_value = True
    mock_provider.get_global_setting.return_value = None
    mock_provider.get_severity_mapping.return_value = {}
    
    return mock_provider


# ============================================================================
# Test Data Factory
# ============================================================================

class TestDataFactory:
    """
    Factory class for creating test data.
    
    BEGINNER NOTES:
    - This class provides methods to create test data
    - It's like a "test data generator"
    - Makes it easy to create consistent test data across tests
    """
    
    @staticmethod
    def create_requirement(id: str = "R001", text: str = "Test requirement", 
                          line_number: int = 1) -> Requirement:
        """Create a Requirement object for testing."""
        return Requirement(id=id, text=text, line_number=line_number)
    
    @staticmethod
    def create_risk(requirement_id: str = "R001", category: RiskCategory = RiskCategory.AMBIGUITY,
                   severity: SeverityLevel = SeverityLevel.MEDIUM,
                   risk_id: str = "R001-AMB-001") -> Risk:
        """Create a Risk object for testing."""
        return Risk(
            id=risk_id,
            category=category,
            severity=severity,
            description="Test risk",
            requirement_id=requirement_id,
            line_number=1,
            evidence="Test evidence",
            suggestion="Test suggestion"
        )
    
    @staticmethod
    def create_requirements(count: int = 3) -> List[Requirement]:
        """Create a list of Requirement objects for testing."""
        return [
            TestDataFactory.create_requirement(
                id=f"R{i+1:03d}",
                text=f"Requirement {i+1}",
                line_number=i+1
            )
            for i in range(count)
        ]
    
    @staticmethod
    def create_risks_by_requirement(requirements: List[Requirement]) -> Dict[str, List[Risk]]:
        """Create a risks_by_requirement dictionary for testing."""
        risks_by_requirement = {}
        for req in requirements:
            risks_by_requirement[req.id] = [
                TestDataFactory.create_risk(
                    requirement_id=req.id,
                    risk_id=f"{req.id}-AMB-001"
                )
            ]
        return risks_by_requirement


@pytest.fixture
def test_data_factory() -> TestDataFactory:
    """
    TestDataFactory instance for testing.
    
    BEGINNER NOTES:
    - This fixture provides a TestDataFactory instance
    - Tests can use it to create test data easily
    - It's like a "test data helper"
    """
    return TestDataFactory()

