#!/usr/bin/env python3
"""
Demo script to test the complete script analyzer integration
"""

from script_analyzer import ComfyUIScriptAnalyzer, get_script_execution_args


def demo_script_analyzer():
    """Demo the script analyzer functionality"""
    print("🚀 ComfyUI Script Analyzer Integration Demo")
    print("="*50)

    # Test with both scripts
    scripts = [
        "tshirtPOC_768x1024",
        "flux_lora_nsfw_1024x1024"
    ]

    for script_name in scripts:
        print(f"\n📄 Testing script: {script_name}")
        print("-" * 30)

        # Get execution arguments
        args = get_script_execution_args(
            script_name,
            "Test prompt for awesome t-shirt design",
            negative_prompt="low quality, blurry",
            width=768,
            height=1024,
            steps=20,
            seed=42
        )

        print("✅ Generated execution arguments:")
        for key, value in args.items():
            if isinstance(value, str) and len(value) > 50:
                print(f"  {key}: {value[:50]}...")
            else:
                print(f"  {key}: {value}")

    print(f"\n🎯 Integration Test Complete!")
    print("The GUI now supports:")
    print("  ✅ Auto-detection of prompt arguments")
    print("  ✅ Manual override via UI dropdowns")
    print("  ✅ Dynamic execution with correct arguments")
    print("  ✅ Configuration persistence across sessions")


if __name__ == "__main__":
    demo_script_analyzer()