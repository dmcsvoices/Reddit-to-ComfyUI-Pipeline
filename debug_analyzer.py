#!/usr/bin/env python3
"""
Debug script to see what the analyzer is parsing
"""

import re
from script_analyzer import ComfyUIScriptAnalyzer


def debug_argument_parsing():
    """Debug the argument parsing"""
    script_path = "tshirtPOC_768x1024.py"

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("🔍 Debugging argument parsing for tshirtPOC_768x1024.py\n")

    # Find the text4 and text5 arguments specifically
    text4_match = re.search(
        r'parser\.add_argument\(\s*["\']--text4["\'](?:,\s*([^)]+))\)',
        content,
        re.MULTILINE | re.DOTALL
    )

    if text4_match:
        print("📝 Found --text4 argument:")
        print("Full match:", text4_match.group(0)[:200] + "...")
        print("Parameters:", text4_match.group(1)[:100] + "...")

        # Look for default value specifically
        params = text4_match.group(1)
        default_match = re.search(r'default\s*=\s*([^,\n]+)', params, re.DOTALL)
        if default_match:
            default_raw = default_match.group(1).strip()
            print(f"Raw default: {default_raw[:100]}...")
            print(f"Default length: {len(default_raw)}")

    print("\n" + "="*50)

    # Let's also check the actual multiline string extraction
    # Find text4 argument block more carefully
    text4_pattern = r'parser\.add_argument\(\s*["\']--text4["\'],?\s*default\s*=\s*([\'"][^\'"]*[\'"]|\'\'\'.+?\'\'\'),?'
    text4_full = re.search(text4_pattern, content, re.DOTALL)

    if text4_full:
        print("📝 Full text4 default value:")
        default_value = text4_full.group(1)
        print(f"Length: {len(default_value)}")
        print(f"First 100 chars: {default_value[:100]}")


if __name__ == "__main__":
    debug_argument_parsing()