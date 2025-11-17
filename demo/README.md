# StressSpec Demo Materials

This folder contains sample reports and demonstration materials for Sprint 2.

## Files Included

### Sample Reports

All reports were generated using `data/sample_requirements.txt` and demonstrate the complete Sprint 2 feature set:

1. **demo_report.html** - Standalone HTML report
   - Professional styling with embedded CSS
   - Color-coded severity badges
   - Executive summary with statistics
   - Top 5 Riskiest Requirements section
   - Print-friendly design

2. **demo_report.md** - Markdown report
   - Detailed formatting
   - Top 5 Riskiest Requirements section
   - Complete risk breakdown

3. **demo_report.csv** - CSV report
   - Score columns (total_score, avg_severity, risk_count)
   - Detailed requirements list
   - Compatible with spreadsheet applications

4. **demo_report.json** - JSON report
   - Structured data format
   - `top_5_riskiest` array included
   - Machine-readable format

### Documentation

- **SPRINT2_SUMMARY.md** - Complete Sprint 2 achievements summary
- **README.md** (this file) - Demo folder overview

## How to Generate Reports

You can generate your own reports using the CLI:

```bash
# Generate HTML report
python main.py --file data/sample_requirements.txt --report-format html --output demo/my_report.html

# Generate Markdown report
python main.py --file data/sample_requirements.txt --report-format md --output demo/my_report.md

# Generate CSV report
python main.py --file data/sample_requirements.txt --report-format csv --output demo/my_report.csv

# Generate JSON report
python main.py --file data/sample_requirements.txt --report-format json --output demo/my_report.json
```

## Features Demonstrated

### 8-Category Risk Detection
- All 8 detectors active (Ambiguity, Missing Detail, Security, Conflict, Performance, Availability, Traceability, Scope)

### Top 5 Riskiest Requirements
- Automatic prioritization based on combined risk scores
- Available in all 4 report formats

### Multi-Format Reporting
- Professional HTML reports for stakeholder presentations
- Detailed Markdown for technical documentation
- CSV for spreadsheet analysis
- JSON for programmatic processing

---

**Note:** These demo files are included for Sprint 2 review and presentation purposes.

