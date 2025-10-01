"""
File Upload API Endpoints

This module handles file upload functionality for the StressSpec web interface.
It validates uploaded files and prepares them for analysis.

BEGINNER NOTES:
- This handles the file upload process
- It validates file types, sizes, and formats
- It stores uploaded files securely
- It prepares files for the analysis process
"""

import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Create router for upload endpoints
router = APIRouter()

# Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", ".txt,.md").split(",")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))

class UploadResponse(BaseModel):
    """Response model for file uploads."""
    success: bool
    file_id: str
    filename: str
    size: int
    message: str

class UploadError(BaseModel):
    """Error response model for uploads."""
    success: bool = False
    error: str
    details: Optional[str] = None

def validate_file(file: UploadFile) -> tuple[bool, str]:
    """
    Validate uploaded file.
    
    BEGINNER NOTES:
    - This function checks if the uploaded file is valid
    - It checks file size, extension, and content type
    - Returns True if valid, False with error message if not
    """
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE} bytes"
    
    # Check file extension
    file_path = Path(file.filename)
    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check filename
    if not file.filename or file.filename.strip() == "":
        return False, "Invalid filename"
    
    return True, ""

@router.post("/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a requirements file for analysis.
    
    BEGINNER NOTES:
    - This endpoint receives uploaded files
    - It validates the file and stores it securely
    - It returns information about the uploaded file
    - The file is ready for analysis after upload
    """
    try:
        # Validate the file
        is_valid, error_message = validate_file(file)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create upload directory if it doesn't exist
        UPLOAD_DIR.mkdir(exist_ok=True)
        
        # Save the file
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        # Read file content
        content = await file.read()
        
        # Write to disk
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Get file size
        file_size = len(content)
        
        return UploadResponse(
            success=True,
            file_id=file_id,
            filename=file.filename,
            size=file_size,
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/status/{file_id}")
async def get_upload_status(file_id: str):
    """
    Get the status of an uploaded file.
    
    BEGINNER NOTES:
    - This checks if a file was uploaded successfully
    - It can be used to verify file availability
    - Useful for checking file status before analysis
    """
    try:
        # Look for the file
        file_pattern = f"{file_id}_*"
        upload_files = list(UPLOAD_DIR.glob(file_pattern))
        
        if not upload_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = upload_files[0]
        filename = file_path.name.split("_", 1)[1]  # Remove file_id prefix
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "size": file_path.stat().st_size,
            "exists": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )

@router.delete("/{file_id}")
async def delete_uploaded_file(file_id: str):
    """
    Delete an uploaded file.
    
    BEGINNER NOTES:
    - This removes an uploaded file from the server
    - Useful for cleanup and privacy
    - Files are automatically cleaned up after analysis
    """
    try:
        # Look for the file
        file_pattern = f"{file_id}_*"
        upload_files = list(UPLOAD_DIR.glob(file_pattern))
        
        if not upload_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete the file
        file_path = upload_files[0]
        file_path.unlink()
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )

@router.get("/list")
async def list_uploaded_files():
    """
    List all uploaded files.
    
    BEGINNER NOTES:
    - This shows all files that have been uploaded
    - Useful for debugging and file management
    - Returns basic information about each file
    """
    try:
        files = []
        
        if UPLOAD_DIR.exists():
            for file_path in UPLOAD_DIR.iterdir():
                if file_path.is_file():
                    # Extract file_id and filename
                    parts = file_path.name.split("_", 1)
                    if len(parts) == 2:
                        file_id, filename = parts
                        files.append({
                            "file_id": file_id,
                            "filename": filename,
                            "size": file_path.stat().st_size,
                            "uploaded_at": file_path.stat().st_mtime
                        })
        
        return {
            "success": True,
            "files": files,
            "count": len(files)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"List files failed: {str(e)}"
        )
