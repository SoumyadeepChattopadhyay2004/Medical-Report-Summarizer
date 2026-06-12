"""
File Processing Module for Medical Report Summarizer
Handles extraction of text from various file formats (PDF, images, text files)
"""

import io
import re
import logging
from typing import Optional, Dict, Any
from pathlib import Path

# PDF processing
import PyPDF2
import pdfplumber

# Image processing and OCR
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class FileProcessor:
    """Process various file formats and extract text content"""
    
    def __init__(self):
        """Initialize file processor"""
        self.max_file_size = Config.MAX_FILE_SIZE
        self.allowed_extensions = Config.ALLOWED_EXTENSIONS
        
    def validate_file(self, file_obj, filename: str) -> Dict[str, Any]:
        """
        Validate uploaded file
        
        Args:
            file_obj: File object from upload
            filename: Name of the file
            
        Returns:
            Dictionary with validation results
        """
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            return {
                "valid": False,
                "error": f"File type {file_ext} not supported. Allowed types: {', '.join(self.allowed_extensions)}"
            }
        
        # Check file size
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(0)  # Reset to beginning
        
        if file_size > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            return {
                "valid": False,
                "error": f"File size exceeds maximum allowed size of {max_mb:.1f}MB"
            }
        
        if file_size == 0:
            return {
                "valid": False,
                "error": "File is empty"
            }
        
        return {
            "valid": True,
            "file_size": file_size,
            "file_extension": file_ext
        }
    
    def extract_text(self, file_obj, filename: str) -> Dict[str, Any]:
        """
        Extract text from file based on its type
        
        Args:
            file_obj: File object
            filename: Name of the file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        # Validate file first
        validation = self.validate_file(file_obj, filename)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"]
            }
        
        file_ext = validation["file_extension"]
        
        try:
            # Route to appropriate extraction method
            if file_ext == '.pdf':
                text = self._extract_from_pdf(file_obj)
            elif file_ext in {'.jpg', '.jpeg', '.png', '.tiff'}:
                text = self._extract_from_image(file_obj)
            elif file_ext == '.txt':
                text = self._extract_from_text(file_obj)
            elif file_ext == '.docx':
                text = self._extract_from_docx(file_obj)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type: {file_ext}"
                }
            
            # Clean and validate extracted text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text or len(cleaned_text.strip()) < 50:
                return {
                    "success": False,
                    "error": "Insufficient text extracted from file. Please ensure the file contains readable medical report content."
                }
            
            return {
                "success": True,
                "text": cleaned_text,
                "file_type": file_ext,
                "file_size": validation["file_size"],
                "text_length": len(cleaned_text)
            }
            
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to extract text: {str(e)}"
            }
    
    def _extract_from_pdf(self, file_obj) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_obj: PDF file object
            
        Returns:
            Extracted text
        """
        text = ""
        
        # Try pdfplumber first (better for complex PDFs)
        try:
            logger.info("Attempting PDF extraction with pdfplumber")
            file_obj.seek(0)
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                logger.info(f"Successfully extracted {len(text)} characters with pdfplumber")
                return text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}")
        
        # Fallback to PyPDF2
        try:
            logger.info("Attempting PDF extraction with PyPDF2")
            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_obj)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            if text.strip():
                logger.info(f"Successfully extracted {len(text)} characters with PyPDF2")
                return text
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
        
        # If both methods fail, try OCR on PDF (for scanned documents)
        if Config.ENABLE_OCR:
            try:
                logger.info("Attempting OCR extraction from PDF")
                file_obj.seek(0)
                # Convert PDF pages to images and OCR
                # This is a simplified approach; full implementation would use pdf2image
                text = "OCR extraction from PDF not fully implemented. Please use image files for scanned documents."
            except Exception as e:
                logger.error(f"OCR extraction from PDF failed: {str(e)}")
        
        return text
    
    def _extract_from_image(self, file_obj) -> str:
        """
        Extract text from image using OCR
        
        Args:
            file_obj: Image file object
            
        Returns:
            Extracted text
        """
        if not Config.ENABLE_OCR:
            raise ValueError("OCR is disabled. Please enable it in configuration.")
        
        try:
            logger.info("Extracting text from image using OCR")
            file_obj.seek(0)
            
            # Open image
            image = Image.open(file_obj)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            # Configure tesseract for better medical text recognition
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            logger.info(f"Successfully extracted {len(text)} characters from image")
            return text
            
        except Exception as e:
            logger.error(f"Error in OCR extraction: {str(e)}")
            raise ValueError(f"Failed to extract text from image: {str(e)}")
    
    def _extract_from_text(self, file_obj) -> str:
        """
        Extract text from plain text file
        
        Args:
            file_obj: Text file object
            
        Returns:
            File content as string
        """
        try:
            logger.info("Reading plain text file")
            file_obj.seek(0)
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    file_obj.seek(0)
                    text = file_obj.read().decode(encoding)
                    logger.info(f"Successfully read text file with {encoding} encoding")
                    return text
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail
            raise ValueError("Unable to decode text file with supported encodings")
            
        except Exception as e:
            logger.error(f"Error reading text file: {str(e)}")
            raise ValueError(f"Failed to read text file: {str(e)}")
    
    def _extract_from_docx(self, file_obj) -> str:
        """
        Extract text from DOCX file
        
        Args:
            file_obj: DOCX file object
            
        Returns:
            Extracted text
        """
        try:
            # Note: This requires python-docx library
            # For now, return a placeholder message
            logger.warning("DOCX extraction not fully implemented")
            return "DOCX file support requires python-docx library. Please convert to PDF or TXT format."
        except Exception as e:
            logger.error(f"Error extracting from DOCX: {str(e)}")
            raise ValueError(f"Failed to extract from DOCX: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause issues
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove multiple consecutive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_patient_info(self, text: str) -> Dict[str, Any]:
        """
        Extract patient information from report text
        
        Args:
            text: Medical report text
            
        Returns:
            Dictionary with patient information
        """
        patient_info = {
            "name": None,
            "age": None,
            "gender": None,
            "date": None,
            "id": None
        }
        
        try:
            # Extract age
            age_patterns = [
                r'Age[:\s]+(\d+)',
                r'(\d+)\s*(?:years?|yrs?|Y)',
                r'Age\s*[:\-]\s*(\d+)'
            ]
            for pattern in age_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    patient_info["age"] = int(match.group(1))
                    break
            
            # Extract gender
            gender_patterns = [
                r'Gender[:\s]+(Male|Female|M|F)',
                r'Sex[:\s]+(Male|Female|M|F)',
                r'\b(Male|Female)\b'
            ]
            for pattern in gender_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    gender = match.group(1).upper()
                    if gender in ['M', 'MALE']:
                        patient_info["gender"] = "Male"
                    elif gender in ['F', 'FEMALE']:
                        patient_info["gender"] = "Female"
                    break
            
            # Extract date
            date_patterns = [
                r'Date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'Date[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})'
            ]
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    patient_info["date"] = match.group(1)
                    break
            
            # Extract patient ID
            id_patterns = [
                r'Patient\s*ID[:\s]+([A-Z0-9]+)',
                r'ID[:\s]+([A-Z0-9]+)',
                r'Registration\s*No[:\s]+([A-Z0-9]+)'
            ]
            for pattern in id_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    patient_info["id"] = match.group(1)
                    break
            
        except Exception as e:
            logger.error(f"Error extracting patient info: {str(e)}")
        
        return patient_info
    
    def extract_test_values(self, text: str) -> list:
        """
        Extract test names and values from report text
        
        Args:
            text: Medical report text
            
        Returns:
            List of dictionaries containing test information
        """
        test_values = []
        
        try:
            # Pattern to match test results: Test Name: Value Unit
            # Examples: "Hemoglobin: 12.5 g/dL", "Glucose: 95 mg/dL"
            pattern = r'([A-Za-z\s]+)[:\s]+(\d+\.?\d*)\s*([a-zA-Z/%]+)?'
            
            matches = re.finditer(pattern, text)
            
            for match in matches:
                test_name = match.group(1).strip()
                value = float(match.group(2))
                unit = match.group(3) if match.group(3) else ""
                
                # Filter out likely false positives
                if len(test_name) > 3 and len(test_name) < 50:
                    test_values.append({
                        "test_name": test_name,
                        "value": value,
                        "unit": unit
                    })
            
        except Exception as e:
            logger.error(f"Error extracting test values: {str(e)}")
        
        return test_values

# Made with Bob
