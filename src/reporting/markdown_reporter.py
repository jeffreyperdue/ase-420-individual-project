from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from src.reporting.base import Reporter, ReportData


class MarkdownReporter(Reporter):
    """
    Writes a Markdown (.md) report.

    BEGINNER NOTES:
    - Markdown is a simple format that's easy for humans to read.
    - We build the file as a list of lines and then join them.
    - Each requirement gets a small section listing its risks.
    """
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        output_path = Path(output) if output else Path("report.md")
        lines = []
        lines.append(f"# StressSpec Report\n")
        lines.append(f"Generated: {datetime.utcnow().isoformat()}Z\n")
        lines.append("")
        lines.append(f"Source file: `{data.source_file}`\n")
        lines.append("")
        total_risks = sum(len(v) for v in data.risks_by_requirement.values())
        lines.append(f"## Summary\n")
        lines.append(f"- Requirements: {len(data.requirements)}\n")
        lines.append(f"- Risks: {total_risks}\n")
        lines.append("")

        for req in data.requirements:
            lines.append(f"### {req.id} (Line {req.line_number})\n")
            lines.append(f"{req.text}\n")
            risks = data.risks_by_requirement.get(req.id, [])
            if risks:
                for r in risks:
                    lines.append(f"- {r.severity.name}: {r.description} — evidence: `{r.evidence}`\n")
            else:
                lines.append("- No risks detected\n")
            lines.append("")

        # Join all lines and write to disk as UTF-8
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path


