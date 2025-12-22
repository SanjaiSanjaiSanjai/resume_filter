# Deployment Guide - Resume Filtering System

## ⚠️ Important Note About Vercel Deployment

Vercel uses **serverless functions** which are stateless. This means:

- ❌ **File uploads won't persist** between requests
- ❌ **Local storage (`uploads/` directory) won't work** on Vercel
- ❌ **Each request runs in a fresh container**

### Recommended Solutions

To deploy this application to production, you have two options:

#### Option 1: Use Cloud Storage (Recommended for Vercel)
- Replace local file storage with **AWS S3**, **Google Cloud Storage**, or **Azure Blob Storage**
- Modify the upload endpoint to save files to cloud storage
- Update the parser to read files from cloud storage
- Consider using a database (PostgreSQL, MongoDB) to store metadata

#### Option 2: Deploy to a Traditional Server
- **Heroku** - Supports persistent file systems with add-ons
- **DigitalOcean App Platform** - Full server support
- **Railway** - Modern deployment platform
- **AWS EC2 / Google Compute Engine** - Full virtual machines
- **Docker + Any Cloud Provider** - Containerized deployment

---

## 🚀 Vercel Deployment (With Limitations)

If you still want to deploy to Vercel for testing/demo purposes (files won't persist):

### Prerequisites

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Create a Vercel account at https://vercel.com

### Deployment Steps

1. **Login to Vercel**
```bash
vercel login
```

2. **Deploy**
```bash
vercel
```

3. **Follow the prompts:**
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - What's your project's name? `resume-filtering-system`
   - In which directory is your code located? `./`
   - Want to override settings? **N**

4. **Deploy to Production**
```bash
vercel --prod
```

### Files Created for Vercel

- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless function entry point
- `.vercelignore` - Files to exclude from deployment
- `runtime.txt` - Python version specification

### Limitations on Vercel

1. **No File Persistence**: Uploaded files are lost after each request
2. **Cold Starts**: First request may be slow
3. **Size Limits**: 
   - Max function size: 50MB
   - Max request body: 4.5MB
4. **Execution Time**: Max 10 seconds for Hobby plan

---

## 🐳 Docker Deployment (Recommended)

Docker provides a consistent environment and works with any cloud provider.

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t resume-filter .

# Run container
docker run -p 8000:8000 resume-filter
```

### Deploy to Cloud

- **Docker Hub** + **DigitalOcean App Platform**
- **Google Cloud Run**
- **AWS ECS/Fargate**
- **Azure Container Instances**

---

## 🚂 Railway Deployment (Easy & Free Tier)

Railway is perfect for this application - it supports file uploads and databases.

### Steps

1. Visit https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Python and deploys
6. Access your app at the provided URL

### Configuration

Add a `railway.json` (optional):
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🟣 Heroku Deployment

### Prerequisites

```bash
# Install Heroku CLI
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
```

### Files Needed

**Procfile**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**runtime.txt**
```
python-3.9.18
```

### Deploy

```bash
# Login
heroku login

# Create app
heroku create resume-filtering-system

# Deploy
git push heroku main

# Open app
heroku open
```

---

## 🔧 Making the App Cloud-Ready

To use cloud storage instead of local files:

### 1. Install AWS S3 SDK

```bash
pip install boto3
```

### 2. Update `utils/parser.py`

```python
import boto3
from io import BytesIO

s3_client = boto3.client('s3')
BUCKET_NAME = 'your-bucket-name'

def upload_to_s3(file, filename):
    s3_client.upload_fileobj(file, BUCKET_NAME, filename)
    
def download_from_s3(filename):
    buffer = BytesIO()
    s3_client.download_fileobj(BUCKET_NAME, filename, buffer)
    buffer.seek(0)
    return buffer
```

### 3. Update `main.py` Upload Endpoint

```python
@app.post("/upload")
async def upload_resumes(files: List[UploadFile] = File(...)):
    for file in files:
        upload_to_s3(file.file, file.filename)
```

---

## 📊 Database Integration

For production, store metadata in a database:

### PostgreSQL with SQLAlchemy

```bash
pip install sqlalchemy psycopg2-binary
```

```python
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    s3_key = Column(String)
    uploaded_at = Column(String)
```

---

## 🌐 Environment Variables

For production deployments, use environment variables:

**.env** (local development)
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_BUCKET_NAME=your_bucket
DATABASE_URL=postgresql://user:pass@host:5432/db
```

Update `main.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
DATABASE_URL = os.getenv('DATABASE_URL')
```

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] Replace local file storage with cloud storage (S3, GCS, etc.)
- [ ] Add database for metadata storage
- [ ] Set up environment variables
- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add CORS configuration
- [ ] Set up logging and monitoring
- [ ] Configure HTTPS/SSL
- [ ] Add health check endpoint
- [ ] Set up backup strategy
- [ ] Configure domain name
- [ ] Add error tracking (Sentry, etc.)

---

## 🎯 Quick Comparison

| Platform | File Storage | Database | Free Tier | Difficulty |
|----------|-------------|----------|-----------|------------|
| **Vercel** | ❌ No | ❌ External | ✅ Yes | Easy |
| **Railway** | ✅ Yes | ✅ Yes | ✅ Yes* | Easy |
| **Heroku** | ⚠️ Ephemeral | ✅ Add-ons | ✅ Yes* | Easy |
| **DigitalOcean** | ✅ Yes | ✅ Yes | ❌ No | Medium |
| **AWS/GCP** | ✅ Yes | ✅ Yes | ✅ Limited | Hard |
| **Docker** | ✅ Yes | ✅ Yes | N/A | Medium |

*Limited hours/resources

---

## 🆘 Support

For deployment issues:
- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app
- Heroku: https://devcenter.heroku.com
- Docker: https://docs.docker.com

---

**Recommendation:** For this application, use **Railway** or **DigitalOcean** for the easiest production deployment with full file storage support.
