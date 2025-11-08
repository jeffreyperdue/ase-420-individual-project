from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.reporting.base import Reporter, ReportData


class JsonReporter(Reporter):
    """
    Writes a JSON report.

    BEGINNER NOTES:
    - JSON is a structured format that other programs can easily parse.
    - We include the source file name and an array of requirements,
      where each has its list of risks.
    """
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        output_path = Path(output) if output else Path("report.json")
        
        # Convert top 5 riskiest to JSON-serializable format
        top_5_data = None
        if data.top_5_riskiest:
            top_5_data = []
            for item in data.top_5_riskiest:
                req = item['requirement']
                top_5_data.append({
                    "requirement_id": req.id,
                    "line_number": req.line_number,
                    "text": req.text,
                    "total_score": item['total_score'],
                    "avg_severity": item['avg_severity'],
                    "risk_count": item['risk_count'],
                    "risks": [r.to_dict() for r in item['risks']]
                })
        
        payload = {
            "source_file": data.source_file,
            "requirements": [
                {
                    "id": req.id,
                    "line_number": req.line_number,
                    "text": req.text,
                    "risks": [r.to_dict() for r in data.risks_by_requirement.get(req.id, [])],
                }
                for req in data.requirements
            ],
        }
        
        # Add top 5 riskiest if available (Week 8 feature)
        if top_5_data:
            payload["top_5_riskiest"] = top_5_data
        
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path


