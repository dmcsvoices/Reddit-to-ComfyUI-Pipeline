#!/usr/bin/env python3
"""
Test ComfyUI Workflow Script
For testing import and auto-detection functionality
"""

import argparse

# Create argument parser
parser = argparse.ArgumentParser(description="Test ComfyUI Workflow")

parser.add_argument(
    "--main_prompt",
    default="A beautiful landscape with mountains",
    help='Main prompt for image generation'
)

parser.add_argument(
    "--negative_prompt",
    default="blurry, low quality",
    help='Negative prompt for image generation'
)

parser.add_argument(
    "--width",
    default=512,
    type=int,
    help='Image width'
)

parser.add_argument(
    "--height",
    default=512,
    type=int,
    help='Image height'
)

parser.add_argument(
    "--steps",
    default=20,
    type=int,
    help='Number of inference steps'
)

def main(**kwargs):
    """Main execution function"""
    args = parser.parse_args()

    print("Test ComfyUI Workflow")
    print(f"Main Prompt: {args.main_prompt}")
    print(f"Negative Prompt: {args.negative_prompt}")
    print(f"Dimensions: {args.width}x{args.height}")
    print(f"Steps: {args.steps}")

    return {"images": "mock_result"}

if __name__ == "__main__":
    main()