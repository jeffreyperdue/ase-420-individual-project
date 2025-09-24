## How to Run StressSpec

### Prerequisites
- Python 3.10+
- pip installed

### Install dependencies
```bash
pip install -r requirements.txt
```

### Basic usage
```bash
python main.py --file data/sample_requirements.txt --verbose
```

### Generate reports
- Markdown (default)
```bash
python main.py --file data/sample_requirements.txt --report-format md --output report.md --verbose
```

- CSV
```bash
python main.py --file data/sample_requirements.txt --report-format csv --output report.csv
```

- JSON
```bash
python main.py --file data/sample_requirements.txt --report-format json --output report.json
```

### Viewing results on Windows (PowerShell)
```powershell
type report.md
type report.csv
type report.json
```

### CLI options

| Option | Description | Default |
|---|---|---|
| `--file, -f` | Path to a .txt or .md requirements file | required |
| `--verbose, -v` | Print progress messages to console | off |
| `--report-format` | Output format: `md`, `csv`, `json` | `md` |
| `--output` | Output file path | `report.<fmt>` |

### What the tool does
1. Loads and cleans your requirements file.
2. Parses each line into a structured requirement with an ID (R001, R002, ...).
3. Runs enabled risk detectors (ambiguity, missing detail, security, conflict).
4. Writes a report with all detected risks per requirement.

### Example (Markdown) output snippet
```md
## Summary
- Requirements: 10
- Risks: 32

### R001 (Line 1)
The system shall allow users to login with email and password
- MEDIUM: Imprecise quantifier 'all' found — evidence: `all`
- HIGH: Action 'allow' lacks sufficient detail — evidence: `allow`
```

### Example (CSV) first rows
```csv
requirement_id,line_number,requirement_text,risk_id,category,severity,severity_name,description,evidence,suggestion
R001,1,"The system shall allow users to login with email and password",R001-AMB-001,ambiguity,2,MEDIUM,"Vague term 'should' found",should,
```

### Example (JSON) structure
```json
{
  "source_file": "data/sample_requirements.txt",
  "requirements": [
    {
      "id": "R001",
      "line_number": 1,
      "text": "The system shall allow users to login...",
      "risks": [{
        "id": "R001-AMB-001",
        "category": "ambiguity",
        "severity": 2,
        "severity_name": "MEDIUM",
        "description": "Vague term 'should' found",
        "evidence": "should"
      }]
    }
  ]
}
```

### Tips
- Keep each requirement on its own line or bullet.
- Comments starting with `#` or `//` are ignored.
- If no `--output` is provided, files are created as `report.md`, `report.csv`, or `report.json` in the project root.

### Troubleshooting
- File not found: ensure the `--file` path exists and uses `.txt` or `.md`.
- Empty file: the loader removes empty and comment lines; ensure content remains.
- Encoding: files are read as UTF-8, falling back to latin-1 if needed.


