"""
Resume Filtering System - FastAPI Backend
Main application file with API endpoints
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import List
import os
import shutil
from pydantic import BaseModel

from utils.parser import ResumeParser


# Initialize FastAPI app
app = FastAPI(
    title="Resume Filtering System",
    description="A web-based resume filtering application",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Constants
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Pydantic models
class FilterRequest(BaseModel):
    keywords: List[str]


class ResumeMatch(BaseModel):
    filename: str
    matched_keywords: List[str]
    score: int


# Helper functions
def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


def get_uploaded_resumes() -> List[str]:
    """Get list of all uploaded resume files"""
    if not os.path.exists(UPLOAD_DIR):
        return []
    
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        if is_allowed_file(filename):
            files.append(filename)
    return files


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_resumes(files: List[UploadFile] = File(...)):
    """
    Upload multiple resume files
    
    Args:
        files: List of files to upload
        
    Returns:
        Success message with list of uploaded files
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    
    for file in files:
        # Validate file extension
        if not is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} has invalid extension. Only PDF and DOCX allowed."
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append(file.filename)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save file {file.filename}: {str(e)}"
            )
    
    return JSONResponse({
        "message": "Resumes uploaded successfully",
        "files": uploaded_files,
        "count": len(uploaded_files)
    })


@app.post("/filter", response_model=dict)
async def filter_resumes(filter_request: FilterRequest):
    """
    Filter resumes based on keywords
    
    Args:
        filter_request: Contains list of keywords to search for
        
    Returns:
        List of matched resumes with scores
    """
    if not filter_request.keywords:
        raise HTTPException(status_code=400, detail="No keywords provided")
    
    resumes = get_uploaded_resumes()
    
    if not resumes:
        return {
            "message": "No resumes found",
            "matched_resumes": [],
            "total_resumes": 0
        }
    
    matched_resumes = []
    
    for filename in resumes:
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Extract text from resume
        text = ResumeParser.extract_text(file_path)
        
        if text:
            # Search for keywords
            result = ResumeParser.search_keywords(text, filter_request.keywords)
            
            # Only include resumes with at least one match
            if result["score"] > 0:
                matched_resumes.append({
                    "filename": filename,
                    "matched_keywords": result["matched_keywords"],
                    "score": result["score"]
                })
    
    # Sort by score (highest first)
    matched_resumes.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "message": f"Found {len(matched_resumes)} matching resumes",
        "matched_resumes": matched_resumes,
        "total_resumes": len(resumes),
        "keywords_searched": filter_request.keywords
    }


@app.get("/resumes")
async def get_resumes():
    """
    Get list of all uploaded resumes
    
    Returns:
        List of resume filenames
    """
    resumes = get_uploaded_resumes()
    
    return {
        "resumes": resumes,
        "count": len(resumes)
    }


@app.delete("/resumes/{filename}")
async def delete_resume(filename: str):
    """
    Delete a specific resume file
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        Success message
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume not found")
    
    try:
        os.remove(file_path)
        return {"message": f"Resume {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete resume: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Resume Filtering System is running"
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
