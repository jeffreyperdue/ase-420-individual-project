# Changelog

All notable changes to the StressSpec project will be documented in this file.

## [Sprint 2] - 2024

### Added

- **Traceability Detector** - Requirement ID validation and linking detection
  - Detects requirements without clear unique identifiers
  - Flags requirements without test coverage references
  - Identifies missing acceptance criteria
  
- **Scope Detector** - Scope creep and boundary violation detection
  - Detects requirements outside defined project boundaries
  - Flags ambiguous feature scope definitions
  - Identifies conflicting scope statements
  
- **Top 5 Riskiest Requirements** - Advanced risk prioritization
  - Calculates combined risk scores per requirement
  - Automatically identifies top 5 most risky requirements
  - Integrated across all report formats (Markdown, CSV, JSON, HTML)
  
- **HTML Report Generation** - Standalone HTML reports
  - Professional styling with embedded CSS
  - Self-contained reports (no web server required)
  - Executive summary with statistics
  - Color-coded severity badges
  - Print-friendly design

### Changed

- Expanded from 6 to 8 risk detection categories
  - Added Traceability and Scope detectors
  - Note: Privacy detector was planned but not implemented; 8 categories achieved via alternative detector mix
  
- Enhanced all report formats with Top 5 Riskiest Requirements
  - Markdown: Dedicated section with detailed breakdown
  - CSV: Score columns added, separate `*_top5.csv` file generated
  - JSON: `top_5_riskiest` array added to report structure
  - HTML: Visual Top 5 section with color-coded severity indicators

- Improved code quality
  - Fixed all deprecation warnings (datetime.utcnow → datetime.now(timezone.utc))
  - Updated Pydantic models (`.dict()` → `.model_dump()`)
  - PEP8 compliance improvements

### Fixed

- Resolved integration test failures (achieved 100% test pass rate)
- Fixed deprecation warnings throughout codebase
  - `datetime.utcnow()` → `datetime.now(timezone.utc)` (15 instances)
  - Pydantic `.dict()` → `.model_dump()` (9 instances)
- Improved error handling and validation
- Fixed Windows file permission issues in logging tests

### Testing

- Test coverage: 86 tests, 100% pass rate
- All 8 detectors validated independently
- Cross-format consistency validated across all 4 report formats
- Integration tests cover complete workflow end-to-end

### Documentation

- Updated README with Sprint 2 features
- Added CHANGELOG.md (this file)
- Updated usage examples for all 4 report formats
- Documented 8-category risk detection system

---

## [Sprint 1] - 2024

### Added

- Core requirement parsing and labeling system
- 6 risk detection categories: Ambiguity, Missing Detail, Security, Conflict, Performance, Availability
- Multi-format reporting (Markdown, CSV, JSON)
- CLI interface with format selection
- Configurable rules system (JSON-based)
- Comprehensive test suite
- Web UI with FastAPI backend
- Complete documentation

---

**Note:** This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) principles.


