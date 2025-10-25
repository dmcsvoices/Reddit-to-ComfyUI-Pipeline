#!/usr/bin/env python3
"""
T-Shirt Design Automation POC - Main Script
Run the complete proof-of-concept workflow
"""

from reddit_collector import get_trending_memes, get_user_subreddit_choice
from llm_transformer import TShirtPromptTransformer
from file_organizer import POCFileOrganizer
import time
from datetime import datetime

def run_poc():
    """Run the complete POC workflow"""

    print("🚀 Starting T-Shirt Design POC...")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    print("-" * 60)

    # Step 1: Get user's subreddit choice
    selected_subreddit = get_user_subreddit_choice()
    print(f"✅ Selected subreddit: r/{selected_subreddit}")

    # Step 2: Get trending content with images
    print(f"\n📱 Collecting trending posts from r/{selected_subreddit}...")
    print("🖼️  Image downloading enabled - this may take longer...")
    trends = get_trending_memes(limit=10, subreddit_name=selected_subreddit, download_images=True)
    print(f"Found {len(trends)} trending posts")

    if not trends:
        print("❌ No trending content found. Check Reddit API credentials.")
        return

    # Step 3: Filter for text-based content
    text_trends = [t for t in trends if t.get('text_content')]
    print(f"Found {len(text_trends)} text-based trends suitable for t-shirts")

    if not text_trends:
        print("❌ No suitable text content found. Try again later.")
        print("💡 Hint: Look for memes with quotes or short phrases")
        return

    # Show what we found
    print("\n📋 Text trends found:")
    for i, trend in enumerate(text_trends[:5], 1):
        print(f"  {i}. \"{trend['text_content']}\" (Score: {trend['score']})")

    # Step 4: Initialize components
    print(f"\n🤖 Initializing LLM transformer...")
    transformer = TShirtPromptTransformer()

    print("📁 Setting up file organization...")
    organizer = POCFileOrganizer()

    # Step 5: Transform trends to ComfyUI prompts
    print(f"\n🔄 Transforming trends to ComfyUI prompts...")
    selected_trends = text_trends[:3]  # Just 3 for POC
    prompt_results = transformer.batch_transform(selected_trends)

    successful_prompts = [r for r in prompt_results if r["success"]]
    print(f"✅ Successfully generated {len(successful_prompts)} ComfyUI prompts")

    if not successful_prompts:
        print("❌ No prompts were generated successfully. Check LMStudio connection.")
        return

    # Step 6: Ask user if they want to continue to generation
    print(f"\n💾 Prompts saved as markdown files in ./poc_output/prompts/")

    # Ask user if they want to continue to Phase 2
    continue_to_generation = input(f"\n🎨 Continue to ComfyUI image generation? (y/N): ").strip().lower()

    # Show generated prompts
    print(f"Generated {len(successful_prompts)} ComfyUI prompts:")
    for result in successful_prompts:
        print(f"  📄 {result['prompt_id']} → {result['prompt_file']}")

    if continue_to_generation in ['y', 'yes']:
        print(f"\n🎨 Starting ComfyUI Generation Phase...")
        generation_results = run_generation_phase(successful_prompts, text_trends, organizer)

        successful_designs = [r for r in generation_results if r.get('success', False)]
        print(f"\n🎉 Complete POC Workflow Finished!")
        print(f"Generated {len(successful_prompts)} prompts and {len(successful_designs)} designs")

        # Log session with generation data
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "phase": "Complete POC - Prompt Generation + ComfyUI Generation",
            "selected_subreddit": selected_subreddit,
            "trends_collected": len(trends),
            "text_trends_found": len(text_trends),
            "prompts_generated": len(successful_prompts),
            "designs_generated": len(successful_designs),
            "successful_prompts": [r['prompt_id'] for r in successful_prompts],
            "successful_designs": [r.get('design_id', 'unknown') for r in successful_designs],
            "next_steps": [
                "Review generated designs for quality",
                "Upload designs to Threadless for testing",
                "Iterate on prompt engineering"
            ]
        }
    else:
        print(f"\n🎉 POC Phase 1 Complete!")
        print(f"💡 To run generation later, use: python run_poc.py generate")

        # Log session - Phase 1 only
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "phase": "POC Phase 1 - Visual Prompt Generation",
            "selected_subreddit": selected_subreddit,
            "trends_collected": len(trends),
            "text_trends_found": len(text_trends),
            "prompts_generated": len(successful_prompts),
            "successful_prompts": [r['prompt_id'] for r in successful_prompts],
            "next_steps": [
                "Review generated visual prompts for quality",
                "Set up ComfyUI for Phase 2 testing",
                "Test actual visual image generation"
            ]
        }

    log_file = organizer.log_session(session_data)

    print(f"\n📊 Session Summary:")
    summary = organizer.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print(f"\n📁 All files saved to: ./poc_output/")
    print(f"📋 Session log: {log_file}")
    print(f"\n✨ Next: Review the generated files to validate quality")
    print(f"🎨 Note: Prompts now focus on VISUAL GRAPHICS, not just text designs")

def run_generation_phase(successful_prompts, text_trends, organizer):
    """Run the ComfyUI generation phase by executing exported scripts directly"""
    import subprocess
    import random
    from pathlib import Path

    # Find the ComfyUI script to execute
    script_name = "tshirtPOC_768x1024.py"
    script_path = Path(script_name)

    if not script_path.exists():
        print(f"❌ ComfyUI script not found: {script_name}")
        print("💡 Export your ComfyUI workflow using SaveAsScript extension")
        return []

    print(f"🎨 Executing ComfyUI script directly: {script_name}")
    generation_results = []

    for i, prompt_result in enumerate(successful_prompts, 1):
        print(f"\n🖼️  Generating design {i}/{len(successful_prompts)}: {prompt_result['prompt_id']}")

        # Find corresponding trend data
        trend_data = next((t for t in text_trends if t['id'] == prompt_result['trend_id']), None)
        if not trend_data:
            print(f"⚠️  Could not find trend data for {prompt_result['trend_id']}")
            continue

        try:
            # Import and execute the ComfyUI script as a module
            import importlib.util

            # Load the module
            spec = importlib.util.spec_from_file_location("comfyui_script", script_path)
            module = importlib.util.module_from_spec(spec)

            # Prepare arguments
            execution_args = {
                'text4': prompt_result['comfyui_prompt'],
                'text5': "",  # negative prompt
                'width6': 768,
                'height7': 1024,
                'steps13': 20,
                'seed12': random.randint(1, 2**32 - 1),
                'filename_prefix18': f"FLUX/reddit_{prompt_result['trend_id']}"
            }

            print(f"   Executing as module with prompt: \"{prompt_result['comfyui_prompt'][:50]}...\"")

            # Execute the script
            spec.loader.exec_module(module)
            result = module.main(**execution_args)

            design_result = {
                "success": True,
                "trend_id": prompt_result['trend_id'],
                "script_result": result
            }
            print(f"✅ Generated successfully")

        except Exception as e:
            design_result = {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "trend_id": prompt_result['trend_id']
            }
            print(f"❌ Error: {e}")

        generation_results.append(design_result)

    return generation_results

def run_poc_with_generation():
    """Extended POC that includes ComfyUI script execution"""
    print("🚀 Starting Extended T-Shirt Design POC with Generation...")

    # Run basic POC first
    run_poc()

    # Check if we have prompts to work with
    organizer = POCFileOrganizer()
    summary = organizer.get_summary()

    if summary['prompts'] == 0:
        print("❌ No prompts available for generation phase")
        return

    # Check for ComfyUI script
    from pathlib import Path
    script_name = "tshirtPOC_768x1024.py"
    script_path = Path(script_name)

    if not script_path.exists():
        print(f"❌ ComfyUI script not found: {script_name}")
        print("💡 Export your ComfyUI workflow using SaveAsScript extension")
        return

    print(f"✅ Found ComfyUI script: {script_name}")

    # Load and process existing prompts
    prompt_files = list((organizer.base_dir / "prompts").glob("*.md"))
    print(f"Found {len(prompt_files)} prompt files to process")

    print("🎨 ComfyUI script execution ready")

def test_components():
    """Test individual components"""
    print("🧪 Testing individual POC components...")

    # Test Reddit collector
    print("\n1. Testing Reddit collector...")
    trends = get_trending_memes(limit=3, subreddit_name="memes", download_images=False)
    print(f"   ✅ Found {len(trends)} trends")

    # Test LLM transformer
    print("\n2. Testing LLM transformer...")
    transformer = TShirtPromptTransformer()
    if transformer.model and trends:
        result = transformer.transform_reddit_to_tshirt_prompt(trends[0])
        if result["success"]:
            print(f"   ✅ Generated prompt: {result['prompt_id']}")
        else:
            print(f"   ❌ Failed: {result['error']}")

    # Test file organizer
    print("\n3. Testing file organizer...")
    organizer = POCFileOrganizer()
    summary = organizer.get_summary()
    print(f"   ✅ File structure ready: {summary}")

    # Test ComfyUI script availability
    print("\n4. Testing ComfyUI script...")
    from pathlib import Path
    script_path = Path("tshirtPOC_768x1024.py")
    if script_path.exists():
        print("   ✅ ComfyUI script found")
    else:
        print("   ⚠️  ComfyUI script not found (export using SaveAsScript)")

    print("\n🎯 Component testing complete!")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_components()
        elif sys.argv[1] == "generate":
            run_poc_with_generation()
        else:
            print("Usage: python run_poc.py [test|generate]")
    else:
        # Default: run basic POC
        run_poc()