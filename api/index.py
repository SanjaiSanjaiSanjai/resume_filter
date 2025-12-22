"""
Vercel serverless function entry point
This wraps the FastAPI application for Vercel deployment
"""

from main import app

# Vercel expects a handler
handler = app
