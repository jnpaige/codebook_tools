#!/usr/bin/env python3
"""
Codebook Parser Module

Parses .Rmd or .md codebook files into individual JSON code entries.
Codebook-agnostic: detects # Binary traits and # Categorical traits section
headers and tags each entry accordingly. Falls back to plain ## parsing
for codebooks that do not use those section headers.

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
        """
        Split content into ## sections and parse each as a code entry.

        If the file contains '# Binary traits' or '# Categorical traits'
        top-level headers, entries are tagged with trait_type accordingly.
        Otherwise, all ## entries are parsed without a trait_type.
        """
        has_trait_sections = bool(
            re.search(r'^# Binary traits', content, re.MULTILINE) or
            re.search(r'^# Categorical traits', content, re.MULTILINE)
        )

        if has_trait_sections:
            return self._parse_with_trait_sections(content)
        else:
            return self._parse_all_entries(content, trait_type=None)

    def _parse_with_trait_sections(self, content: str) -> List[Dict]:
        """Parse by splitting on top-level # headers and assigning trait_type."""
        entries = []

        # Split on single-# headers (not ##)
        top_sections = re.split(r'\n(?=# [^#])', content)

        for section in top_sections:
            section = section.strip()
            if not section:
                continue

            if re.match(r'# Binary traits', section):
                trait_type = 'binary'
            elif re.match(r'# Categorical traits', section):
                trait_type = 'categorical'
            else:
                continue  # skip preamble, definitions, bibliography, etc.

            entries.extend(self._parse_all_entries(section, trait_type=trait_type))

        return entries

    def _parse_all_entries(self, content: str, trait_type: Optional[str]) -> List[Dict]:
        """Split content on ## headers and parse each as a code entry."""
        parts = re.split(r'\n(?=## )', content)
        entries = []
        for part in parts:
            part = part.strip()
            if part.startswith('## '):
                entry = self._parse_entry(part, trait_type)
                if entry:
                    entries.append(entry)
        return entries

    def _parse_entry(self, text: str, trait_type: Optional[str]) -> Optional[Dict]:
        """Parse a single ## section into a code entry dict."""
        title_match = re.search(r'^## (.+?)$', text, re.MULTILINE)
        if not title_match:
            return None

        title = title_match.group(1).strip()

        entry = {
            'title': title,
            'code_id': self._sanitize_filename(title),
            'short_description': self._extract_field(text, r'\*\*Short Description:\*\*\s*(.+?)(?=\n\*\*|$)'),
            'definition': self._extract_field(text, r'\*\*Definition:\*\*\s*(.+?)(?=\n\*\*|$)'),
            'inclusion_criteria': self._extract_field(text, r'\*\*Inclusion criteria:\*\*\s*(.+?)(?=\n\*\*|$)'),
            'exclusion_criteria': self._extract_field(text, r'\*\*Exclusion criteria:\*\*\s*(.+?)(?=\n\*\*|$)'),
            'typical_exemplars': self._extract_field(text, r'\*\*Typical exemplars:\*\*\s*(.+?)(?=\n\*\*|$)'),
            'atypical_exemplars': self._extract_field(text, r'\*\*Atypical exemplars:\*\*\s*(.+?)(?=\n\*\*|$)'),
            'close_but_no': self._extract_field(text, r'\*\*Close but no:\*\*\s*(.+?)(?=\n\*\*|$)'),
            'codebook_name': self.codebook_name,
            'codebook_version': self.codebook_version,
            'parse_date': self.parse_date,
            'full_text': text.strip(),
        }

        if trait_type is not None:
            entry['trait_type'] = trait_type

        return entry

    def _extract_field(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return re.sub(r' +', ' ', match.group(1).strip())
        return ""

    def _sanitize_filename(self, text: str) -> str:
        safe = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'\s+', '_', safe).strip('_')
