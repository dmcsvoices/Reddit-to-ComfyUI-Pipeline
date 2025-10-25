#!/usr/bin/env python3
"""
Test script for the ComfyUI Script Analyzer
"""

from script_analyzer import ComfyUIScriptAnalyzer, analyze_comfyui_script


def test_script_analysis():
    """Test the script analyzer with existing scripts"""
    print("🔍 Testing ComfyUI Script Analyzer\n")

    scripts_to_test = [
        "tshirtPOC_768x1024.py",
        "flux_lora_nsfw_1024x1024.py"
    ]

    analyzer = ComfyUIScriptAnalyzer()

    for script_name in scripts_to_test:
        print(f"📄 Analyzing: {script_name}")
        print("=" * 50)

        try:
            arguments, mapping = analyze_comfyui_script(script_name)

            print(f"Found {len(arguments)} arguments:")

            # Show top scored text arguments
            text_args = [arg for arg in arguments if 'text' in arg.dest.lower()]
            text_args.sort(key=lambda x: x.score, reverse=True)

            for arg in text_args[:5]:  # Show top 5
                print(f"  📝 {arg.name} (dest: {arg.dest})")
                print(f"     Score: {arg.score:.2f}")
                print(f"     Help: {arg.help_text[:60]}...")
                print(f"     Default length: {len(str(arg.default)) if arg.default else 0}")
                print()

            print("🎯 Suggested Mapping:")
            print(f"  Main Prompt: {mapping.main_prompt}")
            print(f"  Negative Prompt: {mapping.negative_prompt}")
            print(f"  Width: {mapping.width}")
            print(f"  Height: {mapping.height}")
            print(f"  Steps: {mapping.steps}")
            print(f"  Seed: {mapping.seed}")

            # Save the mapping
            script_base = script_name.replace('.py', '')
            analyzer.save_mapping(script_base, mapping)
            print(f"💾 Saved mapping to script_configs/{script_base}.json")

            # Test execution args
            test_args = analyzer.get_execution_args(
                script_base,
                "Test prompt for t-shirt design",
                negative_prompt="low quality, blurry",
                width=768,
                height=1024,
                steps=20,
                seed=12345
            )

            print("\n🚀 Execution Args:")
            for key, value in test_args.items():
                if isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value[:50]}...")
                else:
                    print(f"  {key}: {value}")

        except Exception as e:
            print(f"❌ Error analyzing {script_name}: {e}")

        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_script_analysis()