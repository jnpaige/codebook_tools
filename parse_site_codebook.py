#!/usr/bin/env python3
"""
One-off runner: parse Louisiana site form codebook → individual JSON files.
Does NOT modify run_parser.py (which is configured for the procedural unit codebook).

Output: C:\\Users\\jpaige\\Desktop\\Local_repositories\\Codebook_output_llm_repo\\Site_Form_v1.1\\
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from codebook_parser import CodebookParser, create_output_directory_name

CODEBOOK_FILE   = r"C:\Users\jpaige\Desktop\Research_repositories\text_coding_llm_repositories\Site_form_codebook\Louisiana_site_form_codebook_v1.1.Rmd"
CODEBOOK_TYPE   = "procedural"   # same section structure as procedural unit codebook
CODEBOOK_NAME   = "Site_Form"
CODEBOOK_VERSION = "v1.1"
OUTPUT_BASE_DIR = r"C:\Users\jpaige\Desktop\Local_repositories\Codebook_output_llm_repo"
JSON_INDENT     = 2


def main():
    codebook_path = Path(CODEBOOK_FILE)
    if not codebook_path.exists():
        print(f"ERROR: codebook not found: {CODEBOOK_FILE}")
        return 1

    output_dir = Path(OUTPUT_BASE_DIR) / create_output_directory_name(CODEBOOK_NAME, CODEBOOK_VERSION)
    print(f"Output directory: {output_dir}")

    parser = CodebookParser(
        codebook_type=CODEBOOK_TYPE,
        codebook_version=CODEBOOK_VERSION,
        codebook_name=CODEBOOK_NAME,
    )
    parser.parse_file(str(codebook_path))

    if not parser.codes:
        print("ERROR: no code entries found")
        return 1

    parser.save_to_json(str(output_dir), indent=JSON_INDENT)
    print(f"\nDone. {len(parser.codes)} entries written to:\n  {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
