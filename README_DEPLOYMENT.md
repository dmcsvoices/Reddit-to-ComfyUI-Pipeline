# T-Shirt POC Configuration

## Environment Setup
- ComfyUI Path: /Volumes/Tikbalang2TB/Users/tikbalang/comfy_env/ComfyUI
- POC Path: /Volumes/Tikbalang2TB/Users/tikbalang/comfy_env/ComfyUI/tshirt_poc

## Running the POC
From the ComfyUI directory, run:

```bash
# Basic POC workflow (prompts only)
python launch_tshirt_poc.py

# Test individual components
python launch_tshirt_poc.py test

# Full workflow with image generation
python launch_tshirt_poc.py generate
```

## Important Notes
1. Make sure LMStudio is running on http://127.0.0.1:1234
2. Verify Reddit API credentials in tshirt_poc/.env
3. The POC will create output in tshirt_poc/poc_output/

## Troubleshooting
- If ComfyUI modules still can't be imported, check that you're running from the correct environment
- Make sure all POC dependencies are installed: praw, lmstudio, pillow, requests
- Verify the ComfyUI workflow file (tshirtPOC_768x1024.py) is present
