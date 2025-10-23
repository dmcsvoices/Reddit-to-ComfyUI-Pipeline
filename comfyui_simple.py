import requests
import json
import time
import shutil
import random
from pathlib import Path
from datetime import datetime

class SimpleComfyUIGenerator:
    def __init__(self, endpoint="http://localhost:8188"):
        self.endpoint = endpoint
        self.output_dir = Path("./poc_output/designs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Import the ComfyUI workflow script
        try:
            import tshirtPOC_768x1024 as workflow_module
            self.workflow_module = workflow_module
            self.workflow_available = True
            print("✅ ComfyUI workflow module loaded successfully")
        except ImportError as e:
            print(f"❌ Failed to import ComfyUI workflow: {e}")
            print("⚠️  Falling back to placeholder mode")
            self.workflow_module = None
            self.workflow_available = False

    def check_comfyui_status(self):
        """Check if ComfyUI is running and accessible"""
        try:
            response = requests.get(f"{self.endpoint}/system_stats", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def generate_text_design(self, text, trend_id):
        """Generate simple text-based t-shirt design"""

        if not self.check_comfyui_status():
            return {
                "success": False,
                "error": "ComfyUI not accessible at " + self.endpoint
            }

        # Simple prompt for text design
        prompt = f"T-shirt design text: '{text}', modern typography, clean font, centered layout, high contrast, commercial quality, 768x1024 pixels"

        # Basic ComfyUI workflow (simplified)
        workflow = {
            "text_prompt": prompt,
            "width": 768,
            "height": 1024,
            "steps": 20,
            "cfg_scale": 7.5,
            "output_format": "PNG"
        }

        # Execute workflow
        result = self.execute_workflow(workflow)

        if result["success"]:
            # Save with organized naming
            output_file = self.output_dir / f"design_{trend_id}_{int(time.time())}.png"

            # Move the file if it was generated successfully
            if "output_path" in result and Path(result["output_path"]).exists():
                shutil.move(result["output_path"], output_file)
                return {
                    "success": True,
                    "output_path": str(output_file),
                    "trend_id": trend_id,
                    "prompt": prompt
                }

        return {"success": False, "error": result.get("error", "Unknown error")}

    def generate_from_prompt(self, comfyui_prompt, trend_id):
        """Generate design from a ComfyUI prompt"""

        if not self.check_comfyui_status():
            return {
                "success": False,
                "error": "ComfyUI not accessible at " + self.endpoint
            }

        # Create workflow from prompt
        workflow = {
            "text_prompt": comfyui_prompt,
            "width": 768,
            "height": 1024,
            "steps": 20,
            "cfg_scale": 7.5,
            "output_format": "PNG"
        }

        # Execute workflow
        result = self.execute_workflow(workflow)

        if result["success"]:
            # Save with organized naming
            output_file = self.output_dir / f"design_{trend_id}_{int(time.time())}.png"

            # Move the file if it was generated successfully
            if "output_path" in result and Path(result["output_path"]).exists():
                shutil.move(result["output_path"], output_file)
                return {
                    "success": True,
                    "output_path": str(output_file),
                    "trend_id": trend_id,
                    "prompt": comfyui_prompt
                }

        return {"success": False, "error": result.get("error", "Unknown error")}

    def execute_workflow(self, workflow):
        """Execute workflow using ComfyUI SaveAsScript generated module"""
        if not self.workflow_available:
            print(f"🎨 [PLACEHOLDER] Would execute ComfyUI workflow:")
            print(f"   Prompt: {workflow['text_prompt'][:100]}...")
            print(f"   Dimensions: {workflow['width']}x{workflow['height']}")

            # Try external execution approach
            return self.execute_external_workflow(workflow)

        try:
            print(f"🎨 Executing ComfyUI workflow:")
            print(f"   Prompt: {workflow['text_prompt'][:100]}...")
            print(f"   Dimensions: {workflow['width']}x{workflow['height']}")

            # Generate unique filename for this generation
            timestamp = int(datetime.now().timestamp())
            output_filename = f"tshirt_design_{timestamp}.png"
            output_path = self.output_dir / output_filename

            # Execute the workflow with our parameters
            result = self.workflow_module.main(
                text4=workflow['text_prompt'],  # Main prompt
                text5="",  # Negative prompt (empty)
                width6=workflow['width'],
                height7=workflow['height'],
                steps13=workflow.get('steps', 20),
                seed12=random.randint(1, 2**32),  # Random seed for variety
                guidance11=workflow.get('guidance', 4),
                cfg14=workflow.get('cfg', 1),
                sampler_name15=workflow.get('sampler_name', 'dpmpp_2m_sde'),
                scheduler16=workflow.get('scheduler', 'beta'),
                denoise17=workflow.get('denoise', 1),
                filename_prefix18=f"POC_{timestamp}",
                output=str(output_path),  # Direct output path
                queue_size=1
            )

            if result and 'images' in result:
                print(f"✅ ComfyUI generation successful: {output_filename}")
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "message": f"Generated via ComfyUI workflow: {output_filename}",
                    "result_data": result
                }
            else:
                print(f"❌ ComfyUI generation failed: No images in result")
                return {
                    "success": False,
                    "error": "No images generated by ComfyUI workflow"
                }

        except Exception as e:
            print(f"❌ ComfyUI workflow execution error: {str(e)}")
            # Try external execution as fallback
            print("🔄 Attempting external execution fallback...")
            return self.execute_external_workflow(workflow)

    def execute_external_workflow(self, workflow):
        """Execute workflow using external script approach"""
        import subprocess
        import tempfile

        # Save prompt to temporary file for external execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(workflow['text_prompt'])
            prompt_file = f.name

        try:
            # Try to find the tshirt_executor script in multiple locations
            possible_locations = [
                Path(__file__).parent / "tshirt_executor.py",  # Same directory as this script
                Path.cwd() / "tshirt_executor.py",  # Current working directory
                Path("/Volumes/Tikbalang2TB/Users/tikbalang/comfy_env/ComfyUI/tshirt_executor.py"),  # Your ComfyUI path
            ]

            executor_script = None
            for location in possible_locations:
                if location.exists():
                    executor_script = location
                    print(f"📍 Found ComfyUI executor at: {location}")
                    break

            if executor_script is None:
                # Try to deploy the executor automatically
                print("🔄 ComfyUI executor not found, attempting to copy to ComfyUI environment...")
                return self.auto_deploy_and_execute(workflow)

            # Generate trend ID for this execution
            timestamp = int(time.time())
            trend_id = f"poc_{timestamp}"

            print(f"🔄 Executing via external ComfyUI script...")

            # Execute the external script
            result = subprocess.run([
                "python", str(executor_script),
                "--single-prompt", workflow['text_prompt'],
                "--trend-id", trend_id,
                "--output-dir", str(self.output_dir)
            ], capture_output=True, text=True, cwd=str(executor_script.parent))

            if result.returncode == 0:
                # Look for generated file
                generated_files = list(self.output_dir.glob(f"*{trend_id}*.png"))
                if generated_files:
                    output_path = generated_files[0]
                    print(f"✅ External execution successful: {output_path.name}")
                    return {
                        "success": True,
                        "output_path": str(output_path),
                        "message": f"Generated via external ComfyUI executor: {output_path.name}"
                    }

            print(f"❌ External execution failed:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")

            return {
                "success": False,
                "error": f"External execution failed: {result.stderr or 'Unknown error'}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"External execution error: {str(e)}"
            }
        finally:
            # Clean up temporary file
            try:
                Path(prompt_file).unlink()
            except:
                pass

    def auto_deploy_and_execute(self, workflow):
        """Automatically deploy executor to ComfyUI and execute workflow"""
        import shutil

        # Detect ComfyUI installation
        comfyui_locations = [
            Path("/Volumes/Tikbalang2TB/Users/tikbalang/comfy_env/ComfyUI"),
            Path.home() / "ComfyUI",
            Path.cwd() / "ComfyUI"
        ]

        comfyui_path = None
        for location in comfyui_locations:
            if location.exists() and (location / "main.py").exists():
                comfyui_path = location
                print(f"📍 Found ComfyUI installation: {location}")
                break

        if comfyui_path is None:
            return {
                "success": False,
                "error": "ComfyUI installation not found for auto-deployment"
            }

        try:
            # Copy executor script to ComfyUI directory
            source_executor = Path(__file__).parent / "tshirt_executor.py"
            target_executor = comfyui_path / "tshirt_executor.py"

            if source_executor.exists():
                shutil.copy2(source_executor, target_executor)
                print(f"✅ Deployed executor to: {target_executor}")

                # Also copy the workflow script
                source_workflow = Path(__file__).parent / "tshirtPOC_768x1024.py"
                target_workflow = comfyui_path / "tshirtPOC_768x1024.py"
                if source_workflow.exists():
                    shutil.copy2(source_workflow, target_workflow)
                    print(f"✅ Deployed workflow to: {target_workflow}")

                # Now try to execute
                return self.execute_via_deployed_executor(workflow, target_executor, comfyui_path)

            else:
                return {
                    "success": False,
                    "error": f"Source executor not found: {source_executor}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Auto-deployment failed: {str(e)}"
            }

    def execute_via_deployed_executor(self, workflow, executor_script, comfyui_path):
        """Execute workflow via deployed executor"""
        import subprocess

        timestamp = int(time.time())
        trend_id = f"poc_{timestamp}"

        try:
            print(f"🔄 Executing via deployed ComfyUI script...")

            # Execute the external script from ComfyUI directory
            result = subprocess.run([
                "python", str(executor_script),
                "--single-prompt", workflow['text_prompt'],
                "--trend-id", trend_id,
                "--output-dir", str(self.output_dir)
            ], capture_output=True, text=True, cwd=str(comfyui_path))

            if result.returncode == 0:
                # Look for generated file
                generated_files = list(self.output_dir.glob(f"*{trend_id}*.png"))
                if generated_files:
                    output_path = generated_files[0]
                    print(f"✅ Auto-deployed execution successful: {output_path.name}")
                    return {
                        "success": True,
                        "output_path": str(output_path),
                        "message": f"Generated via auto-deployed ComfyUI executor: {output_path.name}"
                    }

            print(f"❌ Auto-deployed execution failed:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")

            return {
                "success": False,
                "error": f"Auto-deployed execution failed: {result.stderr or 'Unknown error'}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Auto-deployed execution error: {str(e)}"
            }

    def create_simple_workflow_api(self, prompt, width=768, height=1024):
        """Create a simple ComfyUI API workflow for text-based design"""
        # This would contain the actual ComfyUI node structure
        # For now, returning a placeholder structure
        workflow_api = {
            "3": {
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 7.5,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "text, watermark, logo, signature, blurry, low quality",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "tshirt_design",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
        return workflow_api

if __name__ == "__main__":
    # Test the ComfyUI generator
    print("🧪 Testing ComfyUI generator...")

    generator = SimpleComfyUIGenerator()

    if generator.check_comfyui_status():
        print("✅ ComfyUI is accessible")

        # Test with sample text
        result = generator.generate_text_design("Test Design", "test123")
        if result["success"]:
            print(f"✅ Test generation successful: {result['output_path']}")
        else:
            print(f"❌ Test generation failed: {result['error']}")
    else:
        print(f"❌ ComfyUI not accessible at {generator.endpoint}")
        print("This is expected for POC Phase 1 - focus on prompt generation first")