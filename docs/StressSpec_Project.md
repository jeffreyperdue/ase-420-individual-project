# Individual Project - StressSpec

## A.I Option: Vibe-Coding

### Current Project Status: MVP COMPLETED ✅ - SPRINT 2 IN PROGRESS

**Sprint 1 (4 weeks) - COMPLETED**  
All core MVP features have been successfully implemented and tested. The system is fully functional with comprehensive risk detection, multi-format reporting, and configurable rules.

**Sprint 2 (5 weeks) - IN PROGRESS**  
Currently working on completing the original 8-category plan and enhancing reporting capabilities. Test coverage at 93.7% (59 passing, 4 failing).

### Features Implemented (Sprint 1)

1. ✅ **Input Ingestion**: Accepts .txt or .md requirements (one per line/bullet)  
2. ✅ **Requirement Parsing & Labeling**: Assigns unique IDs (R001, R002, etc.) and line numbers
3. ✅ **Risk Detection Modules**: 6 detector categories (Ambiguity, Missing Detail, Security, Conflict, Performance, Availability)
4. ✅ **Configurable Rules**: JSON-driven rules with severity levels and enable/disable switches
5. ✅ **Reporting (Markdown, CSV, JSON)**: Multi-format output with CLI format selection
6. ✅ **Severity Scoring**: 5-level severity system (Low, Medium, High, Critical, Blocker)
7. ✅ **Testing**: Comprehensive test suite with 59 passing tests, 4 failing (93.7% pass rate) - working toward 100% coverage
8. ✅ **CLI Interface**: Full command-line interface with verbose output and error handling
9. ✅ **Web UI**: Complete FastAPI web application with modern UI, responsive design, and comprehensive features

### Features Planned (Sprint 2)

1. 🔄 **Complete Test Coverage**: Achieve 100% test pass rate by fixing remaining 4 integration test failures
2. 🔄 **Complete 8-Category Risk Detection**: Add Privacy, Traceability, and Scope detection modules
3. 🔄 **Enhanced Severity Scoring**: Implement "Top 5 Riskiest Requirements" analysis
4. 🔄 **Enhanced HTML Reporting**: Generate standalone HTML reports with professional styling

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
│   ├── detectors/                 # 6 implemented risk detectors
│   ├── factories/
│   │   └── detector_factory.py    # Factory Method for detectors
│   └── reporting/                 # Multi-format reporting system
├── data/
│   ├── rules.json                 # Configurable rules & severities
│   └── sample_requirements.txt    # Sample data
└── tests/                         # Unit & integration tests (31 passing)
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
  - *Status*: **COMPLETED** — Comprehensive test suite with 59 passing tests (93.7% pass rate) covering all components.

- ✅ **Feature #8: Web UI Implementation**  
  - *Status*: **COMPLETED** — Production-ready FastAPI web application with modern UI, responsive design, file upload system, real-time analysis, and comprehensive API.

**Milestone Deliverable (End of Sprint 1):** ✅ **COMPLETED** — Full MVP end-to-end flow from input → risk detection → multi-format reports with severity scoring + complete web application exceeding original scope.

---

### Sprint 2 (5 Weeks) → Complete 8-Category System & Enhanced Reporting

**Current Status**: Ready to begin Sprint 2 development with realistic scope (15-20 hours total, 3-4 hours/week).

- **Feature #1: Complete Test Coverage**  
  - Requirement #1: The system shall achieve 100% test pass rate by resolving remaining integration test failures.  
  - *Plan*: Implement in Week 6 — fix 4 remaining integration test failures + ensure all 63+ tests pass consistently.

- **Feature #2: Risk Detection Modules (Complete 8-Category System)**  
  - Requirement #2: The system shall add Privacy, Traceability, and Scope detection modules to complete the original 8-category plan.  
  - *Note*: Conflict detection already implemented in MVP
  - *Plan*: Implement in Week 6-7 — Privacy detector (Week 6) + Traceability & Scope detectors (Week 7) + updated rules.json.

- **Feature #3: Advanced Severity Scoring**  
  - Requirement #3: The system shall calculate combined risk scores and highlight the "Top 5 riskiest requirements."  
  - *Plan*: Implement in Week 8 — scoring aggregation engine + top 5 riskiest requirements analysis + integration with existing report formats.

- **Feature #4: Enhanced HTML Reporting**  
  - Requirement #4: The system shall generate standalone HTML reports with professional styling suitable for stakeholder presentations.  
  - *Plan*: Implement in Week 9 — Jinja2 HTML templates + Bootstrap styling + executive summary format + self-contained report generation.

- **Feature #5: Documentation & Polish**  
  - Requirement #5: The system shall have updated documentation and all new features shall be tested and validated.  
  - *Plan*: Implement in Week 10 — comprehensive testing + bug fixes + documentation updates + user guides for new features.

**Milestone Deliverable (End of Sprint 2):** Completed tool with all 8 risk detection categories, advanced scoring with "Top 5 riskiest requirements," professional HTML reporting, and 100% test coverage.

---

## Current Implementation Details

### Risk Detection Modules (6 Implemented, 3 Planned)

**Currently Implemented:**
1. **AmbiguityDetector** - Detects vague language and imprecise terms
2. **MissingDetailDetector** - Identifies incomplete requirements and unspecified actors
3. **SecurityDetector** - Flags missing authentication, authorization, and data protection
4. **ConflictDetector** - Finds duplicate and contradictory requirements
5. **PerformanceDetector** - Identifies missing performance specifications
6. **AvailabilityDetector** - Detects missing uptime and reliability requirements

**Planned for Sprint 2:**
7. **PrivacyDetector** - Detects GDPR/CCPA compliance gaps and privacy policy requirements
8. **TraceabilityDetector** - Identifies missing requirement IDs and test coverage references
9. **ScopeDetector** - Flags scope creep and boundary violations

### Configuration System

- **rules.json**: Comprehensive configuration with 6 detector categories (will expand to 9 in Sprint 2)
- **Severity Levels**: 5-level system (Low=1, Medium=2, High=3, Critical=4, Blocker=5)
- **Enable/Disable**: Each detector can be individually enabled or disabled
- **Customizable Rules**: Keywords, patterns, and thresholds configurable per detector
- **Future Enhancement**: Multi-domain configuration profiles planned for Sprint 3+

### Reporting System

- **Markdown Reporter**: Human-readable reports with risk summaries
- **CSV Reporter**: Structured data for analysis and sorting
- **JSON Reporter**: Machine-readable format for integration
- **HTML Reporter**: Planned for Sprint 2 - standalone HTML reports with professional styling
- **CLI Integration**: Format selection via `--report-format` parameter
- **Web UI Integration**: Interactive report viewing and export capabilities
- **Future Enhancement**: "Top 5 Riskiest Requirements" analysis planned for Sprint 2

### Testing & Quality Assurance

- **Test Coverage**: 63 comprehensive tests covering all major components (59 passing, 4 failing - 93.7% pass rate)
- **Unit Tests**: Individual component testing (detectors, parsers, models)
- **Integration Tests**: End-to-end workflow testing
- **Test Categories**:
  - Requirement and Risk model validation
  - File loading and parsing functionality
  - All 6 detector implementations
  - Reporting system integration
  - Web UI functionality and API endpoints
  - Error handling and edge cases
- **Sprint 2 Goal**: Achieve 100% test pass rate by fixing remaining 4 failing tests (currently 93.7% pass rate)

### Usage Examples

```bash
# CLI Usage - Basic usage with Markdown output
python main.py --file data/sample_requirements.txt --verbose

# CLI Usage - Generate CSV report with custom output path
python main.py --file requirements.txt --report-format csv --output analysis.csv

# CLI Usage - Generate JSON report for integration
python main.py --file requirements.md --report-format json --output risks.json

# Web UI Usage - Start the web server
python web/main.py
# Then navigate to http://localhost:8000 for interactive analysis

# Future Usage (Sprint 2) - Generate HTML reports
python main.py --file requirements.txt --report-format html --output analysis.html
```

### Performance & Scalability

- **Efficient Processing**: Handles large requirement documents
- **Memory Management**: Streamlined data structures with dataclasses
- **Error Handling**: Comprehensive error messages and graceful failure handling
- **Extensibility**: Factory pattern allows easy addition of new detectors
- **Web UI Performance**: FastAPI async processing with responsive design
- **Sprint 2 Enhancement**: "Top 5 Riskiest Requirements" analysis for prioritization

### Sprint 2 Development Approach

**Realistic Scope for Solo Developer:**
- **Time Investment**: 15-20 hours total over 5 weeks (3-4 hours/week)
- **Focus Areas**: Complete 8-category plan + enhanced reporting + advanced scoring
- **Development Strategy**: Copy existing patterns, minimal viable features, incremental testing
- **Quality Focus**: Maintain 100% test coverage and code quality standards

**Key Sprint 2 Deliverables:**
1. **100% Test Coverage** - All tests passing reliably
2. **8-Category Risk Detection** - Complete original plan implementation  
3. **Advanced Scoring** - Top 5 riskiest requirements identification
4. **Enhanced Reporting** - Standalone HTML report generation
5. **Updated Documentation** - User guides and examples for new features
