# StressSpec Test Suite Organization

This directory contains the comprehensive test suite for StressSpec, organized by test type.

## Directory Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures (accessible to all tests)
├── unit/                       # Unit tests (21 files)
│   ├── __init__.py
│   ├── test_risk.py
│   ├── test_requirement.py
│   ├── test_requirement_parser.py
│   ├── test_file_loader.py
│   ├── test_scoring.py
│   ├── test_configuration_provider.py
│   ├── test_reporter_factory.py
│   ├── test_observer_pattern.py
│   ├── test_chain_of_responsibility.py
│   ├── test_ambiguity_detector.py
│   ├── test_security_detector.py
│   ├── test_conflict_detector.py
│   ├── test_missing_detail_detector.py
│   ├── test_availability_detector.py
│   ├── test_performance_detector.py
│   ├── test_scope_detector.py
│   ├── test_traceability_detector.py
│   ├── test_analyzer.py
│   ├── test_detector_factory.py
│   ├── test_stress_spec_service.py
│   └── test_error_handling.py
├── integration/                # Integration tests (2 files)
│   ├── __init__.py
│   ├── test_integration.py
│   └── test_integration_new_detectors.py
├── regression/                 # Regression tests (1 file)
│   ├── __init__.py
│   └── test_regression.py
└── acceptance/                 # Acceptance tests (1 file)
    ├── __init__.py
    └── test_acceptance.py
```

## Test Categories

### Unit Tests (`unit/`)
Tests individual components in isolation with mocked dependencies.
- **Models**: Risk, Requirement
- **Core Components**: FileLoader, RequirementParser, Analyzer, Scoring
- **Detectors**: All 8 risk detectors
- **Factories**: DetectorFactory, ReporterFactory
- **Services**: StressSpecService
- **Design Patterns**: Observer, Chain of Responsibility
- **Error Handling**: Custom exceptions, error handlers

### Integration Tests (`integration/`)
Tests complete workflows with multiple components working together.
- End-to-end file processing pipeline
- Complete analysis workflow
- Report generation across all formats
- Top 5 riskiest requirements feature

### Regression Tests (`regression/`)
Tests that verify previously fixed bugs don't reoccur.
- Previously fixed bugs
- Edge cases that caused issues
- Data integrity checks
- Performance regressions
- Version compatibility

### Acceptance Tests (`acceptance/`)
End-to-end tests from the user's perspective.
- User story validation
- Business requirements verification
- Performance requirements
- Error handling from user perspective

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests by Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Regression tests only
pytest tests/regression/

# Acceptance tests only
pytest tests/acceptance/
```

### Run Specific Test File
```bash
pytest tests/unit/test_risk.py
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

## Test Discovery

Pytest automatically discovers tests in all subdirectories. The `conftest.py` file in the root `tests/` directory provides shared fixtures accessible to all test files.

## Configuration Files

### `conftest.py` (Root Level)
- **Location**: `tests/conftest.py`
- **Purpose**: Contains shared pytest fixtures used across all test types
- **Why Root Level**: Pytest automatically discovers `conftest.py` files recursively. Having it in the root makes all fixtures available to unit, integration, regression, and acceptance tests without duplication.
- **Contains**:
  - Test data fixtures (sample_requirement, sample_risk, etc.)
  - Component fixtures (file_loader, parser, factories, etc.)
  - File fixtures (temp_file, temp_file_with_content)
  - Mock configuration fixtures
  - TestDataFactory class

### `__init__.py` Files
- **Root `__init__.py`**: Makes `tests/` a Python package
- **Subdirectory `__init__.py`**: Makes each subdirectory a package and documents the test category
- **Purpose**: Allows Python to recognize directories as packages and enables proper imports

### Organization Rationale
- **Shared fixtures stay in root**: All test types use the same fixtures, so keeping `conftest.py` in the root avoids duplication
- **Category-specific fixtures**: If needed, you can add additional `conftest.py` files in subdirectories for category-specific fixtures
- **No imports needed**: Fixtures are automatically available - just use them as function parameters in test methods

## Documentation

- `TEST_SUITE_ANALYSIS.md` - Analysis of test suite coverage
- `TEST_IMPLEMENTATION_PLAN.md` - Implementation plan and guidelines


