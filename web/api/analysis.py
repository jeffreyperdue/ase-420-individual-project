"""
Analysis API Endpoints

This module handles requirement analysis functionality for the StressSpec web interface.
It integrates with the existing analyzer and detector system.

BEGINNER NOTES:
- This handles the analysis of uploaded requirement files
- It uses the existing analyzer.py and detector system
- It processes files and returns risk analysis results
- It provides real-time progress updates
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

# Import our existing modules
from src.file_loader import FileLoader
from src.requirement_parser import RequirementParser
from src.factories.detector_factory import RiskDetectorFactory
from src.analyzer import analyze_requirements

# Create router for analysis endpoints
router = APIRouter()

# Configuration
ANALYSIS_TIMEOUT = int(os.getenv("ANALYSIS_TIMEOUT", 300))  # 5 minutes
MAX_CONCURRENT_ANALYSES = int(os.getenv("MAX_CONCURRENT_ANALYSES", 5))

class AnalysisRequest(BaseModel):
    """Request model for starting analysis."""
    file_id: str
    options: Optional[Dict] = None

class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    success: bool
    analysis_id: str
    file_id: str
    status: str
    message: str

class AnalysisStatus(BaseModel):
    """Status model for analysis progress."""
    analysis_id: str
    status: str
    progress: int
    message: str
    results: Optional[Dict] = None

class AnalysisResults(BaseModel):
    """Results model for completed analysis."""
    analysis_id: str
    file_id: str
    requirements: List[Dict]
    risks_by_requirement: Dict[str, List[Dict]]
    summary: Dict
    completed_at: str

# In-memory storage for analysis status (in production, use Redis or database)
analysis_status: Dict[str, AnalysisStatus] = {}
analysis_results: Dict[str, AnalysisResults] = {}

async def run_analysis(analysis_id: str, file_id: str, file_path: str):
    """
    Run the analysis in the background.
    
    BEGINNER NOTES:
    - This function runs the actual analysis process
    - It uses our existing analyzer and detector system
    - It updates the status as it progresses
    - It stores the results when complete
    """
    try:
        # Update status to processing
        analysis_status[analysis_id] = AnalysisStatus(
            analysis_id=analysis_id,
            status="processing",
            progress=10,
            message="Loading file..."
        )
        
        # Load the file with structured parsing
        file_loader = FileLoader()
        structured_requirements = file_loader.load_file_structured(file_path)
        
        # Update progress
        analysis_status[analysis_id].progress = 30
        analysis_status[analysis_id].message = "Parsing requirements..."
        
        # Parse structured requirements
        parser = RequirementParser()
        requirements = parser.parse_structured_requirements(structured_requirements)
        
        # Update progress
        analysis_status[analysis_id].progress = 50
        analysis_status[analysis_id].message = "Running risk detectors..."
        
        # Create detectors
        factory = RiskDetectorFactory()
        detectors = factory.create_enabled_detectors() or factory.create_all_detectors()
        
        # Run analysis
        risks_by_requirement = analyze_requirements(requirements, detectors)
        
        # Update progress
        analysis_status[analysis_id].progress = 80
        analysis_status[analysis_id].message = "Generating results..."
        
        # Calculate summary
        total_risks = sum(len(risks) for risks in risks_by_requirement.values())
        risk_categories = {}
        
        for req_id, risks in risks_by_requirement.items():
            for risk in risks:
                category = risk.category.value if hasattr(risk.category, 'value') else str(risk.category)
                if category not in risk_categories:
                    risk_categories[category] = 0
                risk_categories[category] += 1
        
        summary = {
            "total_requirements": len(requirements),
            "total_risks": total_risks,
            "risk_categories": risk_categories,
            "requirements_with_risks": len([req_id for req_id, risks in risks_by_requirement.items() if risks])
        }
        
        # Convert to dictionaries for JSON serialization
        requirements_dict = [
            {
                "id": req.id,
                "text": req.text,
                "line_number": req.line_number
            }
            for req in requirements
        ]
        
        risks_dict = {
            req_id: [
                {
                    "category": risk.category.value if hasattr(risk.category, 'value') else str(risk.category),
                    "severity": risk.severity.name.lower() if hasattr(risk.severity, 'name') else str(risk.severity).lower(),
                    "description": risk.description,
                    "evidence": risk.evidence
                }
                for risk in risks
            ]
            for req_id, risks in risks_by_requirement.items()
        }
        
        # Store results
        analysis_results[analysis_id] = AnalysisResults(
            analysis_id=analysis_id,
            file_id=file_id,
            requirements=requirements_dict,
            risks_by_requirement=risks_dict,
            summary=summary,
            completed_at=str(Path(file_path).stat().st_mtime)
        )
        
        # Update status to completed
        analysis_status[analysis_id] = AnalysisStatus(
            analysis_id=analysis_id,
            status="completed",
            progress=100,
            message="Analysis completed successfully",
            results=analysis_results[analysis_id].dict()
        )
        
    except Exception as e:
        # Update status to error
        analysis_status[analysis_id] = AnalysisStatus(
            analysis_id=analysis_id,
            status="error",
            progress=0,
            message=f"Analysis failed: {str(e)}"
        )

@router.post("/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Start analysis of an uploaded file.
    
    BEGINNER NOTES:
    - This endpoint starts the analysis process
    - It runs in the background so it doesn't block the web interface
    - It returns immediately with an analysis ID
    - The actual analysis happens asynchronously
    """
    try:
        # Generate analysis ID
        analysis_id = f"analysis_{request.file_id}"
        
        # Check if analysis already exists
        if analysis_id in analysis_status:
            return AnalysisResponse(
                success=True,
                analysis_id=analysis_id,
                file_id=request.file_id,
                status="already_exists",
                message="Analysis already exists"
            )
        
        # Find the uploaded file
        upload_dir = Path(os.getenv("UPLOAD_DIR", "uploads"))
        file_pattern = f"{request.file_id}_*"
        upload_files = list(upload_dir.glob(file_pattern))
        
        if not upload_files:
            raise HTTPException(status_code=404, detail="Uploaded file not found")
        
        file_path = str(upload_files[0])
        
        # Initialize status
        analysis_status[analysis_id] = AnalysisStatus(
            analysis_id=analysis_id,
            status="queued",
            progress=0,
            message="Analysis queued"
        )
        
        # Start background task
        background_tasks.add_task(run_analysis, analysis_id, request.file_id, file_path)
        
        return AnalysisResponse(
            success=True,
            analysis_id=analysis_id,
            file_id=request.file_id,
            status="queued",
            message="Analysis started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )

@router.get("/status/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(analysis_id: str):
    """
    Get the status of an analysis.
    
    BEGINNER NOTES:
    - This endpoint checks the progress of an analysis
    - It returns the current status and progress
    - Useful for showing progress bars in the web interface
    """
    try:
        if analysis_id not in analysis_status:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis_status[analysis_id]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis status: {str(e)}"
        )

@router.get("/results/{analysis_id}", response_model=AnalysisResults)
async def get_analysis_results(analysis_id: str):
    """
    Get the results of a completed analysis.
    
    BEGINNER NOTES:
    - This endpoint returns the analysis results
    - Only works for completed analyses
    - Returns all requirements and their associated risks
    """
    try:
        if analysis_id not in analysis_results:
            raise HTTPException(status_code=404, detail="Analysis results not found")
        
        return analysis_results[analysis_id]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis results: {str(e)}"
        )

@router.get("/list")
async def list_analyses():
    """
    List all analyses and their status.
    
    BEGINNER NOTES:
    - This endpoint shows all analyses that have been run
    - Useful for managing multiple analyses
    - Returns status information for each analysis
    """
    return {
        "success": True,
        "analyses": list(analysis_status.values()),
        "count": len(analysis_status)
    }

@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    Delete an analysis and its results.
    
    BEGINNER NOTES:
    - This endpoint removes an analysis from memory
    - Useful for cleanup and privacy
    - Removes both status and results
    """
    if analysis_id in analysis_status:
        del analysis_status[analysis_id]
    
    if analysis_id in analysis_results:
        del analysis_results[analysis_id]
    
    return {
        "success": True,
        "message": "Analysis deleted successfully"
    }
