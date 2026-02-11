#!/usr/bin/env python3
"""
Embedding Pipeline Orchestration Module

Orchestrates the full pipeline:
1. PDF paragraph extraction
2. Embedding generation
3. Finding closest paragraphs to codebook centroid

Author: Jonathan Paige
Date: 2025
"""

import json
from pathlib import Path
from datetime import datetime
import numpy as np
import faiss

from pdf_extractor_module import ParagraphExtractor
from embedding_builder_module import EmbeddingBuilder


def discover_pdfs(pdf_directory: str) -> list:
    """
    Automatically discover all PDFs in directory.
    Uses first 10 characters of filename as citation (with separators replaced by _).
    
    Args:
        pdf_directory: Directory containing PDFs
        
    Returns:
        List of PDF config dicts with path and citation
    """
    import re
    
    pdf_dir = Path(pdf_directory)
    
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_directory}")
    
    # Find all PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {pdf_directory}")
    
    # Create config list
    pdf_configs = []
    for pdf_path in sorted(pdf_files):
        # Get filename without extension
        filename = pdf_path.stem
        
        # Take first 10 characters
        citation_base = filename[:10]
        
        # Replace common separators with underscore
        citation = re.sub(r'[\s\-.,;:()\[\]{}]', '_', citation_base)
        
        # Remove any other special characters except underscore
        citation = re.sub(r'[^\w_]', '', citation)
        
        # Remove consecutive underscores
        citation = re.sub(r'_+', '_', citation)
        
        # Remove leading/trailing underscores
        citation = citation.strip('_')
        
        pdf_configs.append({
            'path': str(pdf_path),
            'citation': citation
        })
    
    return pdf_configs


def load_codes_from_directory(codebook_dir: Path, version: str) -> list:
    """
    Automatically load ALL code entries from codebook directory.
    
    Args:
        codebook_dir: Directory containing parsed codebook
        version: Codebook version
        
    Returns:
        List of code dictionaries
    """
    print(f"\n  Discovering code entries in: {codebook_dir}")
    
    # Find all JSON files matching version pattern
    pattern = f"*_{version}.json"
    code_files = list(codebook_dir.glob(pattern))
    
    # Exclude summary file
    code_files = [f for f in code_files if 'summary' not in f.name.lower()]
    
    if not code_files:
        raise FileNotFoundError(f"No code files found in {codebook_dir} matching pattern '{pattern}'")
    
    codes = []
    for code_file in sorted(code_files):
        with open(code_file, 'r', encoding='utf-8') as f:
            code = json.load(f)
            codes.append(code)
    
    print(f"  ✓ Found {len(codes)} code entries")
    for code in codes[:5]:
        print(f"    - {code['code_id']}: {code['title']}")
    if len(codes) > 5:
        print(f"    ... and {len(codes) - 5} more")
    
    return codes


def save_paragraphs_as_files(paragraphs: list, output_dir: Path):
    """
    Save each paragraph as individual text file with ID as filename.
    
    Args:
        paragraphs: List of paragraph dictionaries
        output_dir: Directory to save paragraph files
    """
    print("\n  Saving individual paragraph files...")
    
    para_dir = output_dir / 'paragraph_files'
    para_dir.mkdir(parents=True, exist_ok=True)
    
    # Save each paragraph as text file
    for para in paragraphs:
        para_id = para['paragraph_id']
        filename = f"{para_id}.txt"
        filepath = para_dir / filename
        
        # Save just the text, no formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(para['text'])
    
    print(f"  ✓ Saved {len(paragraphs)} paragraph files to: {para_dir}")


def save_paragraph_index(paragraphs: list, output_dir: Path):
    """
    Save index/key file mapping paragraph IDs to metadata.
    
    Args:
        paragraphs: List of paragraph dictionaries
        output_dir: Directory to save index
    """
    print("\n  Creating paragraph index...")
    
    # Create simplified index
    index = []
    for para in paragraphs:
        index.append({
            'paragraph_id': para['paragraph_id'],
            'citation': para['citation'],
            'page': para['page'],
            'paragraph_number': para['paragraph_number'],
            'source_file': para['source_file'],
            'char_count': para['char_count']
        })
    
    # Save index
    index_file = output_dir / 'paragraph_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_paragraphs': len(index),
            'total_documents': len(set(p['citation'] for p in index)),
            'paragraphs': index
        }, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Saved paragraph index to: {index_file}")


def find_closest_paragraphs_to_codebook(paragraph_embeddings: np.ndarray,
                                       paragraph_metadata: list,
                                       code_embeddings: np.ndarray,
                                       n_per_pdf: int = 10) -> dict:
    """
    Find paragraphs closest to the codebook's centroid (hyperdimensional center).
    Returns top N paragraphs per PDF that are closest to the overall codebook concept.
    
    Args:
        paragraph_embeddings: Numpy array of paragraph embeddings
        paragraph_metadata: List of paragraph dictionaries
        code_embeddings: Numpy array of code embeddings
        n_per_pdf: Number of closest paragraphs to return per PDF
        
    Returns:
        Dict mapping citation to list of closest paragraph info
    """
    print("\n  Computing codebook centroid (center of all code embeddings)...")
    
    # Compute centroid of all code embeddings
    codebook_centroid = np.mean(code_embeddings, axis=0, keepdims=True)
    
    # Calculate distances from each paragraph to centroid
    # Using L2 distance (Euclidean)
    distances = np.linalg.norm(paragraph_embeddings - codebook_centroid, axis=1)
    
    # Group paragraphs by PDF (citation)
    paragraphs_by_pdf = {}
    for i, para in enumerate(paragraph_metadata):
        citation = para['citation']
        if citation not in paragraphs_by_pdf:
            paragraphs_by_pdf[citation] = []
        
        paragraphs_by_pdf[citation].append({
            'index': i,
            'distance': float(distances[i]),
            'paragraph_id': para['paragraph_id'],
            'page': para['page'],
            'paragraph_number': para['paragraph_number'],
            'text': para['text']
        })
    
    # For each PDF, get N closest paragraphs
    closest_by_pdf = {}
    for citation, paras in paragraphs_by_pdf.items():
        # Sort by distance (closest first)
        sorted_paras = sorted(paras, key=lambda x: x['distance'])
        
        # Take top N
        closest_by_pdf[citation] = sorted_paras[:n_per_pdf]
    
    print(f"  ✓ Found top {n_per_pdf} paragraphs per PDF (total: {len(closest_by_pdf)} PDFs)")
    
    return closest_by_pdf


def save_closest_paragraphs(closest_by_pdf: dict, output_dir: Path):
    """
    Save information about closest paragraphs to codebook.
    
    Args:
        closest_by_pdf: Dict from find_closest_paragraphs_to_codebook
        output_dir: Directory to save results
    """
    print("\n  Saving closest paragraphs results...")
    
    # Save summary JSON
    summary_file = output_dir / 'closest_paragraphs_to_codebook.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(closest_by_pdf, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Saved: closest_paragraphs_to_codebook.json")
    
    # Also save as readable text report
    report_file = output_dir / 'closest_paragraphs_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("PARAGRAPHS CLOSEST TO CODEBOOK CENTROID\n")
        f.write("="*70 + "\n\n")
        f.write("These paragraphs are closest to the 'center' of all codebook entries,\n")
        f.write("meaning they are generally relevant to the codebook's overall concepts.\n\n")
        
        for citation in sorted(closest_by_pdf.keys()):
            f.write(f"\n{'='*70}\n")
            f.write(f"PDF: {citation}\n")
            f.write(f"{'='*70}\n\n")
            
            for i, para in enumerate(closest_by_pdf[citation], 1):
                f.write(f"Rank {i} (distance: {para['distance']:.4f})\n")
                f.write(f"ID: {para['paragraph_id']}\n")
                f.write(f"Page: {para['page']}, Paragraph: {para['paragraph_number']}\n")
                f.write(f"\nText:\n{para['text']}\n")
                f.write(f"\n{'-'*70}\n\n")
    
    print(f"  ✓ Saved: closest_paragraphs_report.txt (human-readable)")


def create_output_directory_name(pdf_configs: list, model_name: str) -> str:
    """
    Create descriptive output directory name.
    
    Args:
        pdf_configs: List of PDF configuration dicts
        model_name: Embedding model name
        
    Returns:
        Directory name string
    """
    # Get first PDF citation as base
    base_citation = pdf_configs[0]['citation'] if pdf_configs else 'pdfs'
    
    # Get model shortname
    model_short = model_name.split('/')[-1]
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # If multiple PDFs, use "multi"
    if len(pdf_configs) > 1:
        return f"{base_citation}_multi_{model_short}_{timestamp}"
    else:
        return f"{base_citation}_{model_short}_{timestamp}"


def run_pipeline(config: dict) -> int:
    """
    Run the complete embedding pipeline.
    
    Args:
        config: Configuration dictionary from YAML
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # ========================================================================
    # STEP 1: Discover PDFs
    # ========================================================================
    print("\n" + "="*70)
    print("DISCOVERING PDFs")
    print("="*70)
    
    try:
        PDF_FILES = discover_pdfs(config['pdfs']['directory'])
        print(f"\n✓ Found {len(PDF_FILES)} PDF(s) in {config['pdfs']['directory']}")
        for pdf in PDF_FILES[:5]:
            print(f"  - {pdf['citation']}")
        if len(PDF_FILES) > 5:
            print(f"  ... and {len(PDF_FILES) - 5} more")
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    
    if not PDF_FILES:
        print("\n❌ ERROR: No PDF files found")
        return 1
    
    # Create output directory
    output_dir_name = create_output_directory_name(PDF_FILES, config['embedding']['model'])
    output_dir = Path(config['output']['base_directory']) / output_dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nOutput directory: {output_dir}")
    
    # ========================================================================
    # STEP 2: Extract Paragraphs from PDFs
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 1: EXTRACTING PARAGRAPHS FROM PDFs")
    print("="*70)
    
    print(f"\nProcessing {len(PDF_FILES)} PDF(s)...")
    
    extractor = ParagraphExtractor(
        min_paragraph_length=config['paragraphs']['min_length'],
        max_paragraph_length=config['paragraphs']['max_length']
    )
    
    paragraphs = extractor.extract_from_multiple_pdfs(PDF_FILES)
    
    if not paragraphs:
        print("\n❌ ERROR: No paragraphs extracted")
        print("   Check PDF paths and extraction settings")
        return 1
    
    print(f"\n✓ Extracted {len(paragraphs)} total paragraphs")
    
    # Save paragraphs as individual files
    save_paragraphs_as_files(paragraphs, output_dir)
    
    # Save paragraph index
    save_paragraph_index(paragraphs, output_dir)
    
    # ========================================================================
    # STEP 3: Load Code Entries
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 2: LOADING CODE ENTRIES")
    print("="*70)
    
    codebook_dir = Path(config['codebook']['directory'])
    
    if not codebook_dir.exists():
        print(f"\n❌ ERROR: Codebook directory not found: {codebook_dir}")
        return 1
    
    codes = load_codes_from_directory(codebook_dir, config['codebook']['version'])
    
    if not codes:
        print("\n❌ ERROR: No codes loaded")
        return 1
    
    # ========================================================================
    # STEP 4: Create Embeddings
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 3: CREATING EMBEDDINGS")
    print("="*70)
    
    builder = EmbeddingBuilder(model_name=config['embedding']['model'])
    
    # Create paragraph embeddings
    print("\nCreating paragraph embeddings:")
    paragraph_embeddings = builder.create_paragraph_embeddings(
        paragraphs,
        batch_size=config['embedding']['batch_size']
    )
    
    # Create code embeddings
    print("\nCreating code embeddings:")
    code_embeddings = builder.create_code_embeddings(
        codes,
        custom_queries=config['embedding'].get('custom_queries', {})
    )
    
    # ========================================================================
    # STEP 5: Save Embeddings and Create FAISS Index
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 4: SAVING EMBEDDINGS")
    print("="*70)
    
    # Save paragraph embeddings
    print("\n  Saving paragraph embeddings...")
    np.save(output_dir / 'paragraph_embeddings.npy', paragraph_embeddings)
    print(f"  ✓ Saved: paragraph_embeddings.npy {paragraph_embeddings.shape}")
    
    # Save code embeddings
    print("\n  Saving code embeddings...")
    np.save(output_dir / 'code_embeddings.npy', code_embeddings)
    
    # Save code metadata
    code_metadata_file = output_dir / 'code_metadata.json'
    with open(code_metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            'codes': codes,
            'custom_queries': config['embedding'].get('custom_queries', {})
        }, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved: code_embeddings.npy {code_embeddings.shape}")
    print(f"  ✓ Saved: code_metadata.json")
    
    # Build and save FAISS index
    print("\n  Building FAISS index...")
    index = builder.build_faiss_index(paragraph_embeddings)
    faiss.write_index(index, str(output_dir / 'paragraph_faiss_index'))
    print(f"  ✓ Saved: paragraph_faiss_index")
    
    # ========================================================================
    # STEP 6: Find Closest Paragraphs to Codebook Centroid
    # ========================================================================
    print("\n" + "="*70)
    print("STEP 5: FINDING PARAGRAPHS CLOSEST TO CODEBOOK")
    print("="*70)
    
    print("\nFinding paragraphs closest to codebook centroid...")
    print("(These are paragraphs generally relevant to codebook concepts)")
    
    # Get number of paragraphs to retrieve per PDF from config
    n_per_pdf = config.get('retrieval', {}).get('paragraphs_per_pdf', 10)
    
    closest_paragraphs = find_closest_paragraphs_to_codebook(
        paragraph_embeddings,
        paragraphs,
        code_embeddings,
        n_per_pdf=n_per_pdf
    )
    
    save_closest_paragraphs(closest_paragraphs, output_dir)
    
    # ========================================================================
    # STEP 7: Save Metadata
    # ========================================================================
    print("\n  Saving metadata...")
    
    metadata = {
        'creation_date': datetime.now().isoformat(),
        'embedding_model': config['embedding']['model'],
        'embedding_dimension': int(paragraph_embeddings.shape[1]),
        'total_paragraphs': len(paragraphs),
        'total_codes': len(codes),
        'pdf_sources': [p['citation'] for p in PDF_FILES],
        'codes_used': [c['code_id'] for c in codes],
        'paragraph_length_range': [config['paragraphs']['min_length'], config['paragraphs']['max_length']],
        'batch_size': config['embedding']['batch_size'],
        'codebook_directory': str(codebook_dir),
        'codebook_version': config['codebook']['version'],
        'paragraphs_per_pdf_retrieved': n_per_pdf
    }
    
    metadata_file = output_dir / 'embedding_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved: embedding_metadata.json")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    print(f"\nInput:")
    print(f"  PDFs processed: {len(PDF_FILES)}")
    for pdf in PDF_FILES:
        print(f"    - {pdf['citation']}")
    
    print(f"\nExtraction:")
    print(f"  Total paragraphs: {len(paragraphs)}")
    print(f"  Paragraph length: {config['paragraphs']['min_length']}-{config['paragraphs']['max_length']} chars")
    
    print(f"\nEmbeddings:")
    print(f"  Model: {config['embedding']['model']}")
    print(f"  Dimension: {paragraph_embeddings.shape[1]}")
    print(f"  Paragraph embeddings: {paragraph_embeddings.shape}")
    print(f"  Code embeddings: {code_embeddings.shape}")
    
    print(f"\nCodes processed:")
    for code in codes:
        print(f"  - {code['code_id']}: {code['title']}")
    
    print(f"\nRetrieval:")
    print(f"  Method: Closest to codebook centroid")
    print(f"  Paragraphs per PDF: {n_per_pdf}")
    print(f"  Total paragraphs retrieved: {sum(len(v) for v in closest_paragraphs.values())}")
    
    print(f"\nOutput saved to: {output_dir}")
    print(f"\nDirectory contents:")
    print(f"  paragraph_files/                    - Individual paragraph text files")
    print(f"  paragraph_index.json                - Paragraph ID mapping")
    print(f"  paragraph_embeddings.npy            - Paragraph embeddings")
    print(f"  code_embeddings.npy                 - Code embeddings")
    print(f"  code_metadata.json                  - Code information")
    print(f"  paragraph_faiss_index               - FAISS search index")
    print(f"  closest_paragraphs_to_codebook.json - Top paragraphs per PDF (JSON)")
    print(f"  closest_paragraphs_report.txt       - Top paragraphs per PDF (readable)")
    print(f"  embedding_metadata.json             - Full metadata")
    
    print("\n" + "="*70)
    print("✓ COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  1. Review closest_paragraphs_report.txt to see most relevant paragraphs")
    print("  2. Use these paragraphs to build LLM prompts")
    print("  3. Send prompts to LMStudio for automated coding")
    print("  4. Compare LLM results with human coding")
    
    return 0
