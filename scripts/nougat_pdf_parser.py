#!/usr/bin/env python3
"""
Nougat-Based PDF Parser Module

Uses Meta's Nougat (Neural Optical Understanding for Academic Documents)
to parse academic PDFs into clean markdown, then extract paragraphs.

Nougat is specifically trained on academic papers and excels at:
- Multi-column layouts
- Mathematical equations
- Tables and figures
- References and citations
- Complex formatting

Author: Jonathan Paige
Date: 2025
"""

import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import tempfile
import json

try:
    # Nougat can be run via command line or imported
    import nougat
    HAS_NOUGAT = True
except ImportError:
    HAS_NOUGAT = False


class NougatPDFParser:
    """Parse academic PDFs using Meta's Nougat model."""
    
    def __init__(
        self,
        min_paragraph_length: int = 400,  
        max_paragraph_length: int = 5000,
        model_tag: str = "0.1.0-small",  # or "0.1.0-base" for better quality
        batch_size: int = 1,
        use_gpu: bool = True
    ):
        """
        Initialize Nougat PDF parser.
        
        Args:
            min_paragraph_length: Minimum characters for valid paragraph
            max_paragraph_length: Maximum characters for valid paragraph
            model_tag: Nougat model version ("0.1.0-small" or "0.1.0-base")
            batch_size: Number of pages to process at once
            use_gpu: Use GPU if available (much faster)
        """
        self.min_length = min_paragraph_length
        self.max_length = max_paragraph_length
        self.model_tag = model_tag
        self.batch_size = batch_size
        self.use_gpu = use_gpu
        
        # Verify Nougat is installed
        self._verify_nougat()
    
    def _verify_nougat(self):
        """Check if Nougat is installed."""
        try:
            # Try running nougat command
            result = subprocess.run(
                ['nougat', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ Nougat is installed")
            else:
                raise Exception("Nougat command not working")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            print("✗ Nougat not found")
            print("\nTo install Nougat:")
            print("  pip install nougat-ocr")
            print("\nNote: First run will download ~1GB model")
            raise ImportError("Nougat not installed. Install with: pip install nougat-ocr")
    
    def extract_from_pdf(self, pdf_path: str, citation: str) -> List[Dict]:
        """
        Extract paragraphs from PDF using Nougat.
        
        Args:
            pdf_path: Path to PDF file
            citation: Citation string for this document
            
        Returns:
            List of paragraph dictionaries with metadata
        """
        print(f"\n  Processing: {Path(pdf_path).name}")
        print(f"  Running Nougat OCR (this may take a few minutes)...")
        
        # Create temporary directory for Nougat output
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run Nougat
            try:
                markdown_text = self._run_nougat(pdf_path, temp_path)
            except Exception as e:
                print(f"  ✗ Nougat processing failed: {e}")
                return []
            
            if not markdown_text:
                print(f"  ✗ No text extracted")
                return []
            
            print(f"  ✓ Extracted {len(markdown_text)} characters")
            
            # Parse markdown into paragraphs
            paragraphs = self._parse_markdown_to_paragraphs(
                markdown_text,
                citation,
                pdf_path
            )
            
            print(f"  ✓ Found {len(paragraphs)} paragraphs\n")
            return paragraphs
    
    def _run_nougat(self, pdf_path: str, output_dir: Path) -> str:
        """
        Run Nougat command-line tool on PDF.
        
        Returns:
            Markdown text extracted from PDF
        """
        # Build nougat command
        cmd = [
            'nougat',
            str(pdf_path),
            '-o', str(output_dir),
            '--model', self.model_tag,
            '--batchsize', str(self.batch_size),
            '--markdown'  # Output as markdown
        ]
        
        # Add GPU flag if not using GPU
        if not self.use_gpu:
            cmd.append('--no-cuda')
        
        # Run nougat
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Nougat failed: {result.stderr}")
            
            # Find output file (Nougat creates .mmd file)
            pdf_name = Path(pdf_path).stem
            output_files = list(output_dir.glob(f"{pdf_name}.mmd"))
            
            if not output_files:
                raise Exception("No output file created")
            
            # Read markdown content
            with open(output_files[0], 'r', encoding='utf-8') as f:
                return f.read()
                
        except subprocess.TimeoutExpired:
            raise Exception("Nougat timed out (>10 minutes)")
        except Exception as e:
            raise Exception(f"Nougat error: {e}")
    
    def _parse_markdown_to_paragraphs(
        self,
        markdown_text: str,
        citation: str,
        pdf_path: str
    ) -> List[Dict]:
        """
        Parse Nougat markdown output into clean paragraphs.
        
        Nougat outputs markdown with:
        - Headers (# ## ###)
        - Paragraphs separated by blank lines
        - Math equations in LaTeX
        - Tables
        - References
        """
        paragraphs = []
        para_num = 1
        
        # Clean the markdown
        cleaned_text = self._clean_nougat_markdown(markdown_text)
        
        # Split into sections by blank lines
        sections = re.split(r'\n\s*\n+', cleaned_text)
        
        # Merge sections that appear to be continuations
        merged_sections = self._merge_paragraph_fragments(sections)
        
        for section in merged_sections:
            section = section.strip()
            
            # Skip headers (lines starting with #)
            if section.startswith('#'):
                continue
            
            # Skip if too short
            if len(section) < self.min_length:
                continue
            
            # Handle overly long sections
            if len(section) > self.max_length:
                # Split into chunks
                chunks = self._split_long_paragraph(section)
                for chunk in chunks:
                    if len(chunk) >= self.min_length:
                        para_id = self._create_paragraph_id(citation, para_num)
                        paragraphs.append({
                            'paragraph_id': para_id,
                            'citation': citation,
                            'page': None,
                            'paragraph_number': para_num,
                            'text': chunk,
                            'char_count': len(chunk),
                            'source_file': str(pdf_path)
                        })
                        para_num += 1
                continue
            
            # Skip if looks like a table (lots of | characters)
            if section.count('|') > 5:
                continue
            
            # Skip if looks like references section
            if self._is_reference_section(section):
                continue
            
            # Skip if mostly LaTeX math
            if self._is_mostly_math(section):
                continue
            
            # Create paragraph entry
            para_id = self._create_paragraph_id(citation, para_num)
            
            paragraph = {
                'paragraph_id': para_id,
                'citation': citation,
                'page': None,  # Nougat doesn't preserve page numbers easily
                'paragraph_number': para_num,
                'text': section,
                'char_count': len(section),
                'source_file': str(pdf_path)
            }
            
            paragraphs.append(paragraph)
            para_num += 1
        
        return paragraphs
    
    def _merge_paragraph_fragments(self, sections: List[str]) -> List[str]:
        """
        Merge sections that appear to be paragraph fragments.
        
        Academic papers often have paragraph breaks that don't align with
        semantic boundaries. This aggressively merges fragments.
        """
        merged = []
        i = 0
        
        while i < len(sections):
            current = sections[i].strip()
            
            # Skip empty sections
            if not current:
                i += 1
                continue
            
            # Look ahead to see if we should merge multiple sections
            while i < len(sections) - 1:
                next_section = sections[i + 1].strip()
                
                if not next_section:
                    i += 1
                    continue
                
                # Aggressive merge conditions:
                should_merge = False
                
                # 1. Current doesn't end with sentence punctuation
                if not re.search(r'[.!?]$', current):
                    should_merge = True
                
                # 2. Current is short (< 400 chars) - likely a fragment
                elif len(current) < 400:
                    should_merge = True
                
                # 3. Next starts with lowercase (clear continuation)
                elif next_section and next_section[0].islower():
                    should_merge = True
                
                # 4. Current ends with connecting words (and, or, but, etc.)
                elif re.search(r'\b(and|or|but|which|that|while|with|from|to)\s*$', current, re.IGNORECASE):
                    should_merge = True
                
                if should_merge:
                    # Merge with next section
                    current = current + ' ' + next_section
                    i += 1  # Move to next section
                else:
                    # Don't merge - stop looking ahead
                    break
            
            # Add the (possibly merged) paragraph
            if current:
                merged.append(current)
            
            i += 1
        
        return merged
    
    def _clean_nougat_markdown(self, text: str) -> str:
        """Clean Nougat markdown output."""
        # Remove excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove Nougat metadata markers
        text = re.sub(r'\[FOOTNOTE:.*?\]', '', text)
        text = re.sub(r'\[FIGURE:.*?\]', '', text)
        
        # Clean up inline LaTeX that's not in math mode
        # (preserve math mode: $...$ and $$...$$)
        
        # Remove markdown formatting for bold/italic (optional)
        # text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold**
        # text = re.sub(r'\*(.*?)\*', r'\1', text)      # *italic*
        
        return text.strip()
    
    def _is_reference_section(self, text: str) -> bool:
        """Check if section looks like references/bibliography."""
        # Common reference patterns
        patterns = [
            r'^\s*\[\d+\]',  # [1], [2], etc.
            r'^\s*\d+\.\s+[A-Z]',  # 1. Author, 2. Author
            r'et al\.',  # Common in references
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        
        # High density of years in parentheses
        year_matches = re.findall(r'\((\d{4})\)', text)
        if len(year_matches) > 3:
            return True
        
        return False
    
    def _is_mostly_math(self, text: str) -> bool:
        """Check if section is mostly mathematical notation."""
        # Count LaTeX math delimiters
        dollar_count = text.count('$')
        backslash_count = text.count('\\')
        
        # If more than 20% is math delimiters, skip
        if dollar_count + backslash_count > len(text) * 0.2:
            return True
        
        return False
    
    def _create_paragraph_id(self, citation: str, para_num: int) -> str:
        """Create unique paragraph ID."""
        citation_key = re.sub(r'[^\w-]', '_', citation)
        return f"{citation_key}_para{para_num}"
    
    def extract_from_multiple_pdfs(self, pdf_configs: List[Dict]) -> List[Dict]:
        """Extract paragraphs from multiple PDFs."""
        all_paragraphs = []
        
        print("\n" + "="*70)
        print("NOUGAT PDF PARSING (Academic Document OCR)")
        print("="*70)
        print("\nNote: First run will download Nougat model (~1GB)")
        print("Subsequent runs will be faster\n")
        
        for i, config in enumerate(pdf_configs, 1):
            print(f"\nPDF {i}/{len(pdf_configs)}")
            pdf_path = config['path']
            citation = config['citation']
            
            paragraphs = self.extract_from_pdf(pdf_path, citation)
            all_paragraphs.extend(paragraphs)
        
        print("\n" + "="*70)
        print(f"TOTAL: {len(all_paragraphs)} paragraphs from {len(pdf_configs)} PDFs")
        print("="*70 + "\n")
        
        return all_paragraphs


# Convenience function
def extract_paragraphs_with_nougat(
    pdf_path: str,
    citation: str,
    model_tag: str = "0.1.0-small"
) -> List[Dict]:
    """
    Quick function to extract paragraphs from a single PDF using Nougat.
    
    Args:
        pdf_path: Path to PDF file
        citation: Citation identifier
        model_tag: Nougat model ("0.1.0-small" or "0.1.0-base")
    
    Example:
        paragraphs = extract_paragraphs_with_nougat(
            "paper.pdf",
            "Smith_2020",
            model_tag="0.1.0-base"
        )
    """
    parser = NougatPDFParser(model_tag=model_tag)
    return parser.extract_from_pdf(pdf_path, citation)
