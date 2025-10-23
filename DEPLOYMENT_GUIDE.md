# T-Shirt POC ComfyUI Deployment Guide

You've identified the core issue: the POC needs to run in the ComfyUI environment where the `comfy` modules are available. This guide provides three deployment options to solve the environment dependency problem.

## Problem Summary

The POC works fine for prompt generation (Phase 1) but fails during ComfyUI execution because:
- The ComfyUI workflow script requires `comfy.options` and other ComfyUI framework modules
- Our POC runs in an isolated environment without these dependencies
- Installing `comfy` via pip doesn't provide the full ComfyUI framework

## Solution Options

### Option 1: Deploy POC to ComfyUI Environment (Recommended)

This is the cleanest solution - copy the POC files into your existing ComfyUI installation.

```bash
# Run the deployment script
python deploy_to_comfyui.py

# Or specify ComfyUI path manually
python deploy_to_comfyui.py --comfyui-path /path/to/your/ComfyUI
```

**What this does:**
1. Automatically finds your ComfyUI installation
2. Copies all POC files to `ComfyUI/tshirt_poc/`
3. Installs POC dependencies in the ComfyUI environment
4. Creates a launch script for easy execution
5. Provides usage instructions

**Then run from ComfyUI directory:**
```bash
cd /path/to/ComfyUI
python launch_tshirt_poc.py          # Full POC workflow
python launch_tshirt_poc.py test     # Test components
python launch_tshirt_poc.py generate # Skip to generation
```

### Option 2: Standalone Prompt Execution

Use the standalone executor to process existing prompts in the ComfyUI environment.

```bash
# First, run POC Phase 1 in your current environment
python run_poc.py

# Then copy comfyui_executor.py to your ComfyUI directory
cp comfyui_executor.py /path/to/ComfyUI/

# Run from ComfyUI environment
cd /path/to/ComfyUI
python comfyui_executor.py --prompt-dir /path/to/poc_output/prompts
```

**Use cases:**
- When you want to keep POC and ComfyUI separate
- For batch processing existing prompts
- Testing ComfyUI generation independently

### Option 3: External Execution Bridge (Automatic Fallback)

The updated `comfyui_simple.py` now includes automatic fallback to external execution.

**How it works:**
1. POC tries to import ComfyUI workflow directly
2. If that fails, it automatically attempts external execution
3. Uses subprocess to call `comfyui_executor.py` from ComfyUI environment

**Requirements:**
- `comfyui_executor.py` must be accessible
- ComfyUI environment must be in system PATH or specified

## Deployment Steps

### Step 1: Choose Your Approach

**For full integration (Option 1):**
```bash
python deploy_to_comfyui.py
```

**For standalone execution (Option 2):**
```bash
# Copy just the executor
cp comfyui_executor.py /path/to/ComfyUI/
cp extract_prompts.py /path/to/ComfyUI/  # Optional, for prompt extraction
```

### Step 2: Set Up ComfyUI Environment

Make sure your ComfyUI environment has the POC dependencies:

```bash
cd /path/to/ComfyUI
pip install praw lmstudio pillow requests
```

### Step 3: Copy Required Files

If using Option 2 or 3, ensure these files are in ComfyUI directory:
- `tshirtPOC_768x1024.py` (your workflow script)
- `comfyui_executor.py` (standalone executor)
- `.env` (Reddit API credentials)

### Step 4: Test the Setup

```bash
# From ComfyUI directory
python comfyui_executor.py --single-prompt "Modern minimalist t-shirt design with geometric patterns, clean vector graphics, commercial quality, 768x1024" --trend-id test
```

## Verification Checklist

✅ **ComfyUI Environment:**
- [ ] ComfyUI runs successfully (`python main.py`)
- [ ] Can import `comfy` modules in Python
- [ ] `tshirtPOC_768x1024.py` is present

✅ **POC Dependencies:**
- [ ] `praw` installed (Reddit API)
- [ ] `lmstudio` installed (LLM integration)
- [ ] `pillow` installed (image processing)
- [ ] `requests` installed (HTTP requests)

✅ **File Structure:**
```
ComfyUI/
├── main.py                    # ComfyUI main
├── tshirt_poc/               # POC files (Option 1)
│   ├── run_poc.py
│   ├── .env
│   └── ...
├── launch_tshirt_poc.py      # Launch script (Option 1)
├── comfyui_executor.py       # Standalone executor (Option 2/3)
└── tshirtPOC_768x1024.py     # Your workflow script
```

## Troubleshooting

### Import Errors
```
ImportError: No module named 'comfy.options'
```
**Solution:** Make sure you're running from the ComfyUI environment, not your isolated POC environment.

### Missing Dependencies
```
ModuleNotFoundError: No module named 'praw'
```
**Solution:** Install POC dependencies in ComfyUI environment:
```bash
cd /path/to/ComfyUI
pip install praw lmstudio pillow requests
```

### File Not Found
```
FileNotFoundError: tshirtPOC_768x1024.py
```
**Solution:** Copy the workflow script to the ComfyUI directory.

### LMStudio Connection
```
Connection refused to http://127.0.0.1:1234
```
**Solution:** Make sure LMStudio is running with a loaded model.

## Usage Examples

### Full Workflow (Option 1)
```bash
cd /path/to/ComfyUI
python launch_tshirt_poc.py
# Prompts for subreddit, generates prompts, asks to continue to generation
```

### Batch Process Existing Prompts (Option 2)
```bash
cd /path/to/ComfyUI
python comfyui_executor.py --prompt-dir /path/to/poc_output/prompts --output-dir ./generated_designs
```

### Single Prompt Test (Any Option)
```bash
cd /path/to/ComfyUI
python comfyui_executor.py --single-prompt "Retro 80s synthwave design, neon colors, vintage aesthetics" --trend-id test123
```

## Next Steps

1. **Choose your deployment option** based on your preferences
2. **Run the deployment script** or manually copy files
3. **Test with a simple prompt** to verify everything works
4. **Run the full POC workflow** from ComfyUI environment
5. **Iterate on prompt quality** and generation parameters

The deployment script (`deploy_to_comfyui.py`) is the recommended approach as it handles all the setup automatically and provides a clean integration.