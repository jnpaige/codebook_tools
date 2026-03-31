# User Guide

Archaeological Text Analysis Pipeline

------------------------------------------------------------------------

## Overview

This guide explains how to install, configure, and run the paragraph
extraction and embedding pipeline.

Supported uses:

-   Codebook-based literature sampling
-   LLM vs expert coding comparison
-   Inter-rater reliability studies
-   Structured thematic analysis

------------------------------------------------------------------------

## Installation

Install Anaconda or Miniconda, then:

conda env create -f environment.yml\
conda activate codebook_parsing

------------------------------------------------------------------------

## Codebook Preparation

Edit run_parser.py:

CODEBOOK_FILE = "path/to/your_codebook.Rmd"\
CODEBOOK_TYPE = "mode" or "procedural"\
CODEBOOK_VERSION = "v1.0"\
CODEBOOK_NAME = "Lithic_Modes"

Run:

python run_parser.py

Output:

parsed_codebooks/Lithic_Modes_v1.0/

------------------------------------------------------------------------

## PDF Preparation

Place PDFs in one directory:

my_pdfs/ ├── Smith_2015_Lithics.pdf ├── Jones_2018_Technology.pdf

------------------------------------------------------------------------

## Configuration (config.yaml)

pdfs: directory: path/to/your/pdfs

codebook: directory: parsed_codebooks/Lithic_Modes_v1.0 version: v1.0

paragraphs: min_length: 200 max_length: 5000 parser: "nougat"

embedding: model: sentence-transformers/all-MiniLM-L6-v2 batch_size: 32

retrieval: paragraphs_per_pdf: 10

------------------------------------------------------------------------

## Running

python run_embeddings.py

------------------------------------------------------------------------

## Output Structure

embeddings/\[run_name\]/

Contains:

-   paragraph_files/
-   paragraph_index.json
-   paragraph_embeddings.npy
-   code_embeddings.npy
-   paragraph_faiss_index
-   closest_paragraphs_report.txt

------------------------------------------------------------------------

## Troubleshooting

No PDFs found → check directory path\
No code entries found → check version matches JSON filenames\
CUDA errors → reduce batch_size\
Nougat slow → expected on CPU

------------------------------------------------------------------------

## Reproducibility

Each run stores:

-   Embedding model name\
-   Extracted paragraphs\
-   Embedding matrices\
-   Retrieval results

Archive full output directory for reproducibility.

------------------------------------------------------------------------

Support: jonathan.n.paige@gmail.com
