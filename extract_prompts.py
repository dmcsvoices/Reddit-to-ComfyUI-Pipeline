#!/usr/bin/env python3
"""
Extract ComfyUI prompts from generated markdown files
"""

import re
from pathlib import Path
import argparse

def extract_comfyui_prompt(markdown_file):
    """Extract just the ComfyUI prompt from a markdown file"""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the ComfyUI Prompt section between triple backticks
        pattern = r'## ComfyUI Prompt\s*\n\s*```\s*\n(.*?)\n\s*```'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()
        else:
            print(f"⚠️  No ComfyUI prompt found in {markdown_file}")
            return None

    except Exception as e:
        print(f"❌ Error reading {markdown_file}: {e}")
        return None

def extract_source_info(markdown_file):
    """Extract source information for context"""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract key info
        reddit_id_match = re.search(r'- \*\*Reddit ID\*\*: (.+)', content)
        title_match = re.search(r'- \*\*Original Title\*\*: (.+)', content)
        score_match = re.search(r'- \*\*Popularity Score\*\*: (.+)', content)
        generation_type_match = re.search(r'- \*\*Generation Type\*\*: (.+)', content)

        return {
            'reddit_id': reddit_id_match.group(1) if reddit_id_match else 'Unknown',
            'title': title_match.group(1) if title_match else 'Unknown',
            'score': score_match.group(1) if score_match else 'Unknown',
            'generation_type': generation_type_match.group(1) if generation_type_match else 'Unknown'
        }

    except Exception as e:
        print(f"❌ Error extracting info from {markdown_file}: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description='Extract ComfyUI prompts from markdown files')
    parser.add_argument('--input-dir', '-i', default='./poc_output/prompts',
                       help='Directory containing prompt markdown files')
    parser.add_argument('--output-file', '-o', default=None,
                       help='Output file for extracted prompts (default: print to console)')
    parser.add_argument('--latest', '-l', action='store_true',
                       help='Extract only the latest prompt file')
    parser.add_argument('--include-metadata', '-m', action='store_true',
                       help='Include source metadata with prompts')

    args = parser.parse_args()

    prompt_dir = Path(args.input_dir)

    if not prompt_dir.exists():
        print(f"❌ Directory {prompt_dir} not found")
        return

    # Get markdown files
    markdown_files = list(prompt_dir.glob("*.md"))

    if not markdown_files:
        print(f"❌ No markdown files found in {prompt_dir}")
        return

    # Sort by modification time, newest first
    markdown_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    if args.latest:
        markdown_files = markdown_files[:1]
        print(f"📄 Processing latest file: {markdown_files[0].name}")
    else:
        print(f"📄 Processing {len(markdown_files)} prompt files...")

    extracted_prompts = []

    for md_file in markdown_files:
        prompt = extract_comfyui_prompt(md_file)
        if prompt:
            if args.include_metadata:
                info = extract_source_info(md_file)
                extracted_prompts.append({
                    'file': md_file.name,
                    'prompt': prompt,
                    'metadata': info
                })
            else:
                extracted_prompts.append(prompt)

    # Output results
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            if args.include_metadata:
                for item in extracted_prompts:
                    f.write(f"# {item['file']}\n")
                    f.write(f"Reddit: {item['metadata']['title']} (ID: {item['metadata']['reddit_id']}, Score: {item['metadata']['score']})\n")
                    f.write(f"Type: {item['metadata']['generation_type']}\n\n")
                    f.write(f"{item['prompt']}\n\n")
                    f.write("-" * 80 + "\n\n")
            else:
                for prompt in extracted_prompts:
                    f.write(f"{prompt}\n\n")
                    f.write("-" * 80 + "\n\n")
        print(f"✅ Extracted prompts saved to: {args.output_file}")
    else:
        # Print to console
        if args.include_metadata:
            for item in extracted_prompts:
                print(f"\n📋 {item['file']}")
                print(f"🔗 Reddit: {item['metadata']['title']} (ID: {item['metadata']['reddit_id']}, Score: {item['metadata']['score']})")
                print(f"🎨 Type: {item['metadata']['generation_type']}")
                print(f"\n💬 ComfyUI Prompt:")
                print("-" * 60)
                print(item['prompt'])
                print("-" * 60)
        else:
            for i, prompt in enumerate(extracted_prompts, 1):
                print(f"\n💬 Prompt {i}:")
                print("-" * 60)
                print(prompt)
                print("-" * 60)

    print(f"\n✅ Extracted {len(extracted_prompts)} ComfyUI prompts")

if __name__ == "__main__":
    main()