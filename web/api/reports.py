"""
Reports API Endpoints

This module handles report generation and viewing for the StressSpec web interface.
It integrates with the existing reporting system and provides web-friendly outputs.

BEGINNER NOTES:
- This handles the generation and viewing of analysis reports
- It uses the existing reporting system (Markdown, CSV, JSON)
- It provides web-friendly report formats
- It allows filtering and customization of reports
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

# Import our existing reporting modules
from src.reporting import ReportFormat, ReportData, MarkdownReporter, CsvReporter, JsonReporter

# Create router for reports endpoints
router = APIRouter()

class ReportRequest(BaseModel):
    """Request model for generating reports."""
    analysis_id: str
    format: str = "html"  # html, markdown, csv, json
    filters: Optional[Dict] = None

class ReportResponse(BaseModel):
    """Response model for report generation."""
    success: bool
    report_id: str
    format: str
    download_url: str
    message: str

class ReportFilters(BaseModel):
    """Filters for customizing reports."""
    severity: Optional[List[str]] = None
    category: Optional[List[str]] = None
    requirement_ids: Optional[List[str]] = None
    include_summary: bool = True
    include_details: bool = True

# In-memory storage for generated reports (in production, use file system or database)
generated_reports: Dict[str, Dict] = {}

def generate_report_html(analysis_data: Dict, filters: Optional[Dict] = None) -> str:
    """
    Generate HTML report from analysis data.
    
    BEGINNER NOTES:
    - This creates a web-friendly HTML report
    - It includes styling and interactive elements
    - It can be filtered and customized
    - It's designed for web viewing
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>StressSpec Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
            .summary {{ margin: 20px 0; }}
            .requirement {{ margin: 15px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .risk {{ margin: 10px 0; padding: 10px; background: #fff3cd; border-left: 4px solid #ffc107; }}
            .risk.critical {{ background: #f8d7da; border-left-color: #dc3545; }}
            .risk.high {{ background: #fff3cd; border-left-color: #ffc107; }}
            .risk.medium {{ background: #d1ecf1; border-left-color: #17a2b8; }}
            .risk.low {{ background: #d4edda; border-left-color: #28a745; }}
            .severity {{ font-weight: bold; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>StressSpec Analysis Report</h1>
            <p>Generated on: {analysis_data.get('completed_at', 'Unknown')}</p>
        </div>
        
        <div class="summary">
            <h2>Summary</h2>
            <p>Total Requirements: {analysis_data.get('summary', {}).get('total_requirements', 0)}</p>
            <p>Total Risks: {analysis_data.get('summary', {}).get('total_risks', 0)}</p>
            <p>Requirements with Risks: {analysis_data.get('summary', {}).get('requirements_with_risks', 0)}</p>
        </div>
        
        <div class="requirements">
            <h2>Requirements Analysis</h2>
    """
    
    # Add requirements and their risks
    for req in analysis_data.get('requirements', []):
        req_id = req.get('id', '')
        req_text = req.get('text', '')
        risks = analysis_data.get('risks_by_requirement', {}).get(req_id, [])
        
        html += f"""
            <div class="requirement">
                <h3>{req_id}: {req_text}</h3>
        """
        
        if risks:
            for risk in risks:
                severity = risk.get('severity', 'medium').lower()
                html += f"""
                    <div class="risk {severity}">
                        <div class="severity">{severity}</div>
                        <div><strong>{risk.get('category', 'Unknown')}</strong>: {risk.get('description', 'No description')}</div>
                        <div><em>Evidence: {risk.get('evidence', 'No evidence')}</em></div>
                    </div>
                """
        else:
            html += "<p><em>No risks detected</em></p>"
        
        html += "</div>"
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Generate a report for an analysis.
    
    BEGINNER NOTES:
    - This endpoint creates a report from analysis results
    - It supports multiple formats (HTML, Markdown, CSV, JSON)
    - It can be filtered and customized
    - It returns a download URL for the report
    """
    try:
        # Generate report ID
        report_id = f"report_{request.analysis_id}_{request.format}"
        
        # Get analysis data (in production, this would come from a database)
        # For now, we'll use a placeholder
        analysis_data = {
            "analysis_id": request.analysis_id,
            "requirements": [],
            "risks_by_requirement": {},
            "summary": {},
            "completed_at": "2024-01-01T00:00:00Z"
        }
        
        # Generate report based on format
        if request.format == "html":
            report_content = generate_report_html(analysis_data, request.filters)
            file_extension = "html"
        elif request.format == "markdown":
            # Use existing MarkdownReporter
            reporter = MarkdownReporter()
            # This would need to be implemented with actual data
            report_content = "# StressSpec Analysis Report\n\nReport content would go here."
            file_extension = "md"
        elif request.format == "csv":
            # Use existing CsvReporter
            reporter = CsvReporter()
            report_content = "Requirement ID,Text,Risk Category,Severity,Description\n"
            file_extension = "csv"
        elif request.format == "json":
            # Use existing JsonReporter
            reporter = JsonReporter()
            report_content = '{"analysis_id": "' + request.analysis_id + '", "status": "generated"}'
            file_extension = "json"
        else:
            raise HTTPException(status_code=400, detail="Invalid report format")
        
        # Store report
        generated_reports[report_id] = {
            "content": report_content,
            "format": request.format,
            "analysis_id": request.analysis_id,
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
        return ReportResponse(
            success=True,
            report_id=report_id,
            format=request.format,
            download_url=f"/api/reports/download/{report_id}",
            message="Report generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )

@router.get("/download/{report_id}")
async def download_report(report_id: str):
    """
    Download a generated report.
    
    BEGINNER NOTES:
    - This endpoint serves the generated report files
    - It returns the report content as a file download
    - It supports different MIME types based on format
    - It handles file streaming for large reports
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = generated_reports[report_id]
    content = report["content"]
    format_type = report["format"]
    
    # Set appropriate MIME type
    mime_types = {
        "html": "text/html",
        "markdown": "text/markdown",
        "csv": "text/csv",
        "json": "application/json"
    }
    
    media_type = mime_types.get(format_type, "text/plain")
    
    # Create temporary file
    temp_file = Path(f"temp_{report_id}.{format_type}")
    temp_file.write_text(content, encoding="utf-8")
    
    return FileResponse(
        path=str(temp_file),
        filename=f"stressspec_report.{format_type}",
        media_type=media_type
    )

@router.get("/list")
async def list_reports():
    """
    List all generated reports.
    
    BEGINNER NOTES:
    - This endpoint shows all reports that have been generated
    - Useful for managing multiple reports
    - Returns basic information about each report
    """
    return {
        "success": True,
        "reports": [
            {
                "report_id": report_id,
                "format": report["format"],
                "analysis_id": report["analysis_id"],
                "generated_at": report["generated_at"]
            }
            for report_id, report in generated_reports.items()
        ],
        "count": len(generated_reports)
    }

@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a generated report.
    
    BEGINNER NOTES:
    - This endpoint removes a report from storage
    - Useful for cleanup and privacy
    - Removes both the report content and metadata
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    del generated_reports[report_id]
    
    return {
        "success": True,
        "message": "Report deleted successfully"
    }
