"""
StressSpec Web UI - Main FastAPI Application

This is the main FastAPI application that serves the web interface for StressSpec.
It provides endpoints for file upload, analysis, and reporting.

BEGINNER NOTES:
- This is the main entry point for the web application
- FastAPI automatically generates API documentation
- It handles routing, middleware, and static file serving
- Think of it as the "web server" that coordinates all web requests
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add the project root to Python path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="StressSpec Web UI",
    description="Web interface for Requirements Stress Tester",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Configure Jinja2 templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Import API routes (we'll create these next)
from web.api import upload, analysis, reports

# Include API routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Main page - serves the StressSpec web interface.
    
    BEGINNER NOTES:
    - This is the "home page" of our web application
    - It renders the main HTML template
    - The template will include our file upload and analysis interface
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "StressSpec - Requirements Stress Tester",
        "version": "1.0.0"
    })

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    BEGINNER NOTES:
    - This endpoint is used to check if the application is running
    - Useful for load balancers and monitoring systems
    - Returns basic status information
    """
    return {
        "status": "healthy",
        "service": "StressSpec Web UI",
        "version": "1.0.0"
    }

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """
    About page with information about StressSpec.
    
    BEGINNER NOTES:
    - This provides information about the application
    - Useful for users who want to learn more about the tool
    - Can include features, usage instructions, etc.
    """
    return templates.TemplateResponse("about.html", {
        "request": request,
        "title": "About StressSpec"
    })

@app.get("/results/{analysis_id}", response_class=HTMLResponse)
async def results_page(request: Request, analysis_id: str):
    """
    Results page for displaying analysis results.
    
    BEGINNER NOTES:
    - This displays the results of a completed analysis
    - Shows requirements, risks, and summary statistics
    - Provides export options for the results
    """
    # Import analysis results (in production, this would come from a database)
    from web.api.analysis import analysis_results
    
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    results = analysis_results[analysis_id]
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "title": "Analysis Results",
        "analysis_id": analysis_id,
        "requirements": results.requirements,
        "risks_by_requirement": results.risks_by_requirement,
        "summary": results.summary,
        "completed_at": results.completed_at
    })

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors with a custom page."""
    return templates.TemplateResponse("404.html", {
        "request": request,
        "title": "Page Not Found"
    }, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors with a custom page."""
    return templates.TemplateResponse("500.html", {
        "request": request,
        "title": "Internal Server Error"
    }, status_code=500)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    
    BEGINNER NOTES:
    - This runs when the application starts up
    - Good place to initialize resources, load configuration, etc.
    - We can add logging, database connections, etc. here
    """
    print("StressSpec Web UI starting up...")
    
    # Create necessary directories
    uploads_dir = Path("uploads")
    logs_dir = Path("logs")
    
    uploads_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)
    
    print("✅ Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    
    BEGINNER NOTES:
    - This runs when the application shuts down
    - Good place to clean up resources, close connections, etc.
    - We can add cleanup tasks here
    """
    print("StressSpec Web UI shutting down...")
    print("✅ Application shutdown complete")

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"Starting StressSpec Web UI on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    uvicorn.run(
        "web.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
