from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from src.reporting.base import Reporter, ReportData


class CsvReporter(Reporter):
    """
    Writes a CSV (comma-separated values) report.

    BEGINNER NOTES:
    - CSV is great for spreadsheets (Excel, Google Sheets).
    - Each row represents one risk. If a requirement has no risks,
      we still write a row so every requirement appears in the file.
    """
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        output_path = Path(output) if output else Path("report.csv")
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "requirement_id",
                "line_number",
                "requirement_text",
                "risk_id",
                "category",
                "severity",
                "severity_name",
                "description",
                "evidence",
                "suggestion",
            ])
            for req in data.requirements:
                risks = data.risks_by_requirement.get(req.id, [])
                if not risks:
                    writer.writerow([req.id, req.line_number, req.text, "", "", "", "", "", "", ""]) 
                else:
                    for r in risks:
                        writer.writerow([
                            req.id,
                            req.line_number,
                            req.text,
                            r.id,
                            r.category.value,
                            r.severity.value,
                            r.severity.name,
                            r.description,
                            r.evidence,
                            r.suggestion or "",
                        ])
        return output_path


