# Codebook Tools — User Guide

Parses `.Rmd` or `.md` codebook files into individual JSON code entries,
one file per code plus a summary file. All downstream work (embeddings,
RAG retrieval, LLM coding) lives in the `procedural_unit_rag` repository.

---

## Installation

```bash
conda env create -f environment.yml
conda activate codebook_parsing
```

---

## Usage

**1. Edit `config.yaml`**

```yaml
codebook_file: C:\path\to\your_codebook.Rmd
codebook_name: Site_Form
codebook_version: v1.1
output_base_dir: C:\path\to\output_directory
json_indent: 2
```

**2. Run**

```bash
python run.py
# or with an explicit config file:
python run.py my_other_config.yaml
```

Output is written to `output_base_dir/codebook_name_version/`.

---

## Output

```
Site_Form_v1.1/
├── pre-contact_component_pre_conta_v1.1.json
├── post-contact_component_post_conta_v1.1.json
├── ...
└── codebook_summary_v1.1.json
```

Each JSON file contains the fields extracted from one `##` section:
`title`, `code_id`, `short_description`, `definition`,
`inclusion_criteria`, `exclusion_criteria`, `typical_exemplars`,
`atypical_exemplars`, `close_but_no`, plus codebook metadata
(`codebook_name`, `codebook_version`, `parse_date`).

For codebooks that use `# Binary traits` and `# Categorical traits`
top-level section headers (currently the site form codebook), each entry
also includes `"trait_type": "binary"` or `"trait_type": "categorical"`.

---

## Codebook file format

The parser expects `##`-level headers for individual codes, with bold
field labels:

```markdown
# Binary traits

## Code title (Short_ID)

**Short Description:** ...

**Definition:** ...

**Inclusion criteria:** ...

**Exclusion criteria:** ...

**Typical exemplars:** ...

**Atypical exemplars:** ...

**Close but no:** ...
```

Codebooks without `# Binary traits` / `# Categorical traits` sections
are parsed the same way — all `##` entries are extracted without a
`trait_type` field.

---

Support: jonathan.n.paige@gmail.com
