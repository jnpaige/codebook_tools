#!/usr/bin/env python3
"""
Codebook Parser Module

Contains all the parsing logic for extracting code entries from codebooks.
This module is imported by the implementation script.

Author: Jonathan Paige
Date: 2025
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class CodebookParser:
    """Parser for extracting individual code entries from codebooks."""
    
    def __init__(self, codebook_type: str, codebook_version: str, codebook_name: str):
        """
        Initialize parser.
        
        Args:
            codebook_type: Either 'procedural' or 'mode'
            codebook_version: Version string (e.g., 'v1.0', 'v1.1')
            codebook_name: Name of the codebook (e.g., 'Procedural_Unit', 'Lithic_Modes')
        """
        self.codebook_type = codebook_type
        self.codebook_version = codebook_version
        self.codebook_name = codebook_name
        self.codes = []
        self.parse_date = datetime.now().isoformat()
        
    def parse_file(self, filepath: str) -> List[Dict]:
        """
        Parse a codebook file and extract all code entries.
        
        Args:
            filepath: Path to the .Rmd or .md codebook file
            
        Returns:
            List of dictionaries, each containing one code entry
        """
        print(f"\nReading codebook from: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove YAML header
        content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
        
        # Split into sections
        if self.codebook_type == 'procedural':
            sections = self._split_procedural_sections(content)
        else:  # mode
            sections = self._split_mode_sections(content)
        
        self.codes = sections
        print(f"Found {len(sections)} code entries")
        return sections
    
    def _split_procedural_sections(self, content: str) -> List[Dict]:
        """Split procedural unit codebook into individual entries."""
        # Split on ## headers but keep the header
        parts = re.split(r'\n(?=## )', content)
        
        entries = []
        for part in parts:
            if not part.strip():
                continue
            
            # Skip non-code sections (Introduction, Definitions, etc.)
            # Only process sections that start with ## (not # or ###)
            if not part.startswith('## ') or part.startswith('### '):
                continue
            
            entry = self._parse_procedural_entry(part)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _split_mode_sections(self, content: str) -> List[Dict]:
        """Split mode codebook into individual entries."""
        # Split on ## Mode headers
        parts = re.split(r'\n(?=## Mode )', content)
        
        entries = []
        for part in parts:
            if not part.strip():
                continue
                
            # Only process Mode sections
            if not part.startswith('## Mode'):
                continue
            
            entry = self._parse_mode_entry(part)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _parse_procedural_entry(self, text: str) -> Optional[Dict]:
        """Parse a single procedural unit entry."""
        entry = {}
        
        # Extract title (## header)
        title_match = re.search(r'^## (.+?)$', text, re.MULTILINE)
        if title_match:
            entry['title'] = title_match.group(1).strip()
            entry['code_id'] = self._sanitize_filename(entry['title'])
        else:
            return None
        
        # Extract fields
        entry['short_description'] = self._extract_field(text, r'\*\*Short Description:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['definition'] = self._extract_field(text, r'\*\*Definition:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['inclusion_criteria'] = self._extract_field(text, r'\*\*Inclusion criteria:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['exclusion_criteria'] = self._extract_field(text, r'\*\*Exclusion criteria:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['typical_exemplars'] = self._extract_field(text, r'\*\*Typical exemplars:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['atypical_exemplars'] = self._extract_field(text, r'\*\*Atypical exemplars:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['close_but_no'] = self._extract_field(text, r'\*\*Close but no:\*\*\s*(.+?)(?=\n\*\*|$)')
        
        # Add metadata
        entry['codebook_type'] = 'procedural_unit'
        entry['codebook_name'] = self.codebook_name
        entry['codebook_version'] = self.codebook_version
        entry['parse_date'] = self.parse_date
        entry['full_text'] = text.strip()
        
        return entry
    
    def _parse_mode_entry(self, text: str) -> Optional[Dict]:
        """Parse a single mode entry."""
        entry = {}
        
        # Extract title (## Mode X)
        title_match = re.search(r'^## (Mode [A-Z0-9]+)', text, re.MULTILINE)
        if title_match:
            entry['title'] = title_match.group(1).strip()
            entry['code_id'] = self._sanitize_filename(entry['title'])
        else:
            return None
        
        # Extract fields
        entry['short_description'] = self._extract_field(text, r'\*\*Short Description:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['definition'] = self._extract_field(text, r'\*\*Definition:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['inclusion_criteria'] = self._extract_field(text, r'\*\*Inclusion criteria:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['exclusion_criteria'] = self._extract_field(text, r'\*\*Exclusion criteria:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['typical_exemplars'] = self._extract_field(text, r'\*\*Typical exemplars:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['atypical_exemplars'] = self._extract_field(text, r'\*\*Atypical exemplars:\*\*\s*(.+?)(?=\n\*\*|$)')
        entry['close_but_no'] = self._extract_field(text, r'\*\*Close but no:\*\*\s*(.+?)(?=\n\*\*|$)')
        
        # Add metadata
        entry['codebook_type'] = 'technological_mode'
        entry['codebook_name'] = self.codebook_name
        entry['codebook_version'] = self.codebook_version
        entry['parse_date'] = self.parse_date
        entry['full_text'] = text.strip()
        
        return entry
    
    def _extract_field(self, text: str, pattern: str) -> str:
        """Extract a field from text using regex pattern."""
        match = re.search(pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # Clean up extra whitespace but preserve paragraph breaks
            content = re.sub(r' +', ' ', content)
            return content
        return ""
    
    def _sanitize_filename(self, text: str) -> str:
        """Create a safe filename from text."""
        # Replace spaces and special chars with underscores
        safe = re.sub(r'[^\w\s-]', '', text.lower())
        safe = re.sub(r'[\s]+', '_', safe)
        return safe
    
    def save_to_json(self, output_dir: str, indent: int = 2):
        """
        Save each code entry to its own JSON file.
        
        Args:
            output_dir: Directory to save JSON files
            indent: JSON indentation level
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nSaving JSON files to: {output_dir}")
        
        for i, code in enumerate(self.codes, 1):
            # Filename includes version
            filename = f"{code['code_id']}_{self.codebook_version}.json"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(code, f, indent=indent, ensure_ascii=False)
            
            print(f"  [{i}/{len(self.codes)}] Saved: {filename}")
        
        # Also save a summary file
        summary = {
            'codebook_name': self.codebook_name,
            'codebook_type': self.codebook_type,
            'codebook_version': self.codebook_version,
            'parse_date': self.parse_date,
            'total_codes': len(self.codes),
            'code_ids': [code['code_id'] for code in self.codes],
            'output_directory': str(output_dir)
        }
        
        summary_filename = f'codebook_summary_{self.codebook_version}.json'
        summary_path = output_path / summary_filename
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=indent, ensure_ascii=False)
        
        print(f"\n✓ Successfully saved {len(self.codes)} code entries")
        print(f"✓ Summary saved to: {summary_filename}")
        print(f"✓ Output directory: {output_dir}")
    



def create_output_directory_name(codebook_name: str, codebook_version: str) -> str:
    """
    Create standardized output directory name.
    
    Args:
        codebook_name: Name of codebook
        codebook_version: Version string
        
    Returns:
        Directory name in format: codebook_name_version
    """
    # Remove spaces, sanitize
    clean_name = re.sub(r'[^\w-]', '_', codebook_name)
    clean_version = re.sub(r'[^\w.-]', '_', codebook_version)
    
    return f"{clean_name}_{clean_version}"
