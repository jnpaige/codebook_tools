#!/usr/bin/env python3
"""
Codebook Parser

Runs all codebooks listed in config.yaml in one pass.

Usage:
    python run.py                  # uses config.yaml in this directory
    python run.py my_config.yaml   # uses specified config file

Author: Jonathan Paige
Date: 2025
"""

import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from codebook_parser import CodebookParser


def load_config(config_path: Path) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_one(entry: dict, output_base_dir: Path, json_indent: int) -> bool:
    codebook_file    = Path(entry['codebook_file'])
    codebook_name    = entry['codebook_name']
    codebook_version = entry['codebook_version']

    if not codebook_file.exists():
        print(f"  ERROR: file not found: {codebook_file}")
        return False

    output_dir = output_base_dir / f"{codebook_name}_{codebook_version}"

    print(f"  Codebook:  {codebook_file.name}")
    print(f"  Output:    {output_dir}")

    parser = CodebookParser(codebook_name=codebook_name, codebook_version=codebook_version)
    parser.parse_file(str(codebook_file))

    if not parser.codes:
        print("  ERROR: no code entries found.")
        return False

    parser.save_to_json(str(output_dir), indent=json_indent)
    return True


def main():
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / 'config.yaml'

    if not config_path.exists():
        print(f"ERROR: config file not found: {config_path}")
        return 1

    config = load_config(config_path)
    output_base_dir = Path(config['output_base_dir'])
    json_indent     = config.get('json_indent', 2)
    codebooks       = config.get('codebooks', [])

    if not codebooks:
        print("ERROR: no codebooks listed in config.")
        return 1

    print(f"Running {len(codebooks)} codebook(s)...\n")

    errors = 0
    for i, entry in enumerate(codebooks, 1):
        print(f"[{i}/{len(codebooks)}] {entry.get('codebook_name', '?')}")
        if not run_one(entry, output_base_dir, json_indent):
            errors += 1
        print()

    if errors:
        print(f"Done with {errors} error(s).")
        return 1

    print("All codebooks parsed successfully.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
