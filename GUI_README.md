# Synthwave GUI for Reddit-to-ComfyUI Pipeline

A retro synthwave-themed graphical interface for the Reddit-to-ComfyUI t-shirt design pipeline.

![Synthwave Theme](https://img.shields.io/badge/Theme-Synthwave-ff00ff)
![Python](https://img.shields.io/badge/Python-3.7+-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green)

## 🎨 Features

### **Synthwave Aesthetic**
- Dark background with neon accents (hot pink, cyan, electric blue)
- Retro ASCII art and styling
- Courier New font for that authentic terminal feel
- Animated splash screen

### **Tabbed Interface**
1. **SCAN SETUP** - Configure Reddit scanning
2. **RESULTS** - View generated prompts and control ComfyUI
3. **COMFYUI CONFIG** - Manage ComfyUI workflow scripts
4. **WORKFLOW MONITOR** - Real-time logs and session statistics

## 🚀 Quick Start

### Running the GUI

```bash
# Run the demo (recommended for first time)
python demo_gui.py

# Or run the GUI directly
python synthwave_gui.py
```

### Prerequisites

```bash
# Required Python packages
pip install tkinter  # Usually included with Python
pip install pillow   # For image processing
pip install pathlib  # For file operations

# Backend dependencies (for full functionality)
pip install praw python-dotenv lmstudio torch torchvision
```

## 📖 User Guide

### 1. SCAN SETUP Tab

**Subreddit Selection:**
- Choose from predefined popular subreddits (r/memes, r/dankmemes, etc.)
- Or select "Custom" and enter any subreddit name

**Trend Scan Parameters:**
- **Min Score**: Minimum upvotes required (100-5000)
- **Max Posts**: Number of posts to scan (5-50)
- **Time Filter**: Posts from last hour/day/week/month/year/all

**Controls:**
- **▶ START SCAN**: Begin Reddit scanning
- **Auto-transform to prompts**: Automatically process results with AI
- Progress bar shows scan progress
- Results display shows found posts with scores

### 2. RESULTS Tab

**Generated Prompts:**
- Treeview showing all generated prompts with status
- **🔄 REFRESH**: Update prompts list from files
- **🗑 CLEAR**: Remove all prompts

**ComfyUI Execution:**
- **Auto-execute checkbox**: Run ComfyUI after all prompts generated
- **▶ START COMFYUI**: Begin design generation
- **⏹ STOP**: Cancel execution
- Shows current selected script

**Progress Monitor:**
- Real-time progress bars
- Current operation status
- Overall completion tracking

### 3. COMFYUI CONFIG Tab

**Script Selection:**
- List of available ComfyUI workflow scripts
- **SELECT SCRIPT**: Choose workflow for execution
- **🔄 REFRESH**: Rescan for new scripts

**Import New Scripts:**
- **BROWSE**: Select .py workflow file
- **📥 IMPORT SCRIPT**: Copy script to project directory

**Script Preview:**
- Shows first 50 lines of selected script
- Syntax highlighting for Python code

### 4. WORKFLOW MONITOR Tab

**Session Overview:**
- Reddit posts scanned count
- Prompts generated count
- Designs created count
- Session time elapsed
- Current status

**Real-time Log:**
- Timestamped log messages
- Color-coded by level (INFO/SUCCESS/WARNING/ERROR)
- **🗑 CLEAR LOG**: Clear all messages
- **Auto-scroll**: Follow latest messages

**System Status:**
- Reddit API connection status
- LLM Transformer status
- ComfyUI status
- File System status

## 🔧 Configuration

### Environment Setup

Create a `.env` file in the project directory:

```env
# Reddit API credentials
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_app_name

# LLM Studio configuration
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_MODEL=your_model_name

# ComfyUI paths
COMFYUI_PATH=/path/to/ComfyUI
```

### ComfyUI Workflow Scripts

The GUI automatically scans for Python files matching the pattern `*POC*.py`. To add new workflows:

1. Export workflow from ComfyUI as Python script
2. Use the "Import New Script" feature in COMFYUI CONFIG tab
3. Or manually copy .py files to the project directory

## 🎯 Workflow Example

1. **Launch GUI**: `python demo_gui.py`
2. **Configure Scan**: Choose subreddit, set parameters
3. **Start Scan**: Click "▶ START SCAN"
4. **Auto-Transform**: AI processes posts → prompts
5. **Review Results**: Check generated prompts in RESULTS tab
6. **Select Script**: Choose ComfyUI workflow in CONFIG tab
7. **Generate Designs**: Click "▶ START COMFYUI"
8. **Monitor Progress**: Watch real-time logs in MONITOR tab

## 🗂 File Structure

```
├── synthwave_gui.py          # Main GUI application
├── demo_gui.py              # Demo runner with mock data
├── GUI_README.md            # This documentation
├── poc_output/              # Generated outputs
│   ├── prompts/            # AI-generated prompts (.md)
│   ├── generated_designs/  # ComfyUI outputs (.png)
│   ├── metadata/           # Design metadata (.json)
│   └── images/             # Downloaded Reddit images
├── logs/                    # Session logs
└── *.py                     # ComfyUI workflow scripts
```

## 🎨 Synthwave Color Palette

- **Background**: `#0a0a0a` (Deep Black)
- **Secondary**: `#1a0f1a` (Dark Purple)
- **Primary Accent**: `#ff00ff` (Hot Pink)
- **Secondary Accent**: `#00ffff` (Cyan)
- **Tertiary Accent**: `#ff0080` (Electric Pink)
- **Success**: `#00ff41` (Neon Green)
- **Warning**: `#ffff00` (Neon Yellow)
- **Error**: `#ff4444` (Neon Red)

## 🔌 Backend Integration

The GUI integrates with existing backend modules:

- `reddit_collector.py` - Reddit API scanning
- `llm_transformer.py` - AI prompt generation
- `comfyui_simple.py` - ComfyUI workflow execution
- `file_organizer.py` - Output management
- `tshirt_executor.py` - Standalone execution

## 🐛 Troubleshooting

**GUI won't start:**
- Check Python version (3.7+ required)
- Verify tkinter installation: `python -c "import tkinter"`

**Backend errors:**
- Check `.env` file configuration
- Verify API credentials
- Ensure ComfyUI is accessible

**Script import fails:**
- Check file permissions
- Verify .py file format
- Ensure sufficient disk space

**Progress stuck:**
- Check internet connection for Reddit API
- Verify LMStudio is running
- Check ComfyUI server status

## 📝 Development Notes

- Built with Python tkinter for cross-platform compatibility
- Threaded backend operations prevent GUI freezing
- Queue-based communication between threads
- Modular design allows easy feature additions
- Synthwave theme implemented with consistent color scheme

## 🎯 Future Enhancements

- [ ] Dark/Light theme toggle
- [ ] Multiple ComfyUI server support
- [ ] Batch script execution
- [ ] Export session reports
- [ ] Plugin system for custom workflows
- [ ] Advanced prompt editing
- [ ] Design gallery with filtering
- [ ] Real-time ComfyUI preview

---

**Enjoy your synthwave journey from Reddit memes to AI-generated t-shirt designs! 🌈✨**