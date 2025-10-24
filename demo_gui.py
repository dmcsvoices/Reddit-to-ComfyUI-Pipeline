#!/usr/bin/env python3
"""
Demo script for the Synthwave GUI
This script demonstrates the Reddit-to-ComfyUI Pipeline GUI with mock data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Check if the GUI file exists
try:
    from synthwave_gui import SynthwaveGUI
    print("✓ GUI module loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import GUI: {e}")
    print("Make sure synthwave_gui.py is in the current directory")
    sys.exit(1)

# Check for required dependencies
required_modules = ['tkinter', 'threading', 'queue', 'pathlib']
missing_modules = []

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f"✗ Missing required modules: {missing_modules}")
    sys.exit(1)

print("✓ All required modules available")

def print_demo_info():
    """Print demo information"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              SYNTHWAVE GUI DEMO - Reddit to ComfyUI         ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  🎨 Features Demonstrated:                                   ║
    ║    • Synthwave-themed splash screen                          ║
    ║    • Tabbed interface with 4 main sections                   ║
    ║    • Reddit subreddit selection (predefined + custom)       ║
    ║    • Trend scan parameters (score, posts, time filter)      ║
    ║    • Real-time progress monitoring                           ║
    ║    • Generated prompts display and management                ║
    ║    • ComfyUI script selection and import                     ║
    ║    • Workflow monitoring with live logs                      ║
    ║                                                              ║
    ║  📋 Tabs:                                                    ║
    ║    1. SCAN SETUP    - Configure and run Reddit scans        ║
    ║    2. RESULTS       - View prompts and control ComfyUI      ║
    ║    3. COMFYUI CONFIG - Manage ComfyUI scripts               ║
    ║    4. WORKFLOW MONITOR - Real-time logs and statistics      ║
    ║                                                              ║
    ║  🎯 Demo Mode: Backend integration is simulated             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def main():
    """Main demo function"""
    print_demo_info()

    try:
        print("🚀 Launching Synthwave GUI...")
        app = SynthwaveGUI()
        print("✓ GUI session completed")

    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()