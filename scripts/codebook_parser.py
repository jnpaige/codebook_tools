#!/usr/bin/env python3
"""
Codebook Parser Module

Parses .Rmd or .md codebook files into individual JSON code entries.
Entries are extracted from under a '# Traits' top-level section header.
Each entry is expected to contain a **Data type:** field (binary, categorical,
or numeric) and a **Response format:** field describing how to record results.

Author: Jonathan Paige
Date: 2025
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class CodebookParser:

    def __init__(self, codebook_name: str, codebook_version: str):
        self.codebook_name = codebook_name
        self.codebook_version = codebook_version
        self.codes: List[Dict] = []
        self.parse_date = datetime.now().isoformat()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse_file(self, filepath: str) -> List[Dict]:
        print(f"Reading: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Strip YAML front-matter and R code chunks
        content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
        content = re.sub(r'```\{r[^`]*?```', '', content, flags=re.DOTALL)

        self.codes = self._parse_entries(content)
        print(f"Found {len(self.codes)} code entries")
        return self.codes

    def save_to_json(self, output_dir: str, indent: int = 2):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"Saving to: {output_dir}")

        for i, code in enumerate(self.codes, 1):
            filename = f"{code['code_id']}_{self.codebook_version}.json"
            with open(output_path / filename, 'w', encoding='utf-8') as f:
                json.dump(code, f, indent=indent, ensure_ascii=False)
            print(f"  [{i}/{len(self.codes)}] {filename}")

        summary = {
            'codebook_name': self.codebook_name,
            'codebook_version': self.codebook_version,
            'parse_date': self.parse_date,
            'total_codes': len(self.codes),
            'code_ids': [c['code_id'] for c in self.codes],
        }
        summary_path = output_path / f"codebook_summary_{self.codebook_version}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=indent, ensure_ascii=False)

        print(f"Done. {len(self.codes)} entries + summary written to {output_dir}")

    # ------------------------------------------------------------------
    # Parsing internals
    # ------------------------------------------------------------------

    def _parse_entries(self, content: str) -> List[Dict]:
        """Extract all ## entries from the '# Traits' section."""
        # Split on single-# headers (not ##)
        top_sections = re.split(r'\n(?=# [^#])', content)

        traits_section = None
        for section in top_sections:
            if re.match(r'# Traits', section.strip()):
                traits_section = section
                break

        if traits_section is None:
            # Fallback: parse all ## entries in the whole file
            return self._parse_subsections(content)

        return self._parse_subsections(traits_section)

    def _parse_subsections(self, content: str) -> List[Dict]:
        """Split content on ## headers and parse each as a code entry."""
        parts = re.split(r'\n(?=## )', content)
        entries = []
        for part in parts:
            part = part.strip()
            if part.startswith('## '):
                entry = self._parse_entry(part)
                if entry:
                    entries.append(entry)
        return entries

    def _parse_entry(self, text: str) -> Optional[Dict]:
        """Parse a single ## section into a code entry dict."""
        title_match = re.search(r'^## (.+?)$', text, re.MULTILINE)
        if not title_match:
            return None

        title = title_match.group(1).strip()

        entry = {
            'title': title,
            'code_id': self._sanitize_filename(title),
            'data_type': self._extract_field(text, r'\*\*Data type:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'short_description': self._extract_field(text, r'\*\*Short Description:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'definition': self._extract_field(text, r'\*\*Definition:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'inclusion_criteria': self._extract_field(text, r'\*\*Inclusion criteria:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'exclusion_criteria': self._extract_field(text, r'\*\*Exclusion criteria:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'typical_exemplars': self._extract_field(text, r'\*\*Typical exemplars:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'atypical_exemplars': self._extract_field(text, r'\*\*Atypical exemplars:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'close_but_no': self._extract_field(text, r'\*\*Close but no:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'categories': self._extract_field(text, r'\*\*Categories:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'response_format': self._extract_field(text, r'\*\*Response format:\*\*\s*(.+?)(?=\n\*\*|\n#|$)'),
            'codebook_name': self.codebook_name,
            'codebook_version': self.codebook_version,
            'parse_date': self.parse_date,
            'full_text': text.strip(),
        }

        # Drop empty optional fields to keep JSON tidy
        for key in ('categories', 'typical_exemplars', 'atypical_exemplars', 'close_but_no'):
            if not entry[key]:
                del entry[key]

        return entry

    def _extract_field(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return re.sub(r' +', ' ', match.group(1).strip())
        return ""

    def _sanitize_filename(self, text: str) -> str:
        safe = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'\s+', '_', safe).strip('_')
