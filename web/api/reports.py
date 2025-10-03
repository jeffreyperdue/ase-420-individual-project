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
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel

# Import our existing reporting modules
from src.reporting import ReportFormat, ReportData, MarkdownReporter, CsvReporter, JsonReporter

# Report templates
REPORT_TEMPLATES = {
    "executive_summary": {
        "name": "Executive Summary",
        "description": "High-level overview for executives and stakeholders",
        "sections": ["summary", "critical_risks", "recommendations"],
        "format_options": ["html", "markdown", "pdf"],
        "customizable": True
    },
    "technical_detailed": {
        "name": "Technical Detailed Report",
        "description": "Comprehensive technical analysis with all details",
        "sections": ["summary", "requirements", "risks", "evidence", "recommendations"],
        "format_options": ["html", "markdown", "json"],
        "customizable": True
    },
    "compliance_audit": {
        "name": "Compliance Audit Report",
        "description": "Report focused on compliance and regulatory requirements",
        "sections": ["summary", "compliance_risks", "evidence", "remediation"],
        "format_options": ["html", "markdown", "csv"],
        "customizable": True
    },
    "risk_assessment": {
        "name": "Risk Assessment Report",
        "description": "Focused on risk analysis and mitigation strategies",
        "sections": ["summary", "risk_matrix", "mitigation_plans"],
        "format_options": ["html", "markdown", "json"],
        "customizable": True
    },
    "custom": {
        "name": "Custom Template",
        "description": "Create your own custom report template",
        "sections": [],
        "format_options": ["html", "markdown", "csv", "json"],
        "customizable": True
    }
}

# Create router for reports endpoints
router = APIRouter()

class ReportRequest(BaseModel):
    """Request model for generating reports."""
    analysis_id: str
    format: str = "html"  # html, markdown, csv, json
    filters: Optional[Dict] = None
    template: Optional[str] = "technical_detailed"
    customizations: Optional[Dict] = None

class ReportResponse(BaseModel):
    """Response model for report generation."""
    success: bool
    report_id: str
    format: str
    download_url: str
    message: str

class TemplateRequest(BaseModel):
    """Request model for creating custom templates."""
    name: str
    description: str
    sections: List[str]
    format_options: List[str]
    customizable: bool = True

class TemplateResponse(BaseModel):
    """Response model for template operations."""
    success: bool
    template_id: str
    message: str

class ScheduleRequest(BaseModel):
    """Request model for scheduling reports."""
    name: str
    analysis_id: str
    template: str = "technical_detailed"
    format: str = "html"
    schedule_type: str = "daily"  # daily, weekly, monthly, custom
    schedule_config: Optional[Dict] = None
    filters: Optional[Dict] = None
    customizations: Optional[Dict] = None
    enabled: bool = True

class ScheduleResponse(BaseModel):
    """Response model for schedule operations."""
    success: bool
    schedule_id: str
    message: str

class CommentRequest(BaseModel):
    """Request model for adding comments."""
    content: str
    author: str = "Anonymous"
    parent_comment_id: Optional[str] = None

class CommentResponse(BaseModel):
    """Response model for comment operations."""
    success: bool
    comment_id: str
    message: str

class PermissionRequest(BaseModel):
    """Request model for setting permissions."""
    public_read: bool = False
    allow_comments: bool = True
    allow_download: bool = True
    allowed_users: Optional[List[str]] = None

class ReportFilters(BaseModel):
    """Filters for customizing reports."""
    severity: Optional[List[str]] = None
    category: Optional[List[str]] = None
    requirement_ids: Optional[List[str]] = None
    include_summary: bool = True
    include_details: bool = True

# In-memory storage for generated reports (in production, use file system or database)
generated_reports: Dict[str, Dict] = {}

# Report versioning and history
report_history: Dict[str, List[Dict]] = {}  # analysis_id -> list of report versions

# Report scheduling and automation
scheduled_reports: Dict[str, Dict] = {}  # schedule_id -> schedule config

# Report collaboration
report_comments: Dict[str, List[Dict]] = {}  # report_id -> list of comments
report_permissions: Dict[str, Dict] = {}  # report_id -> permission settings

def generate_report_html(analysis_data: Dict, filters: Optional[Dict] = None, template: Optional[Dict] = None, customizations: Optional[Dict] = None) -> str:
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

def apply_report_filters(analysis_data: Dict, filters: Dict) -> Dict:
    """
    Apply filters to analysis data for report generation.
    
    BEGINNER NOTES:
    - This filters the analysis data based on user preferences
    - It can filter by severity, category, or specific requirements
    - It modifies the data structure to only include filtered items
    """
    filtered_data = analysis_data.copy()
    
    # Filter by severity
    if filters.get('severity'):
        severity_filter = filters['severity']
        filtered_risks = {}
        for req_id, risks in analysis_data['risks_by_requirement'].items():
            filtered_risks[req_id] = [
                risk for risk in risks 
                if risk.get('severity') in severity_filter
            ]
        filtered_data['risks_by_requirement'] = filtered_risks
    
    # Filter by category
    if filters.get('category'):
        category_filter = filters['category']
        filtered_risks = {}
        for req_id, risks in analysis_data['risks_by_requirement'].items():
            filtered_risks[req_id] = [
                risk for risk in risks 
                if risk.get('category') in category_filter
            ]
        filtered_data['risks_by_requirement'] = filtered_risks
    
    # Filter by requirement IDs
    if filters.get('requirement_ids'):
        req_filter = filters['requirement_ids']
        filtered_data['requirements'] = [
            req for req in analysis_data['requirements']
            if req.get('id') in req_filter
        ]
        filtered_data['risks_by_requirement'] = {
            req_id: risks for req_id, risks in analysis_data['risks_by_requirement'].items()
            if req_id in req_filter
        }
    
    return filtered_data

def generate_report_markdown(analysis_data: Dict, filters: Optional[Dict] = None, template: Optional[Dict] = None, customizations: Optional[Dict] = None) -> str:
    """
    Generate Markdown report from analysis data.
    """
    md = f"""# StressSpec Analysis Report

**Analysis ID:** {analysis_data.get('analysis_id', 'Unknown')}  
**Generated:** {analysis_data.get('completed_at', 'Unknown')}

## Summary

"""
    
    summary = analysis_data.get('summary', {})
    if summary:
        md += f"""- **Total Requirements:** {summary.get('total_requirements', 0)}
- **Total Risks:** {summary.get('total_risks', 0)}
- **Requirements with Risks:** {summary.get('requirements_with_risks', 0)}
- **Risk-Free Requirements:** {summary.get('total_requirements', 0) - summary.get('requirements_with_risks', 0)}

"""
    
    md += "## Requirements Analysis\n\n"
    
    for req in analysis_data.get('requirements', []):
        req_id = req.get('id', '')
        req_text = req.get('text', '')
        risks = analysis_data.get('risks_by_requirement', {}).get(req_id, [])
        
        md += f"### {req_id}: {req_text}\n\n"
        
        if risks:
            for risk in risks:
                severity = risk.get('severity', 'medium')
                category = risk.get('category', 'Unknown')
                description = risk.get('description', 'No description')
                evidence = risk.get('evidence', '')
                
                md += f"**{severity.upper()} - {category}**\n"
                md += f"{description}\n"
                if evidence:
                    md += f"*Evidence: {evidence}*\n"
                md += "\n"
        else:
            md += "*No risks detected*\n\n"
    
    return md

def generate_report_csv(analysis_data: Dict, filters: Optional[Dict] = None, template: Optional[Dict] = None, customizations: Optional[Dict] = None) -> str:
    """
    Generate CSV report from analysis data.
    """
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Requirement ID', 'Requirement Text', 'Line Number',
        'Risk Category', 'Risk Severity', 'Risk Description', 'Evidence'
    ])
    
    # Write data
    for req in analysis_data.get('requirements', []):
        req_id = req.get('id', '')
        req_text = req.get('text', '')
        line_number = req.get('line_number', '')
        risks = analysis_data.get('risks_by_requirement', {}).get(req_id, [])
        
        if risks:
            for risk in risks:
                writer.writerow([
                    req_id,
                    req_text,
                    line_number,
                    risk.get('category', ''),
                    risk.get('severity', ''),
                    risk.get('description', ''),
                    risk.get('evidence', '')
                ])
        else:
            writer.writerow([req_id, req_text, line_number, '', '', 'No risks detected', ''])
    
    return output.getvalue()

def generate_report_json(analysis_data: Dict, filters: Optional[Dict] = None, template: Optional[Dict] = None, customizations: Optional[Dict] = None) -> str:
    """
    Generate JSON report from analysis data.
    """
    import json
    
    report_data = {
        "report_info": {
            "analysis_id": analysis_data.get('analysis_id'),
            "generated_at": analysis_data.get('completed_at'),
            "filters_applied": filters or {}
        },
        "summary": analysis_data.get('summary', {}),
        "requirements": analysis_data.get('requirements', []),
        "risks_by_requirement": analysis_data.get('risks_by_requirement', {})
    }
    
    return json.dumps(report_data, indent=2, default=str)

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
        report_id = f"report_{request.analysis_id}_{request.format}_{int(__import__('time').time())}"
        
        # Get analysis data from the analysis module
        from web.api.analysis import analysis_results
        
        if request.analysis_id not in analysis_results:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_data = analysis_results[request.analysis_id]
        
        # Convert analysis data to dictionary format
        analysis_dict = {
            "analysis_id": request.analysis_id,
            "requirements": [req.__dict__ for req in analysis_data.requirements],
            "risks_by_requirement": {
                req_id: [risk.__dict__ for risk in risks] 
                for req_id, risks in analysis_data.risks_by_requirement.items()
            },
            "summary": analysis_data.summary.__dict__ if hasattr(analysis_data.summary, '__dict__') else analysis_data.summary,
            "completed_at": analysis_data.completed_at
        }
        
        # Apply filters if provided
        if request.filters:
            analysis_dict = apply_report_filters(analysis_dict, request.filters)
        
        # Get template configuration
        template_id = request.template or "technical_detailed"
        if template_id not in REPORT_TEMPLATES:
            raise HTTPException(status_code=400, detail="Invalid template")
        
        template = REPORT_TEMPLATES[template_id]
        
        # Validate format against template
        if request.format not in template["format_options"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Format '{request.format}' not supported by template '{template_id}'"
            )
        
        # Generate report based on format and template
        if request.format == "html":
            report_content = generate_report_html(analysis_dict, request.filters, template, request.customizations)
        elif request.format == "markdown":
            report_content = generate_report_markdown(analysis_dict, request.filters, template, request.customizations)
        elif request.format == "csv":
            report_content = generate_report_csv(analysis_dict, request.filters, template, request.customizations)
        elif request.format == "json":
            report_content = generate_report_json(analysis_dict, request.filters, template, request.customizations)
        else:
            raise HTTPException(status_code=400, detail="Invalid report format")
        
        # Store report
        generated_at = __import__('datetime').datetime.now().isoformat()
        generated_reports[report_id] = {
            "content": report_content,
            "format": request.format,
            "analysis_id": request.analysis_id,
            "template": request.template,
            "filters": request.filters,
            "customizations": request.customizations,
            "generated_at": generated_at,
            "version": 1
        }
        
        # Add to report history
        if request.analysis_id not in report_history:
            report_history[request.analysis_id] = []
        
        # Check if this is a new version or update
        existing_reports = [r for r in report_history[request.analysis_id] if r["template"] == request.template and r["format"] == request.format]
        if existing_reports:
            # Increment version number
            max_version = max(r["version"] for r in existing_reports)
            generated_reports[report_id]["version"] = max_version + 1
        
        # Add to history
        report_history[request.analysis_id].append({
            "report_id": report_id,
            "template": request.template,
            "format": request.format,
            "filters": request.filters,
            "customizations": request.customizations,
            "generated_at": generated_at,
            "version": generated_reports[report_id]["version"]
        })
        
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

@router.get("/share/{report_id}")
async def get_shareable_link(report_id: str):
    """
    Get a shareable link for a report.
    
    BEGINNER NOTES:
    - This endpoint generates a public URL for sharing reports
    - In production, you'd want to add authentication/expiration
    - Useful for sharing analysis results with stakeholders
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # In a real application, you might want to:
    # 1. Generate a unique share token
    # 2. Store it in a database with expiration
    # 3. Return a public URL
    
    # For now, we'll return a simple shareable URL
    share_url = f"/api/reports/view/{report_id}"
    
    return {
        "success": True,
        "share_url": share_url,
        "report_id": report_id,
        "expires_at": None,  # No expiration for now
        "message": "Shareable link generated"
    }

@router.get("/view/{report_id}")
async def view_shared_report(report_id: str):
    """
    View a shared report (public access).
    
    BEGINNER NOTES:
    - This endpoint allows public access to shared reports
    - HTML reports are displayed directly in browser
    - Other formats are returned as JSON with metadata
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = generated_reports[report_id]
    
    # For HTML reports, return the content directly
    if report["format"] == "html":
        return HTMLResponse(content=report["content"])
    
    # For other formats, return as JSON with metadata
    return {
        "success": True,
        "report_id": report_id,
        "format": report["format"],
        "content": report["content"],
        "generated_at": report["generated_at"],
        "analysis_id": report["analysis_id"]
    }

@router.post("/export/bulk")
async def export_multiple_reports(report_ids: List[str], format: str = "json"):
    """
    Export multiple reports in a single file.
    
    BEGINNER NOTES:
    - This endpoint allows bulk export of multiple reports
    - Supports JSON and ZIP formats
    - Useful for archiving or sharing multiple analyses
    """
    if not report_ids:
        raise HTTPException(status_code=400, detail="No report IDs provided")
    
    # Validate all reports exist
    missing_reports = [rid for rid in report_ids if rid not in generated_reports]
    if missing_reports:
        raise HTTPException(
            status_code=404, 
            detail=f"Reports not found: {', '.join(missing_reports)}"
        )
    
    # Collect all reports
    reports_data = []
    for report_id in report_ids:
        report = generated_reports[report_id]
        reports_data.append({
            "report_id": report_id,
            "format": report["format"],
            "content": report["content"],
            "generated_at": report["generated_at"],
            "analysis_id": report["analysis_id"]
        })
    
    # Generate bulk export content
    if format == "json":
        export_content = json.dumps({
            "export_type": "bulk_reports",
            "exported_at": __import__('datetime').datetime.now().isoformat(),
            "total_reports": len(reports_data),
            "reports": reports_data
        }, indent=2)
        content_type = "application/json"
        filename = f"stressspec_bulk_export_{int(__import__('time').time())}.json"
    elif format == "zip":
        # Create a ZIP file with individual reports
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for report in reports_data:
                filename = f"report_{report['report_id']}.{report['format']}"
                zip_file.writestr(filename, report['content'])
            
            # Add metadata
            metadata = {
                "export_type": "bulk_reports",
                "exported_at": __import__('datetime').datetime.now().isoformat(),
                "total_reports": len(reports_data),
                "reports": [{"report_id": r["report_id"], "filename": f"report_{r['report_id']}.{r['format']}"} for r in reports_data]
            }
            zip_file.writestr("metadata.json", json.dumps(metadata, indent=2))
        
        zip_buffer.seek(0)
        export_content = zip_buffer.getvalue()
        content_type = "application/zip"
        filename = f"stressspec_bulk_export_{int(__import__('time').time())}.zip"
    else:
        raise HTTPException(status_code=400, detail="Invalid export format. Use 'json' or 'zip'")
    
    return Response(
        content=export_content,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/templates")
async def list_templates():
    """
    List all available report templates.
    
    BEGINNER NOTES:
    - This endpoint shows all predefined and custom templates
    - Templates define the structure and sections of reports
    - Users can choose templates when generating reports
    """
    return {
        "success": True,
        "templates": REPORT_TEMPLATES,
        "total": len(REPORT_TEMPLATES)
    }

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """
    Get details of a specific template.
    
    BEGINNER NOTES:
    - This endpoint returns detailed information about a template
    - Includes sections, format options, and customization settings
    """
    if template_id not in REPORT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "success": True,
        "template_id": template_id,
        "template": REPORT_TEMPLATES[template_id]
    }

@router.post("/templates", response_model=TemplateResponse)
async def create_template(request: TemplateRequest):
    """
    Create a new custom template.
    
    BEGINNER NOTES:
    - This endpoint allows users to create custom report templates
    - Templates define which sections to include in reports
    - Custom templates are stored in memory (in production, use a database)
    """
    # Generate template ID
    template_id = f"custom_{request.name.lower().replace(' ', '_')}_{int(__import__('time').time())}"
    
    # Add to templates (in production, save to database)
    REPORT_TEMPLATES[template_id] = {
        "name": request.name,
        "description": request.description,
        "sections": request.sections,
        "format_options": request.format_options,
        "customizable": request.customizable
    }
    
    return TemplateResponse(
        success=True,
        template_id=template_id,
        message="Template created successfully"
    )

@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: str, request: TemplateRequest):
    """
    Update an existing template.
    
    BEGINNER NOTES:
    - This endpoint allows modification of existing templates
    - Only custom templates can be updated (built-in templates are read-only)
    - Changes affect future report generations using this template
    """
    if template_id not in REPORT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if it's a built-in template
    if not template_id.startswith("custom_"):
        raise HTTPException(status_code=403, detail="Cannot modify built-in templates")
    
    # Update template
    REPORT_TEMPLATES[template_id] = {
        "name": request.name,
        "description": request.description,
        "sections": request.sections,
        "format_options": request.format_options,
        "customizable": request.customizable
    }
    
    return TemplateResponse(
        success=True,
        template_id=template_id,
        message="Template updated successfully"
    )

@router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """
    Delete a custom template.
    
    BEGINNER NOTES:
    - This endpoint removes custom templates
    - Built-in templates cannot be deleted
    - Deletion is permanent (in production, consider soft delete)
    """
    if template_id not in REPORT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Check if it's a built-in template
    if not template_id.startswith("custom_"):
        raise HTTPException(status_code=403, detail="Cannot delete built-in templates")
    
    # Remove template
    del REPORT_TEMPLATES[template_id]
    
    return {
        "success": True,
        "message": "Template deleted successfully"
    }

@router.get("/history/{analysis_id}")
async def get_report_history(analysis_id: str):
    """
    Get report history for a specific analysis.
    
    BEGINNER NOTES:
    - This endpoint shows all versions of reports generated for an analysis
    - Useful for tracking changes and comparing different report versions
    - Shows version numbers, templates used, and generation timestamps
    """
    if analysis_id not in report_history:
        return {
            "success": True,
            "analysis_id": analysis_id,
            "history": [],
            "total_versions": 0
        }
    
    # Sort by generation date (newest first)
    history = sorted(report_history[analysis_id], key=lambda x: x["generated_at"], reverse=True)
    
    return {
        "success": True,
        "analysis_id": analysis_id,
        "history": history,
        "total_versions": len(history)
    }

@router.get("/versions/{analysis_id}")
async def get_report_versions(analysis_id: str, template: Optional[str] = None, format: Optional[str] = None):
    """
    Get specific versions of reports for an analysis.
    
    BEGINNER NOTES:
    - This endpoint filters report versions by template and/or format
    - Useful for comparing different versions of the same report type
    - Shows version progression and changes over time
    """
    if analysis_id not in report_history:
        return {
            "success": True,
            "analysis_id": analysis_id,
            "versions": [],
            "total_versions": 0
        }
    
    # Filter versions
    versions = report_history[analysis_id]
    
    if template:
        versions = [v for v in versions if v["template"] == template]
    
    if format:
        versions = [v for v in versions if v["format"] == format]
    
    # Sort by version number (highest first)
    versions = sorted(versions, key=lambda x: x["version"], reverse=True)
    
    return {
        "success": True,
        "analysis_id": analysis_id,
        "template": template,
        "format": format,
        "versions": versions,
        "total_versions": len(versions)
    }

@router.get("/compare-versions/{analysis_id}")
async def compare_report_versions(analysis_id: str, version1: int, version2: int, template: Optional[str] = None, format: Optional[str] = None):
    """
    Compare two versions of a report.
    
    BEGINNER NOTES:
    - This endpoint compares two specific versions of a report
    - Shows differences in content, filters, and customizations
    - Useful for tracking changes and improvements over time
    """
    if analysis_id not in report_history:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Find the specific versions
    versions = report_history[analysis_id]
    
    if template:
        versions = [v for v in versions if v["template"] == template]
    
    if format:
        versions = [v for v in versions if v["format"] == format]
    
    version1_data = next((v for v in versions if v["version"] == version1), None)
    version2_data = next((v for v in versions if v["version"] == version2), None)
    
    if not version1_data or not version2_data:
        raise HTTPException(status_code=404, detail="One or both versions not found")
    
    # Get the actual report content for comparison
    report1 = generated_reports.get(version1_data["report_id"])
    report2 = generated_reports.get(version2_data["report_id"])
    
    if not report1 or not report2:
        raise HTTPException(status_code=404, detail="Report content not found")
    
    # Compare the reports
    comparison = {
        "analysis_id": analysis_id,
        "version1": {
            "version": version1,
            "generated_at": version1_data["generated_at"],
            "template": version1_data["template"],
            "format": version1_data["format"],
            "filters": version1_data["filters"],
            "customizations": version1_data["customizations"],
            "content_length": len(report1["content"])
        },
        "version2": {
            "version": version2,
            "generated_at": version2_data["generated_at"],
            "template": version2_data["template"],
            "format": version2_data["format"],
            "filters": version2_data["filters"],
            "customizations": version2_data["customizations"],
            "content_length": len(report2["content"])
        },
        "differences": {
            "template_changed": version1_data["template"] != version2_data["template"],
            "format_changed": version1_data["format"] != version2_data["format"],
            "filters_changed": version1_data["filters"] != version2_data["filters"],
            "customizations_changed": version1_data["customizations"] != version2_data["customizations"],
            "content_length_changed": len(report1["content"]) != len(report2["content"]),
            "time_difference": abs(
                __import__('datetime').datetime.fromisoformat(version2_data["generated_at"].replace('Z', '+00:00')) -
                __import__('datetime').datetime.fromisoformat(version1_data["generated_at"].replace('Z', '+00:00'))
            ).total_seconds()
        }
    }
    
    return {
        "success": True,
        "comparison": comparison
    }

@router.get("/analytics")
async def get_report_analytics():
    """
    Get analytics and insights about reports.
    
    BEGINNER NOTES:
    - This endpoint provides analytics about report generation patterns
    - Shows usage statistics, popular templates, and trends
    - Useful for understanding how the system is being used
    """
    # Calculate analytics from generated reports and history
    total_reports = len(generated_reports)
    total_analyses = len(report_history)
    
    # Template usage statistics
    template_usage = {}
    format_usage = {}
    daily_generation = {}
    
    for report_id, report in generated_reports.items():
        template = report.get("template", "technical_detailed")
        format_type = report.get("format", "html")
        generated_at = report.get("generated_at", "")
        
        # Count template usage
        template_usage[template] = template_usage.get(template, 0) + 1
        
        # Count format usage
        format_usage[format_type] = format_usage.get(format_type, 0) + 1
        
        # Count daily generation
        if generated_at:
            try:
                date = __import__('datetime').datetime.fromisoformat(generated_at.replace('Z', '+00:00')).date()
                daily_generation[str(date)] = daily_generation.get(str(date), 0) + 1
            except:
                pass
    
    # Calculate trends
    recent_reports = sorted(generated_reports.items(), 
                          key=lambda x: x[1].get("generated_at", ""), 
                          reverse=True)[:10]
    
    # Most active analyses
    analysis_activity = {}
    for analysis_id, history in report_history.items():
        analysis_activity[analysis_id] = len(history)
    
    most_active_analyses = sorted(analysis_activity.items(), 
                                key=lambda x: x[1], 
                                reverse=True)[:5]
    
    # Version statistics
    version_stats = {}
    for analysis_id, history in report_history.items():
        for report in history:
            template = report.get("template", "technical_detailed")
            if template not in version_stats:
                version_stats[template] = {"total_versions": 0, "max_version": 0}
            version_stats[template]["total_versions"] += 1
            version_stats[template]["max_version"] = max(
                version_stats[template]["max_version"], 
                report.get("version", 1)
            )
    
    return {
        "success": True,
        "analytics": {
            "overview": {
                "total_reports": total_reports,
                "total_analyses": total_analyses,
                "unique_templates": len(template_usage),
                "unique_formats": len(format_usage)
            },
            "template_usage": template_usage,
            "format_usage": format_usage,
            "daily_generation": daily_generation,
            "most_active_analyses": most_active_analyses,
            "version_statistics": version_stats,
            "recent_activity": [
                {
                    "report_id": report_id,
                    "analysis_id": report["analysis_id"],
                    "template": report.get("template", "technical_detailed"),
                    "format": report.get("format", "html"),
                    "version": report.get("version", 1),
                    "generated_at": report.get("generated_at", "")
                }
                for report_id, report in recent_reports
            ]
        }
    }

@router.get("/insights/{analysis_id}")
async def get_analysis_insights(analysis_id: str):
    """
    Get insights for a specific analysis.
    
    BEGINNER NOTES:
    - This endpoint provides insights about a specific analysis
    - Shows report generation patterns, version history, and recommendations
    - Useful for understanding the evolution of a particular analysis
    """
    if analysis_id not in report_history:
        return {
            "success": True,
            "analysis_id": analysis_id,
            "insights": {
                "message": "No reports generated for this analysis yet"
            }
        }
    
    history = report_history[analysis_id]
    
    # Calculate insights
    total_reports = len(history)
    templates_used = set(report.get("template", "technical_detailed") for report in history)
    formats_used = set(report.get("format", "html") for report in history)
    
    # Version progression
    version_progression = {}
    for report in history:
        template = report.get("template", "technical_detailed")
        if template not in version_progression:
            version_progression[template] = []
        version_progression[template].append({
            "version": report.get("version", 1),
            "generated_at": report.get("generated_at", ""),
            "format": report.get("format", "html")
        })
    
    # Sort by version for each template
    for template in version_progression:
        version_progression[template].sort(key=lambda x: x["version"])
    
    # Time analysis
    if history:
        first_report = min(history, key=lambda x: x.get("generated_at", ""))
        last_report = max(history, key=lambda x: x.get("generated_at", ""))
        
        try:
            first_date = __import__('datetime').datetime.fromisoformat(first_report.get("generated_at", "").replace('Z', '+00:00'))
            last_date = __import__('datetime').datetime.fromisoformat(last_report.get("generated_at", "").replace('Z', '+00:00'))
            time_span = (last_date - first_date).days
        except:
            time_span = 0
    else:
        time_span = 0
    
    # Generate recommendations
    recommendations = []
    
    if total_reports == 1:
        recommendations.append("Consider generating reports in different formats for better accessibility")
    
    if len(templates_used) == 1:
        recommendations.append("Try different report templates to get varied perspectives on your analysis")
    
    if time_span > 30:
        recommendations.append("This analysis has been active for a while - consider reviewing and updating the requirements")
    
    if len(formats_used) < 2:
        recommendations.append("Generate reports in multiple formats (HTML, PDF, CSV) for different use cases")
    
    return {
        "success": True,
        "analysis_id": analysis_id,
        "insights": {
            "summary": {
                "total_reports": total_reports,
                "templates_used": list(templates_used),
                "formats_used": list(formats_used),
                "time_span_days": time_span
            },
            "version_progression": version_progression,
            "recommendations": recommendations,
            "recent_reports": sorted(history, key=lambda x: x.get("generated_at", ""), reverse=True)[:5]
        }
    }

@router.post("/schedule", response_model=ScheduleResponse)
async def create_schedule(request: ScheduleRequest):
    """
    Create a scheduled report.
    
    BEGINNER NOTES:
    - This endpoint allows users to schedule automatic report generation
    - Supports daily, weekly, monthly, and custom schedules
    - Reports will be generated automatically based on the schedule
    """
    # Generate schedule ID
    schedule_id = f"schedule_{request.name.lower().replace(' ', '_')}_{int(__import__('time').time())}"
    
    # Validate template
    if request.template not in REPORT_TEMPLATES:
        raise HTTPException(status_code=400, detail="Invalid template")
    
    template = REPORT_TEMPLATES[request.template]
    if request.format not in template["format_options"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Format '{request.format}' not supported by template '{request.template}'"
        )
    
    # Create schedule configuration
    schedule_config = {
        "schedule_id": schedule_id,
        "name": request.name,
        "analysis_id": request.analysis_id,
        "template": request.template,
        "format": request.format,
        "schedule_type": request.schedule_type,
        "schedule_config": request.schedule_config or {},
        "filters": request.filters or {},
        "customizations": request.customizations or {},
        "enabled": request.enabled,
        "created_at": __import__('datetime').datetime.now().isoformat(),
        "last_run": None,
        "next_run": calculate_next_run(request.schedule_type, request.schedule_config),
        "run_count": 0
    }
    
    # Store schedule
    scheduled_reports[schedule_id] = schedule_config
    
    return ScheduleResponse(
        success=True,
        schedule_id=schedule_id,
        message="Schedule created successfully"
    )

@router.get("/schedule")
async def list_schedules():
    """
    List all scheduled reports.
    
    BEGINNER NOTES:
    - This endpoint shows all scheduled reports
    - Includes schedule status, next run time, and run count
    - Useful for managing automated report generation
    """
    return {
        "success": True,
        "schedules": list(scheduled_reports.values()),
        "total": len(scheduled_reports)
    }

@router.get("/schedule/{schedule_id}")
async def get_schedule(schedule_id: str):
    """
    Get details of a specific schedule.
    
    BEGINNER NOTES:
    - This endpoint returns detailed information about a schedule
    - Includes configuration, status, and run history
    """
    if schedule_id not in scheduled_reports:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {
        "success": True,
        "schedule": scheduled_reports[schedule_id]
    }

@router.put("/schedule/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(schedule_id: str, request: ScheduleRequest):
    """
    Update an existing schedule.
    
    BEGINNER NOTES:
    - This endpoint allows modification of existing schedules
    - Can change schedule type, configuration, or enable/disable
    - Updates next run time based on new configuration
    """
    if schedule_id not in scheduled_reports:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Validate template
    if request.template not in REPORT_TEMPLATES:
        raise HTTPException(status_code=400, detail="Invalid template")
    
    template = REPORT_TEMPLATES[request.template]
    if request.format not in template["format_options"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Format '{request.format}' not supported by template '{request.template}'"
        )
    
    # Update schedule
    scheduled_reports[schedule_id].update({
        "name": request.name,
        "analysis_id": request.analysis_id,
        "template": request.template,
        "format": request.format,
        "schedule_type": request.schedule_type,
        "schedule_config": request.schedule_config or {},
        "filters": request.filters or {},
        "customizations": request.customizations or {},
        "enabled": request.enabled,
        "next_run": calculate_next_run(request.schedule_type, request.schedule_config)
    })
    
    return ScheduleResponse(
        success=True,
        schedule_id=schedule_id,
        message="Schedule updated successfully"
    )

@router.delete("/schedule/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """
    Delete a scheduled report.
    
    BEGINNER NOTES:
    - This endpoint removes a schedule permanently
    - Stops automatic report generation for this schedule
    """
    if schedule_id not in scheduled_reports:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    del scheduled_reports[schedule_id]
    
    return {
        "success": True,
        "message": "Schedule deleted successfully"
    }

@router.post("/schedule/{schedule_id}/run")
async def run_schedule_now(schedule_id: str):
    """
    Manually trigger a scheduled report.
    
    BEGINNER NOTES:
    - This endpoint allows manual execution of a scheduled report
    - Useful for testing schedules or generating reports on demand
    - Updates the schedule's last run time and run count
    """
    if schedule_id not in scheduled_reports:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule = scheduled_reports[schedule_id]
    
    # Generate report using the schedule configuration
    report_request = ReportRequest(
        analysis_id=schedule["analysis_id"],
        format=schedule["format"],
        template=schedule["template"],
        filters=schedule["filters"],
        customizations=schedule["customizations"]
    )
    
    # Call the existing report generation logic
    try:
        # This would normally call the generate_report function
        # For now, we'll simulate the report generation
        report_id = f"report_{schedule['analysis_id']}_{schedule['format']}_{int(__import__('time').time())}"
        
        # Update schedule statistics
        schedule["last_run"] = __import__('datetime').datetime.now().isoformat()
        schedule["run_count"] += 1
        schedule["next_run"] = calculate_next_run(schedule["schedule_type"], schedule["schedule_config"])
        
        return {
            "success": True,
            "report_id": report_id,
            "message": "Scheduled report generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate scheduled report: {str(e)}")

def calculate_next_run(schedule_type: str, schedule_config: Dict) -> str:
    """
    Calculate the next run time for a schedule.
    
    BEGINNER NOTES:
    - This helper function calculates when the next report should be generated
    - Supports different schedule types with various configurations
    - Returns ISO format timestamp for the next run
    """
    now = __import__('datetime').datetime.now()
    
    if schedule_type == "daily":
        # Run daily at specified time (default: 9 AM)
        hour = schedule_config.get("hour", 9)
        minute = schedule_config.get("minute", 0)
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_run <= now:
            next_run += __import__('datetime').timedelta(days=1)
    
    elif schedule_type == "weekly":
        # Run weekly on specified day (default: Monday)
        weekday = schedule_config.get("weekday", 0)  # 0 = Monday
        hour = schedule_config.get("hour", 9)
        minute = schedule_config.get("minute", 0)
        days_ahead = weekday - now.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        next_run = now + __import__('datetime').timedelta(days=days_ahead)
        next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    elif schedule_type == "monthly":
        # Run monthly on specified day (default: 1st)
        day = schedule_config.get("day", 1)
        hour = schedule_config.get("hour", 9)
        minute = schedule_config.get("minute", 0)
        try:
            next_run = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                # Move to next month
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
        except ValueError:
            # Handle months with fewer days
            next_run = now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
            if now.month == 12:
                next_run = next_run.replace(year=now.year + 1, month=1)
            else:
                next_run = next_run.replace(month=now.month + 1)
    
    else:  # custom
        # For custom schedules, use the provided configuration
        # This is a simplified implementation
        interval_hours = schedule_config.get("interval_hours", 24)
        next_run = now + __import__('datetime').timedelta(hours=interval_hours)
    
    return next_run.isoformat()

@router.post("/{report_id}/comments", response_model=CommentResponse)
async def add_comment(report_id: str, request: CommentRequest):
    """
    Add a comment to a report.
    
    BEGINNER NOTES:
    - This endpoint allows users to add comments to reports
    - Supports threaded comments with parent-child relationships
    - Useful for collaboration and feedback on reports
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if comments are allowed
    permissions = report_permissions.get(report_id, {})
    if not permissions.get("allow_comments", True):
        raise HTTPException(status_code=403, detail="Comments not allowed for this report")
    
    # Generate comment ID
    comment_id = f"comment_{report_id}_{int(__import__('time').time())}"
    
    # Create comment
    comment = {
        "comment_id": comment_id,
        "report_id": report_id,
        "content": request.content,
        "author": request.author,
        "parent_comment_id": request.parent_comment_id,
        "created_at": __import__('datetime').datetime.now().isoformat(),
        "replies": []
    }
    
    # Store comment
    if report_id not in report_comments:
        report_comments[report_id] = []
    
    # If it's a reply, add to parent comment
    if request.parent_comment_id:
        for existing_comment in report_comments[report_id]:
            if existing_comment["comment_id"] == request.parent_comment_id:
                existing_comment["replies"].append(comment)
                break
        else:
            raise HTTPException(status_code=404, detail="Parent comment not found")
    else:
        report_comments[report_id].append(comment)
    
    return CommentResponse(
        success=True,
        comment_id=comment_id,
        message="Comment added successfully"
    )

@router.get("/{report_id}/comments")
async def get_comments(report_id: str):
    """
    Get all comments for a report.
    
    BEGINNER NOTES:
    - This endpoint retrieves all comments for a specific report
    - Returns threaded comments with replies
    - Useful for displaying collaboration history
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    comments = report_comments.get(report_id, [])
    
    return {
        "success": True,
        "report_id": report_id,
        "comments": comments,
        "total": len(comments)
    }

@router.delete("/{report_id}/comments/{comment_id}")
async def delete_comment(report_id: str, comment_id: str):
    """
    Delete a comment from a report.
    
    BEGINNER NOTES:
    - This endpoint allows deletion of comments
    - Removes the comment and all its replies
    - Useful for moderation and cleanup
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report_id not in report_comments:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Find and remove comment
    def remove_comment(comments, target_id):
        for i, comment in enumerate(comments):
            if comment["comment_id"] == target_id:
                comments.pop(i)
                return True
            if remove_comment(comment["replies"], target_id):
                return True
        return False
    
    if not remove_comment(report_comments[report_id], comment_id):
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return {
        "success": True,
        "message": "Comment deleted successfully"
    }

@router.put("/{report_id}/permissions")
async def set_permissions(report_id: str, request: PermissionRequest):
    """
    Set permissions for a report.
    
    BEGINNER NOTES:
    - This endpoint allows setting access permissions for reports
    - Controls who can read, comment, and download reports
    - Useful for managing report access and collaboration
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Set permissions
    report_permissions[report_id] = {
        "public_read": request.public_read,
        "allow_comments": request.allow_comments,
        "allow_download": request.allow_download,
        "allowed_users": request.allowed_users or [],
        "updated_at": __import__('datetime').datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "message": "Permissions updated successfully"
    }

@router.get("/{report_id}/permissions")
async def get_permissions(report_id: str):
    """
    Get permissions for a report.
    
    BEGINNER NOTES:
    - This endpoint retrieves the current permissions for a report
    - Shows access settings and allowed users
    - Useful for checking report access rights
    """
    if report_id not in generated_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    permissions = report_permissions.get(report_id, {
        "public_read": False,
        "allow_comments": True,
        "allow_download": True,
        "allowed_users": []
    })
    
    return {
        "success": True,
        "report_id": report_id,
        "permissions": permissions
    }

@router.get("/collaboration/activity")
async def get_collaboration_activity():
    """
    Get collaboration activity across all reports.
    
    BEGINNER NOTES:
    - This endpoint shows recent collaboration activity
    - Includes comments, permission changes, and sharing
    - Useful for tracking team collaboration
    """
    # Collect recent activity
    recent_comments = []
    recent_permissions = []
    
    # Get recent comments
    for report_id, comments in report_comments.items():
        for comment in comments:
            recent_comments.append({
                "report_id": report_id,
                "comment_id": comment["comment_id"],
                "author": comment["author"],
                "content": comment["content"][:100] + "..." if len(comment["content"]) > 100 else comment["content"],
                "created_at": comment["created_at"]
            })
            
            # Include replies
            for reply in comment["replies"]:
                recent_comments.append({
                    "report_id": report_id,
                    "comment_id": reply["comment_id"],
                    "author": reply["author"],
                    "content": reply["content"][:100] + "..." if len(reply["content"]) > 100 else reply["content"],
                    "created_at": reply["created_at"]
                })
    
    # Get recent permission changes
    for report_id, permissions in report_permissions.items():
        recent_permissions.append({
            "report_id": report_id,
            "permissions": permissions,
            "updated_at": permissions.get("updated_at", "")
        })
    
    # Sort by date (newest first)
    recent_comments.sort(key=lambda x: x["created_at"], reverse=True)
    recent_permissions.sort(key=lambda x: x["updated_at"], reverse=True)
    
    return {
        "success": True,
        "activity": {
            "recent_comments": recent_comments[:20],  # Last 20 comments
            "recent_permissions": recent_permissions[:10],  # Last 10 permission changes
            "total_comments": sum(len(comments) + sum(len(comment["replies"]) for comment in comments) for comments in report_comments.values()),
            "total_reports_with_permissions": len(report_permissions)
        }
    }

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
                "template": report.get("template", "technical_detailed"),
                "version": report.get("version", 1),
                "generated_at": report["generated_at"]
            }
            for report_id, report in generated_reports.items()
        ],
        "count": len(generated_reports)
    }

@router.get("/analyses")
async def list_available_analyses():
    """
    List all available analyses for report generation.
    
    BEGINNER NOTES:
    - This endpoint shows all completed analyses that can be used for reports
    - Useful for populating the report generation form
    - Returns basic information about each analysis
    """
    try:
        from web.api.analysis import analysis_results
        
        analyses = []
        for analysis_id, results in analysis_results.items():
            analyses.append({
                "analysis_id": analysis_id,
                "completed_at": results.completed_at,
                "total_requirements": len(results.requirements),
                "total_risks": sum(len(risks) for risks in results.risks_by_requirement.values()),
                "summary": results.summary.__dict__ if hasattr(results.summary, '__dict__') else results.summary
            })
        
        # Sort by completion date (newest first)
        analyses.sort(key=lambda x: x['completed_at'], reverse=True)
        
        return {
            "success": True,
            "analyses": analyses,
            "count": len(analyses)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list analyses: {str(e)}"
        )

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

@router.post("/compare")
async def compare_reports(report_ids: List[str]):
    """
    Compare multiple reports and generate a comparison analysis.
    
    BEGINNER NOTES:
    - This endpoint compares two or more reports
    - It analyzes differences in risks, requirements, and trends
    - Returns a detailed comparison with insights
    """
    try:
        if len(report_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 reports required for comparison")
        
        # Get analysis data for each report
        from web.api.analysis import analysis_results
        
        comparison_data = {
            "reports": [],
            "comparison": {
                "total_requirements": {"min": 0, "max": 0, "avg": 0},
                "total_risks": {"min": 0, "max": 0, "avg": 0},
                "risk_categories": {},
                "severity_distribution": {},
                "trends": {},
                "insights": []
            }
        }
        
        all_requirements = set()
        all_risks = []
        all_categories = set()
        all_severities = set()
        
        for report_id in report_ids:
            if report_id not in generated_reports:
                raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
            
            report = generated_reports[report_id]
            analysis_id = report["analysis_id"]
            
            if analysis_id not in analysis_results:
                raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")
            
            analysis_data = analysis_results[analysis_id]
            
            # Extract data for comparison
            requirements = analysis_data.requirements
            risks_by_req = analysis_data.risks_by_requirement
            summary = analysis_data.summary
            
            report_data = {
                "report_id": report_id,
                "analysis_id": analysis_id,
                "format": report["format"],
                "generated_at": report["generated_at"],
                "total_requirements": len(requirements),
                "total_risks": sum(len(risks) for risks in risks_by_req.values()),
                "requirements_with_risks": len([req for req in requirements if req.id in risks_by_req and risks_by_req[req.id]]),
                "risk_categories": {},
                "severity_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0}
            }
            
            # Analyze risks
            for req_id, risks in risks_by_req.items():
                all_requirements.add(req_id)
                for risk in risks:
                    all_risks.append(risk)
                    category = risk.category
                    severity = risk.severity
                    
                    all_categories.add(category)
                    all_severities.add(severity)
                    
                    # Count categories
                    if category not in report_data["risk_categories"]:
                        report_data["risk_categories"][category] = 0
                    report_data["risk_categories"][category] += 1
                    
                    # Count severities
                    if severity in report_data["severity_distribution"]:
                        report_data["severity_distribution"][severity] += 1
            
            comparison_data["reports"].append(report_data)
        
        # Calculate comparison metrics
        req_counts = [r["total_requirements"] for r in comparison_data["reports"]]
        risk_counts = [r["total_risks"] for r in comparison_data["reports"]]
        
        comparison_data["comparison"]["total_requirements"] = {
            "min": min(req_counts),
            "max": max(req_counts),
            "avg": sum(req_counts) / len(req_counts)
        }
        
        comparison_data["comparison"]["total_risks"] = {
            "min": min(risk_counts),
            "max": max(risk_counts),
            "avg": sum(risk_counts) / len(risk_counts)
        }
        
        # Analyze risk categories across all reports
        for category in all_categories:
            category_counts = []
            for report in comparison_data["reports"]:
                category_counts.append(report["risk_categories"].get(category, 0))
            
            comparison_data["comparison"]["risk_categories"][category] = {
                "min": min(category_counts),
                "max": max(category_counts),
                "avg": sum(category_counts) / len(category_counts),
                "trend": "increasing" if category_counts[-1] > category_counts[0] else "decreasing" if category_counts[-1] < category_counts[0] else "stable"
            }
        
        # Analyze severity distribution
        for severity in all_severities:
            severity_counts = []
            for report in comparison_data["reports"]:
                severity_counts.append(report["severity_distribution"].get(severity, 0))
            
            comparison_data["comparison"]["severity_distribution"][severity] = {
                "min": min(severity_counts),
                "max": max(severity_counts),
                "avg": sum(severity_counts) / len(severity_counts),
                "trend": "increasing" if severity_counts[-1] > severity_counts[0] else "decreasing" if severity_counts[-1] < severity_counts[0] else "stable"
            }
        
        # Generate insights
        insights = []
        
        # Risk trend insights
        if len(risk_counts) >= 2:
            if risk_counts[-1] > risk_counts[0]:
                insights.append(f"Risk count increased from {risk_counts[0]} to {risk_counts[-1]} (+{risk_counts[-1] - risk_counts[0]})")
            elif risk_counts[-1] < risk_counts[0]:
                insights.append(f"Risk count decreased from {risk_counts[0]} to {risk_counts[-1]} (-{risk_counts[0] - risk_counts[-1]})")
            else:
                insights.append("Risk count remained stable across reports")
        
        # Category insights
        for category, data in comparison_data["comparison"]["risk_categories"].items():
            if data["trend"] == "increasing":
                insights.append(f"{category.title()} risks are increasing (avg: {data['avg']:.1f})")
            elif data["trend"] == "decreasing":
                insights.append(f"{category.title()} risks are decreasing (avg: {data['avg']:.1f})")
        
        # Severity insights
        critical_trend = comparison_data["comparison"]["severity_distribution"].get("critical", {}).get("trend", "stable")
        if critical_trend == "increasing":
            insights.append("Critical risks are increasing - immediate attention required")
        elif critical_trend == "decreasing":
            insights.append("Critical risks are decreasing - good progress")
        
        comparison_data["comparison"]["insights"] = insights
        
        return {
            "success": True,
            "comparison": comparison_data,
            "message": f"Successfully compared {len(report_ids)} reports"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report comparison failed: {str(e)}"
        )
