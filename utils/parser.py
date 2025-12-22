"""
Resume Parser Utility
Extracts text content from PDF and DOCX files
"""

import os
from typing import Optional
import PyPDF2
from docx import Document


class ResumeParser:
    """Handles parsing of resume files in PDF and DOCX formats"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Optional[str]:
        """
        Extract text content from a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from PDF {file_path}: {e}")
            return None
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> Optional[str]:
        """
        Extract text content from a DOCX file
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from DOCX {file_path}: {e}")
            return None
    
    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """
        Extract text from resume file (auto-detects format)
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Extracted text or None if extraction fails
        """
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        
        if extension == '.pdf':
            return ResumeParser.extract_text_from_pdf(file_path)
        elif extension == '.docx':
            return ResumeParser.extract_text_from_docx(file_path)
        else:
            print(f"Unsupported file format: {extension}")
            return None
    
    @staticmethod
    def search_keywords(text: str, keywords: list) -> dict:
        """
        Search for keywords in text (case-insensitive)
        
        Args:
            text: Text to search in
            keywords: List of keywords to search for
            
        Returns:
            Dictionary with matched keywords and match count
        """
        if not text:
            return {"matched_keywords": [], "score": 0}
        
        text_lower = text.lower()
        matched = []
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matched.append(keyword)
        
        return {
            "matched_keywords": matched,
            "score": len(matched)
        }
