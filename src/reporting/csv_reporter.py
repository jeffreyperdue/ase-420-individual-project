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
        
        # Calculate risk scores for all requirements to include in CSV
        from src.scoring import calculate_risk_scores
        risk_scores = calculate_risk_scores(data.requirements, data.risks_by_requirement)
        
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Add score columns (Week 8 feature)
            writer.writerow([
                "requirement_id",
                "line_number",
                "requirement_text",
                "total_score",
                "avg_severity",
                "risk_count",
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
                score_data = risk_scores.get(req.id, {'total_score': 0, 'avg_severity': 0.0, 'risk_count': 0})
                total_score = score_data['total_score']
                avg_severity = score_data['avg_severity']
                risk_count = score_data['risk_count']
                
                if not risks:
                    writer.writerow([
                        req.id,
                        req.line_number,
                        req.text,
                        total_score,
                        avg_severity,
                        risk_count,
                        "", "", "", "", "", "", ""
                    ]) 
                else:
                    for r in risks:
                        writer.writerow([
                            req.id,
                            req.line_number,
                            req.text,
                            total_score,
                            avg_severity,
                            risk_count,
                            r.id,
                            r.category.value,
                            r.severity.value,
                            r.severity.name,
                            r.description,
                            r.evidence,
                            r.suggestion or "",
                        ])
        
        # Optionally write a separate top 5 summary CSV if available
        if data.top_5_riskiest:
            summary_path = output_path.parent / f"{output_path.stem}_top5.csv"
            with summary_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "rank",
                    "requirement_id",
                    "line_number",
                    "requirement_text",
                    "total_score",
                    "avg_severity",
                    "risk_count",
                ])
                for idx, item in enumerate(data.top_5_riskiest, 1):
                    req = item['requirement']
                    writer.writerow([
                        idx,
                        req.id,
                        req.line_number,
                        req.text,
                        item['total_score'],
                        item['avg_severity'],
                        item['risk_count'],
                    ])
        
        return output_path


