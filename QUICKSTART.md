# QUICK START GUIDE

## 5-Minute Setup

### 1. Open Anaconda Navigator
   - Launch Anaconda Navigator application

### 2. Create Environment
   - Click **Environments** tab → **Create** button
   - Name: `codebook_parser`
   - Python version: `3.11.14`
   - Click **Create** → Wait 2-5 minutes

### 3. Open Terminal
   - Select `codebook_parser` environment
   - Click **▶** button → **Open Terminal**

### 4. Navigate to Repository
   ```bash
   cd /path/to/codebook_parser_repo
   ```


### 5. Copy environment to yours
    ```bash
    conda env update -f environment.yml
    
    
    conda env update -f environment.yml --prune
    ```



### 5. Edit Configuration
   - Open `run_parser.py` in text editor
   - Find configuration section (line ~20)
   - Change these lines:

   ```python
   CODEBOOK_FILE = "path/to/your/codebook.Rmd"  # ← Change this
   CODEBOOK_TYPE = "mode"                        # ← Or "procedural"
   CODEBOOK_VERSION = "v1.0"                     # ← Your version
   CODEBOOK_NAME = "Lithic_Modes"                # ← Your name
   ```

### 6. Run Parser
   ```bash
   python run_parser.py
   ```

### 7. Find Output
   ```
   parsed_codebooks/
   └── [Your_Codebook_v1.0]/
       ├── [code]_v1.0.json (17 files)
       ├── codebook_summary_v1.0.json
       └── prompts/
           └── [code]_v1.0_prompt.txt (17 files)
   ```

## Configuration Examples

### For Lithic Modes Codebook

```python
CODEBOOK_FILE = "Lithic_Modes_AI_Codebook_v2.Rmd"
CODEBOOK_TYPE = "mode"
CODEBOOK_VERSION = "v1.0"
CODEBOOK_NAME = "Lithic_Modes"
```

### For Procedural Unit Codebook

```python
CODEBOOK_FILE = "Procedural_unit_codebook.Rmd"
CODEBOOK_TYPE = "procedural"
CODEBOOK_VERSION = "v1.1"
CODEBOOK_NAME = "Procedural_Unit"
```

## What You Get

After running, each code entry becomes:

1. **JSON file** (`mode_a_v1.0.json`):
   ```json
   {
     "title": "Mode A",
     "codebook_version": "v1.0",
     "codebook_name": "Lithic_Modes",
     "definition": "...",
     "inclusion_criteria": "...",
     ...
   }
   ```

2. **Prompt template** (`mode_a_v1.0_prompt.txt`):
   ```
   CODEBOOK: Lithic_Modes v1.0
   CODE ID: mode_a
   
   You are coding for: Mode A
   
   DEFINITION: ...
   INCLUSION CRITERIA: ...
   
   TEXT TO ANALYZE:
   {text}
   ```

## Common Issues

❌ **"File not found"**  
✓ Check `CODEBOOK_FILE` path, use absolute path

❌ **"No code entries"**  
✓ Verify codebook format (## headers, **Field:** labels)

❌ **"Wrong Python"**  
✓ Make sure terminal shows `(codebook_parser)` prefix

## Next Steps

1. **Copy output to LLM project**:
   ```bash
   cp -r parsed_codebooks/Lithic_Modes_v1.0 /your/llm/project/
   ```

2. **Use in Python**:
   ```python
   import json
   
   with open("Lithic_Modes_v1.0/mode_a_v1.0.json") as f:
       code = json.load(f)
   
   print(code['codebook_version'])  # v1.0
   ```

3. **Use prompts with LLM**:
   ```python
   with open("Lithic_Modes_v1.0/prompts/mode_a_v1.0_prompt.txt") as f:
       template = f.read()
   
   prompt = template.replace('{text}', your_text)
   response = llm.complete(prompt)
   ```

## Files to Read

- `README.md` - Full documentation
- `docs/SETUP_GUIDE.md` - Detailed setup with screenshots
- `STRUCTURE.md` - Repository organization
- `examples/example_output/` - Sample parsed output

## Getting Help

📧 jonathan.n.paige@gmail.com

See full README.md for troubleshooting and advanced usage.
