#!/usr/bin/env python3
"""
PDF Paragraph Extraction Module

Core logic for extracting paragraphs from PDFs with metadata.
Used by the main implementation script.

Author: Jonathan Paige
Date: 2025
"""

import re
from pathlib import Path
from typing import List, Dict

try:
    import PyPDF2
except ImportError:
    raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")


class ParagraphExtractor:
    """Extract paragraphs from PDFs with metadata."""
    
    def __init__(self, min_paragraph_length: int = 50, max_paragraph_length: int = 5000):
        """
        Initialize extractor.
        
        Args:
            min_paragraph_length: Minimum characters for a valid paragraph
            max_paragraph_length: Maximum characters for a valid paragraph
        """
        self.min_length = min_paragraph_length
        self.max_length = max_paragraph_length
        self.paragraphs = []
        
    def extract_from_pdf(self, pdf_path: str, citation: str) -> List[Dict]:
        """
        Extract paragraphs from a single PDF.
        
        Args:
            pdf_path: Path to PDF file
            citation: Citation string for this document
            
        Returns:
            List of paragraph dictionaries with metadata
        """
        print(f"  Processing: {Path(pdf_path).name}")
        
        paragraphs = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Extract paragraphs from this page
                    page_paragraphs = self._split_into_paragraphs(text)
                    
                    # Add metadata to each paragraph
                    for para_num, para_text in enumerate(page_paragraphs, 1):
                        # Create unique ID
                        para_id = self._create_paragraph_id(citation, page_num + 1, para_num)
                        
                        paragraph = {
                            'paragraph_id': para_id,
                            'citation': citation,
                            'page': page_num + 1,  # 1-indexed
                            'paragraph_number': para_num,
                            'text': para_text,
                            'char_count': len(para_text),
                            'source_file': str(pdf_path)
                        }
                        
                        paragraphs.append(paragraph)
                
                print(f"    Extracted {len(paragraphs)} paragraphs from {total_pages} pages")
                
        except Exception as e:
            print(f"    Error: {e}")
            
        return paragraphs
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Clean text
        text = self._clean_text(text)
        
        # Split on double line breaks
        paragraphs = re.split(r'\n\s*\n+', text)
        
        # Filter and clean
        valid_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            
            # Skip if too short, too long, or header/footer
            if (len(para) < self.min_length or 
                len(para) > self.max_length or 
                self._is_header_or_footer(para)):
                continue
                
            valid_paragraphs.append(para)
        
        return valid_paragraphs
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Fix hyphenation at line breaks
        text = re.sub(r'-\n', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\r\n', '\n', text)
        
        return text
    
    def _is_header_or_footer(self, text: str) -> bool:
        """Heuristic to identify headers/footers."""
        if len(text) < 30:
            return True
        
        # Just page numbers
        if re.match(r'^\d+$', text.strip()):
            return True
        
        # Common header/footer patterns
        header_patterns = [
            r'^\d+\s*$',
            r'^Page \d+',
            r'^\d+\s+of\s+\d+',
            r'^Chapter \d+',
        ]
        
        for pattern in header_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _create_paragraph_id(self, citation: str, page: int, para_num: int) -> str:
        """Create unique paragraph ID."""
        citation_key = re.sub(r'[^\w-]', '_', citation)
        return f"{citation_key}_p{page}_para{para_num}"
    
    def extract_from_multiple_pdfs(self, pdf_configs: List[Dict]) -> List[Dict]:
        """Extract paragraphs from multiple PDFs."""
        all_paragraphs = []
        
        for config in pdf_configs:
            pdf_path = config['path']
            citation = config['citation']
            
            paragraphs = self.extract_from_pdf(pdf_path, citation)
            all_paragraphs.extend(paragraphs)
        
        self.paragraphs = all_paragraphs
        return all_paragraphs
