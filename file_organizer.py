import json
import shutil
from pathlib import Path
from datetime import datetime

class POCFileOrganizer:
    def __init__(self, base_dir="./poc_output"):
        self.base_dir = Path(base_dir)
        self.setup_structure()

    def setup_structure(self):
        """Create simple folder structure"""
        folders = [
            "generated_designs",
            "prompts",
            "metadata",
            "logs"
        ]

        for folder in folders:
            (self.base_dir / folder).mkdir(parents=True, exist_ok=True)

        print(f"📁 Created output structure in: {self.base_dir}")

    def organize_design(self, design_result, trend_data):
        """Organize generated design with metadata"""

        if not design_result["success"]:
            return None

        design_id = f"poc_design_{trend_data['id']}"

        # Move to organized location
        final_path = self.base_dir / "generated_designs" / f"{design_id}.png"

        # Only move if source file exists
        if "output_path" in design_result and Path(design_result["output_path"]).exists():
            shutil.move(design_result["output_path"], final_path)
        else:
            print(f"⚠️  No output file to move for design {design_id}")
            return None

        # Create simple metadata
        metadata = {
            "design_id": design_id,
            "created": datetime.now().isoformat(),
            "source_trend": {
                "reddit_id": trend_data["id"],
                "title": trend_data["title"],
                "score": trend_data["score"]
            },
            "generation": {
                "prompt": design_result["prompt"],
                "specs": {
                    "width": 768,
                    "height": 1024,
                    "format": "PNG"
                }
            },
            "file_path": str(final_path)
        }

        # Save metadata
        metadata_file = self.base_dir / "metadata" / f"{design_id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        return {
            "design_id": design_id,
            "file_path": final_path,
            "metadata_file": metadata_file
        }

    def log_session(self, session_data):
        """Log session results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.base_dir / "logs" / f"session_{timestamp}.json"

        with open(log_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        print(f"📊 Session logged to: {log_file}")
        return log_file

    def get_summary(self):
        """Get summary of generated content"""
        # Count designs from multiple directories
        designs_count = 0
        design_dirs = ["generated_designs", "designs", "images"]

        for dir_name in design_dirs:
            design_dir = self.base_dir / dir_name
            if design_dir.exists():
                designs_count += len(list(design_dir.glob("*.png")))
                designs_count += len(list(design_dir.glob("*.jpg")))
                designs_count += len(list(design_dir.glob("*.jpeg")))

        summary = {
            "prompts": len(list((self.base_dir / "prompts").glob("*.md"))),
            "designs": designs_count,
            "metadata_files": len(list((self.base_dir / "metadata").glob("*.json"))),
            "log_files": len(list((self.base_dir / "logs").glob("*.json")))
        }
        return summary

if __name__ == "__main__":
    # Test the organizer
    print("🧪 Testing file organizer...")

    organizer = POCFileOrganizer()

    # Test sample data
    sample_trend = {
        "id": "test123",
        "title": "Test trend",
        "score": 1500
    }

    sample_design_result = {
        "success": True,
        "output_path": "./test_design.png",
        "prompt": "Test prompt for t-shirt design"
    }

    # Create a dummy file for testing
    test_file = Path("./test_design.png")
    test_file.touch()

    try:
        result = organizer.organize_design(sample_design_result, sample_trend)
        if result:
            print(f"✅ Test organization successful: {result['design_id']}")
        else:
            print("❌ Test organization failed")
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
    finally:
        # Clean up test file if it still exists
        if test_file.exists():
            test_file.unlink()

    # Show summary
    summary = organizer.get_summary()
    print(f"📊 Content summary: {summary}")