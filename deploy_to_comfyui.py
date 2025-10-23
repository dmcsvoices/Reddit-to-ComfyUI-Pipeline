#!/usr/bin/env python3
"""
Deploy T-Shirt POC to ComfyUI Environment
Copy POC files to ComfyUI installation directory for execution
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

class ComfyUIPOCDeployer:
    def __init__(self, comfyui_path=None):
        """
        Initialize deployer with ComfyUI installation path

        Args:
            comfyui_path: Path to ComfyUI installation. If None, will attempt to detect.
        """
        self.poc_dir = Path(__file__).parent
        self.comfyui_path = self.find_comfyui_path(comfyui_path)

        if not self.comfyui_path:
            print("❌ ComfyUI installation not found!")
            print("💡 Please specify the path manually:")
            print("   python deploy_to_comfyui.py --comfyui-path /path/to/ComfyUI")
            sys.exit(1)

        self.poc_target_dir = self.comfyui_path / "tshirt_poc"

    def find_comfyui_path(self, provided_path=None):
        """Find ComfyUI installation directory"""
        if provided_path:
            path = Path(provided_path)
            if path.exists() and (path / "main.py").exists():
                return path

        # Common ComfyUI installation locations
        common_paths = [
            Path.home() / "ComfyUI",
            Path("/opt/ComfyUI"),
            Path("/usr/local/ComfyUI"),
            Path("./ComfyUI"),
            Path("../ComfyUI"),
        ]

        for path in common_paths:
            if path.exists() and (path / "main.py").exists():
                print(f"✅ Found ComfyUI at: {path}")
                return path

        # Try to find it in Python path
        try:
            import comfy
            comfy_path = Path(comfy.__file__).parent.parent
            if (comfy_path / "main.py").exists():
                print(f"✅ Found ComfyUI via Python import: {comfy_path}")
                return comfy_path
        except ImportError:
            pass

        return None

    def copy_poc_files(self):
        """Copy POC files to ComfyUI directory"""
        print(f"📁 Creating POC directory in ComfyUI: {self.poc_target_dir}")
        self.poc_target_dir.mkdir(exist_ok=True)

        # Files to copy
        poc_files = [
            "run_poc.py",
            "reddit_collector.py",
            "llm_transformer.py",
            "comfyui_simple.py",
            "file_organizer.py",
            "image_handler.py",
            "extract_prompts.py",
            "tshirtPOC_768x1024.py",
            ".env",
            "requirements.txt"
        ]

        copied_files = []
        for file_name in poc_files:
            source_file = self.poc_dir / file_name
            target_file = self.poc_target_dir / file_name

            if source_file.exists():
                shutil.copy2(source_file, target_file)
                copied_files.append(file_name)
                print(f"✅ Copied: {file_name}")
            else:
                print(f"⚠️  File not found: {file_name}")

        return copied_files

    def install_dependencies(self):
        """Install POC dependencies in ComfyUI environment"""
        print("\n🔧 Installing POC dependencies...")

        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

        if not in_venv:
            print("⚠️  Not in a virtual environment. ComfyUI might use one.")

        # Try to install dependencies
        requirements_file = self.poc_target_dir / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True, cwd=self.comfyui_path)
                print("✅ Dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                print("💡 You may need to manually install:")
                print("   pip install praw lmstudio pillow requests")
        else:
            # Install essential packages directly
            essential_packages = ["praw", "lmstudio", "pillow", "requests"]
            for package in essential_packages:
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], check=True, cwd=self.comfyui_path)
                    print(f"✅ Installed: {package}")
                except subprocess.CalledProcessError:
                    print(f"⚠️  Failed to install: {package}")

    def create_launch_script(self):
        """Create a launch script in ComfyUI directory"""
        launch_script_content = f"""#!/usr/bin/env python3
\"\"\"
T-Shirt POC Launcher - Run from ComfyUI Environment
\"\"\"

import sys
from pathlib import Path

# Add ComfyUI to Python path
comfyui_path = Path(__file__).parent
sys.path.insert(0, str(comfyui_path))

# Add POC directory to path
poc_path = comfyui_path / "tshirt_poc"
sys.path.insert(0, str(poc_path))

# Change to POC directory for relative paths
import os
os.chdir(str(poc_path))

# Import and run POC
try:
    from run_poc import run_poc, test_components

    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_components()
        elif sys.argv[1] == "generate":
            from run_poc import run_poc_with_generation
            run_poc_with_generation()
        else:
            print("Usage: python launch_tshirt_poc.py [test|generate]")
    else:
        run_poc()

except ImportError as e:
    print(f"❌ Import error: {{e}}")
    print("Make sure all dependencies are installed in this environment")
except Exception as e:
    print(f"❌ Error running POC: {{e}}")
"""

        launch_script = self.comfyui_path / "launch_tshirt_poc.py"
        with open(launch_script, 'w') as f:
            f.write(launch_script_content)

        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(launch_script, 0o755)

        print(f"✅ Created launch script: {launch_script}")
        return launch_script

    def create_config_note(self):
        """Create configuration notes"""
        config_note = f"""# T-Shirt POC Configuration

## Environment Setup
- ComfyUI Path: {self.comfyui_path}
- POC Path: {self.poc_target_dir}

## Running the POC
From the ComfyUI directory, run:

```bash
# Basic POC workflow (prompts only)
python launch_tshirt_poc.py

# Test individual components
python launch_tshirt_poc.py test

# Full workflow with image generation
python launch_tshirt_poc.py generate
```

## Important Notes
1. Make sure LMStudio is running on http://127.0.0.1:1234
2. Verify Reddit API credentials in tshirt_poc/.env
3. The POC will create output in tshirt_poc/poc_output/

## Troubleshooting
- If ComfyUI modules still can't be imported, check that you're running from the correct environment
- Make sure all POC dependencies are installed: praw, lmstudio, pillow, requests
- Verify the ComfyUI workflow file (tshirtPOC_768x1024.py) is present
"""

        config_file = self.poc_target_dir / "README_DEPLOYMENT.md"
        with open(config_file, 'w') as f:
            f.write(config_note)

        print(f"✅ Created configuration guide: {config_file}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Deploy T-Shirt POC to ComfyUI Environment')
    parser.add_argument('--comfyui-path', '-p', help='Path to ComfyUI installation')
    parser.add_argument('--no-deps', action='store_true', help='Skip dependency installation')

    args = parser.parse_args()

    print("🚀 T-Shirt POC ComfyUI Deployment")
    print("=" * 50)

    deployer = ComfyUIPOCDeployer(args.comfyui_path)

    print(f"📁 ComfyUI found at: {deployer.comfyui_path}")
    print(f"📁 Deploying to: {deployer.poc_target_dir}")

    # Copy files
    copied_files = deployer.copy_poc_files()

    # Install dependencies
    if not args.no_deps:
        deployer.install_dependencies()
    else:
        print("⏭️  Skipping dependency installation")

    # Create launch script
    launch_script = deployer.create_launch_script()

    # Create configuration guide
    deployer.create_config_note()

    print("\n🎉 Deployment Complete!")
    print("=" * 50)
    print(f"📁 POC files copied to: {deployer.poc_target_dir}")
    print(f"🚀 Launch script created: {launch_script}")
    print("\n💡 Next steps:")
    print(f"1. cd {deployer.comfyui_path}")
    print("2. python launch_tshirt_poc.py")
    print("\n📖 See README_DEPLOYMENT.md in the POC directory for full instructions")

if __name__ == "__main__":
    main()