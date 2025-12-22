# Resume Filtering System

A web-based resume filtering application that allows recruiters and HR professionals to efficiently manage and search through multiple resumes using keyword-based filtering.

## 📋 Overview

This system provides a simple yet powerful interface to upload, store, and filter resumes based on specific keywords such as skills, job roles, and technologies. Built with FastAPI for high performance and a clean HTML/CSS frontend for ease of use.

---

## ✨ Features

- **Multi-Resume Upload**: Upload multiple resumes in PDF or DOCX format
- **Keyword-Based Filtering**: Search resumes using skills, technologies, or job-related keywords
- **Case-Insensitive Search**: Ensures accurate results regardless of keyword casing
- **Multiple Keyword Support**: Filter using multiple keywords simultaneously
- **Clean and Intuitive UI**: Simple, user-friendly interface for all users
- **Fast REST API**: FastAPI-powered backend for quick response times
- **Local Storage**: Resumes stored securely on the server

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python, FastAPI |
| **Frontend** | HTML, CSS, JavaScript |
| **Resume Parsing** | PyPDF2 (PDF files), python-docx (DOCX files) |
| **Storage** | Local file system / SQLite (optional) |
| **Server** | Uvicorn (ASGI server) |

---

## 📁 Project Structure

```
Resume-Filtering-System/
│
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
│
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   │   └── styles.css     # Frontend styling
│   └── js/
│       └── script.js      # Frontend logic (optional)
│
├── templates/             # HTML templates
│   └── index.html         # Main UI page
│
├── uploads/               # Directory for uploaded resumes
│   └── (resume files)
│
└── utils/                 # Utility functions
    └── parser.py          # Resume parsing logic
```

---

## 🚀 Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/resume-filtering-system.git
cd resume-filtering-system
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
```
fastapi
uvicorn[standard]
python-multipart
PyPDF2
python-docx
```

### Step 4: Create Required Directories

```bash
mkdir uploads
```

---

## ▶️ How to Run the Project

### Start the FastAPI Server

```bash
uvicorn main:app --reload
```

The application will be available at: **http://127.0.0.1:8000**

### Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🔌 API Endpoints

### 1. **GET /** 
- **Description**: Serves the main HTML page
- **Response**: HTML interface

### 2. **POST /upload**
- **Description**: Upload multiple resume files
- **Request**: Multipart form data with file uploads
- **Accepted Formats**: PDF, DOCX
- **Response**: 
  ```json
  {
    "message": "Resumes uploaded successfully",
    "files": ["resume1.pdf", "resume2.docx"]
  }
  ```

### 3. **POST /filter**
- **Description**: Filter resumes based on keywords
- **Request Body**:
  ```json
  {
    "keywords": ["python", "machine learning", "fastapi"]
  }
  ```
- **Response**:
  ```json
  {
    "matched_resumes": [
      {
        "filename": "john_doe.pdf",
        "matched_keywords": ["python", "fastapi"],
        "score": 2
      }
    ]
  }
  ```

### 4. **GET /resumes**
- **Description**: Get list of all uploaded resumes
- **Response**:
  ```json
  {
    "resumes": ["resume1.pdf", "resume2.docx", "resume3.pdf"]
  }
  ```

---

## 🔍 How Resume Filtering Works

The resume filtering system follows these steps:

1. **Upload**: Users upload resumes (PDF/DOCX format) through the web interface
2. **Storage**: Files are saved in the `uploads/` directory on the server
3. **Parsing**: When a filter request is made, the system:
   - Reads each resume file
   - Extracts text content using PyPDF2 (for PDFs) or python-docx (for DOCX)
4. **Keyword Matching**: 
   - Searches for user-provided keywords in the extracted text
   - Performs case-insensitive matching
   - Supports multiple keywords
5. **Ranking**: Resumes are ranked based on the number of matched keywords
6. **Results**: Returns a list of matching resumes with their match scores

**Example:**
- Keywords: `["Python", "Django", "REST API"]`
- Resume contains: "Experienced Python developer with Django and REST API experience"
- Result: ✅ Match (3/3 keywords found)

---

## 📸 Screenshots

> **Note**: Add screenshots of your application here

### Home Page
![Home Page](screenshots/home.png)

### Upload Interface
![Upload Interface](screenshots/upload.png)

### Filter Results
![Filter Results](screenshots/results.png)

---

## 🔮 Future Improvements

- [ ] Add user authentication and authorization
- [ ] Implement database storage (PostgreSQL/MongoDB) for scalability
- [ ] Advanced filtering with ranking algorithms (TF-IDF, NLP)
- [ ] Resume parsing improvements using AI/ML models
- [ ] Export filtered results to CSV/Excel
- [ ] Email integration for shortlisted candidates
- [ ] Support for more file formats (TXT, RTF)
- [ ] Resume preview functionality
- [ ] Advanced search filters (experience years, education, location)
- [ ] Dark mode support
- [ ] Responsive mobile design
- [ ] Resume analytics dashboard

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**

- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- FastAPI Documentation
- Python Resume Parsing Libraries Community
- Open Source Contributors

---

## 📞 Support

If you encounter any issues or have questions, please:
- Open an issue on GitHub
- Contact via email
- Check the documentation

---

**⭐ If you find this project useful, please consider giving it a star!**
