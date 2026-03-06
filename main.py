"""
Resume Filtering System - FastAPI Backend
Main application file with API endpoints
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from typing import List, Optional
import os
import shutil
from pydantic import BaseModel

from utils.parser import ResumeParser

# Base directory for templates (static files served by Vercel CDN from public/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Initialize FastAPI app
app = FastAPI(
    title="Resume Filtering System",
    description="A web-based resume filtering application",
    version="1.0.0"
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions so the serverless process doesn't crash (avoids FUNCTION_INVOCATION_FAILED)."""
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__},
    )

# CORS configuration - simplified to avoid Content-Length issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session configuration (for signup) - re-enabled with simplified config
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("RESUME_FILTER_SECRET_KEY", "change-this-secret"),
)

# Static files
# - On Vercel: static assets are served from the public/ directory by the platform.
# - Locally: mount /static from the source static/ folder so changes to
#   static/js and static/css are reflected immediately during development.
IS_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not IS_VERCEL and os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates (absolute path for Vercel serverless)
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Constants
# Upload base directory:
# - Vercel: only /tmp is writable
# - Local dev: keep uploads inside the repo so "view" works reliably on Windows/macOS/Linux
UPLOAD_BASE_DIR = "/tmp/uploads" if IS_VERCEL else os.path.join(BASE_DIR, "tmp", "uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

# Simple user management (in-memory)
REGISTERED_USERS: dict[str, str] = {}

# Ensure upload base directory exists (skip if not writable in some envs)
try:
    os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)
except OSError:
    pass


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


def _get_session_username(request: Request) -> Optional[str]:
    user = request.session.get("user") or {}
    username = user.get("username")
    if isinstance(username, str) and username.strip():
        return username.strip()
    return None


def _require_username(request: Request) -> str:
    username = _get_session_username(request)
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return username


def _user_upload_dir(username: str) -> str:
    """
    Per-user upload directory. This prevents one user's resumes from being visible to others.
    """
    # Keep it simple: directory name is username. (If you later add real auth, use a stable user id.)
    return os.path.join(UPLOAD_BASE_DIR, username)


def _ensure_user_upload_dir(username: str) -> str:
    path = _user_upload_dir(username)
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        # If the runtime can't create folders, treat as server error.
        raise HTTPException(status_code=500, detail="Upload storage is not available")
    return path


def get_uploaded_resumes(user_dir: str) -> List[str]:
    """Get list of all uploaded resume files"""
    if not os.path.exists(user_dir):
        return []
    
    files = []
    for filename in os.listdir(user_dir):
        if is_allowed_file(filename):
            files.append(filename)
    return files


def _safe_resume_path(user_dir: str, filename: str) -> str:
    """
    Resolve a resume filename to an absolute path inside the user's upload directory.
    Prevents path traversal and blocks unsupported extensions.
    """
    if not filename or filename != os.path.basename(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not is_allowed_file(filename):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    return os.path.join(user_dir, filename)


# API Endpoints
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Render the signup page"""
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})


@app.post("/signup")
async def signup(request: Request, username: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    """Handle signup form submission"""
    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Passwords do not match"},
            status_code=400,
        )

    if not username.strip():
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Username is required"},
            status_code=400,
        )

    if username in REGISTERED_USERS:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Username already exists"},
            status_code=400,
        )

    # Store user and log them in
    REGISTERED_USERS[username] = password
    request.session["user"] = {"username": username}
    return RedirectResponse(url="/", status_code=302)


@app.get("/logout")
async def logout(request: Request):
    """Log the user out and redirect to signup page"""
    # Delete this user's uploaded resumes on logout (fresh start for the next session).
    username = _get_session_username(request)
    if username:
        user_dir = _user_upload_dir(username)
        try:
            shutil.rmtree(user_dir, ignore_errors=True)
        except Exception:
            # If deletion fails, still allow logout.
            pass
    request.session.clear()
    return RedirectResponse(url="/signup", status_code=302)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML page (protected)"""
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/signup", status_code=302)

    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # Avoid noisy 404s in local logs; you can replace this with a real icon later.
    return JSONResponse(status_code=204, content=None)


@app.post("/upload")
async def upload_resumes(request: Request, files: List[UploadFile] = File(...)):
    """
    Upload multiple resume files
    
    Args:
        files: List of files to upload
        
    Returns:
        Success message with list of uploaded files
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Scope uploads to the logged-in user
    username = _require_username(request)
    user_dir = _ensure_user_upload_dir(username)
    
    uploaded_files = []
    
    for file in files:
        # Validate file extension
        if not is_allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} has invalid extension. Only PDF and DOCX allowed."
            )
        
        # Save file
        file_path = os.path.join(user_dir, file.filename)
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
async def filter_resumes(request: Request, filter_request: FilterRequest):
    """
    Filter resumes based on keywords
    
    Args:
        filter_request: Contains list of keywords to search for
        
    Returns:
        List of matched resumes with scores
    """
    if not filter_request.keywords:
        raise HTTPException(status_code=400, detail="No keywords provided")
    
    # Filter within this user's uploads only
    username = _require_username(request)
    user_dir = _ensure_user_upload_dir(username)

    resumes = get_uploaded_resumes(user_dir)
    
    if not resumes:
        return JSONResponse(
            content={
                "message": "No resumes found",
                "matched_resumes": [],
                "total_resumes": 0
            }
        )
    
    matched_resumes = []
    
    for filename in resumes:
        file_path = os.path.join(user_dir, filename)
        
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
    
    response_data = {
        "message": f"Found {len(matched_resumes)} matching resumes",
        "matched_resumes": matched_resumes,
        "total_resumes": len(resumes),
        "keywords_searched": filter_request.keywords
    }
    
    # Use JSONResponse without explicit Content-Length to allow chunked encoding
    return JSONResponse(content=response_data)


@app.get("/resumes")
async def get_resumes(request: Request):
    """
    Get list of all uploaded resumes
    
    Returns:
        List of resume filenames
    """
    username = _require_username(request)
    user_dir = _ensure_user_upload_dir(username)
    resumes = get_uploaded_resumes(user_dir)
    
    return {
        "resumes": resumes,
        "count": len(resumes)
    }


@app.get("/resumes/view/{filename}")
async def view_resume(request: Request, filename: str):
    """
    Serve a resume file for viewing (PDFs open inline in browser).

    Security:
    - Requires a logged-in session (same as the main UI).
    - Prevents path traversal by restricting to basename-only filenames.
    """
    username = _get_session_username(request)
    if not username:
        # For browser/iframe usage, redirecting is clearer than a JSON 401.
        return RedirectResponse(url="/signup", status_code=302)

    user_dir = _ensure_user_upload_dir(username)
    file_path = _safe_resume_path(user_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume not found")

    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    media_type = "application/pdf" if ext == ".pdf" else "application/octet-stream"

    # Use streaming response to avoid Content-Length issues
    from fastapi.responses import StreamingResponse
    import io
    
    def iterfile():
        with open(file_path, mode="rb") as file_like:
            yield from file_like

    headers = {
        "Content-Disposition": f'inline; filename="{filename}"',
        "Cache-Control": "no-store",
    }
    
    return StreamingResponse(
        iterfile(), 
        media_type=media_type, 
        headers=headers
    )


@app.delete("/resumes/{filename}")
async def delete_resume(request: Request, filename: str):
    """
    Delete a specific resume file
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        Success message
    """
    username = _require_username(request)
    user_dir = _ensure_user_upload_dir(username)
    file_path = _safe_resume_path(user_dir, filename)
    
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
