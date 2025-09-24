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
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path


