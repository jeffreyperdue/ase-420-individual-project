# StressSpec - Requirements Stress Tester

A Python-based tool for analyzing requirement documents and detecting potential risks and issues before development begins.

## Project Overview

StressSpec acts as a "wind tunnel" for requirements, helping project managers, business analysts, and development teams identify hidden risks in requirement documents early in the development process.

## Current Implementation Status ✅

### Completed Features

1. **Input Ingestion** - Accepts .txt and .md files with one requirement per line
2. **Requirement Parsing & Labeling** - Assigns unique IDs (R001, R002, etc.) and line numbers
3. **Risk Detection** - 8 categories: Ambiguity, Missing Detail, Security, Conflict, Performance, Availability, Traceability, Scope
4. **Configurable Rules** - JSON-driven rules in `data/rules.json` with severities and enable switches
5. **Risk Scoring & Analytics** - Combined risk scores per requirement with "Top 5 Riskiest Requirements" analysis
6. **Reporting** - Multi-format outputs: Markdown, CSV, JSON (all include top 5 riskiest)
7. **CLI Interface** - Report format selection and output path
8. **Testing** - Comprehensive unit and integration tests

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
│   ├── scoring.py                 # Risk scoring and top 5 analysis (Week 8)
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
│   │   ├── availability_detector.py
│   │   ├── traceability_detector.py
│   │   └── scope_detector.py
│   ├── factories/
│   │   └── detector_factory.py    # Factory Method for detectors
│   └── reporting/
│       ├── base.py                # Reporter interface + types
│       ├── markdown_reporter.py   # MD writer
│       ├── csv_reporter.py        # CSV writer
│       ├── json_reporter.py       # JSON writer
│       ├── html_reporter.py      # HTML writer (Week 9)
│       └── templates/
│           └── report_template.html  # HTML report template
├── data/
│   ├── rules.json                 # Configurable rules & severities
│   └── sample_requirements.txt    # Sample data
└── tests/                         # Unit & integration tests
    ├── test_requirement.py
    ├── test_file_loader.py
    ├── test_requirement_parser.py
    ├── test_integration.py
    ├── test_performance_detector.py
    ├── test_availability_detector.py
    └── test_scoring.py            # Risk scoring tests (Week 8)
```

## Usage

### CLI Usage

```bash
# Parse a requirements file and generate Markdown report
python main.py --file data/sample_requirements.txt --report-format md --verbose

# Generate CSV, JSON, or HTML reports
python main.py --file data/sample_requirements.txt --report-format csv --output report.csv
python main.py --file data/sample_requirements.txt --report-format json --output report.json
python main.py --file data/sample_requirements.txt --report-format html --output report.html
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
- **Configurable Risk Detection**: 8 detector categories enabled via JSON rules
- **Risk Scoring**: Combined risk scores per requirement (sum of severity values)
- **Top 5 Riskiest Requirements**: Automatically identifies and highlights the most critical requirements
- **Multi-format Reporting**: Markdown, CSV, JSON, HTML outputs (all include top 5 riskiest)
- **Comment Filtering**: Automatically ignores lines starting with `#` or `//`
- **Whitespace Handling**: Strips leading/trailing whitespace and filters empty lines
- **Error Handling**: Comprehensive error messages for common issues

## Risk Scoring & Top 5 Analysis

StressSpec includes an advanced risk scoring system that calculates combined risk scores for each requirement and identifies the top 5 riskiest requirements for prioritization.

### Scoring Algorithm

**Total Risk Score**: The sum of all risk severity values for a requirement.
- Low = 1 point
- Medium = 2 points
- High = 3 points
- Critical = 4 points
- Blocker = 5 points

**Ranking Logic**: Requirements are ranked by:
1. Total score (descending - higher is riskier)
2. Risk count (descending - more risks is riskier)
3. Requirement ID (ascending - for consistent ordering in ties)

**Example**:
- Requirement R001 has 2 risks: HIGH (3) + MEDIUM (2) = Total Score: 5
- Requirement R002 has 1 risk: CRITICAL (4) = Total Score: 4
- R001 would be ranked higher than R002 due to higher total score

### Top 5 Riskiest Requirements

The "Top 5 Riskiest Requirements" feature automatically identifies the requirements with the highest combined risk scores. This helps teams:

- **Prioritize Review**: Focus on the most critical requirements first
- **Risk Management**: Identify which requirements need immediate attention
- **Resource Allocation**: Allocate more time and resources to high-risk items

### Report Formats

**Markdown Reports**: Include a dedicated "Top 5 Riskiest Requirements" section with:
- Requirement ID and score
- Risk count and average severity
- Detailed breakdown of all risks

**JSON Reports**: Include a `top_5_riskiest` array with complete requirement and risk details

**CSV Reports**: Include score columns (`total_score`, `avg_severity`, `risk_count`) in the main CSV and generate a separate `*_top5.csv` file with the top 5 summary

**HTML Reports**: Standalone, self-contained HTML reports with embedded CSS styling. Include:
- Visual executive summary with statistics
- Highlighted "Top 5 Riskiest Requirements" section with color-coded severity badges
- Detailed requirements list with risk indicators
- Print-friendly design for documentation

### Example Output

```markdown
## Top 5 Riskiest Requirements

These requirements have the highest combined risk scores and should be prioritized for review.

### 1. R001 - Score: 7 (Risk Count: 2)
**Line 1:** The system shall allow users to login with password

**Risk Details:**
- Total Score: 7
- Average Severity: 3.5
- Risk Count: 2

**Detected Risks:**
- **HIGH** (security): Missing authentication requirement
  - Evidence: `password`
- **CRITICAL** (security): Missing encryption specification
  - Evidence: `login`
```

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

Tests cover:
- Requirement and risk models
- File loading and parsing
- All 8 risk detectors (ambiguity, missing detail, security, conflict, performance, availability, traceability, scope)
- Risk scoring and top 5 analysis (Week 8)
- Reporting integration and end-to-end pipeline
- Multi-format report generation (Markdown, CSV, JSON)

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

- See `web_utils/WEB_SETUP.md` for detailed web setup instructions.
- See `web_utils/QUICK_START.md` for quick start guide.

## Requirements

- Python 3.10+
- pytest (for testing)

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest tests/ -v`
4. Use the tool: `python main.py --file your_requirements.txt`
