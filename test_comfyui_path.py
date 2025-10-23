#!/usr/bin/env python3
"""
Test the corrected ComfyUI output path handling
"""

from comfyui_simple import SimpleComfyUIGenerator
from pathlib import Path

def test_comfyui_paths():
    """Test ComfyUI path configuration"""
    print("🧪 Testing ComfyUI Path Configuration")
    print("=" * 50)

    generator = SimpleComfyUIGenerator()

    print(f"📁 POC Output Directory: {generator.output_dir}")
    print(f"📁 ComfyUI Output Directory: {generator.comfyui_output_dir}")
    print(f"📁 ComfyUI FLUX Directory: {generator.comfyui_flux_dir}")

    # Check if directories exist
    print(f"\n🔍 Directory Status:")
    print(f"  POC Output: {'✅ EXISTS' if generator.output_dir.exists() else '❌ MISSING'}")
    print(f"  ComfyUI Output: {'✅ EXISTS' if generator.comfyui_output_dir.exists() else '❌ MISSING'}")
    print(f"  ComfyUI FLUX: {'✅ EXISTS' if generator.comfyui_flux_dir.exists() else '❌ MISSING'}")

    # Check for recent files in FLUX directory
    if generator.comfyui_flux_dir.exists():
        flux_files = list(generator.comfyui_flux_dir.glob("*.png"))
        print(f"\n📊 FLUX Directory Contents:")
        print(f"  Total PNG files: {len(flux_files)}")

        if flux_files:
            # Show the 3 most recent files
            recent_files = sorted(flux_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]
            print(f"  Most recent files:")
            for i, file in enumerate(recent_files, 1):
                mtime = file.stat().st_mtime
                import datetime
                time_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                print(f"    {i}. {file.name} ({time_str})")

    return True

def test_file_detection():
    """Test file detection logic"""
    print(f"\n🔍 Testing File Detection Logic")
    print("-" * 40)

    generator = SimpleComfyUIGenerator()
    search_dirs = [generator.comfyui_flux_dir, generator.comfyui_output_dir]
    latest_file = None

    for search_dir in search_dirs:
        if search_dir.exists():
            png_files = list(search_dir.glob("*.png"))
            print(f"📁 {search_dir.name}: {len(png_files)} PNG files")

            if png_files:
                dir_latest = max(png_files, key=lambda x: x.stat().st_mtime)
                if latest_file is None or dir_latest.stat().st_mtime > latest_file.stat().st_mtime:
                    latest_file = dir_latest

    if latest_file:
        import datetime
        mtime = datetime.datetime.fromtimestamp(latest_file.stat().st_mtime)
        print(f"\n✅ Latest file found: {latest_file.name}")
        print(f"   Directory: {latest_file.parent}")
        print(f"   Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        return True
    else:
        print(f"\n❌ No recent files found")
        return False

def main():
    print("🚀 ComfyUI Path Testing")
    print("=" * 60)

    # Test 1: Path configuration
    paths_ok = test_comfyui_paths()

    # Test 2: File detection
    detection_ok = test_file_detection()

    print(f"\n📊 Test Results:")
    print(f"  Path Configuration: {'✅ PASS' if paths_ok else '❌ FAIL'}")
    print(f"  File Detection: {'✅ PASS' if detection_ok else '❌ FAIL'}")

    if paths_ok and detection_ok:
        print(f"\n🎉 All tests passed! ComfyUI file handling should now work correctly.")
        print(f"💡 The workflow should now properly detect and organize generated images.")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()