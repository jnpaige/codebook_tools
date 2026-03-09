# Codebook Parser

A tool for extracting individual code entries from lithic technology codebooks and preparing them for use with Large Language Models (LLMs).

## Quick Start

1. Set up Python environment (see [Environment Setup](#environment-setup))
2. Edit configuration in `run_parser.py`
3. Run: `python run_parser.py`
4. Find output in `parsed_codebooks/`

## What This Does

The parser:
- ✅ Extracts each code entry from your codebook
- ✅ Saves each as an individual JSON file
- ✅ Includes codebook version in every file
- ✅ Generates LLM-ready prompt templates
- ✅ Creates organized output directory
- ✅ Ready to copy into your LLM workflow

## Repository Structure

```
codebook_parser/
├── run_parser.py              # Main script (EDIT THIS)
├── scripts/
│   └── codebook_parser.py     # Parser logic (don't edit)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── docs/
│   └── SETUP_GUIDE.md        # Detailed setup instructions
└── examples/
    └── example_output/        # Sample parsed output
```

## Environment Setup

### Option 1: Anaconda Navigator (Recommended for Beginners)

**Step 1: Create New Environment**

1. Open **Anaconda Navigator**
2. Click **Environments** tab (left sidebar)
3. Click **Create** button at bottom
4. Enter environment name: `codebook_parser`
5. Select **Python** version: `3.11.14`
   - If 3.11.14 not available, use latest 3.11.x version
6. Click **Create**
7. Wait for environment to be created

**Step 2: Activate Environment and Install (if needed)**

1. In Anaconda Navigator, select your new `codebook_parser` environment
2. Click the ▶ button next to environment name
3. Select **Open Terminal**
4. In the terminal that opens, navigate to this directory:
   ```bash
   cd path/to/codebook_parser
   ```
5. Verify Python version:
   ```bash
   python --version
   # Should show Python 3.11.14 or 3.11.x
   ```
6. Install requirements (none needed for basic use):
   ```bash
   conda env update -f environment.yml
   ```
   Note: The parser uses only Python standard library, so this step is optional

**Step 3: Run Parser**

Still in the terminal from Step 2:

```bash
python run_parser.py
```

### Option 2: Command Line (Anaconda)

If you prefer command line:

```bash
# Create environment with Python 3.11.14
conda create -n codebook_parser python=3.11.14

# Activate environment
conda activate codebook_parser

# Navigate to repository
cd path/to/codebook_parser

# Run parser
python run_parser.py
```

### Option 3: Standard Python (No Anaconda)

If you have Python 3.11+ installed:

```bash
# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Run parser
python run_parser.py
```

## Configuration

Edit the configuration section at the top of `run_parser.py`:

```python
# ============================================================================
# CONFIGURATION - FILL IN THESE VALUES
# ============================================================================

# Path to your codebook file (.Rmd or .md)
CODEBOOK_FILE = "path/to/your/codebook.Rmd"

# Type of codebook: 'procedural' or 'mode'
CODEBOOK_TYPE = "mode"

# Version of the codebook (e.g., 'v1.0', 'v1.1', 'v2.0')
CODEBOOK_VERSION = "v1.0"

# Name of the codebook (used in output directory name)
CODEBOOK_NAME = "Lithic_Modes"

# Where to save output
OUTPUT_BASE_DIR = "parsed_codebooks"

# Whether to generate LLM prompt templates (True/False)
GENERATE_PROMPTS = True

# JSON formatting - indent level (2 or 4 recommended)
JSON_INDENT = 2
```

### Configuration Examples

**Example 1: Procedural Unit Codebook v1.1**
```python
CODEBOOK_FILE = "Procedural_unit_codebook.Rmd"
CODEBOOK_TYPE = "procedural"
CODEBOOK_VERSION = "v1.1"
CODEBOOK_NAME = "Procedural_Unit"
OUTPUT_BASE_DIR = "parsed_codebooks"
GENERATE_PROMPTS = True
JSON_INDENT = 2
```

**Example 2: Lithic Modes Codebook v1.0**
```python
CODEBOOK_FILE = "Lithic_Modes_AI_Codebook_v2.Rmd"
CODEBOOK_TYPE = "mode"
CODEBOOK_VERSION = "v1.0"
CODEBOOK_NAME = "Lithic_Modes"
OUTPUT_BASE_DIR = "parsed_codebooks"
GENERATE_PROMPTS = True
JSON_INDENT = 2
```

## Running the Parser

Once configured, simply run:

```bash
python run_parser.py
```

You'll see output like:

```
======================================================================
CODEBOOK PARSER
======================================================================

CONFIGURATION:
  Codebook file:    Lithic_Modes_AI_Codebook_v2.Rmd
  Codebook type:    mode
  Codebook name:    Lithic_Modes
  Codebook version: v1.0
  Generate prompts: True
  JSON indent:      2

Output directory: parsed_codebooks/Lithic_Modes_v1.0

======================================================================

Reading codebook from: Lithic_Modes_AI_Codebook_v2.Rmd
Found 17 code entries

Saving JSON files to: parsed_codebooks/Lithic_Modes_v1.0
  [1/17] Saved: mode_a_v1.0.json
  [2/17] Saved: mode_b_v1.0.json
  ...

✓ Successfully saved 17 code entries
✓ Summary saved to: codebook_summary_v1.0.json
✓ Output directory: parsed_codebooks/Lithic_Modes_v1.0

Generating LLM prompts...
  [1/17] Generated: mode_a_v1.0_prompt.txt
  ...

✓ Successfully generated 17 prompt templates
✓ Prompts directory: parsed_codebooks/Lithic_Modes_v1.0/prompts

======================================================================
✓ PARSING COMPLETE!
======================================================================
```

## Output Structure

The parser creates a directory structure like this:

```
parsed_codebooks/
└── Lithic_Modes_v1.0/              # Directory name includes version
    ├── mode_a_v1.0.json            # Each code as JSON (with version)
    ├── mode_b_v1.0.json
    ├── mode_c_v1.0.json
    ├── ...
    ├── codebook_summary_v1.0.json  # Summary file (with version)
    └── prompts/                     # LLM prompts (if enabled)
        ├── mode_a_v1.0_prompt.txt
        ├── mode_b_v1.0_prompt.txt
        └── ...
```

### JSON File Format

Each JSON file contains:

```json
{
  "title": "Mode A",
  "code_id": "mode_a",
  "short_description": "Stone percussors damaged by repetitive percussion...",
  "definition": "Stone percussors are clasts (rounded pebbles or cobbles)...",
  "inclusion_criteria": "Described in text OR shown in figures.",
  "exclusion_criteria": "Not described in text AND not shown in figures.",
  "typical_exemplars": "Text explicitly mentions hammerstones...",
  "atypical_exemplars": "Pestles showing both grinding...",
  "close_but_no": "Ground stone tools with only grinding/polishing...",
  "codebook_type": "technological_mode",
  "codebook_name": "Lithic_Modes",
  "codebook_version": "v1.0",
  "parse_date": "2025-02-10T15:30:00.123456",
  "full_text": "## Mode A\n\n**Short Description:**..."
}
```

### Prompt File Format

Each prompt file is ready to use with an LLM:

```
CODEBOOK: Lithic_Modes v1.0
CODE TYPE: technological_mode
CODE ID: mode_a

You are coding archaeological literature for the presence or absence of: Mode A

DEFINITION:
[Full definition from codebook]

SHORT DESCRIPTION:
[Brief description]

INCLUSION CRITERIA:
[When to code as present]

EXCLUSION CRITERIA:
[When to code as absent]

...

TEXT TO ANALYZE:
{text}

Provide your analysis in the following format:

PRESENT: [Yes/No/Uncertain]
EVIDENCE: [Quotes from text]
REASONING: [Explanation]
...
```

## Using the Output with LLMs

### Step 1: Copy Output to Your LLM Workflow

```bash
# Copy entire versioned directory
cp -r parsed_codebooks/Lithic_Modes_v1.0 /path/to/llm/workflow/
```

### Step 2: Load in Python

```python
import json
from pathlib import Path

# Load a specific code
code_dir = Path("Lithic_Modes_v1.0")
with open(code_dir / "mode_a_v1.0.json") as f:
    code = json.load(f)

print(f"Codebook: {code['codebook_name']} {code['codebook_version']}")
print(f"Code: {code['title']}")

# Load its prompt
with open(code_dir / "prompts" / "mode_a_v1.0_prompt.txt") as f:
    prompt_template = f.read()

# Insert your text
archaeological_text = "The assemblage includes hammerstones..."
prompt = prompt_template.replace('{text}', archaeological_text)

# Send to LLM
response = your_llm_api.complete(prompt)
```

### Step 3: Process All Codes

```python
# Load summary to get all code IDs
with open(code_dir / "codebook_summary_v1.0.json") as f:
    summary = json.load(f)

print(f"Codebook: {summary['codebook_name']} {summary['codebook_version']}")
print(f"Total codes: {summary['total_codes']}")

# Process each code
for code_id in summary['code_ids']:
    # Load code
    code_file = code_dir / f"{code_id}_{summary['codebook_version']}.json"
    with open(code_file) as f:
        code = json.load(f)
    
    # Process with LLM
    print(f"Analyzing for: {code['title']}")
    # ... your LLM code here ...
```

## Supported Codebooks

### Procedural Unit Codebook
- **Type**: `procedural`
- **Codes**: Individual lithic manufacturing techniques
- **Example codes**: Heat treatment, faceting, cresting, etc.

### Technological Mode Codebook (Shea's Modes A-I)
- **Type**: `mode`
- **Codes**: Major technological strategies
- **Example codes**: Mode A (percussors), Mode G2 (blade cores), etc.

Both codebooks must follow the same format:

```markdown
## Code Title

**Short Description:** ...

**Definition:** ...

**Inclusion criteria:** ...

**Exclusion criteria:** ...

**Typical exemplars:** ...

**Atypical exemplars:** ...

**Close but no:** ...
```

## Troubleshooting

### Error: "Codebook file not found"
- Check the path in `CODEBOOK_FILE`
- Use absolute path if relative path doesn't work
- Make sure file has `.Rmd` or `.md` extension

### Error: "No code entries found"
- Verify codebook format matches expected structure
- Check that code entries start with `##` (two hashes)
- Ensure field labels match exactly: `**Short Description:**`, etc.

### Error: "Invalid CODEBOOK_TYPE"
- Must be exactly `'procedural'` or `'mode'` (with quotes)
- Check for typos

### Wrong Python Version
```bash
# In Anaconda terminal
python --version

# Should show 3.11.14 or 3.11.x
# If not, you're not in the right environment
```

### Parser Runs But No Output
- Check `OUTPUT_BASE_DIR` path
- Verify you have write permissions
- Look for error messages in terminal

## Version Control Best Practices

### Why Version Everything?

1. **Reproducibility**: Know exactly which codebook version was used
2. **Comparison**: Easily compare results from different versions
3. **Documentation**: Track changes over time
4. **Collaboration**: Team members use same version

### Recommended Workflow

```bash
# Parse v1.0
CODEBOOK_VERSION = "v1.0"
python run_parser.py
# Creates: Lithic_Modes_v1.0/

# Later, parse v1.1 (after codebook updates)
CODEBOOK_VERSION = "v1.1"
python run_parser.py
# Creates: Lithic_Modes_v1.1/

# Now you have both versions
parsed_codebooks/
├── Lithic_Modes_v1.0/
└── Lithic_Modes_v1.1/
```

### Using Different Versions in Research

```python
# Compare LLM performance across codebook versions
results_v1_0 = analyze_with_codebook("Lithic_Modes_v1.0")
results_v1_1 = analyze_with_codebook("Lithic_Modes_v1.1")

# Calculate agreement
kappa = cohen_kappa(results_v1_0, results_v1_1)
print(f"Agreement between versions: {kappa}")
```

## Advanced Usage

### Custom Output Directory

```python
# Save to specific location
OUTPUT_BASE_DIR = "/path/to/llm_project/codebooks"
```

### Multiple Codebooks

```python
# Parse multiple versions or types
# Just run run_parser.py with different configs

# Result:
parsed_codebooks/
├── Procedural_Unit_v1.0/
├── Procedural_Unit_v1.1/
├── Lithic_Modes_v1.0/
└── Lithic_Modes_v2.0/
```

### Disable Prompts (JSON Only)

```python
# If you want JSON only, no prompts
GENERATE_PROMPTS = False
```

## Getting Help

1. Check this README
2. See `docs/SETUP_GUIDE.md` for detailed instructions
3. Look at `examples/example_output/` for sample output
4. Contact: jonathan.n.paige@gmail.com

## Citation

If using this parser in research:

```
Paige, J. N. (2025). Codebook Parser for Lithic Technology Analysis.
Version 1.0. https://github.com/[your-repo]/codebook_parser
```

Also cite the relevant codebook:

```
# For Procedural Units
[Your procedural unit codebook citation]

# For Technological Modes
Shea, J. J. (2013). Lithic Modes A-I: A New Framework for Describing 
Global-Scale Variation in Stone Tool Technology. Journal of 
Archaeological Method and Theory, 20(1), 151-186.
```

## License

[To be determined]

## Authors

Jonathan Paige  
jonathan.n.paige@gmail.com

## Changelog

### Version 1.0 (2025-02-10)
- Initial release
- Support for both procedural and mode codebooks
- Automatic version tracking in all outputs
- LLM prompt generation
- Anaconda Navigator setup guide
