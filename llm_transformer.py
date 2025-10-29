import lmstudio as lms
import json
from pathlib import Path
from datetime import datetime
import os

class TShirtPromptTransformer:
    def __init__(self, model_instance=None, model_name="qwen/qwen3-vl-30b@4bit", output_dir="./poc_output/prompts", use_vision=True):
        """
        Initialize transformer with either an external model instance or by creating one

        Args:
            model_instance: Pre-loaded LMStudio model instance (preferred)
            model_name: Model name to load if model_instance is None (fallback)
            output_dir: Directory for saving prompts
            use_vision: Enable vision/multimodal capabilities
        """
        self.model_name = model_name
        self.use_vision = use_vision

        if model_instance is not None:
            # Use provided model instance
            self.model = model_instance
            print(f"✅ Using provided LMStudio model instance")
            if use_vision:
                print("🔍 Vision mode enabled - will process images when available")
        else:
            # Fallback: create model instance
            try:
                self.model = lms.llm(model_name)
                print(f"✅ Connected to LMStudio model: {model_name}")
                if use_vision:
                    print("🔍 Vision mode enabled - will process images when available")
            except Exception as e:
                print(f"❌ Failed to connect to LMStudio: {str(e)}")
                print("Make sure LMStudio is running and the model is loaded")
                self.model = None
                self.use_vision = False

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def update_model(self, model_instance, model_name=None):
        """Update the model instance used by the transformer

        Args:
            model_instance: New LMStudio model instance
            model_name: Optional model name for tracking
        """
        self.model = model_instance
        if model_name:
            self.model_name = model_name
        print(f"✅ Model updated: {model_name or 'instance provided'}")

    def validate_model(self):
        """Validate that the model is available and responsive

        Returns:
            bool: True if model is valid, False otherwise
        """
        if not self.model:
            print("❌ Model validation failed: No model instance")
            return False

        try:
            # Simple validation check by attempting a minimal response
            test_response = self.model.respond("Test")
            return True
        except Exception as e:
            print(f"❌ Model validation failed: {str(e)}")
            return False

    def reconnect_model(self):
        """Attempt to reconnect to the model using the stored model name

        Returns:
            bool: True if reconnection successful, False otherwise
        """
        if not self.model_name:
            print("❌ Cannot reconnect: No model name stored")
            return False

        try:
            print(f"🔄 Attempting to reconnect to model: {self.model_name}")
            self.model = lms.llm(self.model_name)
            print(f"✅ Model reconnected successfully: {self.model_name}")
            return True
        except Exception as e:
            print(f"❌ Model reconnection failed: {str(e)}")
            self.model = None
            return False

    def transform_reddit_to_tshirt_prompt(self, trend_data):
        """Transform Reddit trend into optimized ComfyUI t-shirt design prompt with optional image analysis"""

        # Validate model before proceeding
        if not self.validate_model():
            # Attempt reconnection if validation fails
            print("🔄 Model validation failed, attempting reconnection...")
            if not self.reconnect_model():
                return {
                    "success": False,
                    "error": "LMStudio model not available - validation and reconnection failed",
                    "trend_id": trend_data['id']
                }

        # Check if we have images to analyze
        has_images = self.use_vision and trend_data.get('images') and len(trend_data['images']) > 0
        image_analysis = ""

        if has_images:
            image_path = trend_data['images'][0]  # Use first image
            try:
                image_analysis = self.analyze_image(image_path)
                print(f"🔍 Analyzed image: {os.path.basename(image_path)}")
            except Exception as e:
                print(f"⚠️  Image analysis failed: {str(e)}")
                has_images = False

        # Determine the source of text content for better prompt context
        text_content = trend_data.get('text_content', 'N/A')
        title = trend_data['title']
        text_source = "extracted" if text_content != title else "title"

        transformation_prompt = f"""
You are a professional t-shirt design prompt engineer. Transform this Reddit trend into a detailed ComfyUI prompt for generating a trendy visual t-shirt design.

Reddit Content:
- Title: {title}
- Text Content: {text_content} (source: {text_source})
- Popularity Score: {trend_data['score']}
- Content Type: {"Image + Text" if has_images else "Text-only post"}{"" if not has_images else f'''
- Image Analysis: {image_analysis}'''}

Requirements for the ComfyUI visual design prompt:
- Create a VISUAL GRAPHIC design, not just text
- Include illustrations, characters, symbols, or visual elements that represent the trend{"" if not has_images else '''
- INCORPORATE visual elements and themes from the analyzed image'''}
- Combine visual elements with minimal text if needed
- Must be suitable for t-shirt printing (768x1024px, high contrast, bold graphics)
- Include specific art style (cartoon, minimalist, retro, modern, etc.)
- Specify colors, composition, and visual hierarchy
- Make it commercially appealing and trendy
- Focus on creating an engaging visual that captures the essence of the trend{"" if not has_images else " and the visual content from the image"}
- Include technical specs: "768x1024 pixels, 300 DPI, RGB, transparent background"
- Specify artistic style (vector art, illustration, graphic design, etc.)

Output only the ComfyUI prompt text for VISUAL GRAPHICS, no other explanation.
"""

        try:
            # Get LLM response - use vision if we have images
            if has_images:
                image_path = trend_data['images'][0]
                image_handle = lms.prepare_image(image_path)
                chat = lms.Chat()
                chat.add_user_message(transformation_prompt, images=[image_handle])
                response = self.model.respond(chat)
            else:
                response = self.model.respond(transformation_prompt)

            # Extract text from response object
            comfyui_prompt = str(response) if hasattr(response, '__str__') else response.text

            # Save prompt as markdown file
            prompt_id = f"prompt_{trend_data['id']}_{int(datetime.now().timestamp())}"
            prompt_file = self.output_dir / f"{prompt_id}.md"

            # Create detailed prompt file
            image_info = ""
            if has_images:
                image_info = f"""
## Image Analysis
- **Source Image**: {os.path.basename(trend_data['images'][0])}
- **Vision Model Used**: Yes (multimodal generation)
- **Image Analysis**: {image_analysis if image_analysis else 'Visual elements incorporated'}
"""

            prompt_content = f"""# T-Shirt Design Prompt ({"Multimodal" if has_images else "Text-Only"})

## Source Information
- **Reddit ID**: {trend_data['id']}
- **Original Title**: {trend_data['title']}
- **Text Content**: {trend_data.get('text_content', 'N/A')}
- **Popularity Score**: {trend_data['score']}
- **Generated**: {datetime.now().isoformat()}
- **Generation Type**: {"Vision + Text" if has_images else "Text Only"}{image_info}

## ComfyUI Prompt

```
{comfyui_prompt.strip()}
```

## Technical Specifications
- **Dimensions**: 768x1024 pixels
- **Resolution**: 300 DPI
- **Color Mode**: RGB
- **Background**: Transparent
- **Format**: PNG
- **Design Type**: {"Visual graphic with image-inspired elements" if has_images else "Visual graphic design"}

## Notes
- Optimized for Threadless Artist Shop requirements
- Generated via LMStudio LLM transformation{"" if not has_images else " with vision model"}
- {"Image-informed design based on Reddit post visual content" if has_images else "Text-based design generation"}
"""

            # Save the markdown file
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt_content)

            return {
                "success": True,
                "prompt_id": prompt_id,
                "comfyui_prompt": comfyui_prompt.strip(),
                "prompt_file": str(prompt_file),
                "trend_id": trend_data['id']
            }

        except Exception as e:
            error_msg = str(e)

            # Check for specific model-related errors that might be recoverable
            if any(keyword in error_msg.lower() for keyword in ['model not found', 'connection', 'timeout', 'network']):
                print(f"🔄 Detected recoverable model error: {error_msg}")

                # Attempt to reconnect and retry once
                if self.reconnect_model():
                    print("🔄 Retrying transformation after model reconnection...")
                    try:
                        # Retry the transformation with the reconnected model
                        return self._retry_transformation(trend_data)
                    except Exception as retry_error:
                        print(f"❌ Retry failed: {retry_error}")
                        return {
                            "success": False,
                            "error": f"Initial error: {error_msg}. Retry after reconnection also failed: {str(retry_error)}",
                            "trend_id": trend_data['id'],
                            "recovery_attempted": True
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Model error (reconnection failed): {error_msg}",
                        "trend_id": trend_data['id'],
                        "recovery_attempted": True
                    }
            else:
                # Non-recoverable error
                return {
                    "success": False,
                    "error": error_msg,
                    "trend_id": trend_data['id'],
                    "recovery_attempted": False
                }

    def _retry_transformation(self, trend_data):
        """Retry transformation with current model (used after reconnection)

        Args:
            trend_data: The trend data to transform

        Returns:
            dict: Transformation result
        """
        # Re-validate model before retry
        if not self.validate_model():
            raise Exception("Model validation failed after reconnection")

        # Check if we have images to analyze (same logic as main method)
        has_images = self.use_vision and trend_data.get('images') and len(trend_data['images']) > 0
        image_analysis = ""

        if has_images:
            image_path = trend_data['images'][0]
            try:
                image_analysis = self.analyze_image(image_path)
                print(f"🔍 Re-analyzed image: {os.path.basename(image_path)}")
            except Exception as e:
                print(f"⚠️  Image re-analysis failed: {str(e)}")
                has_images = False

        # Determine the source of text content
        text_content = trend_data.get('text_content', 'N/A')
        title = trend_data['title']
        text_source = "extracted" if text_content != title else "title"

        transformation_prompt = f"""
You are a professional t-shirt design prompt engineer. Transform this Reddit trend into a detailed ComfyUI prompt for generating a trendy visual t-shirt design.

Reddit Content:
- Title: {title}
- Text Content: {text_content} (source: {text_source})
- Popularity Score: {trend_data['score']}
- Content Type: {"Image + Text" if has_images else "Text-only post"}{"" if not has_images else f'''
- Image Analysis: {image_analysis}'''}

Requirements for the ComfyUI visual design prompt:
- Create a VISUAL GRAPHIC design, not just text
- Include illustrations, characters, symbols, or visual elements that represent the trend{"" if not has_images else '''
- INCORPORATE visual elements and themes from the analyzed image'''}
- Combine visual elements with minimal text if needed
- Must be suitable for t-shirt printing (768x1024px, high contrast, bold graphics)
- Include specific art style (cartoon, minimalist, retro, modern, etc.)
- Specify colors, composition, and visual hierarchy
- Make it commercially appealing and trendy
- Focus on creating an engaging visual that captures the essence of the trend{"" if not has_images else " and the visual content from the image"}
- Include technical specs: "768x1024 pixels, 300 DPI, RGB, transparent background"
- Specify artistic style (vector art, illustration, graphic design, etc.)

Output only the ComfyUI prompt text for VISUAL GRAPHICS, no other explanation.
"""

        # Get LLM response - use vision if we have images
        if has_images:
            image_path = trend_data['images'][0]
            image_handle = lms.prepare_image(image_path)
            chat = lms.Chat()
            chat.add_user_message(transformation_prompt, images=[image_handle])
            response = self.model.respond(chat)
        else:
            response = self.model.respond(transformation_prompt)

        # Extract text from response object
        comfyui_prompt = str(response) if hasattr(response, '__str__') else response.text

        # Save prompt as markdown file (same logic as main method)
        prompt_id = f"prompt_{trend_data['id']}_{int(datetime.now().timestamp())}_retry"
        prompt_file = self.output_dir / f"{prompt_id}.md"

        # Create detailed prompt file
        image_info = ""
        if has_images:
            image_info = f"""
## Image Analysis
- **Source Image**: {os.path.basename(trend_data['images'][0])}
- **Vision Model Used**: Yes (multimodal generation)
- **Image Analysis**: {image_analysis if image_analysis else 'Visual elements incorporated'}
"""

        prompt_content = f"""# T-Shirt Design Prompt ({"Multimodal" if has_images else "Text-Only"}) - RETRY

## Source Information
- **Reddit ID**: {trend_data['id']}
- **Original Title**: {trend_data['title']}
- **Text Content**: {trend_data.get('text_content', 'N/A')}
- **Popularity Score**: {trend_data['score']}
- **Generated**: {datetime.now().isoformat()}
- **Generation Type**: {"Vision + Text" if has_images else "Text Only"} (Retry after reconnection){image_info}

## ComfyUI Prompt

```
{comfyui_prompt.strip()}
```

## Technical Specifications
- **Dimensions**: 768x1024 pixels
- **Resolution**: 300 DPI
- **Color Mode**: RGB
- **Background**: Transparent
- **Format**: PNG
- **Design Type**: {"Visual graphic with image-inspired elements" if has_images else "Visual graphic design"}

## Notes
- Optimized for Threadless Artist Shop requirements
- Generated via LMStudio LLM transformation{"" if not has_images else " with vision model"}
- {"Image-informed design based on Reddit post visual content" if has_images else "Text-based design generation"}
- **RETRY**: This prompt was generated after model reconnection
"""

        # Save the markdown file
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_content)

        return {
            "success": True,
            "prompt_id": prompt_id,
            "comfyui_prompt": comfyui_prompt.strip(),
            "prompt_file": str(prompt_file),
            "trend_id": trend_data['id'],
            "retry_success": True
        }

    def batch_transform(self, trends_list):
        """Transform multiple trends into ComfyUI prompts"""
        results = []

        for trend in trends_list:
            print(f"🤖 Transforming trend: '{trend.get('title', 'Unknown')[:50]}...'")
            result = self.transform_reddit_to_tshirt_prompt(trend)
            results.append(result)

            if result["success"]:
                print(f"✅ Generated prompt: {result['prompt_id']}")
            else:
                print(f"❌ Failed: {result['error']}")

        return results

    def analyze_image(self, image_path):
        """Analyze image using vision model to understand visual content"""
        try:
            image_handle = lms.prepare_image(image_path)
            analysis_prompt = """Analyze this image and describe:
1. Main visual elements, objects, characters, or scenes
2. Color scheme and visual style
3. Mood, emotion, or atmosphere
4. Key visual themes that could be adapted for t-shirt design
5. Any text or symbols present

Keep description concise but detailed, focusing on design-relevant aspects."""

            chat = lms.Chat()
            chat.add_user_message(analysis_prompt, images=[image_handle])
            response = self.model.respond(chat)

            return str(response) if hasattr(response, '__str__') else response.text

        except Exception as e:
            print(f"❌ Image analysis error: {str(e)}")
            return "Image analysis failed - proceeding with text-only generation"

if __name__ == "__main__":
    # Test the transformer
    print("🧪 Testing LLM transformer...")

    # Sample trend data for testing
    sample_trend = {
        "id": "test123",
        "title": "When you finally understand the assignment",
        "score": 2500,
        "text_content": "finally understand the assignment"
    }

    transformer = TShirtPromptTransformer()
    if transformer.model:
        result = transformer.transform_reddit_to_tshirt_prompt(sample_trend)
        if result["success"]:
            print(f"✅ Test successful! Generated: {result['prompt_id']}")
        else:
            print(f"❌ Test failed: {result['error']}")
    else:
        print("❌ Cannot test - LMStudio not available")