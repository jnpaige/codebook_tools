# Archaeological Text Analysis Pipeline

The Archaeological Text Analysis Pipeline is a Python-based research
tool designed to extract paragraphs from  PDFs
and retrieve passages that are semantically relevant to structured
analytical codebooks. The system was developed to support reproducible,
codebook-driven literature sampling and structured text analysis in
archaeological research.

This repository is intended for researchers conducting systematic
thematic coding, inter-rater reliability studies, comparisons between
large language models and human experts, and structured corpus analysis.
The pipeline combines modern sentence embedding models with vector
similarity search to identify text that is conceptually closest to
predefined analytical categories.

------------------------------------------------------------------------

## What the Pipeline Does

The pipeline performs four primary operations. First, it extracts
paragraphs from  PDFs using configurable parsing
methods. Second, it converts each paragraph into a semantic embedding,
which represents the meaning of the text in vector space. Third, it
embeds structured codebook entries using the same embedding model.
Finally, it retrieves the paragraphs that are most semantically similar
to the codebook content.

The output consists of clean paragraph text files, embedding matrices
for both paragraphs and codebook entries, a FAISS similarity index for
efficient retrieval, and a ranked report listing the most relevant
passages. These outputs can be archived to preserve reproducibility and
reused for downstream analysis.

------------------------------------------------------------------------

## Installation

Clone the repository and create the conda environment:

``` bash
git clone https://github.com/your-repo/codebook-analysis-pipeline.git
cd codebook-analysis-pipeline
conda env create -f environment.yml
conda activate codebook_parsing
```

The environment installs PyTorch, sentence-transformers, FAISS, and
optional PDF parsing tools required for the pipeline.

------------------------------------------------------------------------

## Preparing a Codebook

The pipeline expects a structured `.Rmd` or `.md` codebook file. To
parse your codebook into JSON format, edit `run_parser.py` and set the
required parameters:

``` python
CODEBOOK_FILE = "path/to/your_codebook.Rmd"
CODEBOOK_TYPE = "mode"        # or "procedural"
CODEBOOK_VERSION = "v1.0"
CODEBOOK_NAME = "Lithic_Modes"
```

Then run:

``` bash
python run_parser.py
```

This will create a directory inside `parsed_codebooks/` containing one
JSON file per code entry, along with a summary file. That directory will
later be referenced in the main configuration file.

------------------------------------------------------------------------

## Configuring the Pipeline

Edit `config.yaml` to point to your PDF directory and parsed codebook
folder:

``` yaml
pdfs:
  directory: path/to/your/pdfs

codebook:
  directory: parsed_codebooks/Lithic_Modes_v1.0
  version: v1.0

paragraphs:
  parser: "nougat"
```

The recommended parser for academic journal articles is `"nougat"`,
which is designed to handle multi-column layouts. The embedding model
and retrieval settings can also be adjusted in this file if needed.

------------------------------------------------------------------------

## Running the Pipeline

Once the configuration file is complete, run the embedding pipeline
with:

``` bash
python run_embeddings.py
```

During execution, the system extract paragraphs from each pdf,
load codebook entries, generate embeddings, build a similarity index,
and retrieve the most relevant paragraphs.

------------------------------------------------------------------------

## Output Structure

Results are written to a timestamped directory inside the `embeddings/`
folder. This directory contains individual paragraph text files,
embedding matrices stored as NumPy arrays, a FAISS similarity index, and
a human-readable report listing the top-ranked paragraphs per PDF.

Because the full set of extracted paragraphs and embeddings are
preserved, each run can be archived to ensure reproducibility.


------------------------------------------------------------------------

## Intended Research Uses

The pipeline is suitable for systematic paragraph sampling across large
corpora, preparation of structured inputs for large language models,
comparison of retrieval behavior across codebook versions, and
controlled experiments examining agreement between human coders and
automated systems.

------------------------------------------------------------------------

## Citation

If you use this pipeline in published research, please cite:

``` bibtex
@software{paige2025codebook,
  author = {Paige, Jonathan N.},
  title = {Archaeological Text Analysis Pipeline},
  year = {2026},
  version = {1.0}
}
```

If you use the Nougat parser for PDF extraction, please also cite the
original Nougat publication.

------------------------------------------------------------------------

## Author

Jonathan N. Paige\
Department of Anthropology\
New Mexico Consortium
