from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.reporting.base import Reporter, ReportData


class HtmlReporter(Reporter):
    """
    Writes an HTML (.html) report using Jinja2 templates.

    BEGINNER NOTES:
    - HTML is a web format that can be viewed in browsers.
    - We use Jinja2 templates to separate the structure from the data.
    - The template includes inline CSS for a self-contained, standalone report.
    - Each requirement gets a section listing its risks with visual severity indicators.
    """
    
    def __init__(self):
        """Initialize the HTML reporter with Jinja2 environment."""
        # Set up Jinja2 environment to load templates from the reporting directory
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def write(self, data: ReportData, output: Optional[str] = None) -> Path:
        """
        Generate an HTML report from the provided data.
        
        Args:
            data: ReportData containing requirements, risks, and metadata
            output: Optional output file path (defaults to report.html)
            
        Returns:
            Path to the generated HTML file
        """
        output_path = Path(output) if output else Path("report.html")
        
        # Calculate summary statistics
        total_risks = sum(len(v) for v in data.risks_by_requirement.values())
        
        # Calculate risk category breakdown
        risk_categories = {}
        for req_id, risks in data.risks_by_requirement.items():
            for risk in risks:
                category = risk.category.value
                if category not in risk_categories:
                    risk_categories[category] = 0
                risk_categories[category] += 1
        
        # Prepare template context
        context = {
            "title": "StressSpec Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_file": data.source_file,
            "total_requirements": len(data.requirements),
            "total_risks": total_risks,
            "risk_categories": risk_categories,
            "top_5_riskiest": data.top_5_riskiest,
            "requirements": data.requirements,
            "risks_by_requirement": data.risks_by_requirement,
        }
        
        # Load and render template
        template = self.env.get_template("report_template.html")
        html_content = template.render(**context)
        
        # Write to file
        output_path.write_text(html_content, encoding="utf-8")
        return output_path

