#!/usr/bin/env python3
"""
Debug script to simulate the exact GUI initialization sequence
to identify why the LLM transformer is not being used.
"""

print("🐛 Debugging GUI Initialization Sequence")
print("=" * 60)

# Step 1: Simulate the exact import sequence from the GUI
print("Step 1: Module imports...")
print("-" * 30)

try:
    from llm_transformer import TShirtPromptTransformer
    LLM_AVAILABLE = True
    print(f"✅ LLM_AVAILABLE = {LLM_AVAILABLE}")
except ImportError as e:
    print(f"⚠️ LLM transformer not available: {e}")
    LLM_AVAILABLE = False

try:
    from comfyui_simple import SimpleComfyUIGenerator
    COMFYUI_AVAILABLE = True
    print(f"✅ COMFYUI_AVAILABLE = {COMFYUI_AVAILABLE}")
except ImportError as e:
    print(f"⚠️ ComfyUI not available: {e}")
    COMFYUI_AVAILABLE = False

# Step 2: Simulate GUI class initialization
print("\nStep 2: GUI class initialization...")
print("-" * 30)

class DebugGUI:
    def __init__(self):
        print("Initializing backend instances...")

        # Backend instances (exactly like in the GUI)
        self.llm_transformer = None
        self.comfyui = None

        print("Initializing LLM transformer...")
        if LLM_AVAILABLE:
            try:
                self.llm_transformer = TShirtPromptTransformer()
                print("✅ LLM transformer initialized")
                print(f"   Model status: {self.llm_transformer.model is not None}")
            except Exception as e:
                print(f"❌ LLM transformer failed: {e}")
                self.llm_transformer = None
        else:
            print("❌ LLM transformer not available (demo mode)")
            self.llm_transformer = None

        print(f"Final llm_transformer state: {self.llm_transformer is not None}")

# Step 3: Test the initialization
print("\nStep 3: Creating GUI instance...")
print("-" * 30)

gui = DebugGUI()

# Step 4: Test the transformation logic
print("\nStep 4: Testing transformation logic...")
print("-" * 30)

# Simulate a Reddit post
sample_post = {
    'id': 'debug123',
    'title': 'Debug test post',
    'text_content': 'Testing transformation',
    'score': 500
}

print("Testing transformation path...")
if gui.llm_transformer:
    print("✅ Using LLM transformer (CORRECT PATH)")
    try:
        result = gui.llm_transformer.transform_reddit_to_tshirt_prompt(sample_post)
        if result.get('success', False):
            print(f"✅ Transformation successful: {result.get('prompt_id')}")
        else:
            print(f"❌ Transformation failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Transform failed: {e}")
else:
    print("❌ Using demo mode (WRONG PATH - this shouldn't happen!)")

print("\n" + "=" * 60)
print("🎯 DIAGNOSIS:")
if gui.llm_transformer:
    print("✅ LLM transformer is working correctly in this test")
    print("❓ If GUI is still using demo mode, the issue is elsewhere")
else:
    print("❌ LLM transformer failed during GUI initialization")
    print("🔍 This explains the demo mode fallback")