# StressSpec - Requirements Stress Tester

A Python-based tool for analyzing requirement documents and detecting potential risks and issues before development begins.

## Project Overview

StressSpec acts as a "wind tunnel" for requirements, helping project managers, business analysts, and development teams identify hidden risks in requirement documents early in the development process.

## Week 1 Implementation Status ✅

### Completed Features

1. **Input Ingestion** - Accepts .txt and .md files with one requirement per line
2. **Requirement Parsing & Labeling** - Assigns unique IDs (R001, R002, etc.) and line numbers
3. **Error Handling** - Comprehensive error handling for missing files, invalid extensions, and empty files
4. **CLI Interface** - Command-line interface with argument parsing
5. **Unit Testing** - Complete test suite with 24 passing tests

### Project Structure

```
StressSpec/
├── main.py                 # Main entry point with CLI
├── requirements.txt        # Python dependencies
├── src/
│   ├── __init__.py
│   ├── file_loader.py      # File loading and processing
│   ├── requirement_parser.py # Requirement parsing logic
│   └── models/
│       ├── __init__.py
│       └── requirement.py  # Requirement data model
├── data/
│   ├── sample_requirements.txt
│   └── sample_requirements.md
└── tests/
    ├── __init__.py
    ├── test_requirement.py
    ├── test_file_loader.py
    └── test_requirement_parser.py
```

## Usage

### Basic Usage

```bash
# Parse a requirements file
python main.py --file data/sample_requirements.txt

# Verbose output
python main.py --file data/sample_requirements.md --verbose
```

### Supported File Formats

- `.txt` files with one requirement per line
- `.md` files with requirements in bullet points or numbered lists

### Features

- **Automatic ID Assignment**: Each requirement gets a unique ID (R001, R002, etc.)
- **Line Number Tracking**: Maintains traceability to original file location
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
- **Factory Pattern**: Parser creates Requirement objects with consistent IDs
- **Strategy Pattern**: Extensible file loading for different formats

## Testing

Run the complete test suite:

```bash
python -m pytest tests/ -v
```

All 24 tests pass, covering:
- Requirement model validation
- File loading with various scenarios
- Parser functionality and ID generation
- Error handling for edge cases

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

## Next Steps (Week 2)

- Risk detection modules (ambiguity, availability, performance, security)
- Configurable rules system (rules.json)
- Basic severity scoring
- Multi-format reporting (Markdown, CSV, JSON)

## Requirements

- Python 3.7+
- pytest (for testing)

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest tests/ -v`
4. Use the tool: `python main.py --file your_requirements.txt`
