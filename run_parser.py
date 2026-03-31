#!/usr/bin/env python3
"""
Codebook Parser Implementation Script

INSTRUCTIONS:
1. Fill in the configuration section below
2. Run this script: python run_parser.py
3. Find your parsed codebook in the output directory

Author: Jonathan Paige
Date: 2025
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from codebook_parser import CodebookParser, create_output_directory_name


# ============================================================================
# CONFIGURATION - FILL IN THESE VALUES
# ============================================================================

# Path to your codebook file (.Rmd or .md)
CODEBOOK_FILE = r"C:\Users\jpaige\Desktop\Research_repositories\Procedural.unit.codebook\paper\Procedural unit codebook.Rmd"

# Type of codebook: 'procedural' or 'mode'
CODEBOOK_TYPE = "procedural"  # Change to 'procedural' for procedural unit codebook

# Version of the codebook (e.g., 'v1.0', 'v1.1', 'v2.0')
CODEBOOK_VERSION = "v1.1"

# Name of the codebook (used in output directory name)
# Examples: 'Procedural_Unit', 'Lithic_Modes', 'Stone_Tool_Technology'
CODEBOOK_NAME = "Procedural_Unit"

# Where to save output (will create subdirectory with name and version)
OUTPUT_BASE_DIR = r"C:\Use1rs\jpaige\Desktop\Local_repositories\Codebook_output_llm_repo"


# JSON formatting - indent level (2 or 4 recommended)
JSON_INDENT = 2

# ============================================================================
# END CONFIGURATION
# ============================================================================


def main():
    """Run the codebook parser with configured settings."""
    
    print("="*70)
    print("CODEBOOK PARSER")
    print("="*70)
    
    # Validate inputs
    codebook_path = Path(CODEBOOK_FILE)
    if not codebook_path.exists():
        print(f"\n❌ ERROR: Codebook file not found: {CODEBOOK_FILE}")
        print("\nPlease check the CODEBOOK_FILE path in the configuration section.")
        return 1
    
    if CODEBOOK_TYPE not in ['procedural', 'mode']:
        print(f"\n❌ ERROR: Invalid CODEBOOK_TYPE: {CODEBOOK_TYPE}")
        print("   Must be either 'procedural' or 'mode'")
        return 1
    
    # Display configuration
    print("\nCONFIGURATION:")
    print(f"  Codebook file:    {CODEBOOK_FILE}")
    print(f"  Codebook type:    {CODEBOOK_TYPE}")
    print(f"  Codebook name:    {CODEBOOK_NAME}")
    print(f"  Codebook version: {CODEBOOK_VERSION}")
    print(f"  JSON indent:      {JSON_INDENT}")
    
    # Create output directory name
    output_dir_name = create_output_directory_name(CODEBOOK_NAME, CODEBOOK_VERSION)
    output_dir = Path(OUTPUT_BASE_DIR) / output_dir_name
    
    print(f"\nOutput directory: {output_dir}")
    print("\n" + "="*70)
    
    # Initialize parser
    parser = CodebookParser(
        codebook_type=CODEBOOK_TYPE,
        codebook_version=CODEBOOK_VERSION,
        codebook_name=CODEBOOK_NAME
    )
    
    # Parse the codebook
    try:
        parser.parse_file(str(codebook_path))
    except Exception as e:
        print(f"\n❌ ERROR parsing codebook: {e}")
        return 1
    
    if not parser.codes:
        print("\n❌ ERROR: No code entries found in codebook")
        print("   Check that the file format matches the expected structure")
        return 1
    
    # Save JSON files
    try:
        parser.save_to_json(str(output_dir), indent=JSON_INDENT)
    except Exception as e:
        print(f"\n❌ ERROR saving JSON files: {e}")
        return 1

    # Success message
    print("\n" + "="*70)
    print("✓ PARSING COMPLETE!")
    print("="*70)
    print(f"\nYour parsed codebook is ready in:")
    print(f"  {output_dir}")
    print(f"\nContents:")
    print(f"  • {len(parser.codes)} JSON files (one per code)")
    print(f"  • 1 summary JSON file")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
