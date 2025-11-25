# Refactoring Suggestions for StressSpec

This document provides refactoring suggestions based on analysis of the codebase compared to Software Design course materials covering Design Patterns, APIEC (Abstraction, Polymorphism, Inheritance, Encapsulation, Composition), Refactoring techniques, SOLID principles, and Testing best practices.

## Executive Summary

The StressSpec codebase demonstrates good use of several design patterns (Factory Method, Strategy, Template Method) and follows many SOLID principles. However, there are opportunities for improvement in:

1. **SOLID Principles** - Some violations of Single Responsibility and Dependency Inversion
2. **Design Patterns** - Opportunities to apply additional patterns (Observer, Decorator, Chain of Responsibility)
3. **Refactoring** - Code smells that can be addressed (Long Method, Feature Envy, Duplicate Code)
4. **Abstraction & Encapsulation** - Some tight coupling and missing abstractions
5. **Error Handling** - Inconsistent exception handling patterns
6. **Testing** - Opportunities for better test structure and mocking

---

## 1. SOLID Principles Refactoring

### 1.1 Single Responsibility Principle (SRP) Violations

#### Issue: `BaseRiskDetector` has multiple responsibilities
**Location:** `src/detectors/base.py`

**Problem:**
- Loads configuration (file I/O)
- Manages severity mapping (business logic)
- Provides text normalization utilities (utility functions)
- Creates Risk objects (object construction)

**Suggestion:**
```python
# Extract Configuration Manager
class DetectorConfigManager:
    """Manages detector configuration loading and access."""
    def __init__(self, rules_file: str):
        self.rules_file = rules_file
        self.config = self._load_configuration()
    
    def get_detector_config(self, detector_name: str) -> Dict:
        """Get configuration for a specific detector."""
        pass
    
    def is_detector_enabled(self, detector_name: str) -> bool:
        """Check if detector is enabled."""
        pass

# Extract Risk Factory
class RiskFactory:
    """Creates Risk objects with proper ID generation and validation."""
    def create_risk(self, requirement: Requirement, category: RiskCategory, 
                   description: str, evidence: str, severity: SeverityLevel) -> Risk:
        """Create a Risk object with auto-generated ID."""
        pass

# Extract Text Utilities
class TextNormalizer:
    """Handles text normalization and keyword matching."""
    def normalize_text(self, text: str, case_sensitive: bool = False) -> str:
        pass
    
    def contains_keywords(self, text: str, keywords: List[str]) -> List[str]:
        pass
```

**Benefits:**
- Each class has a single, well-defined responsibility
- Easier to test individual components
- Configuration can be mocked for testing
- Text utilities can be reused elsewhere

---

#### Issue: `analyzer.py` mixes orchestration with error handling
**Location:** `src/analyzer.py`

**Problem:**
- Orchestrates detector execution
- Handles exceptions silently
- No logging or error reporting

**Suggestion:**
```python
# Extract Error Handler
class DetectorErrorHandler:
    """Handles errors during detector execution."""
    def handle_detector_error(self, detector: RiskDetector, 
                             requirement: Requirement, error: Exception) -> List[Risk]:
        """Handle detector errors with logging and optional error risks."""
        logger.warning(f"Detector {detector.get_detector_name()} failed: {error}")
        # Optionally return an error risk
        return []

# Refactored analyzer
def analyze_requirements(requirements: List[Requirement],
                        detectors: List[RiskDetector],
                        error_handler: Optional[DetectorErrorHandler] = None) -> Dict[str, List[Risk]]:
    """Run detectors with proper error handling."""
    error_handler = error_handler or DetectorErrorHandler()
    # ... rest of implementation
```

---

#### Issue: `main.py` orchestrates too many concerns
**Location:** `main.py`

**Problem:**
- Parses arguments
- Coordinates file loading
- Runs analysis
- Generates reports
- Handles errors

**Suggestion:**
```python
# Extract Application Service
class StressSpecService:
    """Orchestrates the complete analysis workflow."""
    def __init__(self, file_loader: FileLoader, parser: RequirementParser,
                 factory: RiskDetectorFactory, reporter_factory: ReporterFactory):
        self.file_loader = file_loader
        self.parser = parser
        self.factory = factory
        self.reporter_factory = reporter_factory
    
    def analyze_file(self, file_path: str, report_format: ReportFormat) -> Path:
        """Complete analysis workflow."""
        # Load → Parse → Analyze → Report
        pass

# Simplified main
def main():
    args = parse_arguments()
    service = StressSpecService(...)
    output_path = service.analyze_file(args.file, ReportFormat(args.report_format))
    print(f"Report written to: {output_path}")
```

---

### 1.2 Open/Closed Principle (OCP) Improvements

#### Issue: Reporter selection uses if/elif chain
**Location:** `main.py` lines 148-155

**Problem:**
- Adding new report formats requires modifying main.py
- Violates Open/Closed Principle

**Suggestion:**
```python
# Create Reporter Factory
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
    
    def register_reporter(self, format: ReportFormat, reporter_class: Type[Reporter]):
        """Register a new reporter type (for extensibility)."""
        self._reporters[format] = reporter_class
```

**Benefits:**
- New formats can be added without modifying existing code
- Follows Open/Closed Principle
- Consistent with existing Factory pattern usage

---

### 1.3 Liskov Substitution Principle (LSP) - Already Good

The detector hierarchy properly follows LSP - all detectors can be substituted through the `RiskDetector` interface.

---

### 1.4 Interface Segregation Principle (ISP) - Minor Improvements

#### Issue: `Reporter` interface is minimal (good), but could be more specific
**Location:** `src/reporting/base.py`

**Suggestion:**
```python
# More specific interfaces
class ReportWriter(ABC):
    """Interface for writing reports."""
    @abstractmethod
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        pass

class ReportValidator(ABC):
    """Interface for validating report data."""
    @abstractmethod
    def validate(self, data: ReportData) -> bool:
        pass

# Reporter can implement both
class Reporter(ReportWriter, ReportValidator):
    """Combined reporter interface."""
    pass
```

---

### 1.5 Dependency Inversion Principle (DIP) Violations

#### Issue: Direct instantiation of concrete classes
**Location:** Multiple files

**Problem:**
- `main.py` directly creates `FileLoader()`, `RequirementParser()`, `RiskDetectorFactory()`
- `analyzer.py` directly uses concrete detector types
- Hard to test and swap implementations

**Suggestion:**
```python
# Use Dependency Injection
class StressSpecService:
    def __init__(self, 
                 file_loader: FileLoader,
                 parser: RequirementParser,
                 detector_factory: RiskDetectorFactory,
                 reporter_factory: ReporterFactory):
        self.file_loader = file_loader
        self.parser = parser
        self.detector_factory = detector_factory
        self.reporter_factory = reporter_factory

# In main.py or a factory
def create_service() -> StressSpecService:
    """Factory method for creating service with dependencies."""
    return StressSpecService(
        file_loader=FileLoader(),
        parser=RequirementParser(),
        detector_factory=RiskDetectorFactory(),
        reporter_factory=ReporterFactory()
    )
```

**Benefits:**
- Easy to inject mocks for testing
- Can swap implementations (e.g., different file loaders)
- Follows Dependency Inversion Principle

---

## 2. Design Patterns - Additional Patterns to Apply

### 2.1 Observer Pattern for Progress Reporting

#### Current Issue: No progress reporting in CLI
**Location:** `main.py`, `src/analyzer.py`

**Suggestion:**
```python
# Observer Pattern for Progress
class AnalysisProgressObserver(ABC):
    """Observer interface for analysis progress."""
    @abstractmethod
    def on_progress(self, stage: str, progress: int, message: str):
        pass

class ConsoleProgressObserver(AnalysisProgressObserver):
    """Console-based progress observer."""
    def on_progress(self, stage: str, progress: int, message: str):
        print(f"[{progress}%] {stage}: {message}")

class AnalysisOrchestrator:
    """Orchestrator that notifies observers of progress."""
    def __init__(self):
        self.observers: List[AnalysisProgressObserver] = []
    
    def add_observer(self, observer: AnalysisProgressObserver):
        self.observers.append(observer)
    
    def notify_progress(self, stage: str, progress: int, message: str):
        for observer in self.observers:
            observer.on_progress(stage, progress, message)
    
    def analyze(self, requirements: List[Requirement], detectors: List[RiskDetector]):
        self.notify_progress("Loading", 10, "Starting analysis...")
        # ... analysis steps with progress updates
```

**Benefits:**
- Decouples progress reporting from analysis logic
- Can add multiple observers (console, file, web socket)
- Follows Observer pattern from course materials

---

### 2.2 Chain of Responsibility for Risk Filtering

#### Current Issue: All risks are reported, no filtering chain
**Location:** `src/analyzer.py`

**Suggestion:**
```python
# Chain of Responsibility Pattern
class RiskFilter(ABC):
    """Base class for risk filtering chain."""
    def __init__(self, next_filter: Optional['RiskFilter'] = None):
        self.next_filter = next_filter
    
    def filter(self, risks: List[Risk]) -> List[Risk]:
        """Filter risks and pass to next filter in chain."""
        filtered = self._apply_filter(risks)
        if self.next_filter:
            return self.next_filter.filter(filtered)
        return filtered
    
    @abstractmethod
    def _apply_filter(self, risks: List[Risk]) -> List[Risk]:
        """Apply this filter's logic."""
        pass

class SeverityThresholdFilter(RiskFilter):
    """Filter out risks below severity threshold."""
    def __init__(self, min_severity: SeverityLevel, next_filter: Optional[RiskFilter] = None):
        super().__init__(next_filter)
        self.min_severity = min_severity
    
    def _apply_filter(self, risks: List[Risk]) -> List[Risk]:
        return [r for r in risks if r.severity.value >= self.min_severity.value]

class DuplicateRiskFilter(RiskFilter):
    """Filter out duplicate risks."""
    def _apply_filter(self, risks: List[Risk]) -> List[Risk]:
        seen = set()
        unique = []
        for risk in risks:
            key = (risk.requirement_id, risk.category, risk.evidence)
            if key not in seen:
                seen.add(key)
                unique.append(risk)
        return unique

# Usage
filter_chain = SeverityThresholdFilter(
    SeverityLevel.MEDIUM,
    DuplicateRiskFilter()
)
filtered_risks = filter_chain.filter(all_risks)
```

**Benefits:**
- Flexible filtering pipeline
- Easy to add new filters
- Follows Chain of Responsibility pattern

---

### 2.3 Decorator Pattern for Enhanced Reporting

#### Current Issue: Reporters are separate classes, no composition
**Location:** `src/reporting/`

**Suggestion:**
```python
# Decorator Pattern for Report Enhancement
class ReportDecorator(Reporter):
    """Base decorator for report enhancements."""
    def __init__(self, reporter: Reporter):
        self.reporter = reporter
    
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        return self.reporter.write(data, output)

class TimestampedReportDecorator(ReportDecorator):
    """Adds timestamp to report."""
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        # Add timestamp to data
        enhanced_data = self._add_timestamp(data)
        return self.reporter.write(enhanced_data, output)
    
    def _add_timestamp(self, data: ReportData) -> ReportData:
        # Modify data to include timestamp
        pass

class SummaryReportDecorator(ReportDecorator):
    """Adds executive summary to report."""
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        enhanced_data = self._add_summary(data)
        return self.reporter.write(enhanced_data, output)

# Usage
base_reporter = MarkdownReporter()
decorated = SummaryReportDecorator(
    TimestampedReportDecorator(base_reporter)
)
decorated.write(data)
```

**Benefits:**
- Composable report features
- Can mix and match enhancements
- Follows Decorator pattern

---

### 2.4 Strategy Pattern Enhancement - Already Used Well

The detector system already uses Strategy pattern effectively. Consider adding:
- **Composite Strategy**: Combine multiple detection strategies
- **Strategy Selection**: Choose strategies based on requirement type

---

## 3. Refactoring Techniques

### 3.1 Extract Method - Long Methods

#### Issue: `run_analysis` is too long (200+ lines)
**Location:** `web/api/analysis.py` lines 70-216

**Suggestion:**
```python
# Break into smaller methods
class AnalysisService:
    """Service for running requirement analysis."""
    
    def run_analysis(self, analysis_id: str, file_id: str, file_path: str):
        """Orchestrate complete analysis workflow."""
        try:
            self._update_status(analysis_id, "processing", 10, "Loading file...")
            requirements = self._load_and_parse_requirements(file_path)
            
            self._update_status(analysis_id, "processing", 50, "Running risk detectors...")
            risks_by_requirement = self._detect_risks(requirements)
            
            self._update_status(analysis_id, "processing", 70, "Calculating risk scores...")
            risk_scores, top_5 = self._calculate_scores(requirements, risks_by_requirement)
            
            self._update_status(analysis_id, "processing", 80, "Generating results...")
            summary = self._generate_summary(requirements, risks_by_requirement)
            
            self._store_results(analysis_id, file_id, requirements, risks_by_requirement, 
                             summary, top_5, file_path)
            self._update_status(analysis_id, "completed", 100, "Analysis completed successfully")
        except Exception as e:
            self._handle_error(analysis_id, e)
    
    def _load_and_parse_requirements(self, file_path: str) -> List[Requirement]:
        """Load and parse requirements from file."""
        file_loader = FileLoader()
        structured_requirements = file_loader.load_file_structured(file_path)
        parser = RequirementParser()
        return parser.parse_structured_requirements(structured_requirements)
    
    def _detect_risks(self, requirements: List[Requirement]) -> Dict[str, List[Risk]]:
        """Run risk detection on requirements."""
        factory = RiskDetectorFactory()
        detectors = factory.create_enabled_detectors() or factory.create_all_detectors()
        return analyze_requirements(requirements, detectors)
    
    def _calculate_scores(self, requirements: List[Requirement], 
                         risks_by_requirement: Dict[str, List[Risk]]):
        """Calculate risk scores and identify top riskiest."""
        risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
        top_5 = get_top_riskiest(requirements, risk_scores, top_n=5)
        return risk_scores, top_5
    
    def _generate_summary(self, requirements: List[Requirement],
                         risks_by_requirement: Dict[str, List[Risk]]) -> Dict:
        """Generate analysis summary statistics."""
        total_risks = sum(len(risks) for risks in risks_by_requirement.values())
        risk_categories = self._count_risk_categories(risks_by_requirement)
        return {
            "total_requirements": len(requirements),
            "total_risks": total_risks,
            "risk_categories": risk_categories,
            "requirements_with_risks": len([r for r in risks_by_requirement.values() if r])
        }
    
    def _count_risk_categories(self, risks_by_requirement: Dict[str, List[Risk]]) -> Dict[str, int]:
        """Count risks by category."""
        categories = {}
        for risks in risks_by_requirement.values():
            for risk in risks:
                category = risk.category.value
                categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _store_results(self, analysis_id: str, file_id: str, requirements: List[Requirement],
                     risks_by_requirement: Dict[str, List[Risk]], summary: Dict,
                     top_5: List[Dict], file_path: str):
        """Store analysis results."""
        # Convert to dictionaries and store
        pass
    
    def _update_status(self, analysis_id: str, status: str, progress: int, message: str):
        """Update analysis status."""
        analysis_status[analysis_id] = AnalysisStatus(
            analysis_id=analysis_id,
            status=status,
            progress=progress,
            message=message
        )
    
    def _handle_error(self, analysis_id: str, error: Exception):
        """Handle analysis errors."""
        analysis_status[analysis_id] = AnalysisStatus(
            analysis_id=analysis_id,
            status="error",
            progress=0,
            message=f"Analysis failed: {str(error)}"
        )
```

**Benefits:**
- Each method has a single responsibility
- Easier to test individual steps
- More readable and maintainable

---

### 3.2 Replace Magic Numbers with Symbolic Constants

#### Issue: Magic numbers in progress percentages
**Location:** `web/api/analysis.py`

**Suggestion:**
```python
# Extract constants
class AnalysisProgress:
    """Constants for analysis progress stages."""
    LOADING = 10
    PARSING = 30
    DETECTING = 50
    SCORING = 70
    GENERATING = 80
    COMPLETE = 100

# Usage
self._update_status(analysis_id, "processing", AnalysisProgress.LOADING, "Loading file...")
```

---

### 3.3 Extract Class - Feature Envy

#### Issue: `BaseRiskDetector.create_risk` knows too much about Risk ID generation
**Location:** `src/detectors/base.py` lines 177-213

**Suggestion:**
```python
# Extract Risk ID Generator
class RiskIdGenerator:
    """Generates unique risk IDs."""
    def __init__(self):
        self._counters: Dict[str, int] = {}
    
    def generate_id(self, requirement_id: str, category: RiskCategory) -> str:
        """Generate unique risk ID for requirement and category."""
        key = f"{requirement_id}-{category.value}"
        self._counters[key] = self._counters.get(key, 0) + 1
        counter = self._counters[key]
        return f"{requirement_id}-{category.value.upper()[:3]}-{counter:03d}"

# Use in BaseRiskDetector
class BaseRiskDetector:
    def __init__(self, rules_file: str = "data/rules.json", 
                 risk_id_generator: Optional[RiskIdGenerator] = None):
        # ...
        self.risk_id_generator = risk_id_generator or RiskIdGenerator()
    
    def create_risk(self, ...):
        risk_id = self.risk_id_generator.generate_id(requirement.id, self.get_category())
        # ...
```

---

### 3.4 Introduce Parameter Object

#### Issue: Methods with many parameters
**Location:** Multiple locations

**Suggestion:**
```python
# Parameter Object Pattern
@dataclass
class AnalysisOptions:
    """Options for running analysis."""
    enabled_detectors: Optional[List[str]] = None
    min_severity: SeverityLevel = SeverityLevel.LOW
    include_suggestions: bool = True
    filter_duplicates: bool = True

# Usage
def analyze_requirements(requirements: List[Requirement],
                        detectors: List[RiskDetector],
                        options: AnalysisOptions) -> Dict[str, List[Risk]]:
    # Use options.min_severity, options.filter_duplicates, etc.
    pass
```

---

### 3.5 Replace Conditional with Polymorphism

#### Issue: Type checking in `analysis.py` for risk category conversion
**Location:** `web/api/analysis.py` lines 130, 155

**Suggestion:**
```python
# Add to_dict method to Risk (already exists, but enhance it)
# Use polymorphism instead of type checking
risks_dict = {
    req_id: [risk.to_dict() for risk in risks]
    for req_id, risks in risks_by_requirement.items()
}
```

---

## 4. Abstraction & Encapsulation Improvements

### 4.1 Abstract Configuration Access

#### Issue: Direct JSON file access throughout codebase
**Location:** `src/detectors/base.py`, `src/factories/detector_factory.py`

**Suggestion:**
```python
# Abstract Configuration Interface
class ConfigurationProvider(ABC):
    """Abstract interface for configuration access."""
    @abstractmethod
    def get_detector_config(self, detector_name: str) -> Dict:
        pass
    
    @abstractmethod
    def is_detector_enabled(self, detector_name: str) -> bool:
        pass

# JSON File Implementation
class JsonFileConfigurationProvider(ConfigurationProvider):
    """JSON file-based configuration provider."""
    def __init__(self, rules_file: str):
        self.config = self._load_config(rules_file)
    
    def get_detector_config(self, detector_name: str) -> Dict:
        return self.config.get('detectors', {}).get(detector_name, {})
    
    def is_detector_enabled(self, detector_name: str) -> bool:
        config = self.get_detector_config(detector_name)
        return config.get('enabled', False)

# Database Implementation (for future)
class DatabaseConfigurationProvider(ConfigurationProvider):
    """Database-based configuration provider."""
    # Implementation for database-backed config
    pass
```

**Benefits:**
- Can swap configuration sources (file, database, API)
- Easier to test with mock configurations
- Better encapsulation

---

### 4.2 Encapsulate File Operations

#### Issue: File paths and operations scattered
**Location:** Multiple files

**Suggestion:**
```python
# File Repository Pattern
class FileRepository(ABC):
    """Abstract file repository interface."""
    @abstractmethod
    def save(self, content: str, filename: str) -> Path:
        pass
    
    @abstractmethod
    def load(self, filepath: str) -> str:
        pass
    
    @abstractmethod
    def exists(self, filepath: str) -> bool:
        pass

class LocalFileRepository(FileRepository):
    """Local filesystem file repository."""
    def __init__(self, base_path: Path):
        self.base_path = base_path
    
    def save(self, content: str, filename: str) -> Path:
        file_path = self.base_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def load(self, filepath: str) -> str:
        return Path(filepath).read_text(encoding='utf-8')
    
    def exists(self, filepath: str) -> bool:
        return Path(filepath).exists()
```

---

## 5. Error Handling Improvements

### 5.1 Replace Error Code with Exception

#### Issue: Silent failures in `analyzer.py`
**Location:** `src/analyzer.py` lines 28-32

**Current:**
```python
try:
    risks = detector.detect_risks(requirement)
except Exception:
    risks = []  # Silent failure
```

**Suggestion:**
```python
# Custom Exceptions
class DetectorExecutionError(StressSpecException):
    """Exception raised when detector execution fails."""
    pass

# Proper error handling
try:
    risks = detector.detect_risks(requirement)
except DetectorExecutionError as e:
    logger.error(f"Detector {detector.get_detector_name()} failed: {e}")
    # Optionally: return error risk or re-raise
    raise
except Exception as e:
    logger.error(f"Unexpected error in detector {detector.get_detector_name()}: {e}")
    raise DetectorExecutionError(f"Detector failed: {e}") from e
```

---

### 5.2 Introduce Null Object Pattern

#### Issue: None checks scattered throughout
**Location:** Multiple files

**Suggestion:**
```python
# Null Object Pattern
class NullReporter(Reporter):
    """Null object reporter that does nothing."""
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        # Return a dummy path or raise NotImplementedError
        return Path("/dev/null")

class NullDetector(RiskDetector):
    """Null object detector that finds no risks."""
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        return []
    
    def get_detector_name(self) -> str:
        return "Null Detector"
    
    def get_category(self) -> RiskCategory:
        return RiskCategory.AMBIGUITY  # Dummy value

# Usage - no None checks needed
reporter = reporter or NullReporter()
detector = detector or NullDetector()
```

---

## 6. Testing Improvements

### 6.1 Improve Test Structure

#### Suggestion: Use Test Fixtures and Factories

```python
# Test Fixtures
@pytest.fixture
def sample_requirement():
    """Fixture for sample requirement."""
    return Requirement(id="R001", line_number=1, text="The system shall allow users to login")

@pytest.fixture
def sample_requirements():
    """Fixture for multiple requirements."""
    return [
        Requirement(id="R001", line_number=1, text="Requirement 1"),
        Requirement(id="R002", line_number=2, text="Requirement 2"),
    ]

@pytest.fixture
def mock_detector():
    """Fixture for mock detector."""
    detector = Mock(spec=RiskDetector)
    detector.detect_risks.return_value = []
    detector.get_detector_name.return_value = "Mock Detector"
    detector.get_category.return_value = RiskCategory.AMBIGUITY
    return detector

# Test Factory
class TestDataFactory:
    """Factory for creating test data."""
    @staticmethod
    def create_requirement(id: str = "R001", text: str = "Test requirement") -> Requirement:
        return Requirement(id=id, line_number=1, text=text)
    
    @staticmethod
    def create_risk(requirement_id: str = "R001", 
                   category: RiskCategory = RiskCategory.AMBIGUITY) -> Risk:
        return Risk(
            id=f"{requirement_id}-RISK-001",
            category=category,
            severity=SeverityLevel.MEDIUM,
            description="Test risk",
            requirement_id=requirement_id,
            line_number=1,
            evidence="test"
        )
```

---

### 6.2 Improve Mock Usage

#### Suggestion: Use Dependency Injection for Testing

```python
# In tests, inject mocks
def test_analyzer_with_mock_detectors():
    """Test analyzer with mocked detectors."""
    mock_detector = Mock(spec=RiskDetector)
    mock_detector.detect_risks.return_value = [
        TestDataFactory.create_risk()
    ]
    
    requirements = [TestDataFactory.create_requirement()]
    detectors = [mock_detector]
    
    result = analyze_requirements(requirements, detectors)
    
    assert len(result["R001"]) == 1
    mock_detector.detect_risks.assert_called_once()
```

---

## 7. Composition Over Inheritance

### 7.1 Prefer Composition for Text Utilities

#### Current: Inheritance in `BaseRiskDetector`
**Location:** `src/detectors/base.py`

**Suggestion:**
```python
# Use Composition
class BaseRiskDetector(RiskDetector):
    def __init__(self, rules_file: str = "data/rules.json",
                 text_normalizer: Optional[TextNormalizer] = None,
                 risk_factory: Optional[RiskFactory] = None):
        self.config_manager = DetectorConfigManager(rules_file)
        self.text_normalizer = text_normalizer or TextNormalizer()
        self.risk_factory = risk_factory or RiskFactory()
        self._setup_detector()
    
    def normalize_text(self, text: str) -> str:
        """Delegate to text normalizer."""
        return self.text_normalizer.normalize_text(text, 
            case_sensitive=self.config_manager.get_global_setting('case_sensitive', False))
    
    def contains_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Delegate to text normalizer."""
        return self.text_normalizer.contains_keywords(text, keywords)
```

**Benefits:**
- More flexible - can swap implementations
- Easier to test - can inject mock normalizer
- Follows composition over inheritance principle

---

## 8. Additional Refactoring Opportunities

### 8.1 Extract Constants

#### Issue: Hard-coded strings and values
**Location:** Multiple files

**Suggestion:**
```python
# Constants Module
class Constants:
    """Application-wide constants."""
    DEFAULT_RULES_FILE = "data/rules.json"
    DEFAULT_REPORT_FORMAT = ReportFormat.MD
    SUPPORTED_FILE_EXTENSIONS = {'.txt', '.md'}
    DEFAULT_SEVERITY = SeverityLevel.MEDIUM
    RISK_ID_FORMAT = "{requirement_id}-{category}-{counter:03d}"
    REQUIREMENT_ID_FORMAT = "R{counter:03d}"
```

---

### 8.2 Introduce Assertions

#### Issue: Missing validation in some methods
**Location:** Various

**Suggestion:**
```python
def analyze_requirements(requirements: List[Requirement],
                        detectors: List[RiskDetector]) -> Dict[str, List[Risk]]:
    """Run detectors against requirements."""
    assert requirements is not None, "Requirements list cannot be None"
    assert len(requirements) > 0, "Requirements list cannot be empty"
    assert detectors is not None, "Detectors list cannot be None"
    assert len(detectors) > 0, "At least one detector must be provided"
    
    # ... rest of implementation
```

---

### 8.3 Remove Control Flag

#### Issue: Boolean flags for control flow
**Location:** Various

**Suggestion:**
```python
# Instead of:
if verbose:
    print("Message")

# Use Strategy:
class OutputStrategy(ABC):
    @abstractmethod
    def output(self, message: str):
        pass

class VerboseOutputStrategy(OutputStrategy):
    def output(self, message: str):
        print(message)

class SilentOutputStrategy(OutputStrategy):
    def output(self, message: str):
        pass

# Usage
output_strategy = VerboseOutputStrategy() if verbose else SilentOutputStrategy()
output_strategy.output("Message")
```

---

## 9. Priority Recommendations

### High Priority (Immediate Impact)
1. **Extract ReporterFactory** - Remove if/elif chain in main.py
2. **Extract AnalysisService** - Break down long `run_analysis` method
3. **Improve Error Handling** - Replace silent failures with proper exceptions
4. **Dependency Injection** - Make components testable and swappable

### Medium Priority (Quality Improvements)
5. **Extract Configuration Manager** - Abstract configuration access
6. **Observer Pattern for Progress** - Better progress reporting
7. **Extract Method Refactoring** - Break down long methods
8. **Introduce Parameter Objects** - Reduce parameter lists

### Low Priority (Nice to Have)
9. **Chain of Responsibility** - For risk filtering
10. **Decorator Pattern** - For report enhancements
11. **Null Object Pattern** - Reduce None checks
12. **Test Fixtures** - Improve test structure

---

## 10. Implementation Strategy

1. **Start with High Priority items** - These provide immediate benefits
2. **Refactor incrementally** - One pattern/principle at a time
3. **Maintain test coverage** - Ensure refactoring doesn't break tests
4. **Document changes** - Update architecture documentation
5. **Code reviews** - Get feedback on design decisions

---

## Conclusion

The StressSpec codebase is well-structured but has opportunities for improvement following Software Design principles. The suggested refactorings will:

- Improve maintainability through better separation of concerns
- Enhance testability through dependency injection
- Increase extensibility through proper use of design patterns
- Follow SOLID principles more closely
- Apply refactoring techniques from course materials

These changes should be implemented incrementally, with thorough testing at each step.

