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

# Optional: Try to import pdfminer for better extraction
try:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LAParams, LTTextContainer, LTTextBox, LTTextLine
    HAS_PDFMINER = True
except ImportError:
    HAS_PDFMINER = False


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
        
        # Use pdfminer if available (best text extraction with layout analysis)
        if HAS_PDFMINER:
            return self._extract_with_pdfminer(pdf_path, citation)
        else:
            return self._extract_with_pypdf2(pdf_path, citation)
    
    def _extract_with_pdfminer(self, pdf_path: str, citation: str) -> List[Dict]:
        """
        Extract using pdfminer.six - excellent paragraph detection with layout analysis.
        
        pdfminer preserves the PDF layout structure and can identify text blocks,
        which correspond much better to actual paragraphs than simple text extraction.
        """
        paragraphs = []
        
        try:
            # LAParams controls layout analysis
            # line_margin: max spacing between lines in same paragraph
            # word_margin: max spacing between words
            # boxes_flow: text flow detection (-1.0 to 1.0, None for disable)
            laparams = LAParams(
                line_margin=0.5,      # Lines closer than this are same paragraph
                word_margin=0.1,      # Word spacing
                boxes_flow=None,       # no text flow detection.  
                detect_vertical=False # Don't detect vertical text
            )
            
            page_num = 0
            for page_layout in extract_pages(pdf_path, laparams=laparams):
                page_num += 1
                para_num = 1
                
                # Extract text containers (these are usually paragraphs)
                for element in page_layout:
                    # LTTextBox represents a text block (usually a paragraph)
                    if isinstance(element, LTTextContainer):
                        text = element.get_text().strip()
                        
                        # Skip if too short or looks like header/footer
                        if (len(text) < self.min_length or 
                            len(text) > self.max_length or
                            self._is_header_or_footer(text)):
                            continue
                        
                        # Clean up hyphenation and whitespace
                        text = self._clean_text(text)
                        
                        # Check again after cleaning
                        if len(text) < self.min_length:
                            continue
                        
                        para_id = self._create_paragraph_id(citation, page_num, para_num)
                        
                        paragraph = {
                            'paragraph_id': para_id,
                            'citation': citation,
                            'page': page_num,
                            'paragraph_number': para_num,
                            'text': text,
                            'char_count': len(text),
                            'source_file': str(pdf_path)
                        }
                        
                        paragraphs.append(paragraph)
                        para_num += 1
            
            print(f"    Extracted {len(paragraphs)} paragraphs from {page_num} pages (pdfminer)")
            
        except Exception as e:
            print(f"    Error with pdfminer: {e}")
            # Fallback to PyPDF2
            return self._extract_with_pypdf2(pdf_path, citation)
        
        return paragraphs
    
    def _extract_with_pypdf2(self, pdf_path: str, citation: str) -> List[Dict]:
        """Extract using PyPDF2 with improved paragraph detection."""
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
                
                print(f"    Extracted {len(paragraphs)} paragraphs from {total_pages} pages (PyPDF2)")
                
        except Exception as e:
            print(f"    Error: {e}")
            
        return paragraphs
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs using multiple strategies.
        
        Tries in order:
        1. Indentation-based splitting
        2. Blank line splitting
        3. Sentence-based chunking (fallback)
        """
        # Clean text
        text = self._clean_text(text)
        
        # Strategy 1: Split on blank lines or indentation
        paragraphs = self._split_by_structure(text)
        
        # If we got reasonable paragraphs, use them
        if paragraphs and len(paragraphs) > 1:
            avg_length = sum(len(p) for p in paragraphs) / len(paragraphs)
            if 100 < avg_length < 2000:  # Reasonable paragraph length
                return self._filter_paragraphs(paragraphs)
        
        # Strategy 2: Sentence-based chunking as fallback
        paragraphs = self._chunk_by_sentences(text)
        return self._filter_paragraphs(paragraphs)
    
    def _split_by_structure(self, text: str) -> List[str]:
        """Split by paragraph structure (indentation and blank lines)."""
        # Split on: double line breaks, or line break + 2+ spaces (indentation)
        paragraphs = re.split(r'\n\s*\n+|\n(?=\s{2,})', text)
        
        # Also split on patterns like:
        # - Line ending with period followed by capital letter on next line
        # - Line break before section headings (all caps, title case)
        result = []
        for para in paragraphs:
            # Further split if we detect new paragraphs within
            sub_paras = re.split(r'\.(?=\s+[A-Z][a-z]+)', para)
            result.extend(sub_paras)
        
        return [p.strip() for p in result if p.strip()]
    
    def _chunk_by_sentences(self, text: str, target_size: int = 800) -> List[str]:
        """
        Chunk text by sentences to target size.
        
        Args:
            text: Input text
            target_size: Target characters per chunk
        """
        # Split into sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds target, start new chunk
            if current_length + sentence_length > target_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Add remaining
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _filter_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """Filter paragraphs by length and content."""
        valid = []
        for para in paragraphs:
            para = para.strip()
            
            # Skip if too short, too long, or header/footer
            if (len(para) < self.min_length or 
                len(para) > self.max_length or 
                self._is_header_or_footer(para)):
                continue
            
            valid.append(para)
        
        return valid
    
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
