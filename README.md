# 🚀 Reddit-to-ComfyUI Pipeline

**Automated T-Shirt Design Generation from Trending Reddit Content**

Transform viral Reddit trends into print-ready t-shirt designs using AI-powered automation! This pipeline monitors Reddit for trending content, processes it through Vision-Language Models, and generates commercial-quality designs using ComfyUI workflows.

![Pipeline Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-orange) ![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

🎯 **Trend Monitoring**: Automatically scrapes trending content from Reddit subreddits
🖼️ **Multimodal AI**: Processes both text and images using Vision-Language Models
🎨 **Design Generation**: Creates 768x1024 print-ready designs via ComfyUI
📁 **Smart Organization**: Automatically organizes outputs with metadata tracking
🔄 **Flexible Execution**: Multiple deployment options for different environments
⚡ **Batch Processing**: Handle multiple trends in a single workflow

## 🎬 How It Works

```
📱 Reddit API → 🤖 LLM Processing → 🎨 ComfyUI Generation → 👕 Print-Ready Design
```

1. **Content Collection**: Monitors specified subreddits for trending posts
2. **AI Transformation**: Uses LMStudio's local LLM to convert trends into design prompts
3. **Visual Generation**: Executes ComfyUI workflows to create t-shirt graphics
4. **Quality Control**: Organizes outputs with metadata for easy review

## 🛠️ Installation

### Prerequisites

- **Python 3.8+**
- **ComfyUI** ([Installation Guide](https://github.com/comfyanonymous/ComfyUI))
- **LMStudio** ([Download](https://lmstudio.ai/)) with a compatible LLM model
- **Reddit API Credentials** ([Get them here](https://www.reddit.com/prefs/apps))

### Step 1: Clone the Repository

```bash
git clone https://github.com/dmcsvoices/Reddit-to-ComfyUI-Pipeline.git
cd Reddit-to-ComfyUI-Pipeline
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install ComfyUI SaveAsScript Extension

This pipeline requires the SaveAsScript extension to convert ComfyUI workflows into Python scripts:

```bash
cd path/to/your/ComfyUI/custom_nodes
git clone https://github.com/atmaranto/ComfyUI-SaveAsScript.git
```

**Important**: After installing, restart ComfyUI and use the SaveAsScript feature to export your t-shirt design workflow as a Python script.

### Step 4: Configure Environment

Create a `.env` file with your Reddit API credentials:

```bash
# Reddit API Configuration
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=YourApp/1.0 by YourUsername

# LMStudio Configuration (optional)
LMSTUDIO_ENDPOINT=http://127.0.0.1:1234
LMSTUDIO_MODEL=llama-3.2-1b-instruct
```

### Step 5: Set Up ComfyUI Workflow

1. Create your t-shirt design workflow in ComfyUI
2. Use the **SaveAsScript** extension to export it as `tshirtPOC_768x1024.py`
3. Place the exported script in the project directory

## 🚀 Quick Start

### Basic Usage

```bash
# Run the complete pipeline
python run_poc.py

# Test individual components
python run_poc.py test

# Run with generation phase
python run_poc.py generate
```

### Advanced Usage

```bash
# Process specific subreddit
python run_poc.py --subreddit memes

# Extract ComfyUI prompts from existing runs
python extract_prompts.py --latest --include-metadata

# Execute standalone prompt
python tshirt_executor.py --single-prompt "Your design prompt here"
```

## 📁 Project Structure

```
Reddit-to-ComfyUI-Pipeline/
├── 📄 run_poc.py                 # Main workflow orchestrator
├── 🤖 reddit_collector.py        # Reddit API integration
├── 🧠 llm_transformer.py         # LLM prompt processing
├── 🖼️ image_handler.py           # Image downloading & processing
├── 🎨 comfyui_simple.py          # ComfyUI workflow execution
├── 📁 file_organizer.py          # Output organization
├── 🔧 tshirt_executor.py         # Standalone ComfyUI executor
├── 📊 extract_prompts.py         # Prompt extraction utility
├── 🚀 deploy_to_comfyui.py       # Environment deployment
├── 📖 DEPLOYMENT_GUIDE.md        # Detailed setup instructions
└── 📋 requirements.txt           # Python dependencies
```

## 🎯 Workflow Examples

### Example 1: Meme to T-Shirt

**Input**: Trending meme from r/memes
**Processing**: AI extracts quotable text and visual concepts
**Output**: Modern graphic design with meme reference

### Example 2: Viral Quote

**Input**: Popular text post from r/Showerthoughts
**Processing**: LLM transforms into commercial design prompt
**Output**: Typography-focused t-shirt design

### Example 3: Image Meme

**Input**: Image meme with text overlay
**Processing**: Vision model analyzes both image and text
**Output**: Recreated design suitable for printing

## ⚙️ Configuration

### ComfyUI Integration

The pipeline supports multiple ComfyUI integration methods:

1. **Direct Integration**: Run within ComfyUI environment
2. **External Execution**: Bridge between isolated environments
3. **Auto-Deployment**: Automatic file copying and setup

### LMStudio Models

Recommended models for t-shirt design generation:
- `llama-3.2-1b-instruct` (fast, good quality)
- `llama-3.2-3b-instruct` (better quality, slower)
- Any model supporting vision inputs for multimodal processing

## 📈 Output Specifications

All generated designs meet commercial print standards:

- **Resolution**: 768x1024 pixels at 300 DPI
- **Format**: PNG with transparent background
- **Color Mode**: RGB for digital printing compatibility
- **Print Method**: Optimized for DTG (Direct-to-Garment)

## 🛠️ Troubleshooting

### Common Issues

**ComfyUI Import Errors**
```bash
# Solution: Run from ComfyUI environment
cd /path/to/ComfyUI
python /path/to/pipeline/run_poc.py
```

**Reddit API Rate Limits**
```bash
# Solution: Reduce collection frequency
# Edit reddit_collector.py: time.sleep(2)  # Add delays
```

**LMStudio Connection Failed**
```bash
# Solution: Ensure LMStudio is running
# Check: http://127.0.0.1:1234/v1/models
```

### Deployment Options

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

## 🎨 Customization

### Adding New Subreddits

Edit `reddit_collector.py` to monitor additional subreddits:

```python
SUBREDDIT_OPTIONS = [
    "memes", "dankmemes", "wholesomememes",
    "showerthoughts", "unpopularopinion",
    "your_custom_subreddit"  # Add here
]
```

### Modifying Design Prompts

Customize the LLM transformation in `llm_transformer.py`:

```python
def create_system_prompt(self):
    return """
    Your custom system prompt for design generation...
    Focus on: [your specific requirements]
    """
```

### Custom ComfyUI Workflows

1. Design your workflow in ComfyUI
2. Export using SaveAsScript extension
3. Replace `tshirtPOC_768x1024.py` with your exported script
4. Update parameter mappings in `comfyui_simple.py`

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)** - Powerful AI workflow platform
- **[ComfyUI-SaveAsScript](https://github.com/atmaranto/ComfyUI-SaveAsScript)** - Essential workflow export tool
- **[LMStudio](https://lmstudio.ai/)** - Local LLM inference platform
- **[PRAW](https://praw.readthedocs.io/)** - Python Reddit API Wrapper

## 🔗 Related Projects

- [ComfyUI Custom Nodes](https://github.com/comfyanonymous/ComfyUI/wiki/Custom-Nodes)
- [Stable Diffusion Models](https://huggingface.co/models?pipeline_tag=text-to-image)
- [LMStudio Model Library](https://lmstudio.ai/models)

## 📊 Stats & Analytics

Track your design generation metrics:
- **Trends Processed**: View in `poc_output/logs/`
- **Success Rate**: Monitor via session summaries
- **Popular Subreddits**: Analyze trending sources
- **Design Quality**: Review generated outputs

---

**⭐ Star this repo if you found it useful!**

**💬 Questions? Open an issue or start a discussion!**

**🚀 Ready to turn Reddit trends into profitable t-shirt designs? Let's go!**