#!/usr/bin/env python3
"""
Test the fixed file handling for ComfyUI generated images
"""

from file_organizer import POCFileOrganizer
from pathlib import Path

def test_file_summary():
    """Test the updated file summary function"""
    print("🧪 Testing File Organization Summary")
    print("=" * 50)

    organizer = POCFileOrganizer()
    summary = organizer.get_summary()

    print(f"📊 Current Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Check if we have images in the images directory
    images_dir = Path("./poc_output/images")
    if images_dir.exists():
        png_files = list(images_dir.glob("*.png"))
        jpg_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg"))

        print(f"\n📁 Files in poc_output/images/:")
        print(f"  PNG files: {len(png_files)}")
        print(f"  JPG files: {len(jpg_files)}")

        if png_files:
            print(f"\n✅ PNG files found:")
            for png_file in png_files[:3]:  # Show first 3
                print(f"    {png_file.name}")

        if jpg_files:
            print(f"\n✅ JPG files found:")
            for jpg_file in jpg_files[:3]:  # Show first 3
                print(f"    {jpg_file.name}")

    return summary['designs'] > 0

def test_comfyui_generator():
    """Test the ComfyUI generator initialization"""
    try:
        from comfyui_simple import SimpleComfyUIGenerator
        generator = SimpleComfyUIGenerator()

        print(f"\n🎨 ComfyUI Generator Test:")
        print(f"  Output dir: {generator.output_dir}")
        print(f"  ComfyUI output dir: {generator.comfyui_output_dir}")
        print(f"  Workflow available: {generator.workflow_available}")

        return True
    except Exception as e:
        print(f"❌ ComfyUI generator error: {e}")
        return False

def main():
    print("🚀 Testing Fixed File Handling")
    print("=" * 60)

    # Test 1: File summary
    summary_works = test_file_summary()

    # Test 2: ComfyUI generator
    generator_works = test_comfyui_generator()

    print(f"\n📊 Test Results:")
    print(f"  File Summary: {'✅ PASS' if summary_works else '❌ FAIL'}")
    print(f"  ComfyUI Generator: {'✅ PASS' if generator_works else '❌ FAIL'}")

    if summary_works and generator_works:
        print(f"\n🎉 All tests passed! File handling should now work correctly.")
        print(f"💡 Try running: python run_poc.py")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()