#!/usr/bin/env python3
"""
Test script to debug why the GUI is falling back to demo mode
when LLM transformer should be working.
"""

print("🔍 Testing LLM Transformer Initialization")
print("=" * 50)

# Test 1: Direct import
print("1. Testing direct import...")
try:
    from llm_transformer import TShirtPromptTransformer
    print("   ✅ Direct import successful")
except ImportError as e:
    print(f"   ❌ Direct import failed: {e}")
    exit(1)

# Test 2: Test GUI's import logic
print("2. Testing GUI import logic...")
try:
    from llm_transformer import TShirtPromptTransformer
    LLM_AVAILABLE = True
    print("   ✅ GUI import logic successful")
except ImportError as e:
    print(f"   ❌ GUI import logic failed: {e}")
    LLM_AVAILABLE = False

print(f"   LLM_AVAILABLE: {LLM_AVAILABLE}")

# Test 3: Test initialization
print("3. Testing initialization...")
if LLM_AVAILABLE:
    try:
        llm_transformer = TShirtPromptTransformer()
        print("   ✅ Initialization successful")
        print(f"   Model available: {llm_transformer.model is not None}")

        if llm_transformer.model is not None:
            print("   🎯 LLM transformer is fully functional!")
        else:
            print("   ⚠️  LLM transformer initialized but model is None (LMStudio issue)")

    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        llm_transformer = None
else:
    print("   ❌ Skipped - LLM not available")
    llm_transformer = None

# Test 4: Check if the issue is in GUI initialization process
print("4. Testing potential GUI conflicts...")

# Import other modules that the GUI imports to see if there are conflicts
try:
    print("   Testing other imports...")
    import tkinter as tk
    from pathlib import Path
    import threading
    import queue
    print("   ✅ No import conflicts detected")
except Exception as e:
    print(f"   ❌ Import conflict detected: {e}")

# Test 5: Test actual transformation
print("5. Testing actual transformation...")
if LLM_AVAILABLE and llm_transformer and llm_transformer.model:
    try:
        sample_post = {
            'id': 'test123',
            'title': 'Test meme about coding',
            'text_content': 'When you finally fix the bug',
            'score': 1000
        }

        print("   Running transformation...")
        result = llm_transformer.transform_reddit_to_tshirt_prompt(sample_post)

        if result.get('success', False):
            print("   ✅ Transformation successful!")
            print(f"   Generated prompt ID: {result.get('prompt_id', 'unknown')}")
        else:
            print(f"   ❌ Transformation failed: {result.get('error', 'unknown error')}")

    except Exception as e:
        print(f"   ❌ Transformation test failed: {e}")
else:
    print("   ⏭️  Skipped - LLM not fully available")

print("\n" + "=" * 50)
print("🎯 CONCLUSION:")

if LLM_AVAILABLE and llm_transformer and llm_transformer.model:
    print("✅ LLM Transformer is FULLY FUNCTIONAL")
    print("❓ The GUI should NOT be falling back to demo mode")
    print("🐛 There may be a bug in the GUI's initialization logic")
else:
    print("❌ LLM Transformer has issues:")
    if not LLM_AVAILABLE:
        print("   - Import failed")
    elif not llm_transformer:
        print("   - Initialization failed")
    elif not llm_transformer.model:
        print("   - LMStudio connection failed")