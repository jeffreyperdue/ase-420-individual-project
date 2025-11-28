# Individual Project - StressSpec

## A.I Option: Vibe-Coding

### Current Project Status: SPRINT 1 & SPRINT 2 COMPLETED ✅

**Sprint 1 (4 weeks) - COMPLETED**  
All core MVP features have been successfully implemented and tested. The system is fully functional with comprehensive risk detection, multi-format reporting, and configurable rules.

**Sprint 2 (5 weeks) - COMPLETED**  
All Sprint 2 features have been successfully implemented. The project now includes 8-category risk detection, advanced scoring with Top 5 Riskiest Requirements, HTML reporting, and comprehensive test coverage with 241+ tests across 4 test types (unit, integration, regression, acceptance).

### Features Implemented (Sprint 1)

1. ✅ **Input Ingestion**: Accepts .txt or .md requirements (one per line/bullet)  
2. ✅ **Requirement Parsing & Labeling**: Assigns unique IDs (R001, R002, etc.) and line numbers
3. ✅ **Risk Detection Modules**: 6 detector categories (Ambiguity, Missing Detail, Security, Conflict, Performance, Availability)
4. ✅ **Configurable Rules**: JSON-driven rules with severity levels and enable/disable switches
5. ✅ **Reporting (Markdown, CSV, JSON)**: Multi-format output with CLI format selection
6. ✅ **Severity Scoring**: 5-level severity system (Low, Medium, High, Critical, Blocker)
7. ✅ **Testing**: Comprehensive test suite organized by test type (unit, integration, regression, acceptance) with 241+ test cases covering all components
8. ✅ **CLI Interface**: Full command-line interface with verbose output and error handling
9. ✅ **Web UI**: Complete FastAPI web application with modern UI, responsive design, and comprehensive features

### Features Completed (Sprint 2)

1. ✅ **Comprehensive Test Suite**: Implemented complete test coverage across 4 test types (unit, integration, regression, acceptance) with 241+ test cases organized in structured subdirectories
2. ✅ **Complete 8-Category Risk Detection**: Added Traceability and Scope detection modules (8 categories total)
3. ✅ **Enhanced Severity Scoring**: Implemented "Top 5 Riskiest Requirements" analysis with cross-format support
4. ✅ **Enhanced HTML Reporting**: Standalone HTML reports with professional styling for stakeholder presentations

### Architecture Overview

The project follows SOLID principles and implements several design patterns:

- **Factory Method Pattern**: `RiskDetectorFactory` for creating detector instances
- **Strategy Pattern**: Extensible risk detection algorithms
- **Template Method Pattern**: Shared workflow in `BaseRiskDetector`
- **Data Classes**: Clean, immutable data structures for requirements and risks

### Project Structure
```
StressSpec/
├── main.py                        # CLI entry point
├── requirements.txt               # Dependencies
├── src/
│   ├── file_loader.py             # File loading and processing
│   ├── requirement_parser.py      # Requirement parsing logic
│   ├── analyzer.py                # Runs detectors and aggregates risks
│   ├── models/
│   │   ├── requirement.py         # Requirement data model
│   │   └── risk.py                # Risk data model + severity
│   ├── detectors/                 # 8 implemented risk detectors
│   ├── factories/
│   │   └── detector_factory.py    # Factory Method for detectors
│   └── reporting/                 # Multi-format reporting system
├── data/
│   ├── rules.json                 # Configurable rules & severities
│   └── sample_requirements.txt    # Sample data
└── tests/                         # Comprehensive test suite (241+ tests)
    ├── __init__.py                # Test package initialization
    ├── conftest.py                # Shared pytest fixtures (accessible to all)
    ├── test_suite_guide.md        # Test suite documentation
    ├── unit/                      # Unit tests (21 files, ~176 tests)
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
    ├── integration/               # Integration tests (2 files, ~10 tests)
    │   ├── __init__.py
    │   ├── test_integration.py
    │   └── test_integration_new_detectors.py
    ├── regression/                # Regression tests (1 file, ~30 tests)
    │   ├── __init__.py
    │   └── test_regression.py
    └── acceptance/                # Acceptance tests (1 file, ~35 tests)
        ├── __init__.py
        └── test_acceptance.py
```

---

## Requirements

### Epic User Story

**As a** project manager,  
**I want to** analyze requirement documents for hidden risks,  
**so that** I can improve requirement quality and reduce project failures before development begins.

### User Stories

**Input Ingestion**  
**As a** developer,  
**I want to** upload a .txt or .md file containing requirements (one per line or bullet),  
**so that** the tool can process them automatically.

**Requirement Parsing & Labeling**  
**As a** QA engineer,  
**I want to** see each requirement assigned an ID and line number,  
**so that** I can trace flagged risks back to the original text.

**Risk Detection - Ambiguity**  
**As a** business analyst,  
**I want to** detect vague or ambiguous language in requirements,  
**so that** unclear requirements are highlighted for revision.

**Risk Detection - Missing Details**  
**As a** business analyst,  
**I want to** identify incomplete requirements with missing specifications,  
**so that** requirements can be completed before development begins.

**Risk Detection - Security**  
**As a** security engineer,  
**I want to** detect missing authentication, authorization, and data protection requirements,  
**so that** security gaps are identified early in the process.

**Risk Detection - Conflicts**  
**As a** project manager,  
**I want to** identify duplicate or contradictory requirements,  
**so that** conflicts can be resolved before development starts.

**Risk Detection - Performance**  
**As a** performance engineer,  
**I want to** detect missing performance specifications,  
**so that** performance requirements are clearly defined.

**Risk Detection - Availability**  
**As a** system administrator,  
**I want to** detect missing uptime and reliability requirements,  
**so that** availability expectations are explicitly stated.

**Configurable Rules**  
**As a** compliance officer,  
**I want to** edit a rules.json file to add or change detection terms,  
**so that** the tool adapts to different domains (e.g., finance, healthcare).

**Multi-Format Reporting**  
**As a** project manager,  
**I want to** generate reports in Markdown, CSV, and JSON formats,  
**so that** I can share results with the team in multiple ways.

**Severity Scoring**  
**As a** team lead,  
**I want to** see each flagged risk assigned a severity level (Low, Medium, High, Critical, Blocker),  
**so that** I can prioritize which requirements need attention first.

**CLI Interface**  
**As a** developer,  
**I want to** use command-line options to specify input files and output formats,  
**so that** I can integrate the tool into automated workflows.

**Testing & Quality Assurance**  
**As a** developer,  
**I want to** have comprehensive test coverage for all components,  
**so that** I can ensure the tool works reliably and can be maintained safely.

---

## What is the Problem?

Most software project failures stem from unclear, unrealistic, or incomplete requirements.  
Studies show fixing requirement defects late can cost 5–10x more, and around 37% of enterprise project failures are linked to poor requirements.  

Current tools help write or clarify requirements, but they don’t stress-test them for hidden risks like ambiguity, conflicts, compliance gaps, or scalability issues.  
Teams often only discover these problems after coding begins, when fixing them is expensive and disruptive.

---

## Why is it Important?

Catching requirement problems early:

- Saves time and money by preventing costly rework later in development.  
- Improves quality by ensuring requirements are testable, realistic, and aligned with regulations.  
- Supports collaboration between project managers, analysts, developers, and QA by providing traceable, prioritized risk reports.  
- **Recruiter/industry relevance**: A tool like this demonstrates practical application of AI/rule-based analysis to real-world software engineering challenges.

---

## How Will You Solve It (Design Overview)?

The solution is a Python-based Requirements Stress Tester that acts like a “wind tunnel” for requirements:

- **Input Ingestion**: Accept .txt or .md files with one requirement per line.  
- **Requirement Parsing & Labeling**: Assign each requirement an ID (e.g., R001) and line number for traceability.  
- **Risk Detection Modules**: Run checks in categories such as ambiguity, availability, performance, security, privacy, conflicts, and scope. Each check is modular, keyword/regex-driven, and returns flags.  
- **Configurable Rules**: Store detection rules in rules.json so users can update keywords/conditions without editing code.  
- **Severity Scoring**: Assign each flag a severity (High/Medium/Low) and calculate totals to rank risky requirements.  
- **Reporting**: Generate outputs in Markdown (human-readable), CSV (sortable), and JSON (machine-readable). Reports link each flag back to its requirement ID and evidence.

---

## Milestones

### Sprint 1 (4 Weeks) → MVP COMPLETED ✅

- ✅ **Feature #1: Input Ingestion**  
  - Requirement #1: The system shall accept .txt or .md files with one requirement per line or bullet.  
  - *Status*: **COMPLETED** — CLI interface, file loader, and comprehensive error handling implemented.

- ✅ **Feature #2: Requirement Parsing & Labeling**  
  - Requirement #2: The system shall parse lines into requirement objects with IDs (R001…) and line numbers.  
  - *Status*: **COMPLETED** — Parser module built with ID assignment (R001, R002, etc.) and line number tracking.

- ✅ **Feature #3: Risk Detection Modules (expanded)**  
  - Requirement #3: The system shall flag risks in at least 4 categories: Ambiguity, Availability, Performance, Security.  
  - *Status*: **COMPLETED** — **6 detector categories implemented**: Ambiguity, Missing Detail, Security, Conflict, Performance, Availability.

- ✅ **Feature #4: Configurable Rules (advanced)**  
  - Requirement #4: The system shall load detection rules from rules.json so categories can be updated without code changes.  
  - *Status*: **COMPLETED** — JSON-driven configuration with severity levels, enable/disable switches, and comprehensive rule sets.

- ✅ **Feature #5: Reporting (Markdown + CSV + JSON)**  
  - Requirement #5: The system shall generate report.md, report.csv, and risk_log.json with traceable requirement IDs.  
  - *Status*: **COMPLETED** — Multi-format reporting system with CLI format selection and custom output paths.

- ✅ **Feature #6: Severity Scoring (advanced)**  
  - Requirement #6: The system shall assign a default severity (High, Medium, Low) to each category.  
  - *Status*: **COMPLETED** — **5-level severity system**: Low, Medium, High, Critical, Blocker with numeric scoring.

- ✅ **Feature #7: Testing & Quality Assurance**  
  - *Status*: **COMPLETED** — Comprehensive test suite with unit, integration, regression, and acceptance tests covering all components with 241+ test cases.

- ✅ **Feature #8: Web UI Implementation**  
  - *Status*: **COMPLETED** — Production-ready FastAPI web application with modern UI, responsive design, file upload system, real-time analysis, and comprehensive API.

**Milestone Deliverable (End of Sprint 1):** ✅ **COMPLETED** — Full MVP end-to-end flow from input → risk detection → multi-format reports with severity scoring + complete web application exceeding original scope.

---

### Sprint 2 (5 Weeks) → Complete 8-Category System & Enhanced Reporting ✅

**Status**: COMPLETED - All Sprint 2 features successfully implemented and tested.

- ✅ **Feature #1: Comprehensive Test Suite Implementation**  
  - Requirement #1: The system shall have comprehensive test coverage across unit, integration, regression, and acceptance test types.  
  - *Status*: **COMPLETED** — Complete test suite implemented with 241+ test cases organized into 4 test categories (unit: 21 files, integration: 2 files, regression: 1 file, acceptance: 1 file). All tests passing with 100% reliability.

- ✅ **Feature #2: Risk Detection Modules (Complete 8-Category System)**  
  - Requirement #2: The system shall add Traceability and Scope detection modules to complete the original 8-category plan.  
  - *Note*: Privacy detector was planned but not implemented. 8 categories achieved via Traceability + Scope detectors.
  - *Status*: **COMPLETED** — Traceability and Scope detectors implemented in Week 7. All 8 categories now functional.

- ✅ **Feature #3: Advanced Severity Scoring**  
  - Requirement #3: The system shall calculate combined risk scores and highlight the "Top 5 riskiest requirements."  
  - *Status*: **COMPLETED** — Scoring aggregation engine implemented in Week 8. Top 5 Riskiest Requirements available in all report formats.

- ✅ **Feature #4: Enhanced HTML Reporting**  
  - Requirement #4: The system shall generate standalone HTML reports with professional styling suitable for stakeholder presentations.  
  - *Status*: **COMPLETED** — Standalone HTML reports with professional styling implemented in Week 9. Includes executive summary and Top 5 section.

- ✅ **Feature #5: Documentation & Polish**  
  - Requirement #5: The system shall have updated documentation and all new features shall be tested and validated.  
  - *Status*: **COMPLETED** — Comprehensive testing completed in Week 10. All deprecation warnings fixed. Documentation updated.

**Milestone Deliverable (End of Sprint 2):** ✅ **COMPLETED** — Tool now includes all 8 risk detection categories, advanced scoring with "Top 5 riskiest requirements," professional HTML reporting, and comprehensive test suite with 241+ tests across 4 test types (unit, integration, regression, acceptance).

---

## Current Implementation Details

### Risk Detection Modules (8 Implemented) ✅

**All 8 Categories Implemented:**
1. **AmbiguityDetector** - Detects vague language and imprecise terms
2. **MissingDetailDetector** - Identifies incomplete requirements and unspecified actors
3. **SecurityDetector** - Flags missing authentication, authorization, and data protection
4. **ConflictDetector** - Finds duplicate and contradictory requirements
5. **PerformanceDetector** - Identifies missing performance specifications
6. **AvailabilityDetector** - Detects missing uptime and reliability requirements
7. **TraceabilityDetector** - Identifies missing requirement IDs and test coverage references (Sprint 2)
8. **ScopeDetector** - Flags scope creep and boundary violations (Sprint 2)

**Note:** Privacy detector was originally planned but not implemented. However, the 8-category goal was achieved through Traceability and Scope detectors.

### Configuration System

- **rules.json**: Comprehensive configuration with 8 detector categories (all categories implemented)
- **Severity Levels**: 5-level system (Low=1, Medium=2, High=3, Critical=4, Blocker=5)
- **Enable/Disable**: Each detector can be individually enabled or disabled
- **Customizable Rules**: Keywords, patterns, and thresholds configurable per detector
- **Future Enhancement**: Multi-domain configuration profiles planned for Sprint 3+

### Reporting System

- **Markdown Reporter**: Human-readable reports with risk summaries and Top 5 Riskiest Requirements
- **CSV Reporter**: Structured data for analysis and sorting with score columns and Top 5 summary
- **JSON Reporter**: Machine-readable format for integration with top_5_riskiest array
- **HTML Reporter**: Standalone HTML reports with professional styling for stakeholder presentations (Sprint 2)
- **CLI Integration**: Format selection via `--report-format` parameter
- **Web UI Integration**: Interactive report viewing and export capabilities
- **Top 5 Riskiest Requirements**: Available in all 4 report formats (Sprint 2)

### Testing & Quality Assurance

- **Test Coverage**: 241+ comprehensive tests organized by test type (100% pass rate)
- **Test Organization**: Tests organized into 4 categories with structured subdirectories:
  - **Unit Tests** (`tests/unit/`): 21 test files covering individual components in isolation
  - **Integration Tests** (`tests/integration/`): 2 test files for end-to-end workflow testing
  - **Regression Tests** (`tests/regression/`): 1 test file verifying previously fixed bugs don't reoccur
  - **Acceptance Tests** (`tests/acceptance/`): 1 test file for user story and business requirement validation

- **Unit Test Coverage** (21 files):
  - Models: Risk, Requirement validation and behavior
  - Core Components: FileLoader, RequirementParser, Analyzer, Scoring
  - All 8 Detectors: Comprehensive tests for Ambiguity, Security, Conflict, Missing Detail, Performance, Availability, Traceability, Scope
  - Factories: DetectorFactory, ReporterFactory
  - Services: StressSpecService orchestration
  - Design Patterns: Observer, Chain of Responsibility
  - Error Handling: Custom exceptions, error handlers, middleware

- **Integration Test Coverage** (2 files):
  - Complete workflow from file loading to report generation
  - Cross-format report validation (MD, CSV, JSON, HTML)
  - Top 5 Riskiest Requirements integration across all formats
  - Multi-detector interaction testing

- **Regression Test Coverage** (1 file):
  - Previously fixed bugs (unicode handling, special characters, zero risks, etc.)
  - Edge cases that caused issues (long text, whitespace, mixed line endings)
  - Data integrity checks (unique IDs, line numbers, text preservation)
  - Performance regressions (analysis time, memory usage)
  - Version compatibility (report formats, config files)

- **Acceptance Test Coverage** (1 file):
  - User Story 1: Upload and Analyze Requirements
  - User Story 2: View Risk Details
  - User Story 3: Download Reports
  - User Story 4: Business Requirements Validation (all 8 risk categories)
  - User Story 5: Performance Requirements
  - User Story 6: Error Handling from user perspective

- **Test Infrastructure**:
  - Shared fixtures in `conftest.py` (accessible to all test types)
  - TestDataFactory for consistent test data creation
  - Comprehensive test documentation and organization
  - Pytest best practices throughout

- **Sprint 2 Achievement**: ✅ Comprehensive test suite implemented - 241+ tests across 4 test types, all passing reliably

### Usage Examples

#### Web Interface (Primary Method)

**Start the Development Server:**
```bash
# Method 1: Using the run script (recommended)
python web_utils/run_web.py

# Method 2: Direct FastAPI
python -m uvicorn web.main:app --host 127.0.0.1 --port 8000 --reload

# Method 3: Using main app
python web/main.py
```

**Access Points:**
- Main Web Interface: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/api/docs
- Health Check: http://127.0.0.1:8000/health

**Web Interface Features:**
- File upload with drag-and-drop support
- Real-time analysis progress
- Interactive results display with filtering
- Multi-format report downloads (HTML, Markdown, CSV, JSON)
- Sample file downloads for testing

#### CLI Usage (Advanced/Integration)

```bash
# Basic usage with Markdown output
python main.py --file data/sample_requirements.txt --verbose

# Generate CSV report with custom output path
python main.py --file requirements.txt --report-format csv --output analysis.csv

# Generate JSON report for integration
python main.py --file requirements.md --report-format json --output risks.json

# Generate HTML reports (Sprint 2 feature)
python main.py --file requirements.txt --report-format html --output analysis.html
```

**CLI Options:**
- `--file` - Path to requirements file (required)
- `--report-format` - Output format: `md`, `csv`, `json`, or `html` (default: `md`)
- `--output` - Custom output file path (optional)
- `--verbose` - Show detailed processing information

### Performance & Scalability

- **Efficient Processing**: Handles large requirement documents efficiently
- **Memory Management**: Streamlined data structures with dataclasses
- **Error Handling**: Comprehensive error messages and graceful failure handling
- **Extensibility**: Factory pattern allows easy addition of new detectors
- **Web UI Performance**: FastAPI async processing with responsive design
- **Sprint 2 Enhancement**: ✅ "Top 5 Riskiest Requirements" analysis implemented for prioritization

### Web Interface Architecture

**Technology Stack:**
- **FastAPI** - Modern, fast web framework for building APIs
- **Jinja2** - Template engine for HTML rendering
- **HTMX** - Dynamic HTML interactions without complex JavaScript
- **Bootstrap 5** - Responsive UI framework
- **Uvicorn** - ASGI server for FastAPI

**Key Components:**
- **File Upload System** - Handles .txt and .md file uploads with validation
- **Analysis Processing** - Background task processing for requirement analysis
- **Report Generation** - Multi-format report generation (HTML, Markdown, CSV, JSON)
- **API Endpoints** - RESTful API for programmatic access
- **Real-time Updates** - HTMX-powered dynamic UI updates

**File Structure:**
```
web/
├── main.py                    # FastAPI app entry point
├── static/                    # Static files (CSS, JS, images)
│   ├── css/                   # Stylesheets
│   ├── js/                    # JavaScript (including HTMX)
│   └── images/                # Images and icons
├── templates/                 # Jinja2 HTML templates
│   └── reports/               # Report templates
└── api/                       # API endpoint modules
    ├── upload.py              # File upload endpoints
    ├── analysis.py            # Analysis processing endpoints
    └── reports.py             # Report generation endpoints
```

### Setup & Configuration

**Automated Setup:**
```bash
python web_utils/setup_web.py
```

**Manual Setup Steps:**
1. Install dependencies: `pip install -r requirements.txt`
2. Create directories: `mkdir -p uploads logs`
3. Start server: `python web_utils/run_web.py`

**Environment Configuration (.env file):**
```bash
# Development settings
DEBUG=True
ENVIRONMENT=development

# Server configuration
HOST=127.0.0.1
PORT=8000
RELOAD=True

# File upload settings
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=.txt,.md
UPLOAD_DIR=uploads

# Analysis settings
ANALYSIS_TIMEOUT=300  # 5 minutes
MAX_CONCURRENT_ANALYSES=5
```

### Sprint 2 Development Results ✅

**Sprint 2 Completed Successfully:**
- **Time Investment**: Completed within planned 15-20 hours over 5 weeks
- **Focus Areas**: ✅ Complete 8-category plan + enhanced reporting + advanced scoring
- **Development Strategy**: Followed existing patterns, incremental testing, quality focus
- **Quality Achievement**: ✅ 100% test coverage maintained throughout

**Sprint 2 Deliverables - All Completed:**
1. ✅ **Comprehensive Test Suite** - 241+ tests across 4 test types (unit, integration, regression, acceptance) all passing reliably
2. ✅ **8-Category Risk Detection** - Complete original plan implementation (Traceability + Scope added)
3. ✅ **Advanced Scoring** - Top 5 riskiest requirements identification across all formats
4. ✅ **Enhanced Reporting** - Standalone HTML report generation with professional styling
5. ✅ **Updated Documentation** - README, project docs, test documentation, and user guides updated

**Sprint 2 Status**: ✅ Complete - Ready for review and presentation

---

## Technical Implementation Details

### Design Principles Applied

#### SOLID Principles

- **Single Responsibility Principle**: Each class has one clear responsibility
  - `FileLoader`: Handles file operations only
  - `RequirementParser`: Handles parsing logic only
  - `Requirement`: Represents requirement data only
  - Each detector handles one specific risk category

- **Open/Closed Principle**: Open for extension, closed for modification
  - New detectors can be added without modifying existing code
  - Factory pattern allows easy addition of new detector types

- **Liskov Substitution Principle**: Derived classes can replace base classes
  - All detectors inherit from `BaseRiskDetector` and are interchangeable

- **Interface Segregation Principle**: Clients shouldn't depend on unused interfaces
  - Clean separation between detectors, parsers, and reporters

- **Dependency Inversion Principle**: Depend on abstractions, not concretions
  - Factory pattern creates detectors based on configuration
  - Reporters implement common interface

#### Design Patterns

- **Factory Method Pattern**: `RiskDetectorFactory` for creating detector instances
- **Strategy Pattern**: Extensible risk detection algorithms
- **Template Method Pattern**: Shared workflow in `BaseRiskDetector`
- **Data Classes**: Clean, immutable data structures for requirements and risks
- **Observer Pattern**: Event-driven architecture for analysis progress

### Code Quality Metrics

- **Test Coverage**: 241+ comprehensive tests across 4 test types (100% pass rate)
  - Unit Tests: 21 files covering all components in isolation
  - Integration Tests: 2 files for end-to-end workflows
  - Regression Tests: 1 file for bug prevention and data integrity
  - Acceptance Tests: 1 file for user story validation
- **Code Organization**: Modular structure with clear separation of concerns
- **Test Organization**: Tests organized by type in structured subdirectories for maintainability
- **Error Handling**: Comprehensive error messages and graceful failure handling
- **Type Hints**: Extensive use of Python type hints for better code clarity
- **Documentation**: Inline comments and docstrings throughout codebase
- **PEP8 Compliance**: Code follows Python style guidelines

### Testing Strategy

**Comprehensive 4-Type Test Suite:**

**1. Unit Tests** (`tests/unit/` - 21 files):
- Individual component testing in isolation with mocked dependencies
- Models: Risk and Requirement validation, string representations, methods
- Core Components: FileLoader, RequirementParser, Analyzer, Scoring functions
- All 8 Detectors: Comprehensive tests for each detector (Ambiguity, Security, Conflict, Missing Detail, Performance, Availability, Traceability, Scope)
- Factories: DetectorFactory and ReporterFactory creation and configuration
- Services: StressSpecService workflow orchestration
- Design Patterns: Observer pattern, Chain of Responsibility pattern
- Error Handling: Custom exceptions, error handlers, middleware
- Edge case validation and boundary testing

**2. Integration Tests** (`tests/integration/` - 2 files):
- End-to-end workflow testing from file upload to report generation
- Complete pipeline validation (load → parse → analyze → score → report)
- Cross-format report validation (MD, CSV, JSON, HTML)
- Top 5 Riskiest Requirements integration across all formats
- Multi-detector interaction testing
- Real file processing with temporary files

**3. Regression Tests** (`tests/regression/` - 1 file):
- Previously fixed bugs verification (unicode, special characters, zero risks, etc.)
- Edge cases that caused issues in the past (long text, whitespace, mixed line endings)
- Data integrity checks (unique IDs, line numbers, text preservation, risk evidence accuracy)
- Performance regression prevention (analysis time benchmarks, memory usage)
- Version compatibility (report formats, configuration files)

**4. Acceptance Tests** (`tests/acceptance/` - 1 file):
- User story validation from user perspective
- Business requirements verification (all 8 risk categories detected)
- Performance requirements (analysis completion time, file size handling)
- Error handling from user perspective (clear error messages, recovery)
- Complete user workflows (upload → analyze → download reports)

**Test Infrastructure:**
- Shared fixtures in root `conftest.py` (accessible to all test types)
- TestDataFactory for consistent test data creation
- Organized structure for maintainability and clarity
- Pytest best practices with proper fixture usage

### Configuration System

**rules.json Structure:**
- Detector enable/disable switches
- Severity level definitions
- Keyword and pattern configurations
- Category-specific thresholds
- Customizable detection rules

**Configuration Features:**
- JSON-based configuration (no code changes needed)
- Per-detector customization
- Severity level assignment
- Pattern and keyword management
- Easy domain adaptation (finance, healthcare, etc.)

### Reporting System Architecture

**Reporter Interface:**
- Common interface for all report formats
- Consistent data structure across formats
- Top 5 Riskiest Requirements in all formats
- Extensible design for future formats

**Report Formats:**
- **Markdown**: Human-readable technical documentation
- **CSV**: Spreadsheet-compatible data with score columns
- **JSON**: Machine-readable format for integration
- **HTML**: Standalone reports with professional styling

**Report Features:**
- Executive summary with statistics
- Top 5 Riskiest Requirements section
- Detailed requirements list with risk indicators
- Risk breakdown by category
- Severity color-coding (HTML reports)
- Print-friendly design (HTML reports)
