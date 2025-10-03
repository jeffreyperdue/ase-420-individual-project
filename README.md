# StressSpec - Requirements Stress Tester

A Python-based tool for analyzing requirement documents and detecting potential risks and issues before development begins.

## Project Overview

StressSpec acts as a "wind tunnel" for requirements, helping project managers, business analysts, and development teams identify hidden risks in requirement documents early in the development process.

## Current Implementation Status ✅

### Completed Features

1. **Input Ingestion** - Accepts .txt and .md files with one requirement per line
2. **Requirement Parsing & Labeling** - Assigns unique IDs (R001, R002, etc.) and line numbers
3. **Risk Detection** - Ambiguity, Missing Detail, Security, Conflict, Performance, Availability
4. **Configurable Rules** - JSON-driven rules in `data/rules.json` with severities and enable switches
5. **Reporting** - Multi-format outputs: Markdown, CSV, JSON
6. **CLI Interface** - Report format selection and output path
7. **Testing** - Comprehensive unit and integration tests (31 passing)

### Project Structure

```
StressSpec/
├── main.py                        # CLI entry point
├── requirements.txt               # Dependencies
├── web_utils/                     # Web interface utilities
│   ├── run_web.py                 # Development server
│   ├── setup_web.py               # Web setup script
│   ├── WEB_SETUP.md               # Web setup guide
│   └── QUICK_START.md             # Web quick start
├── web/                           # Web application
│   ├── main.py                    # FastAPI web server
│   ├── static/                    # CSS, JS, images
│   └── templates/                 # HTML templates
├── src/
│   ├── file_loader.py             # File loading and processing
│   ├── requirement_parser.py      # Requirement parsing logic
│   ├── analyzer.py                # Runs detectors and aggregates risks
│   ├── models/
│   │   ├── requirement.py         # Requirement data model
│   │   └── risk.py                # Risk data model + severity
│   ├── detectors/
│   │   ├── base.py                # BaseRiskDetector + helpers
│   │   ├── ambiguity_detector.py
│   │   ├── missing_detail_detector.py
│   │   ├── security_detector.py
│   │   ├── conflict_detector.py
│   │   ├── performance_detector.py
│   │   └── availability_detector.py
│   ├── factories/
│   │   └── detector_factory.py    # Factory Method for detectors
│   └── reporting/
│       ├── base.py                # Reporter interface + types
│       ├── markdown_reporter.py   # MD writer
│       ├── csv_reporter.py        # CSV writer
│       └── json_reporter.py       # JSON writer
├── data/
│   ├── rules.json                 # Configurable rules & severities
│   └── sample_requirements.txt    # Sample data
└── tests/                         # Unit & integration tests (31)
    ├── test_requirement.py
    ├── test_file_loader.py
    ├── test_requirement_parser.py
    ├── test_integration.py
    ├── test_performance_detector.py
    └── test_availability_detector.py
```

## Usage

### CLI Usage

```bash
# Parse a requirements file and generate Markdown report
python main.py --file data/sample_requirements.txt --report-format md --verbose

# Generate CSV or JSON reports
python main.py --file data/sample_requirements.txt --report-format csv --output report.csv
python main.py --file data/sample_requirements.txt --report-format json --output report.json
```

### Web Interface Usage

```bash
# Start the web development server
python web_utils/run_web.py

# Then visit http://127.0.0.1:8000 in your browser
```

For detailed web setup instructions, see `web_utils/WEB_SETUP.md` and `web_utils/QUICK_START.md`.

### Supported File Formats

- `.txt` files with one requirement per line
- `.md` files with requirements in bullet points or numbered lists

### Features

- **Automatic ID Assignment**: Each requirement gets a unique ID (R001, R002, etc.)
- **Line Number Tracking**: Maintains traceability to original file location
- **Configurable Risk Detection**: 6 detector categories enabled via JSON rules
- **Multi-format Reporting**: Markdown, CSV, JSON outputs
- **Comment Filtering**: Automatically ignores lines starting with `#` or `//`
- **Whitespace Handling**: Strips leading/trailing whitespace and filters empty lines
- **Error Handling**: Comprehensive error messages for common issues

## Design Principles Applied

### SOLID Principles

- **Single Responsibility Principle**: Each class has one clear responsibility
  - `FileLoader`: Handles file operations only
  - `RequirementParser`: Handles parsing logic only
  - `Requirement`: Represents requirement data only

### Design Patterns

- **Data Classes**: Used `@dataclass` for clean, immutable data structures
- **Factory Method**: Detector creation via `RiskDetectorFactory`
- **Strategy + Template Method**: Extensible detection algorithms with shared workflow

## Testing

Run the project tests:

```bash
python -m pytest -q tests
```

All 31 tests pass, covering:
- Requirement and risk models
- File loading and parsing
- Detectors (ambiguity, missing detail, security, conflict, performance, availability)
- Reporting integration and end-to-end pipeline

## Sample Output

```
Successfully parsed 10 requirements:
--------------------------------------------------
R001: Line 1
  The system shall allow users to login with email and password

R002: Line 2
  The system shall display user dashboard after successful login

R003: Line 3
  The system shall support password reset functionality
...
```

## Documentation

- See `docs/HOWTO.md` for a step-by-step guide and examples.

## Requirements

- Python 3.10+
- pytest (for testing)

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest tests/ -v`
4. Use the tool: `python main.py --file your_requirements.txt`
