# Codebook Tools — User Guide

Parses `.Rmd` or `.md` codebook files into individual JSON code entries,
one file per code plus a summary file. All downstream work (RAG retrieval,
LLM coding) lives in the `procedural_unit_rag` repository.

---

## Usage

**1. Edit `config.yaml`**

```yaml
output_base_dir: C:\path\to\output
json_indent: 2

codebooks:
  - codebook_file: C:\path\to\first_codebook.Rmd
    codebook_name: Procedural_Unit
    codebook_version: v1.1
  - codebook_file: C:\path\to\second_codebook.Rmd
    codebook_name: Lithic_Modes
    codebook_version: v0.1
```

**2. Run**

```bash
python run.py
# or with an explicit config:
python run.py my_other_config.yaml
```

Output lands in `output_base_dir/codebook_name_version/`.

---

## Output

```
Site_Form_v1.1/
├── pre-contact_component_pre_conta_v1.1.json
├── ...
└── codebook_summary_v1.1.json
```

Each JSON entry contains:

| Field | Description |
|---|---|
| `title` | The `## ` heading text |
| `code_id` | Sanitized filename stem |
| `data_type` | `binary`, `categorical`, or `numeric` |
| `short_description` | From `**Short Description:**` |
| `definition` | From `**Definition:**` |
| `inclusion_criteria` | From `**Inclusion criteria:**` |
| `exclusion_criteria` | From `**Exclusion criteria:**` |
| `typical_exemplars` | From `**Typical exemplars:**` (omitted if empty) |
| `atypical_exemplars` | From `**Atypical exemplars:**` (omitted if empty) |
| `close_but_no` | From `**Close but no:**` (omitted if empty) |
| `categories` | From `**Categories:**` — categorical entries only |
| `response_format` | From `**Response format:**` — what columns to produce |
| `codebook_name` | From config |
| `codebook_version` | From config |
| `parse_date` | ISO timestamp |
| `full_text` | Raw entry text |

---

## Codebook file format

Entries live under a `# Traits` top-level section. Each entry is a `## `
heading followed by bold-label fields:

```markdown
# Traits

## Code title (Short_ID)

**Data type:** binary

**Short Description:** ...

**Definition:** ...

**Inclusion criteria:** ...

**Exclusion criteria:** ...

**Typical exemplars:** ...

**Atypical exemplars:** ...

**Close but no:** ...

**Response format:** Three values per coded document: (1) **present_absent** —
1 if present, 0 if absent; (2) **inclusion_pages** — semicolon-separated page
numbers where inclusion criteria are met, or "none"; (3) **exclusion_pages** —
semicolon-separated page numbers where exclusion criteria are met, or "none".
```

**Categorical entries** also include a `**Categories:**` field listing each
possible value with its definition. The `**Response format:**` for categorical
entries describes the output column structure (which may be a semicolon-
separated vector, as for NRHP, or a single value).

**Numeric entries** describe the unit, "not reported" / "unknown" handling,
and any calculation guidance in `**Response format:**`.

---

## Data type conventions

| `data_type` | `response_format` structure |
|---|---|
| `binary` | `present_absent` (1/0), `inclusion_pages`, `exclusion_pages` |
| `categorical` | Defined per-entry in `**Response format:**`; may be a vector |
| `numeric` | A single value in specified units; "not reported" or "unknown" allowed |

The `response_format` field from each JSON entry is the authoritative source
for what columns the LLM should produce. The RAG preamble should give
general structured-output instructions and then reference this field for
entry-specific formatting.

---

Support: jonathan.n.paige@gmail.com
