#!/usr/bin/env python3
"""
Paragraph Extraction and Embedding Pipeline

INSTRUCTIONS:
1. Fill in the configuration section below
2. Run this script: python run_embeddings.py
3. Find your embeddings in the output directory
"""

import sys
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from pipeline_orchestrator import run_pipeline

# ============================================================================
# CONFIGURATION - FILL IN THESE VALUES
# ============================================================================

# Path to your configuration YAML file
CONFIG_FILE = r"C:\Users\jpaige\Desktop\Local_repositories\Codebook_output_llm_repo\config.yaml"


# ============================================================================
# END CONFIGURATION
# ============================================================================


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def main():
    """Run the embedding pipeline with configured settings."""

    print("=" * 70)
    print("PARAGRAPH EXTRACTION AND EMBEDDING PIPELINE")
    print("=" * 70)

    # Validate config file exists
    config_path = Path(CONFIG_FILE)
    if not config_path.exists():
        print(f"\n❌ ERROR: Config file not found: {CONFIG_FILE}")
        print("\nPlease check the CONFIG_FILE path in the configuration section.")
        return 1

    # Load configuration
    print("\nLOADING CONFIGURATION:")
    print(f"  Config file: {CONFIG_FILE}")

    try:
        config = load_config(str(config_path))
    except Exception as e:
        print(f"\n❌ ERROR loading config: {e}")
        return 1

    # Display configuration summary
    print("\nCONFIGURATION SUMMARY:")
    print(f"  PDF directory:        {config['pdfs']['directory']}")
    print(f"  Codebook directory:   {config['codebook']['directory']}")
    print(f"  Codebook version:     {config['codebook']['version']}")
    print(f"  Embedding model:      {config['embedding']['model']}")
    print(f"  Paragraphs per PDF:   {config.get('retrieval', {}).get('paragraphs_per_pdf', 10)}")
    print(f"  Output directory:     {config['output']['base_directory']}")

    print("\n" + "=" * 70)

    # Run the pipeline
    return run_pipeline(config)


if __name__ == '__main__':
    sys.exit(main())