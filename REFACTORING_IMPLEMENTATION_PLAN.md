# Refactoring Implementation Plan

This document provides a detailed, phased implementation plan for the refactoring suggestions in `REFACTORING_SUGGESTIONS.md`. The plan prioritizes safety, incremental changes, and maintaining 100% test coverage throughout the refactoring process.

## Table of Contents

1. [Pre-Refactoring Preparation](#pre-refactoring-preparation)
2. [Phase 1: Foundation & Low-Risk Refactorings](#phase-1-foundation--low-risk-refactorings)
3. [Phase 2: SOLID Principles - Core Refactorings](#phase-2-solid-principles---core-refactorings)
4. [Phase 3: Design Patterns - Additional Patterns](#phase-3-design-patterns---additional-patterns)
5. [Phase 4: Advanced Refactorings](#phase-4-advanced-refactorings)
6. [Phase 5: Testing & Quality Improvements](#phase-5-testing--quality-improvements)
7. [Safety Measures & Validation](#safety-measures--validation)
8. [Rollback Procedures](#rollback-procedures)

---

## Pre-Refactoring Preparation

### Step 0.1: Establish Baseline
**Duration:** 1-2 hours  
**Risk Level:** None

**Tasks:**
1. ✅ Run full test suite and document current state
   ```bash
   pytest tests/ -v --cov=src --cov-report=html --cov-report=term
   ```
2. ✅ Document current test coverage (should be 100%)
3. ✅ Create baseline report outputs for comparison
   - Run analysis on sample files
   - Save outputs: `baseline_reports/`
4. ✅ Create feature branch: `git checkout -b refactoring/phase-1-foundation`
5. ✅ Document current API contracts (CLI arguments, web API endpoints)

**Success Criteria:**
- All 86 tests passing
- Test coverage report generated
- Baseline reports saved for comparison
- Feature branch created

**Validation:**
- Compare outputs before/after each phase
- Ensure no functional changes

---

## Phase 1: Foundation & Low-Risk Refactorings

**Duration:** 2-3 days  
**Risk Level:** Low  
**Goal:** Extract constants, improve code organization without changing behavior

### Step 1.1: Extract Constants Module
**Files to Modify:**
- `src/constants.py` (NEW)
- `src/detectors/base.py`
- `web/api/analysis.py`
- `main.py`

**Implementation:**
1. Create `src/constants.py`:
   ```python
   """Application-wide constants."""
   from pathlib import Path
   from src.models.risk import SeverityLevel
   from src.reporting import ReportFormat
   
   class Constants:
       DEFAULT_RULES_FILE = "data/rules.json"
       DEFAULT_REPORT_FORMAT = ReportFormat.MD
       SUPPORTED_FILE_EXTENSIONS = {'.txt', '.md'}
       DEFAULT_SEVERITY = SeverityLevel.MEDIUM
       RISK_ID_FORMAT = "{requirement_id}-{category}-{counter:03d}"
       REQUIREMENT_ID_FORMAT = "R{counter:03d}"
   
   class AnalysisProgress:
       """Constants for analysis progress stages."""
       LOADING = 10
       PARSING = 30
       DETECTING = 50
       SCORING = 70
       GENERATING = 80
       COMPLETE = 100
   ```

2. Replace magic numbers/strings in:
   - `web/api/analysis.py` (progress percentages)
   - `src/detectors/base.py` (default rules file)
   - `main.py` (default report format)

**Testing Strategy:**
- ✅ Run existing tests (should all pass)
- ✅ Verify no functional changes
- ✅ Check that constants are used correctly

**Rollback Plan:**
- Revert constants.py and restore hard-coded values

---

### Step 1.2: Create ReporterFactory
**Files to Modify:**
- `src/factories/reporter_factory.py` (NEW)
- `main.py`
- `web/api/analysis.py` (if applicable)

**Implementation:**
1. Create `src/factories/reporter_factory.py`:
   ```python
   """Factory for creating reporters based on format."""
   from typing import Dict, Type
   from src.reporting import ReportFormat, Reporter, MarkdownReporter, 
                            CsvReporter, JsonReporter, HtmlReporter
   
   class ReporterFactory:
       """Factory for creating reporters based on format."""
       _reporters: Dict[ReportFormat, Type[Reporter]] = {
           ReportFormat.MD: MarkdownReporter,
           ReportFormat.CSV: CsvReporter,
           ReportFormat.JSON: JsonReporter,
           ReportFormat.HTML: HtmlReporter,
       }
       
       def create_reporter(self, format: ReportFormat) -> Reporter:
           """Create reporter for specified format."""
           reporter_class = self._reporters.get(format)
           if not reporter_class:
               raise ValueError(f"Unsupported report format: {format}")
           return reporter_class()
       
       def register_reporter(self, format: ReportFormat, 
                           reporter_class: Type[Reporter]):
           """Register a new reporter type (for extensibility)."""
           self._reporters[format] = reporter_class
   ```

2. Update `main.py` lines 148-155:
   ```python
   # Before:
   if fmt is ReportFormat.MD:
       reporter = MarkdownReporter()
   elif fmt is ReportFormat.CSV:
       reporter = CsvReporter()
   # ...
   
   # After:
   from src.factories.reporter_factory import ReporterFactory
   reporter_factory = ReporterFactory()
   reporter = reporter_factory.create_reporter(fmt)
   ```

**Testing Strategy:**
- ✅ Run all existing tests
- ✅ Test each report format still works
- ✅ Verify report outputs are identical to baseline
- ✅ Add unit tests for ReporterFactory

**New Tests to Add:**
```python
# tests/test_reporter_factory.py
def test_create_markdown_reporter():
    factory = ReporterFactory()
    reporter = factory.create_reporter(ReportFormat.MD)
    assert isinstance(reporter, MarkdownReporter)

def test_create_all_formats():
    factory = ReporterFactory()
    for fmt in ReportFormat:
        reporter = factory.create_reporter(fmt)
        assert reporter is not None

def test_register_new_reporter():
    factory = ReporterFactory()
    factory.register_reporter(ReportFormat.MD, CustomReporter)
    reporter = factory.create_reporter(ReportFormat.MD)
    assert isinstance(reporter, CustomReporter)
```

**Rollback Plan:**
- Revert to if/elif chain in main.py
- Delete reporter_factory.py

---

### Step 1.3: Extract AnalysisProgress Constants
**Files to Modify:**
- `web/api/analysis.py`

**Implementation:**
1. Import constants from Step 1.1
2. Replace all hard-coded progress percentages:
   ```python
   # Before:
   analysis_status[analysis_id].progress = 10
   
   # After:
   from src.constants import AnalysisProgress
   analysis_status[analysis_id].progress = AnalysisProgress.LOADING
   ```

**Testing Strategy:**
- ✅ Run web API tests
- ✅ Verify progress values unchanged
- ✅ Test analysis workflow end-to-end

**Rollback Plan:**
- Restore hard-coded numbers

---

## Phase 2: SOLID Principles - Core Refactorings

**Duration:** 5-7 days  
**Risk Level:** Medium  
**Goal:** Improve SOLID compliance, extract responsibilities

### Step 2.1: Extract TextNormalizer Class
**Files to Modify:**
- `src/utils/text_normalizer.py` (NEW)
- `src/detectors/base.py`

**Implementation:**
1. Create `src/utils/text_normalizer.py`:
   ```python
   """Text normalization and keyword matching utilities."""
   from typing import List
   
   class TextNormalizer:
       """Handles text normalization and keyword matching."""
       
       def normalize_text(self, text: str, case_sensitive: bool = False) -> str:
           """Normalize text for comparison."""
           if not case_sensitive:
               text = text.lower()
           return text.strip()
       
       def contains_keywords(self, text: str, keywords: List[str], 
                           case_sensitive: bool = False) -> List[str]:
           """Check if text contains any keywords."""
           normalized_text = self.normalize_text(text, case_sensitive)
           found_keywords = []
           
           for keyword in keywords:
               normalized_keyword = self.normalize_text(keyword, case_sensitive)
               if normalized_keyword in normalized_text:
                   found_keywords.append(keyword)
           
           return found_keywords
   ```

2. Update `BaseRiskDetector` to use composition:
   ```python
   class BaseRiskDetector(RiskDetector):
       def __init__(self, rules_file: str = "data/rules.json",
                    text_normalizer: Optional[TextNormalizer] = None):
           # ... existing init code ...
           self.text_normalizer = text_normalizer or TextNormalizer()
       
       def normalize_text(self, text: str) -> str:
           """Delegate to text normalizer."""
           case_sensitive = self.global_settings.get('case_sensitive', False)
           return self.text_normalizer.normalize_text(text, case_sensitive)
       
       def contains_keywords(self, text: str, keywords: List[str]) -> List[str]:
           """Delegate to text normalizer."""
           case_sensitive = self.global_settings.get('case_sensitive', False)
           return self.text_normalizer.contains_keywords(text, keywords, case_sensitive)
   ```

**Testing Strategy:**
- ✅ Run all detector tests (should pass unchanged)
- ✅ Verify text normalization behavior identical
- ✅ Test with case_sensitive=True/False
- ✅ Add unit tests for TextNormalizer

**New Tests:**
```python
# tests/test_text_normalizer.py
def test_normalize_text_lowercase():
    normalizer = TextNormalizer()
    assert normalizer.normalize_text("  HELLO  ", False) == "hello"

def test_contains_keywords():
    normalizer = TextNormalizer()
    keywords = ["login", "password"]
    assert normalizer.contains_keywords("User can LOGIN", keywords) == ["login"]
```

**Rollback Plan:**
- Move methods back to BaseRiskDetector
- Delete text_normalizer.py

---

### Step 2.2: Extract RiskIdGenerator
**Files to Modify:**
- `src/utils/risk_id_generator.py` (NEW)
- `src/detectors/base.py`

**Implementation:**
1. Create `src/utils/risk_id_generator.py`:
   ```python
   """Generates unique risk IDs."""
   from typing import Dict
   from src.models.risk import RiskCategory
   
   class RiskIdGenerator:
       """Generates unique risk IDs."""
       def __init__(self):
           self._counters: Dict[str, int] = {}
       
       def generate_id(self, requirement_id: str, category: RiskCategory) -> str:
           """Generate unique risk ID."""
           key = f"{requirement_id}-{category.value}"
           self._counters[key] = self._counters.get(key, 0) + 1
           counter = self._counters[key]
           return f"{requirement_id}-{category.value.upper()[:3]}-{counter:03d}"
       
       def reset(self):
           """Reset counters (for testing)."""
           self._counters.clear()
   ```

2. Update `BaseRiskDetector.create_risk()`:
   ```python
   def __init__(self, rules_file: str = "data/rules.json",
                risk_id_generator: Optional[RiskIdGenerator] = None):
       # ... existing code ...
       self.risk_id_generator = risk_id_generator or RiskIdGenerator()
   
   def create_risk(self, requirement: Requirement, description: str, 
                   evidence: str, severity: Optional[str] = None,
                   suggestion: Optional[str] = None) -> Risk:
       """Create a Risk object with proper ID and metadata."""
       risk_id = self.risk_id_generator.generate_id(
           requirement.id, self.get_category()
       )
       # ... rest of method unchanged ...
   ```

**Testing Strategy:**
- ✅ Run all detector tests
- ✅ Verify risk IDs generated correctly
- ✅ Test ID uniqueness across multiple risks
- ✅ Add unit tests for RiskIdGenerator

**New Tests:**
```python
# tests/test_risk_id_generator.py
def test_generate_unique_ids():
    generator = RiskIdGenerator()
    id1 = generator.generate_id("R001", RiskCategory.AMBIGUITY)
    id2 = generator.generate_id("R001", RiskCategory.AMBIGUITY)
    assert id1 != id2
    assert id1.endswith("-001")
    assert id2.endswith("-002")
```

**Rollback Plan:**
- Restore ID generation logic to BaseRiskDetector
- Delete risk_id_generator.py

---

### Step 2.3: Extract DetectorConfigManager
**Files to Modify:**
- `src/config/detector_config_manager.py` (NEW)
- `src/detectors/base.py`
- `src/factories/detector_factory.py`

**Implementation:**
1. Create `src/config/detector_config_manager.py`:
   ```python
   """Manages detector configuration loading and access."""
   import json
   from pathlib import Path
   from typing import Dict, Any
   
   class DetectorConfigManager:
       """Manages detector configuration loading and access."""
       def __init__(self, rules_file: str):
           self.rules_file = rules_file
           self.config = self._load_configuration()
       
       def _load_configuration(self) -> Dict[str, Any]:
           """Load configuration from rules.json file."""
           try:
               rules_path = Path(self.rules_file)
               if not rules_path.exists():
                   raise FileNotFoundError(f"Rules file not found: {self.rules_file}")
               
               with open(rules_path, 'r', encoding='utf-8') as f:
                   config = json.load(f)
               
               return config
           except json.JSONDecodeError as e:
               raise ValueError(f"Invalid JSON in rules file {self.rules_file}: {e}")
           except Exception as e:
               raise ValueError(f"Error loading rules file {self.rules_file}: {e}")
       
       def get_detector_config(self, detector_name: str) -> Dict[str, Any]:
           """Get configuration for a specific detector."""
           return self.config.get('detectors', {}).get(detector_name, {})
       
       def is_detector_enabled(self, detector_name: str) -> bool:
           """Check if detector is enabled."""
           config = self.get_detector_config(detector_name)
           return config.get('enabled', False)
       
       def get_global_setting(self, key: str, default: Any = None) -> Any:
           """Get global setting value."""
           return self.config.get('global_settings', {}).get(key, default)
       
       def get_severity_mapping(self) -> Dict[str, Any]:
           """Get severity mapping configuration."""
           return self.config.get('severity_mapping', {})
   ```

2. Update `BaseRiskDetector`:
   ```python
   class BaseRiskDetector(RiskDetector):
       def __init__(self, rules_file: str = "data/rules.json",
                    config_manager: Optional[DetectorConfigManager] = None):
           self.config_manager = config_manager or DetectorConfigManager(rules_file)
           self._setup_detector()
       
       def _setup_detector(self) -> None:
           """Setup detector-specific configuration."""
           detector_name = self.get_category().value
           self.detector_config = self.config_manager.get_detector_config(detector_name)
           self.severity_mapping = self.config_manager.get_severity_mapping()
           self.global_settings = self.config_manager.config.get('global_settings', {})
           
           if not self.detector_config.get('enabled', False):
               raise ValueError(f"Detector {detector_name} is disabled in configuration")
   ```

3. Update `RiskDetectorFactory` to use config manager:
   ```python
   def create_enabled_detectors(self) -> List[RiskDetector]:
       """Create only detectors that are enabled in the configuration."""
       enabled_detectors = []
       config_manager = DetectorConfigManager(self.rules_file)
       
       for detector_type in self._detector_registry.keys():
           if config_manager.is_detector_enabled(detector_type):
               try:
                   detector = self.create_detector(detector_type)
                   enabled_detectors.append(detector)
               except Exception as e:
                   print(f"Warning: Could not create {detector_type} detector: {e}")
       
       return enabled_detectors
   ```

**Testing Strategy:**
- ✅ Run all detector tests
- ✅ Verify configuration loading unchanged
- ✅ Test with missing/invalid config files
- ✅ Add unit tests for DetectorConfigManager

**New Tests:**
```python
# tests/test_detector_config_manager.py
def test_load_configuration():
    manager = DetectorConfigManager("data/rules.json")
    assert manager.config is not None

def test_get_detector_config():
    manager = DetectorConfigManager("data/rules.json")
    config = manager.get_detector_config("ambiguity")
    assert isinstance(config, dict)

def test_is_detector_enabled():
    manager = DetectorConfigManager("data/rules.json")
    assert manager.is_detector_enabled("ambiguity") in [True, False]
```

**Rollback Plan:**
- Restore config loading to BaseRiskDetector
- Delete detector_config_manager.py

---

### Step 2.4: Extract RiskFactory
**Files to Modify:**
- `src/factories/risk_factory.py` (NEW)
- `src/detectors/base.py`

**Implementation:**
1. Create `src/factories/risk_factory.py`:
   ```python
   """Factory for creating Risk objects."""
   from typing import Optional
   from src.models.requirement import Requirement
   from src.models.risk import Risk, RiskCategory, SeverityLevel
   from src.utils.risk_id_generator import RiskIdGenerator
   
   class RiskFactory:
       """Creates Risk objects with proper ID generation and validation."""
       def __init__(self, id_generator: Optional[RiskIdGenerator] = None):
           self.id_generator = id_generator or RiskIdGenerator()
       
       def create_risk(self, requirement: Requirement, category: RiskCategory,
                      description: str, evidence: str, 
                      severity: SeverityLevel,
                      suggestion: Optional[str] = None) -> Risk:
           """Create a Risk object with auto-generated ID."""
           risk_id = self.id_generator.generate_id(requirement.id, category)
           
           return Risk(
               id=risk_id,
               category=category,
               severity=severity,
               description=description,
               requirement_id=requirement.id,
               line_number=requirement.line_number,
               evidence=evidence,
               suggestion=suggestion
           )
   ```

2. Update `BaseRiskDetector`:
   ```python
   def __init__(self, rules_file: str = "data/rules.json",
                risk_factory: Optional[RiskFactory] = None,
                risk_id_generator: Optional[RiskIdGenerator] = None):
       # ... existing code ...
       id_gen = risk_id_generator or RiskIdGenerator()
       self.risk_factory = risk_factory or RiskFactory(id_gen)
   
   def create_risk(self, requirement: Requirement, description: str,
                   evidence: str, severity: Optional[str] = None,
                   suggestion: Optional[str] = None) -> Risk:
       """Create a Risk object with proper ID and metadata."""
       if severity is None:
           severity = self.detector_config.get('severity', 'medium')
       severity_level = self.get_severity_level(severity)
       
       return self.risk_factory.create_risk(
           requirement=requirement,
           category=self.get_category(),
           description=description,
           evidence=evidence,
           severity=severity_level,
           suggestion=suggestion
       )
   ```

**Testing Strategy:**
- ✅ Run all detector tests
- ✅ Verify risk creation unchanged
- ✅ Test risk ID generation
- ✅ Add unit tests for RiskFactory

**Rollback Plan:**
- Restore create_risk to BaseRiskDetector
- Delete risk_factory.py

---

### Step 2.5: Extract DetectorErrorHandler
**Files to Modify:**
- `src/utils/detector_error_handler.py` (NEW)
- `src/analyzer.py`

**Implementation:**
1. Create `src/utils/detector_error_handler.py`:
   ```python
   """Handles errors during detector execution."""
   import logging
   from typing import List
   from src.models.requirement import Requirement
   from src.models.risk import Risk
   from src.detectors.base import RiskDetector
   
   logger = logging.getLogger(__name__)
   
   class DetectorErrorHandler:
       """Handles errors during detector execution."""
       def __init__(self, log_errors: bool = True, 
                    return_error_risks: bool = False):
           self.log_errors = log_errors
           self.return_error_risks = return_error_risks
       
       def handle_detector_error(self, detector: RiskDetector,
                                requirement: Requirement, 
                                error: Exception) -> List[Risk]:
           """Handle detector errors with logging and optional error risks."""
           if self.log_errors:
               logger.warning(
                   f"Detector {detector.get_detector_name()} failed "
                   f"for requirement {requirement.id}: {error}",
                   exc_info=True
               )
           
           if self.return_error_risks:
               # Optionally return an error risk
               # This would require creating an error risk
               pass
           
           return []
   ```

2. Update `src/analyzer.py`:
   ```python
   from src.utils.detector_error_handler import DetectorErrorHandler
   
   def analyze_requirements(
       requirements: List[Requirement],
       detectors: List[RiskDetector],
       error_handler: Optional[DetectorErrorHandler] = None
   ) -> Dict[str, List[Risk]]:
       """Run all detectors against each requirement."""
       error_handler = error_handler or DetectorErrorHandler()
       risks_by_requirement: Dict[str, List[Risk]] = {
           req.id: [] for req in requirements
       }
       
       for requirement in requirements:
           for detector in detectors:
               try:
                   risks = detector.detect_risks(requirement)
               except Exception as e:
                   risks = error_handler.handle_detector_error(
                       detector, requirement, e
                   )
               if risks:
                   risks_by_requirement[requirement.id].extend(risks)
       
       return risks_by_requirement
   ```

**Testing Strategy:**
- ✅ Run all analyzer tests
- ✅ Test error handling behavior
- ✅ Verify errors are logged
- ✅ Add unit tests for DetectorErrorHandler

**New Tests:**
```python
# tests/test_detector_error_handler.py
def test_handle_detector_error():
    handler = DetectorErrorHandler()
    detector = Mock(spec=RiskDetector)
    requirement = Requirement(id="R001", line_number=1, text="Test")
    error = Exception("Test error")
    
    result = handler.handle_detector_error(detector, requirement, error)
    assert result == []
```

**Rollback Plan:**
- Restore try/except in analyzer.py
- Delete detector_error_handler.py

---

### Step 2.6: Extract StressSpecService
**Files to Modify:**
- `src/services/stress_spec_service.py` (NEW)
- `main.py`

**Implementation:**
1. Create `src/services/stress_spec_service.py`:
   ```python
   """Service for orchestrating the complete analysis workflow."""
   from pathlib import Path
   from typing import Optional
   from src.file_loader import FileLoader
   from src.requirement_parser import RequirementParser
   from src.factories.detector_factory import RiskDetectorFactory
   from src.factories.reporter_factory import ReporterFactory
   from src.analyzer import analyze_requirements
   from src.scoring import calculate_risk_scores, get_top_riskiest
   from src.reporting import ReportFormat, ReportData
   
   class StressSpecService:
       """Orchestrates the complete analysis workflow."""
       def __init__(self, 
                    file_loader: Optional[FileLoader] = None,
                    parser: Optional[RequirementParser] = None,
                    detector_factory: Optional[RiskDetectorFactory] = None,
                    reporter_factory: Optional[ReporterFactory] = None):
           self.file_loader = file_loader or FileLoader()
           self.parser = parser or RequirementParser()
           self.detector_factory = detector_factory or RiskDetectorFactory()
           self.reporter_factory = reporter_factory or ReporterFactory()
       
       def analyze_file(self, file_path: str, 
                       report_format: ReportFormat,
                       output_path: Optional[str] = None) -> Path:
           """Complete analysis workflow."""
           # Load file
           raw_lines = self.file_loader.load_file(file_path)
           
           # Parse requirements
           requirements = self.parser.parse_requirements(raw_lines)
           
           # Run detectors
           detectors = (self.detector_factory.create_enabled_detectors() or 
                       self.detector_factory.create_all_detectors())
           risks_by_requirement = analyze_requirements(requirements, detectors)
           
           # Calculate scores
           risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
           top_5_riskiest = get_top_riskiest(requirements, risk_scores, top_n=5)
           
           # Generate report
           data = ReportData(
               requirements=requirements,
               risks_by_requirement=risks_by_requirement,
               source_file=file_path,
               top_5_riskiest=top_5_riskiest,
           )
           
           reporter = self.reporter_factory.create_reporter(report_format)
           return reporter.write(data, output_path)
   ```

2. Update `main.py`:
   ```python
   from src.services.stress_spec_service import StressSpecService
   
   def main() -> None:
       try:
           args = parse_arguments()
           
           if args.verbose:
               print("StressSpec - Requirements Stress Tester")
               print("=" * 50)
               print(f"Input file: {args.file}")
               print()
           
           # Use service for analysis
           service = StressSpecService()
           output_path = service.analyze_file(
               args.file,
               ReportFormat(args.report_format),
               args.output
           )
           
           if args.verbose:
               print(f"Report written to: {output_path}")
               
       except FileNotFoundError as e:
           print(f"Error: File not found - {e}", file=sys.stderr)
           sys.exit(1)
       # ... rest of error handling ...
   ```

**Testing Strategy:**
- ✅ Run all integration tests
- ✅ Verify CLI behavior unchanged
- ✅ Test all report formats
- ✅ Add unit tests for StressSpecService

**New Tests:**
```python
# tests/test_stress_spec_service.py
def test_analyze_file_complete_workflow():
    service = StressSpecService()
    # Use temp file
    output = service.analyze_file("data/sample_requirements.txt", ReportFormat.MD)
    assert output.exists()
```

**Rollback Plan:**
- Restore main.py to original
- Delete stress_spec_service.py

---

## Phase 3: Design Patterns - Additional Patterns

**Duration:** 4-5 days  
**Risk Level:** Medium  
**Goal:** Add Observer, Chain of Responsibility, Decorator patterns

### Step 3.1: Implement Observer Pattern for Progress
**Files to Modify:**
- `src/patterns/observer.py` (NEW)
- `src/analyzer.py` (optional enhancement)
- `web/api/analysis.py` (use observer)

**Implementation:**
1. Create observer infrastructure (see REFACTORING_SUGGESTIONS.md section 2.1)
2. Integrate with existing progress reporting in web API
3. Make it optional (backward compatible)

**Testing Strategy:**
- ✅ Verify existing progress reporting still works
- ✅ Test observer pattern independently
- ✅ Add unit tests

**Rollback Plan:**
- Remove observer, restore direct progress updates

---

### Step 3.2: Implement Chain of Responsibility for Risk Filtering
**Files to Modify:**
- `src/filters/risk_filter.py` (NEW)
- `src/analyzer.py` (optional integration)

**Implementation:**
1. Create filter chain infrastructure (see REFACTORING_SUGGESTIONS.md section 2.2)
2. Make it optional (default: no filtering)
3. Add configuration option to enable filtering

**Testing Strategy:**
- ✅ Verify default behavior unchanged (no filtering)
- ✅ Test filter chain independently
- ✅ Add unit tests

**Rollback Plan:**
- Remove filter chain, restore direct risk reporting

---

### Step 3.3: Implement Decorator Pattern for Reports
**Files to Modify:**
- `src/reporting/decorators.py` (NEW)
- Make it optional

**Implementation:**
1. Create decorator infrastructure (see REFACTORING_SUGGESTIONS.md section 2.3)
2. Make it optional (default: no decorators)
3. Add configuration option to enable decorators

**Testing Strategy:**
- ✅ Verify default behavior unchanged
- ✅ Test decorators independently
- ✅ Add unit tests

**Rollback Plan:**
- Remove decorators, restore direct reporting

---

## Phase 4: Advanced Refactorings

**Duration:** 3-4 days  
**Risk Level:** Medium-High  
**Goal:** Improve error handling, add abstractions

### Step 4.1: Improve Error Handling
**Files to Modify:**
- `src/exceptions.py` (NEW or enhance existing)
- `src/analyzer.py`
- All detector files

**Implementation:**
1. Create custom exceptions (if not exists)
2. Replace silent failures with proper exceptions
3. Add logging

**Testing Strategy:**
- ✅ Verify error handling improved
- ✅ Test error scenarios
- ✅ Ensure backward compatibility

**Rollback Plan:**
- Restore previous error handling

---

### Step 4.2: Abstract Configuration Access
**Files to Modify:**
- `src/config/configuration_provider.py` (NEW)
- `src/config/detector_config_manager.py` (update to use provider)

**Implementation:**
1. Create ConfigurationProvider interface
2. Update DetectorConfigManager to use provider
3. Keep JSON file as default implementation

**Testing Strategy:**
- ✅ Verify configuration loading unchanged
- ✅ Test with mock provider
- ✅ Add unit tests

**Rollback Plan:**
- Restore direct JSON file access

---

## Phase 5: Testing & Quality Improvements

**Duration:** 2-3 days  
**Risk Level:** Low  
**Goal:** Improve test structure, add fixtures

### Step 5.1: Create Test Fixtures
**Files to Modify:**
- `tests/conftest.py` (NEW or enhance)
- Update existing tests to use fixtures

**Implementation:**
1. Create pytest fixtures for common test data
2. Create TestDataFactory
3. Update existing tests to use fixtures

**Testing Strategy:**
- ✅ All existing tests still pass
- ✅ New fixtures work correctly
- ✅ Test coverage maintained

---

### Step 5.2: Improve Mock Usage
**Files to Modify:**
- Update tests to use dependency injection for mocking
- Add mock factories

**Implementation:**
1. Update tests to inject mocks
2. Create mock factories
3. Improve test isolation

**Testing Strategy:**
- ✅ All tests pass
- ✅ Better test isolation
- ✅ Easier to maintain

---

## Safety Measures & Validation

### Continuous Validation Checklist

After each step, verify:

1. **Test Suite**
   ```bash
   pytest tests/ -v
   ```
   - ✅ All tests pass
   - ✅ No new test failures
   - ✅ Test coverage maintained or improved

2. **Functional Validation**
   - ✅ Run CLI with sample files
   - ✅ Compare outputs to baseline
   - ✅ Verify all report formats work
   - ✅ Test web API endpoints

3. **Code Quality**
   ```bash
   pylint src/
   mypy src/ --ignore-missing-imports
   ```
   - ✅ No new linting errors
   - ✅ Type checking passes

4. **Performance**
   - ✅ No significant performance degradation
   - ✅ Memory usage acceptable

5. **Backward Compatibility**
   - ✅ CLI arguments unchanged
   - ✅ API contracts unchanged
   - ✅ Report formats unchanged
   - ✅ Configuration file format unchanged

### Comparison Script

Create a script to compare outputs:

```python
# scripts/compare_outputs.py
"""Compare refactored outputs with baseline."""
import json
from pathlib import Path

def compare_reports(baseline_path: Path, current_path: Path):
    """Compare two report files."""
    # Implementation for comparing reports
    pass
```

---

## Rollback Procedures

### Per-Step Rollback

Each step includes:
1. Git commit after successful validation
2. Tag for rollback point: `git tag refactoring/step-X.X-complete`
3. Rollback command: `git reset --hard refactoring/step-X.X-complete`

### Full Rollback

If major issues occur:

```bash
# Return to main branch
git checkout main

# Or return to specific phase
git checkout refactoring/phase-1-complete
```

### Partial Rollback

If only one component fails:

1. Identify failing component
2. Revert specific files: `git checkout main -- path/to/file.py`
3. Fix issues and re-apply

---

## Success Criteria

### Phase Completion Criteria

Each phase is complete when:
- ✅ All tests pass (100% pass rate maintained)
- ✅ All functional validations pass
- ✅ Code review approved
- ✅ Documentation updated
- ✅ Git commit and tag created

### Overall Success Criteria

Refactoring is complete when:
- ✅ All phases completed
- ✅ Test coverage ≥ 100%
- ✅ All functional tests pass
- ✅ Performance maintained or improved
- ✅ Code quality improved (linting, type checking)
- ✅ Documentation updated
- ✅ No breaking changes to API/CLI

---

## Timeline Estimate

| Phase | Duration | Risk Level |
|-------|----------|------------|
| Preparation | 1-2 hours | None |
| Phase 1: Foundation | 2-3 days | Low |
| Phase 2: SOLID | 5-7 days | Medium |
| Phase 3: Design Patterns | 4-5 days | Medium |
| Phase 4: Advanced | 3-4 days | Medium-High |
| Phase 5: Testing | 2-3 days | Low |
| **Total** | **16-22 days** | |

**Note:** Timeline assumes:
- Working 4-6 hours per day on refactoring
- Time for testing and validation included
- Buffer time for unexpected issues

---

## Risk Mitigation

### High-Risk Areas

1. **BaseRiskDetector refactoring** (Step 2.1-2.4)
   - **Risk:** Breaking all detectors
   - **Mitigation:** 
     - Extensive testing after each extraction
     - Keep old methods as wrappers initially
     - Gradual migration

2. **Service extraction** (Step 2.6)
   - **Risk:** Breaking CLI workflow
   - **Mitigation:**
     - Maintain backward compatibility
     - Test CLI thoroughly
     - Keep old code as fallback initially

3. **Error handling changes** (Step 4.1)
   - **Risk:** Changing error behavior
   - **Mitigation:**
     - Make changes opt-in initially
     - Preserve existing error handling
     - Gradual migration

### Testing Strategy

1. **Unit Tests:** Test each extracted component independently
2. **Integration Tests:** Test complete workflows
3. **Regression Tests:** Compare outputs with baseline
4. **Performance Tests:** Ensure no degradation

---

## Communication Plan

### During Refactoring

1. **Daily Status Updates**
   - What was completed
   - What's in progress
   - Any blockers
   - Test results

2. **Phase Completion Reports**
   - Summary of changes
   - Test results
   - Performance metrics
   - Next steps

3. **Issue Tracking**
   - Document any issues encountered
   - Solutions applied
   - Lessons learned

---

## Conclusion

This implementation plan provides a safe, incremental approach to refactoring the StressSpec codebase. By following this plan:

- ✅ Changes are made incrementally
- ✅ Each step is validated before proceeding
- ✅ Rollback procedures are clear
- ✅ Test coverage is maintained
- ✅ Backward compatibility is preserved

The plan prioritizes safety and validation, ensuring that refactoring improves code quality without breaking existing functionality.

