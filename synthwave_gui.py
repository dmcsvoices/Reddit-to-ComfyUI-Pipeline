#!/usr/bin/env python3
"""
Synthwave-themed GUI for Reddit-to-ComfyUI Pipeline
Features tabbed interface, real-time progress monitoring, and ComfyUI script management
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font
import threading
import queue
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import glob

# Import our existing backend modules with error handling
try:
    from script_analyzer import ComfyUIScriptAnalyzer, ArgumentInfo, PromptMapping
except ImportError:
    print("Warning: Script analyzer not available")
    ComfyUIScriptAnalyzer = None

try:
    from reddit_collector import get_trending_memes, get_user_subreddit_choice
    REDDIT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Reddit collector not available: {e}")
    REDDIT_AVAILABLE = False

try:
    from llm_transformer import TShirtPromptTransformer
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LLM transformer not available: {e}")
    LLM_AVAILABLE = False

# ComfyUI-SaveAsScript approach - no imports needed, direct script execution
COMFYUI_AVAILABLE = True  # Always available since we execute scripts directly

try:
    from file_organizer import POCFileOrganizer
    FILE_ORG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ File organizer not available: {e}")
    FILE_ORG_AVAILABLE = False


class SynthwaveColors:
    """Enhanced Synthwave color palette with glowing effects"""
    # Deep dark backgrounds for contrast
    BACKGROUND = "#0d0208"  # Deep dark red-black
    SECONDARY = "#1a0f1a"   # Dark purple
    PANEL_BG = "#0f051a"    # Slightly lighter dark purple

    # Vibrant neon accents
    PRIMARY_ACCENT = "#ff0080"     # Hot pink/magenta
    SECONDARY_ACCENT = "#00d4ff"   # Electric cyan
    TERTIARY_ACCENT = "#ff6b35"    # Neon orange
    QUATERNARY_ACCENT = "#7209b7"  # Deep purple

    # Bright neon colors
    NEON_PINK = "#ff0080"
    NEON_CYAN = "#00ffff"
    NEON_PURPLE = "#b300ff"
    NEON_ORANGE = "#ff6b35"
    NEON_GREEN = "#39ff14"
    NEON_YELLOW = "#ffff00"

    # Text colors
    TEXT = "#ffffff"
    TEXT_BRIGHT = "#ffffff"
    TEXT_DIM = "#cccccc"
    TEXT_ACCENT = "#ff0080"

    # Status colors with glow
    SUCCESS = "#39ff14"     # Bright neon green
    WARNING = "#ffff00"     # Bright yellow
    ERROR = "#ff073a"       # Bright red

    # Glow effect colors (lighter versions for borders)
    GLOW_PINK = "#ff33a1"
    GLOW_CYAN = "#33ffff"
    GLOW_PURPLE = "#cc33ff"
    GLOW_ORANGE = "#ff8533"
    GLOW_GREEN = "#66ff33"

    # Gradient colors for effects
    GRADIENT_START = "#ff0080"
    GRADIENT_MID = "#7209b7"
    GRADIENT_END = "#00d4ff"

    # Border and highlight colors
    BORDER_BRIGHT = "#ff0080"
    BORDER_DIM = "#660033"
    HIGHLIGHT = "#ff33a1"


class ModelState:
    """Model lifecycle states"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"      # Currently being used
    FAILED = "failed"
    RECONNECTING = "reconnecting"


class SplashScreen:
    """Synthwave-themed splash screen with loading animation"""

    def __init__(self, parent_callback):
        self.parent_callback = parent_callback

        # Create main window first to avoid Toplevel issues
        self.root = tk.Tk()
        self.root.title("Reddit-to-ComfyUI Pipeline")
        self.root.geometry("600x400")
        self.root.configure(bg=SynthwaveColors.BACKGROUND)
        self.root.resizable(False, False)

        # Center the splash screen
        self.center_window()

        # Remove window decorations for clean look
        self.root.overrideredirect(True)

        self.setup_splash_content()
        self.animate_splash()

    def center_window(self):
        """Center the splash screen on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def setup_splash_content(self):
        """Create splash screen content"""
        # Main container
        main_frame = tk.Frame(self.root, bg=SynthwaveColors.BACKGROUND)
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)

        # Title with synthwave styling
        title_font = font.Font(family="Courier New", size=24, weight="bold")
        title_label = tk.Label(
            main_frame,
            text="REDDIT → COMFYUI",
            font=title_font,
            fg=SynthwaveColors.PRIMARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        title_label.pack(pady=(20, 10))

        subtitle_font = font.Font(family="Courier New", size=12)
        subtitle_label = tk.Label(
            main_frame,
            text="AI-POWERED T-SHIRT DESIGN PIPELINE",
            font=subtitle_font,
            fg=SynthwaveColors.SECONDARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        subtitle_label.pack(pady=(0, 30))

        # ASCII art style logo
        logo_font = font.Font(family="Courier New", size=8)
        logo_text = """
    ╔═══════════════════════════════════════╗
    ║  ██████╗ ███████╗██████╗ ██████╗ ██╗  ║
    ║  ██╔══██╗██╔════╝██╔══██╗██╔══██╗██║  ║
    ║  ██████╔╝█████╗  ██║  ██║██║  ██║██║  ║
    ║  ██╔══██╗██╔══╝  ██║  ██║██║  ██║██║  ║
    ║  ██║  ██║███████╗██████╔╝██████╔╝██║  ║
    ║  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚═╝  ║
    ╚═══════════════════════════════════════╝
        """
        logo_label = tk.Label(
            main_frame,
            text=logo_text,
            font=logo_font,
            fg=SynthwaveColors.TERTIARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND,
            justify='center'
        )
        logo_label.pack(pady=(10, 20))

        # Loading indicator
        self.loading_label = tk.Label(
            main_frame,
            text="INITIALIZING...",
            font=subtitle_font,
            fg=SynthwaveColors.WARNING,
            bg=SynthwaveColors.BACKGROUND
        )
        self.loading_label.pack(pady=(20, 10))

        # Progress bar with synthwave styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Synthwave.Horizontal.TProgressbar",
            background=SynthwaveColors.PRIMARY_ACCENT,
            troughcolor=SynthwaveColors.SECONDARY,
            borderwidth=0,
            lightcolor=SynthwaveColors.PRIMARY_ACCENT,
            darkcolor=SynthwaveColors.PRIMARY_ACCENT
        )

        self.progress_bar = ttk.Progressbar(
            main_frame,
            style="Synthwave.Horizontal.TProgressbar",
            length=400,
            mode='indeterminate'
        )
        self.progress_bar.pack(pady=(10, 20))

    def animate_splash(self):
        """Animate the splash screen"""
        print("🎬 Starting splash animation...")
        self.progress_bar.start(10)

        # Simulate loading steps with simpler timing
        loading_steps = [
            "INITIALIZING...",
            "LOADING MODULES...",
            "CONFIGURING AI...",
            "PREPARING INTERFACE...",
            "READY TO LAUNCH!"
        ]

        # Use a more reliable timing approach
        total_steps = len(loading_steps)
        step_duration = 800  # milliseconds per step

        def update_loading(step_index=0):
            if step_index < total_steps:
                print(f"📋 Splash step {step_index + 1}/{total_steps}: {loading_steps[step_index]}")
                self.loading_label.config(text=loading_steps[step_index])
                # Schedule next step
                if step_index < total_steps - 1:
                    self.root.after(step_duration, lambda idx=step_index + 1: update_loading(idx))
                else:
                    # Last step, launch main app after delay
                    self.root.after(step_duration, self.launch_main_app)
            else:
                # Fallback - should not reach here
                self.launch_main_app()

        # Start the animation
        update_loading(0)

    def launch_main_app(self):
        """Close splash and launch main application"""
        print("💥 Destroying splash screen...")
        self.root.destroy()
        print("🎯 Calling main app callback...")
        self.parent_callback()


class SynthwaveGUI:
    """Main synthwave-themed GUI application"""

    def __init__(self):
        self.root = None
        self.notebook = None
        self.queue = queue.Queue()

        # Backend instances
        self.llm_transformer = None
        self.current_model_instance = None  # Track the loaded model instance
        self.current_model_state = ModelState.UNLOADED  # Track model lifecycle state
        self.default_fallback_model = "qwen/qwen3-vl-30b@4bit"  # Default model for fallback
        self.comfyui = None
        self.file_organizer = None

        # GUI state
        self.current_scan_results = []
        self.generated_prompts = []
        self.current_session_prompts = []  # Prompts from current scan session only
        self.selected_comfyui_script = "tshirtPOC_768x1024.py"
        self.available_scripts = []

        # Threading
        self.scan_thread = None
        self.transform_thread = None
        self.comfyui_thread = None

        # Start with splash screen
        self.show_splash()

    def show_splash(self):
        """Display splash screen"""
        self.splash = SplashScreen(self.create_main_window)
        # Start the splash screen main loop
        self.splash.root.mainloop()

    def create_main_window(self):
        """Create the main application window"""
        try:
            print("🏗️ Creating main window...")
            self.root = tk.Tk()
            self.root.title("Reddit-to-ComfyUI Pipeline - Synthwave Edition")
            self.root.geometry("1200x800")
            self.root.configure(bg=SynthwaveColors.BACKGROUND)
            self.root.resizable(True, True)

            print("🎨 Configuring styles...")
            # Configure ttk styling for synthwave theme
            self.configure_styles()

            print("🔧 Initializing backend...")
            # Initialize backend
            self.initialize_backend()

            print("🖼️ Creating main interface...")
            # Create main interface
            self.create_main_interface()

            print("⚙️ Starting queue processing...")
            # Start queue processing
            self.process_queue()

            print("🚀 Starting main loop...")
            # Start the main loop
            self.root.mainloop()
            print("👋 Main loop finished")

        except Exception as e:
            print(f"❌ Error creating main window: {e}")
            import traceback
            traceback.print_exc()

    def configure_styles(self):
        """Configure enhanced synthwave theme with glowing effects"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure notebook (tabs) with neon glow effect
        style.configure(
            "Synthwave.TNotebook",
            background=SynthwaveColors.BACKGROUND,
            borderwidth=2,
            relief='flat'
        )
        style.configure(
            "Synthwave.TNotebook.Tab",
            background=SynthwaveColors.SECONDARY,
            foreground=SynthwaveColors.TEXT_BRIGHT,
            padding=[25, 12],
            font=('Courier New', 11, 'bold'),
            borderwidth=2,
            relief='raised'
        )
        style.map(
            "Synthwave.TNotebook.Tab",
            background=[
                ('selected', SynthwaveColors.PRIMARY_ACCENT),
                ('active', SynthwaveColors.GLOW_PINK)
            ],
            foreground=[
                ('selected', SynthwaveColors.BACKGROUND),
                ('active', SynthwaveColors.TEXT_BRIGHT)
            ],
            relief=[('selected', 'solid')]
        )

        # Configure frames with subtle borders
        style.configure(
            "Synthwave.TFrame",
            background=SynthwaveColors.BACKGROUND,
            borderwidth=2,
            relief='flat'
        )

        # Enhanced button styles with glow simulation
        style.configure(
            "Synthwave.TButton",
            background=SynthwaveColors.PRIMARY_ACCENT,
            foreground=SynthwaveColors.BACKGROUND,
            font=('Courier New', 10, 'bold'),
            padding=[20, 10],
            borderwidth=3,
            relief='raised'
        )
        style.map(
            "Synthwave.TButton",
            background=[
                ('active', SynthwaveColors.GLOW_PINK),
                ('pressed', SynthwaveColors.SECONDARY_ACCENT)
            ],
            foreground=[
                ('active', SynthwaveColors.BACKGROUND),
                ('pressed', SynthwaveColors.BACKGROUND)
            ],
            relief=[
                ('pressed', 'sunken'),
                ('active', 'solid')
            ]
        )

        # Special glow button style for important actions
        style.configure(
            "SynthwaveGlow.TButton",
            background=SynthwaveColors.NEON_CYAN,
            foreground=SynthwaveColors.BACKGROUND,
            font=('Courier New', 11, 'bold'),
            padding=[25, 12],
            borderwidth=4,
            relief='raised'
        )
        style.map(
            "SynthwaveGlow.TButton",
            background=[
                ('active', SynthwaveColors.GLOW_CYAN),
                ('pressed', SynthwaveColors.NEON_PURPLE)
            ],
            relief=[
                ('pressed', 'sunken'),
                ('active', 'solid')
            ]
        )

    def initialize_backend(self):
        """Initialize backend modules"""
        print("🔧 Initializing backend modules...")

        # Initialize file organizer
        if FILE_ORG_AVAILABLE:
            try:
                self.file_organizer = POCFileOrganizer()
                print("✅ File organizer initialized")
            except Exception as e:
                print(f"❌ File organizer failed: {e}")
                self.file_organizer = None
        else:
            print("❌ File organizer not available")
            self.file_organizer = None

        # Initialize LLM transformer - will be created when model is loaded
        if LLM_AVAILABLE:
            print("✅ LLM functionality available - transformer will be created when model is loaded")
            self.llm_transformer = None  # Will be created with model instance in load_selected_model()
        else:
            print("❌ LLM transformer not available (demo mode)")
            self.llm_transformer = None

        # ComfyUI-SaveAsScript approach - no initialization needed
        self.comfyui = None  # Not needed - we execute scripts directly
        print("✅ ComfyUI script execution ready (SaveAsScript approach)")

        # Scan for available ComfyUI scripts
        self.scan_comfyui_scripts()

        # Log summary
        available_count = sum([
            self.file_organizer is not None,
            self.llm_transformer is not None,
            True  # ComfyUI scripts always available
        ])
        print(f"🎯 Backend initialization complete: {available_count}/3 modules available")

        if available_count == 0:
            print("⚠️ Running in demo mode - no backend functionality available")

    def scan_comfyui_scripts(self):
        """Scan for available ComfyUI scripts in the current directory"""
        # Look for all Python files, then filter out GUI files
        all_py_files = glob.glob("*.py")

        # Files to exclude (GUI files and backend modules)
        exclude_files = {
            "synthwave_gui.py",
            "synthwave_gui_fixed.py",
            "synthwave_gui_simple.py",
            "demo_gui.py",
            "reddit_collector.py",
            "llm_transformer.py",
            "comfyui_simple.py",
            "file_organizer.py",
            "tshirt_executor.py"
        }

        # Filter to likely ComfyUI workflow scripts
        workflow_scripts = []
        for script in all_py_files:
            if script not in exclude_files:
                # Include files that likely contain ComfyUI workflows
                # Check for common ComfyUI patterns in filename or prioritize POC files
                if any(keyword in script.lower() for keyword in ['workflow', 'comfy', 'poc', 'tshirt', 'flux']):
                    workflow_scripts.append(script)
                else:
                    # For other .py files, do a quick content check
                    try:
                        with open(script, 'r', encoding='utf-8') as f:
                            content = f.read(200)  # Read first 200 chars
                            if any(keyword in content.lower() for keyword in ['comfyui', 'workflow', 'queue_prompt']):
                                workflow_scripts.append(script)
                    except:
                        # If we can't read the file, skip it
                        pass

        self.available_scripts = workflow_scripts

        # Ensure default script is included
        if "tshirtPOC_768x1024.py" not in self.available_scripts:
            self.available_scripts.insert(0, "tshirtPOC_768x1024.py")

        print(f"📜 Found {len(self.available_scripts)} ComfyUI scripts: {self.available_scripts}")

    def validate_comfyui_script(self, script_path):
        """Validate that script is compatible with module import"""
        try:
            if not Path(script_path).exists():
                return False, "Script file does not exist"

            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for required components
            has_main_function = 'def main(' in content
            has_saveimage = 'SaveImage' in content or 'saveimage' in content.lower()
            has_return_dict = 'return dict(' in content

            # Check for ComfyUI patterns
            has_comfyui_patterns = any(pattern in content.lower() for pattern in [
                'comfyui', 'workflow', 'queue_prompt', 'get_value_at_index'
            ])

            # Check for common SaveAsScript bugs: missing variable initializations
            has_manager_usage = 'if has_manager:' in content
            has_manager_init = 'has_manager = False' in content or 'has_manager = True' in content

            custom_nodes_usage = '_custom_nodes_imported' in content
            custom_nodes_init = '_custom_nodes_imported = False' in content or '_custom_nodes_imported = True' in content

            custom_path_usage = '_custom_path_added' in content
            custom_path_init = '_custom_path_added = False' in content or '_custom_path_added = True' in content

            issues = []
            warnings = []

            if not has_main_function:
                issues.append("Missing 'def main(' function")
            if not has_saveimage:
                issues.append("No SaveImage node detected")
            if not has_return_dict:
                issues.append("Missing 'return dict(' statement")
            if not has_comfyui_patterns:
                issues.append("No ComfyUI patterns detected")

            # Check for SaveAsScript bugs (warnings, not errors - we can fix these)
            auto_fixable = []
            if has_manager_usage and not has_manager_init:
                auto_fixable.append("has_manager")
            if custom_nodes_usage and not custom_nodes_init:
                auto_fixable.append("_custom_nodes_imported")
            if custom_path_usage and not custom_path_init:
                auto_fixable.append("_custom_path_added")

            if auto_fixable:
                warnings.append(f"Missing variable initializations: {', '.join(auto_fixable)} (will be auto-fixed)")

            if issues:
                return False, "; ".join(issues)
            else:
                message = "Script appears compatible"
                if warnings:
                    message += f" (warnings: {'; '.join(warnings)})"
                return True, message

        except Exception as e:
            return False, f"Error reading script: {str(e)}"

    def clear_module_cache(self, module_name):
        """Clear cached module to force reload"""
        import sys
        if module_name in sys.modules:
            del sys.modules[module_name]
            print(f"🔄 Cleared cached module: {module_name}")

    def create_main_interface(self):
        """Create the main tabbed interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=SynthwaveColors.BACKGROUND)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Header with title
        header_frame = tk.Frame(main_container, bg=SynthwaveColors.BACKGROUND, height=60)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)

        title_font = font.Font(family="Courier New", size=18, weight="bold")
        title_label = tk.Label(
            header_frame,
            text="REDDIT → COMFYUI PIPELINE",
            font=title_font,
            fg=SynthwaveColors.PRIMARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        title_label.pack(pady=15)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container, style="Synthwave.TNotebook")
        self.notebook.pack(fill='both', expand=True)

        # Create tabs (reordered: Scan, Config, Gallery)
        self.create_scan_setup_tab()
        self.create_comfyui_config_tab()
        self.create_gallery_tab()
        # Results tab removed - functionality moved to Scan Setup tab
        # Monitor tab removed - was not providing critical functionality

    def create_scan_setup_tab(self):
        """Create the scan setup tab"""
        scan_frame = ttk.Frame(self.notebook, style="Synthwave.TFrame")
        self.notebook.add(scan_frame, text="SCAN SETUP")

        # Main content (no scrolling needed with side-by-side layout)
        main_content = tk.Frame(scan_frame, bg=SynthwaveColors.BACKGROUND)
        main_content.pack(fill='both', expand=True, padx=20, pady=20)

        # Top section: Subreddit Selection and Parameters side by side
        top_section = tk.Frame(main_content, bg=SynthwaveColors.BACKGROUND)
        top_section.pack(fill='x', pady=(0, 20))

        # Left column: Subreddit Selection
        left_column = tk.Frame(top_section, bg=SynthwaveColors.BACKGROUND)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Right column: Scan Parameters
        right_column = tk.Frame(top_section, bg=SynthwaveColors.BACKGROUND)
        right_column.pack(side='right', fill='both', expand=True, padx=(10, 0))

        # Create sections in their respective columns
        self.create_subreddit_selection(left_column)
        self.create_trend_parameters(right_column)

        # Scan Controls (full width)
        self.create_scan_controls(main_content)

        # Results Display (full width)
        self.create_scan_results_display(main_content)

    def create_subreddit_selection(self, parent):
        """Create subreddit selection section"""
        # Section header
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ SUBREDDIT SELECTION ─┐",
            font=header_font,
            fg=SynthwaveColors.PRIMARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        # Subreddit selection frame with neon glow border
        subreddit_frame = tk.Frame(parent, bg=SynthwaveColors.PANEL_BG, relief='solid', bd=3, highlightbackground=SynthwaveColors.NEON_PINK, highlightthickness=2)
        subreddit_frame.pack(fill='both', expand=True, pady=(0, 0))

        # Variables for radio buttons
        self.subreddit_var = tk.StringVar(value="memes")
        self.custom_subreddit_var = tk.StringVar()

        # Content frame
        content_frame = tk.Frame(subreddit_frame, bg=SynthwaveColors.SECONDARY)
        content_frame.pack(fill='x', padx=15, pady=15)

        # Predefined subreddits in a vertical list (more compact for side-by-side)
        predefined_subreddits = ["memes", "dankmemes", "wholesomememes", "ProgrammerHumor", "gaming", "funny"]

        button_font = font.Font(family="Courier New", size=10)
        for subreddit in predefined_subreddits:
            radio_btn = tk.Radiobutton(
                content_frame,
                text=f"r/{subreddit}",
                variable=self.subreddit_var,
                value=subreddit,
                font=button_font,
                fg=SynthwaveColors.TEXT,
                bg=SynthwaveColors.SECONDARY,
                activebackground=SynthwaveColors.PRIMARY_ACCENT,
                activeforeground=SynthwaveColors.BACKGROUND,
                selectcolor=SynthwaveColors.PRIMARY_ACCENT,
                command=self.on_subreddit_change
            )
            radio_btn.pack(anchor='w', pady=2)

        # Custom subreddit section
        custom_frame = tk.Frame(content_frame, bg=SynthwaveColors.SECONDARY)
        custom_frame.pack(fill='x', pady=(10, 0))

        custom_radio = tk.Radiobutton(
            custom_frame,
            text="Custom:",
            variable=self.subreddit_var,
            value="custom",
            font=button_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY,
            activebackground=SynthwaveColors.SECONDARY_ACCENT,
            activeforeground=SynthwaveColors.BACKGROUND,
            selectcolor=SynthwaveColors.SECONDARY_ACCENT,
            command=self.on_subreddit_change
        )
        custom_radio.pack(side='left', anchor='w')

        self.custom_entry = tk.Entry(
            custom_frame,
            textvariable=self.custom_subreddit_var,
            font=button_font,
            bg=SynthwaveColors.BACKGROUND,
            fg=SynthwaveColors.TEXT,
            insertbackground=SynthwaveColors.PRIMARY_ACCENT,
            width=20,
            state='disabled'
        )
        self.custom_entry.pack(side='left', padx=(10, 0))

        # Help text
        help_label = tk.Label(
            content_frame,
            text="(Enter subreddit name without 'r/' prefix)",
            font=('Courier New', 8),
            fg=SynthwaveColors.SECONDARY_ACCENT,
            bg=SynthwaveColors.SECONDARY
        )
        help_label.pack(anchor='w', pady=(5, 0))

    def create_trend_parameters(self, parent):
        """Create trend scan parameters section"""
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ TREND SCAN PARAMETERS ─┐",
            font=header_font,
            fg=SynthwaveColors.SECONDARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        params_frame = tk.Frame(parent, bg=SynthwaveColors.PANEL_BG, relief='solid', bd=3, highlightbackground=SynthwaveColors.NEON_CYAN, highlightthickness=2)
        params_frame.pack(fill='both', expand=True, pady=(0, 0))

        content_frame = tk.Frame(params_frame, bg=SynthwaveColors.SECONDARY)
        content_frame.pack(fill='x', padx=15, pady=15)

        label_font = font.Font(family="Courier New", size=10)

        # Min Score parameter
        score_frame = tk.Frame(content_frame, bg=SynthwaveColors.SECONDARY)
        score_frame.pack(fill='x', pady=5)

        tk.Label(
            score_frame,
            text="Min Score:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY,
            width=12,
            anchor='w'
        ).pack(side='left')

        self.min_score_var = tk.IntVar(value=500)
        score_scale = tk.Scale(
            score_frame,
            from_=100,
            to=5000,
            orient='horizontal',
            variable=self.min_score_var,
            font=('Courier New', 9),
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY,
            activebackground=SynthwaveColors.TERTIARY_ACCENT,
            highlightbackground=SynthwaveColors.SECONDARY,
            troughcolor=SynthwaveColors.BACKGROUND,
            length=150
        )
        score_scale.pack(side='left', padx=(5, 0))

        # Max posts parameter (simplified for side-by-side layout)
        posts_frame = tk.Frame(content_frame, bg=SynthwaveColors.SECONDARY)
        posts_frame.pack(fill='x', pady=5)

        tk.Label(
            posts_frame,
            text="Max Posts:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY,
            width=12,
            anchor='w'
        ).pack(side='left')

        self.max_posts_var = tk.IntVar(value=5)
        posts_scale = tk.Scale(
            posts_frame,
            from_=3,
            to=50,
            orient='horizontal',
            variable=self.max_posts_var,
            font=('Courier New', 9),
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY,
            activebackground=SynthwaveColors.SECONDARY_ACCENT,
            highlightbackground=SynthwaveColors.SECONDARY,
            troughcolor=SynthwaveColors.BACKGROUND,
            length=150
        )
        posts_scale.pack(side='left', padx=(5, 0))

        # Time filter parameter
        time_frame = tk.Frame(content_frame, bg=SynthwaveColors.SECONDARY)
        time_frame.pack(fill='x', pady=(10, 5))

        tk.Label(
            time_frame,
            text="Time Filter:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY,
            width=12,
            anchor='w'
        ).pack(anchor='w')

        # Time filter options
        time_options_frame = tk.Frame(time_frame, bg=SynthwaveColors.SECONDARY)
        time_options_frame.pack(fill='x', pady=(5, 0))

        self.time_filter_var = tk.StringVar(value="day")
        time_options = [("Hour", "hour"), ("Day", "day"), ("Week", "week"), ("Month", "month")]

        for i, (label, value) in enumerate(time_options):
            radio_btn = tk.Radiobutton(
                time_options_frame,
                text=label,
                variable=self.time_filter_var,
                value=value,
                font=('Courier New', 9),
                fg=SynthwaveColors.TEXT,
                bg=SynthwaveColors.SECONDARY,
                selectcolor=SynthwaveColors.TERTIARY_ACCENT,
                indicatoron=0,
                width=6
            )
            radio_btn.pack(side='left', padx=1)

    def create_scan_controls(self, parent):
        """Create scan control buttons and ComfyUI execution controls"""
        # Main controls container
        controls_frame = tk.Frame(parent, bg=SynthwaveColors.BACKGROUND)
        controls_frame.pack(fill='x', pady=10)

        button_font = font.Font(family="Courier New", size=12, weight="bold")
        label_font = font.Font(family="Courier New", size=10)

        # Left section: Buttons
        buttons_frame = tk.Frame(controls_frame, bg=SynthwaveColors.BACKGROUND)
        buttons_frame.pack(side='left', fill='y')

        # Start scan button with glow effect
        self.start_scan_btn = tk.Button(
            buttons_frame,
            text="▶ START SCAN",
            font=button_font,
            bg=SynthwaveColors.SUCCESS,
            fg=SynthwaveColors.BACKGROUND,
            activebackground=SynthwaveColors.GLOW_GREEN,
            relief='raised',
            bd=4,
            padx=25,
            pady=12,
            highlightbackground=SynthwaveColors.NEON_GREEN,
            highlightthickness=2,
            command=self.start_scan
        )
        self.start_scan_btn.pack(side='left', padx=(0, 15))

        # ComfyUI execution button with cyan glow
        self.start_execution_btn = tk.Button(
            buttons_frame,
            text="▶ START COMFYUI",
            font=button_font,
            bg=SynthwaveColors.SECONDARY_ACCENT,
            fg=SynthwaveColors.BACKGROUND,
            activebackground=SynthwaveColors.GLOW_CYAN,
            relief='raised',
            bd=4,
            padx=25,
            pady=12,
            highlightbackground=SynthwaveColors.NEON_CYAN,
            highlightthickness=2,
            state='disabled',
            command=self.start_comfyui_execution
        )
        self.start_execution_btn.pack(side='left', padx=(0, 10))

        # Stop execution button
        self.stop_execution_btn = tk.Button(
            buttons_frame,
            text="⏹ STOP",
            font=button_font,
            bg=SynthwaveColors.ERROR,
            fg=SynthwaveColors.TEXT,
            activebackground=SynthwaveColors.TERTIARY_ACCENT,
            relief='flat',
            padx=15,
            pady=10,
            state='disabled',
            command=self.stop_comfyui_execution
        )
        self.stop_execution_btn.pack(side='left', padx=5)

        # Middle section: Checkboxes (vertical layout)
        checkboxes_frame = tk.Frame(controls_frame, bg=SynthwaveColors.BACKGROUND)
        checkboxes_frame.pack(side='left', fill='y', padx=(20, 0))

        # Auto-transform checkbox
        self.auto_transform_var = tk.BooleanVar(value=True)
        auto_transform_check = tk.Checkbutton(
            checkboxes_frame,
            text="Auto-transform to prompts",
            variable=self.auto_transform_var,
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.BACKGROUND,
            activebackground=SynthwaveColors.BACKGROUND,
            selectcolor=SynthwaveColors.PRIMARY_ACCENT
        )
        auto_transform_check.pack(anchor='w')

        # Auto-execute checkbox
        self.auto_execute_var = tk.BooleanVar(value=False)
        auto_execute_check = tk.Checkbutton(
            checkboxes_frame,
            text="Auto-execute ComfyUI after prompts",
            variable=self.auto_execute_var,
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.BACKGROUND,
            activebackground=SynthwaveColors.BACKGROUND,
            selectcolor=SynthwaveColors.PRIMARY_ACCENT
        )
        auto_execute_check.pack(anchor='w')

        # Right section: Progress and script info
        right_frame = tk.Frame(controls_frame, bg=SynthwaveColors.BACKGROUND)
        right_frame.pack(side='right', fill='y')

        # Current script label
        self.current_script_label = tk.Label(
            right_frame,
            text=f"Script: {self.selected_comfyui_script}",
            font=label_font,
            fg=SynthwaveColors.WARNING,
            bg=SynthwaveColors.BACKGROUND
        )
        self.current_script_label.pack(anchor='e', pady=(0, 5))

        # Progress bar
        self.scan_progress = ttk.Progressbar(
            right_frame,
            style="Synthwave.Horizontal.TProgressbar",
            length=300,
            mode='determinate'
        )
        self.scan_progress.pack(anchor='e')

    def create_scan_results_display(self, parent):
        """Create scan results display area"""
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ SCAN RESULTS ─┐",
            font=header_font,
            fg=SynthwaveColors.TERTIARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(20, 10))

        # Results frame
        results_frame = tk.Frame(parent, bg=SynthwaveColors.PANEL_BG, relief='solid', bd=3, highlightbackground=SynthwaveColors.NEON_ORANGE, highlightthickness=2)
        results_frame.pack(fill='both', expand=True, padx=10)

        # Results textbox with scrollbar (changed from listbox to handle all output)
        textbox_frame = tk.Frame(results_frame, bg=SynthwaveColors.SECONDARY)
        textbox_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.scan_results_textbox = tk.Text(
            textbox_frame,
            font=font.Font(family="Courier New", size=9),
            bg=SynthwaveColors.BACKGROUND,
            fg=SynthwaveColors.TEXT,
            selectbackground=SynthwaveColors.PRIMARY_ACCENT,
            selectforeground=SynthwaveColors.BACKGROUND,
            height=12,
            wrap=tk.WORD,
            state=tk.DISABLED  # Read-only by default
        )

        scrollbar_results = ttk.Scrollbar(textbox_frame, orient="vertical", command=self.scan_results_textbox.yview)
        self.scan_results_textbox.configure(yscrollcommand=scrollbar_results.set)

        self.scan_results_textbox.pack(side="left", fill="both", expand=True)
        scrollbar_results.pack(side="right", fill="y")

    def write_to_scan_results(self, text, color=None):
        """Helper method to write text to scan results textbox"""
        try:
            self.scan_results_textbox.config(state=tk.NORMAL)

            # Add timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_text = f"[{timestamp}] {text}\n"

            self.scan_results_textbox.insert(tk.END, full_text)

            # Auto-scroll to bottom
            self.scan_results_textbox.see(tk.END)

            # Make read-only again
            self.scan_results_textbox.config(state=tk.DISABLED)

            # Update the display
            self.scan_results_textbox.update_idletasks()
        except Exception as e:
            print(f"Error writing to scan results: {e}")

    def clear_scan_results(self):
        """Helper method to clear scan results textbox"""
        try:
            self.scan_results_textbox.config(state=tk.NORMAL)
            self.scan_results_textbox.delete(1.0, tk.END)
            self.scan_results_textbox.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Error clearing scan results: {e}")

    def on_subreddit_change(self):
        """Handle subreddit selection change"""
        if self.subreddit_var.get() == "custom":
            self.custom_entry.config(state='normal')
            self.custom_entry.focus()
        else:
            self.custom_entry.config(state='disabled')

    def start_scan(self):
        """Start the Reddit scan process"""
        # Get selected subreddit
        if self.subreddit_var.get() == "custom":
            subreddit = self.custom_subreddit_var.get().strip()
            if not subreddit:
                messagebox.showerror("Error", "Please enter a custom subreddit name")
                return
        else:
            subreddit = self.subreddit_var.get()

        # Get scan parameters
        min_score = self.min_score_var.get()
        max_posts = self.max_posts_var.get()
        time_filter = self.time_filter_var.get()

        # Disable scan button and show progress
        self.start_scan_btn.config(state='disabled', text="SCANNING...")
        self.scan_progress.config(mode='indeterminate')
        self.scan_progress.start()

        # Clear previous results
        self.clear_scan_results()
        self.write_to_scan_results(f"🔍 Starting scan of r/{subreddit} ({time_filter})...")
        self.current_scan_results = []
        self.current_session_prompts = []  # Clear prompts from previous scan

        print(f"🎯 Scanning r/{subreddit} for {max_posts} posts (min score: {min_score}, time: {time_filter})")

        # Start scan in background thread
        self.scan_thread = threading.Thread(
            target=self.run_scan,
            args=(subreddit, min_score, max_posts, time_filter),
            daemon=True
        )
        self.scan_thread.start()

    def on_subreddit_change(self):
        """Handle subreddit selection change"""
        if self.subreddit_var.get() == "custom":
            self.custom_entry.config(state='normal')
            self.custom_entry.focus()
        else:
            self.custom_entry.config(state='disabled')

    def run_scan(self, subreddit, min_score, max_posts, time_filter):
        """Run the scan in background thread"""
        try:
            # Check if Reddit functionality is available
            if REDDIT_AVAILABLE:
                # Use the reddit collector function directly
                results = get_trending_memes(
                    limit=max_posts,
                    subreddit_name=subreddit,
                    download_images=True
                )
                # Note: The current reddit_collector doesn't support min_score and time_filter yet
                # This would need to be implemented in the backend
                # For now, we filter results by min_score locally
                if results:
                    results = [post for post in results if post.get('score', 0) >= min_score]
            else:
                # Generate mock data for demo with time filter indication
                import random
                import time
                results = []
                for i in range(max_posts):
                    # Adjust scores based on time filter for demo
                    if time_filter == "hour":
                        base_range = (500, 2000)
                    elif time_filter == "day":
                        base_range = (1000, 5000)
                    elif time_filter == "week":
                        base_range = (2000, 10000)
                    else:  # month
                        base_range = (5000, 20000)

                    # Ensure score is at least min_score
                    score_min = max(min_score, base_range[0])
                    score_max = max(score_min + 100, base_range[1])  # Ensure range is valid

                    results.append({
                        'id': f'demo_{time_filter}_{i}',
                        'title': f'Demo Post {i+1}: {subreddit} trending ({time_filter}, min score: {min_score})',
                        'score': random.randint(score_min, score_max),
                        'url': 'https://demo.url',
                        'created': '2024-01-01T00:00:00',
                        'text_content': f'Demo text {i+1} from {time_filter}',
                        'images': []
                    })
                    time.sleep(0.5)  # Simulate processing

            self.queue.put({
                'type': 'scan_complete',
                'results': results,
                'subreddit': subreddit
            })

        except Exception as e:
            self.queue.put({
                'type': 'error',
                'error': f"Scan failed: {str(e)}"
            })

    # =========================================================================
    # RESULTS TAB METHODS - NO LONGER USED (functionality moved to Scan Setup tab)
    # =========================================================================

    def create_results_tab_DEPRECATED(self):
        """Create the results display tab"""
        results_frame = ttk.Frame(self.notebook, style="Synthwave.TFrame")
        self.notebook.add(results_frame, text="RESULTS")

        # Main container
        main_container = tk.Frame(results_frame, bg=SynthwaveColors.BACKGROUND)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Generated Prompts Section
        self.create_prompts_section(main_container)

        # ComfyUI Execution Controls
        self.create_execution_controls(main_container)

        # Progress and Status Section
        self.create_progress_section(main_container)

    def create_prompts_section(self, parent):
        """Create the generated prompts section"""
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ GENERATED PROMPTS ─┐",
            font=header_font,
            fg=SynthwaveColors.PRIMARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        # Prompts container
        prompts_container = tk.Frame(parent, bg=SynthwaveColors.SECONDARY, relief='ridge', bd=2)
        prompts_container.pack(fill='both', expand=True, pady=(0, 20), padx=10)

        # Toolbar for prompts
        toolbar = tk.Frame(prompts_container, bg=SynthwaveColors.SECONDARY)
        toolbar.pack(fill='x', padx=10, pady=(10, 0))

        button_font = font.Font(family="Courier New", size=9, weight="bold")

        # Refresh prompts button
        refresh_btn = tk.Button(
            toolbar,
            text="🔄 REFRESH",
            font=button_font,
            bg=SynthwaveColors.SECONDARY_ACCENT,
            fg=SynthwaveColors.BACKGROUND,
            relief='flat',
            padx=10,
            pady=5,
            command=self.refresh_prompts
        )
        refresh_btn.pack(side='left', padx=(0, 5))

        # Clear prompts button
        clear_btn = tk.Button(
            toolbar,
            text="🗑 CLEAR",
            font=button_font,
            bg=SynthwaveColors.ERROR,
            fg=SynthwaveColors.TEXT,
            relief='flat',
            padx=10,
            pady=5,
            command=self.clear_prompts
        )
        clear_btn.pack(side='left', padx=5)

        # Prompts count label
        self.prompts_count_label = tk.Label(
            toolbar,
            text="Prompts: 0",
            font=button_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        self.prompts_count_label.pack(side='right')

        # Prompts treeview
        tree_frame = tk.Frame(prompts_container, bg=SynthwaveColors.SECONDARY)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Configure treeview style
        style = ttk.Style()
        style.configure(
            "Synthwave.Treeview",
            background=SynthwaveColors.BACKGROUND,
            foreground=SynthwaveColors.TEXT,
            fieldbackground=SynthwaveColors.BACKGROUND,
            font=('Courier New', 9)
        )
        style.configure(
            "Synthwave.Treeview.Heading",
            background=SynthwaveColors.PRIMARY_ACCENT,
            foreground=SynthwaveColors.BACKGROUND,
            font=('Courier New', 10, 'bold')
        )

        columns = ('status', 'source', 'title', 'score', 'generated')
        self.prompts_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            style="Synthwave.Treeview",
            height=12
        )

        # Configure columns
        self.prompts_tree.heading('status', text='Status')
        self.prompts_tree.heading('source', text='Source')
        self.prompts_tree.heading('title', text='Title')
        self.prompts_tree.heading('score', text='Score')
        self.prompts_tree.heading('generated', text='Generated')

        self.prompts_tree.column('status', width=80, anchor='center')
        self.prompts_tree.column('source', width=120, anchor='center')
        self.prompts_tree.column('title', width=300, anchor='w')
        self.prompts_tree.column('score', width=80, anchor='center')
        self.prompts_tree.column('generated', width=120, anchor='center')

        # Scrollbars for treeview
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.prompts_tree.yview)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.prompts_tree.xview)
        self.prompts_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        self.prompts_tree.pack(side="left", fill="both", expand=True)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")

    def create_execution_controls(self, parent):
        """Create ComfyUI execution controls"""
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ COMFYUI EXECUTION ─┐",
            font=header_font,
            fg=SynthwaveColors.SECONDARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        controls_container = tk.Frame(parent, bg=SynthwaveColors.SECONDARY, relief='ridge', bd=2)
        controls_container.pack(fill='x', pady=(0, 20), padx=10)

        controls_frame = tk.Frame(controls_container, bg=SynthwaveColors.SECONDARY)
        controls_frame.pack(fill='x', padx=15, pady=15)

        button_font = font.Font(family="Courier New", size=11, weight="bold")
        label_font = font.Font(family="Courier New", size=10)

        # Auto-execute checkbox
        self.auto_execute_var = tk.BooleanVar(value=False)
        auto_execute_check = tk.Checkbutton(
            controls_frame,
            text="Auto-execute ComfyUI after all prompts generated",
            variable=self.auto_execute_var,
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY,
            activebackground=SynthwaveColors.SECONDARY,
            selectcolor=SynthwaveColors.PRIMARY_ACCENT
        )
        auto_execute_check.pack(anchor='w', pady=(0, 10))

        # Execution controls row
        exec_controls_frame = tk.Frame(controls_frame, bg=SynthwaveColors.SECONDARY)
        exec_controls_frame.pack(fill='x', pady=5)

        # Start execution button
        self.start_execution_btn = tk.Button(
            exec_controls_frame,
            text="▶ START COMFYUI",
            font=button_font,
            bg=SynthwaveColors.SUCCESS,
            fg=SynthwaveColors.BACKGROUND,
            activebackground=SynthwaveColors.PRIMARY_ACCENT,
            relief='flat',
            padx=20,
            pady=8,
            state='disabled',
            command=self.start_comfyui_execution
        )
        self.start_execution_btn.pack(side='left', padx=(0, 10))

        # Stop execution button
        self.stop_execution_btn = tk.Button(
            exec_controls_frame,
            text="⏹ STOP",
            font=button_font,
            bg=SynthwaveColors.ERROR,
            fg=SynthwaveColors.TEXT,
            activebackground=SynthwaveColors.TERTIARY_ACCENT,
            relief='flat',
            padx=15,
            pady=8,
            state='disabled',
            command=self.stop_comfyui_execution
        )
        self.stop_execution_btn.pack(side='left', padx=5)

        # Current script label
        self.current_script_label = tk.Label(
            exec_controls_frame,
            text=f"Script: {self.selected_comfyui_script}",
            font=label_font,
            fg=SynthwaveColors.WARNING,
            bg=SynthwaveColors.SECONDARY
        )
        self.current_script_label.pack(side='right')

    def create_progress_section(self, parent):
        """Create progress monitoring section"""
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ PROGRESS MONITOR ─┐",
            font=header_font,
            fg=SynthwaveColors.TERTIARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        progress_container = tk.Frame(parent, bg=SynthwaveColors.SECONDARY, relief='ridge', bd=2)
        progress_container.pack(fill='x', padx=10)

        progress_frame = tk.Frame(progress_container, bg=SynthwaveColors.SECONDARY)
        progress_frame.pack(fill='x', padx=15, pady=15)

        label_font = font.Font(family="Courier New", size=10)

        # Current operation label
        self.current_operation_label = tk.Label(
            progress_frame,
            text="Status: Ready",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        self.current_operation_label.pack(anchor='w', pady=(0, 5))

        # Progress bar for current operation
        self.operation_progress = ttk.Progressbar(
            progress_frame,
            style="Synthwave.Horizontal.TProgressbar",
            length=500,
            mode='determinate'
        )
        self.operation_progress.pack(fill='x', pady=(0, 10))

        # Overall progress
        overall_frame = tk.Frame(progress_frame, bg=SynthwaveColors.SECONDARY)
        overall_frame.pack(fill='x')

        self.overall_progress_label = tk.Label(
            overall_frame,
            text="Overall: 0/0",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        self.overall_progress_label.pack(side='left')

        self.overall_progress = ttk.Progressbar(
            overall_frame,
            style="Synthwave.Horizontal.TProgressbar",
            length=300,
            mode='determinate'
        )
        self.overall_progress.pack(side='right', fill='x', expand=True, padx=(10, 0))

    def refresh_prompts(self):
        """Refresh the prompts list from current scan session"""
        try:
            # Use prompts from current scan session only (Results tab removed - using text logging)
            self.generated_prompts = self.current_session_prompts.copy()

            print(f"📋 Refreshing prompts display: {len(self.generated_prompts)} prompts")
            self.write_to_scan_results(f"📋 Refreshed prompts: {len(self.generated_prompts)} prompts available")

            # Log each prompt for visibility
            for i, prompt_data in enumerate(self.current_session_prompts, 1):
                reddit_id = prompt_data.get('reddit_id', 'unknown')
                title = prompt_data.get('title', 'Unknown Title')
                score = prompt_data.get('score', '0')

                # Check if design exists
                design_exists = self.check_design_exists(reddit_id)
                status = "✓ Complete" if design_exists else "⏳ Pending"

                # Update status in the prompt data
                prompt_data['status'] = status

                # Log prompt details to scan results
                title_preview = title[:40] + "..." if len(title) > 40 else title
                self.write_to_scan_results(f"   {i}. {status} r/{reddit_id[:8]} [{score}] {title_preview}")

            # Update count and enable execution if prompts exist
            count = len(self.current_session_prompts)

            if count > 0:
                # Enable ComfyUI execution button when we have prompts
                self.start_execution_btn.config(state='normal')
                self.write_to_scan_results(f"✅ ComfyUI execution enabled: {count} prompts ready")
                print(f"✅ ComfyUI execution enabled: {count} prompts ready")
            else:
                self.start_execution_btn.config(state='disabled')
                self.write_to_scan_results(f"⏸️ ComfyUI execution disabled: no prompts available")

        except Exception as e:
            error_msg = f"Failed to refresh prompts: {str(e)}"
            print(f"❌ {error_msg}")
            self.write_to_scan_results(f"❌ {error_msg}")
            messagebox.showerror("Error", error_msg)

    def check_design_exists(self, reddit_id):
        """Check if a design exists for the given reddit ID"""
        designs_dir = Path("poc_output/generated_designs")
        if designs_dir.exists():
            pattern = f"*{reddit_id}*.png"
            return len(list(designs_dir.glob(pattern))) > 0
        return False

    def clear_prompts(self):
        """Clear all prompts (Results tab removed - using text logging)"""
        if messagebox.askyesno("Confirm", "Clear all generated prompts? This cannot be undone."):
            self.generated_prompts = []
            self.current_session_prompts = []  # Also clear current session prompts
            self.start_execution_btn.config(state='disabled')
            self.write_to_scan_results("🗑️ All prompts cleared")

    def start_comfyui_execution(self):
        """Start ComfyUI execution for all prompts"""
        if not self.generated_prompts:
            messagebox.showwarning("Warning", "No prompts available for execution")
            return

        # Update UI state
        self.start_execution_btn.config(state='disabled', text="EXECUTING...")
        self.stop_execution_btn.config(state='normal')
        # Use scan_progress bar for execution progress (operation_progress removed with Results tab)
        self.scan_progress.config(mode='determinate', value=0, maximum=len(self.generated_prompts))

        # Start execution in background thread
        self.comfyui_thread = threading.Thread(
            target=self.run_comfyui_execution,
            daemon=True
        )
        self.comfyui_thread.start()

    def stop_comfyui_execution(self):
        """Stop ComfyUI execution"""
        # Implementation for stopping execution
        self.start_execution_btn.config(state='normal', text="▶ START COMFYUI")
        self.stop_execution_btn.config(state='disabled')
        if hasattr(self, 'current_operation_label'):
            self.current_operation_label.config(text="Status: Stopped")

    def run_comfyui_execution(self):
        """Run ComfyUI execution in background thread"""
        try:
            total_prompts = len(self.generated_prompts)
            script_name = self.selected_comfyui_script.replace('.py', '')

            for i, prompt_data in enumerate(self.generated_prompts):
                # Update progress
                self.queue.put({
                    'type': 'comfyui_progress',
                    'current': i + 1,
                    'total': total_prompts,
                    'prompt_title': prompt_data['title']
                })

                try:
                    # Execute ComfyUI script with correct arguments
                    success = self.execute_comfyui_script(prompt_data, script_name)

                    if not success:
                        self.queue.put({
                            'type': 'error',
                            'error': f"Failed to execute prompt {i+1}: {prompt_data['title'][:50]}..."
                        })
                except Exception as e:
                    self.queue.put({
                        'type': 'error',
                        'error': f"Error executing prompt {i+1}: {str(e)}"
                    })

            self.queue.put({
                'type': 'comfyui_complete',
                'total_processed': total_prompts
            })

        except Exception as e:
            self.queue.put({
                'type': 'error',
                'error': f"ComfyUI execution failed: {str(e)}"
            })

    def execute_comfyui_script(self, prompt_data, script_name):
        """Execute ComfyUI script as imported module (ENHANCED WITH ALL IMPROVEMENTS)"""
        import random
        import importlib.util
        import sys
        import importlib
        from pathlib import Path

        try:
            # Step 1: Validate script compatibility before execution
            script_path = Path(self.selected_comfyui_script)
            if not script_path.exists():
                print(f"❌ Script not found: {script_path}")
                return False

            # Validate script is compatible with module import
            is_valid, validation_message = self.validate_comfyui_script(script_path)
            if not is_valid:
                print(f"❌ Script validation failed: {validation_message}")
                print(f"   This script may not be compatible with SaveAsScript module import")
                return False

            print(f"✅ Script validation passed: {validation_message}")

            # Step 2: Read and extract prompt content
            prompt_file = prompt_data['file']
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract the prompt text
            import re
            prompt_match = re.search(r'## ComfyUI Prompt\s*```([^`]+)```', content, re.DOTALL)
            if prompt_match:
                prompt_text = prompt_match.group(1).strip()
            else:
                # Fallback: use title as prompt
                prompt_text = prompt_data['title']

            # Step 3: Prepare execution arguments
            if self.script_analyzer:
                execution_args = self.script_analyzer.get_execution_args(
                    script_name,
                    prompt_text,
                    negative_prompt="",
                    width=768,
                    height=1024,
                    steps=20,
                    seed=random.randint(1, 2**32 - 1)
                )
            else:
                # Default arguments for exported ComfyUI script
                execution_args = {
                    'text4': prompt_text,
                    'text5': "",
                    'width6': 768,
                    'height7': 1024,
                    'steps13': 20,
                    'seed12': random.randint(1, 2**32 - 1)
                }

            self.write_to_scan_results(f"🎨 Executing ComfyUI script: {self.selected_comfyui_script}")
            self.write_to_scan_results(f"   Arguments: {len(execution_args)} parameters")

            # Step 4: Enhanced module loading with unique names and reload support
            # Fix: Use unique module name based on script filename to avoid caching issues
            module_name = f"comfyui_script_{script_path.stem}"

            # Clear any cached version to force reload
            self.clear_module_cache(module_name)

            # Load the module with unique name
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            if spec is None:
                print(f"❌ Failed to create module spec for: {script_path}")
                return False

            module = importlib.util.module_from_spec(spec)
            if module is None:
                print(f"❌ Failed to create module from spec for: {script_path}")
                return False

            # Step 5: Execute the script with enhanced error handling
            try:
                # Execute the module
                spec.loader.exec_module(module)

                # Fix: Ensure common SaveAsScript variables are defined (common bugs)
                fixes_applied = []
                if not hasattr(module, 'has_manager'):
                    module.has_manager = False
                    fixes_applied.append("has_manager")

                # Additional common fixes for SaveAsScript issues
                if not hasattr(module, '_custom_nodes_imported'):
                    module._custom_nodes_imported = False
                    fixes_applied.append("_custom_nodes_imported")

                if not hasattr(module, '_custom_path_added'):
                    module._custom_path_added = False
                    fixes_applied.append("_custom_path_added")

                if fixes_applied:
                    print(f"🔧 Auto-fixed missing variables: {', '.join(fixes_applied)}")

                # Verify the main function exists
                if not hasattr(module, 'main'):
                    print(f"❌ Script does not have a 'main' function")
                    return False

                # Call the main function with our arguments
                print(f"🔧 Calling main function with {len(execution_args)} arguments...")
                result = module.main(**execution_args)

                self.write_to_scan_results(f"✅ ComfyUI script executed successfully")
                self.write_to_scan_results(f"   Result type: {type(result)}")

                # Step 6: Enhanced result processing and image saving
                if isinstance(result, dict):
                    if 'images' in result:
                        # Extract data from result
                        images = result['images']
                        filename_prefix = result.get('filename_prefix', 'synthwave_generated')
                        prompt_data_for_save = result.get('prompt', {})

                        # Enhanced image count reporting
                        image_count = len(images) if hasattr(images, '__len__') else 1
                        self.write_to_scan_results(f"💾 Saving {image_count} generated image(s)...")

                        # Method 1: Try ComfyUI's native SaveImage
                        try:
                            # Find ComfyUI directory and add to path
                            comfy_paths = [
                                "/Volumes/Tikbalang2TB/Users/tikbalang/comfy_env/ComfyUI",  # Known path
                                str(Path.cwd().parent),  # Parent directory
                                str(Path.cwd()),  # Current directory
                            ]

                            comfyui_found = False
                            for comfy_path in comfy_paths:
                                comfy_extras_path = Path(comfy_path) / "comfy_extras"
                                if comfy_extras_path.exists():
                                    if str(comfy_path) not in sys.path:
                                        sys.path.insert(0, str(comfy_path))
                                    print(f"🔍 Using ComfyUI path: {comfy_path}")
                                    comfyui_found = True
                                    break

                            if comfyui_found:
                                from comfy_extras.nodes_saveimage import SaveImage
                                saveimage = SaveImage()

                                # Add timestamp to filename_prefix for uniqueness
                                import time
                                timestamp = int(time.time() * 1000)  # Millisecond timestamp
                                unique_prefix = f"{filename_prefix}_{timestamp}"
                                print(f"🔧 Using unique filename prefix: {unique_prefix}")

                                # Save the images using ComfyUI's save function
                                saved_result = saveimage.save_images(
                                    filename_prefix=unique_prefix,
                                    images=images,
                                    prompt=prompt_data_for_save
                                )

                                # Enhanced saved file reporting
                                if 'ui' in saved_result and 'images' in saved_result['ui']:
                                    saved_files = saved_result['ui']['images']
                                    self.write_to_scan_results(f"📁 Images saved successfully via ComfyUI:")
                                    for i, img_info in enumerate(saved_files, 1):
                                        filename = img_info.get('filename', f'image_{i}')
                                        subfolder = img_info.get('subfolder', '')
                                        if subfolder:
                                            filepath = f"{subfolder}/{filename}"
                                        else:
                                            filepath = filename
                                        self.write_to_scan_results(f"   {i}. {filepath}")
                                else:
                                    print(f"📁 Images saved with result: {saved_result}")

                                return True
                            else:
                                raise ImportError("ComfyUI path not found")

                        except ImportError as import_error:
                            print(f"⚠️ ComfyUI SaveImage not available: {import_error}")
                            print(f"   Falling back to direct tensor saving...")

                            # Method 2: Fallback - Direct tensor to image saving
                            try:
                                import torch
                                from PIL import Image
                                import numpy as np

                                # Create output directory
                                output_dir = Path("output") / "synthwave_generated"
                                output_dir.mkdir(parents=True, exist_ok=True)

                                saved_files = []

                                # Convert tensor images to PIL and save
                                for i, img_tensor in enumerate(images):
                                    # Convert from torch tensor to numpy array
                                    if hasattr(img_tensor, 'cpu'):
                                        img_array = img_tensor.cpu().numpy()
                                    else:
                                        img_array = np.array(img_tensor)

                                    # Ensure proper format (0-255, uint8)
                                    if img_array.max() <= 1.0:
                                        img_array = (img_array * 255).astype(np.uint8)
                                    else:
                                        img_array = img_array.astype(np.uint8)

                                    # Handle different tensor shapes
                                    if len(img_array.shape) == 4:  # (batch, height, width, channels)
                                        img_array = img_array[0]
                                    if len(img_array.shape) == 3 and img_array.shape[0] in [1, 3, 4]:  # (channels, height, width)
                                        img_array = np.transpose(img_array, (1, 2, 0))

                                    # Create PIL Image
                                    if img_array.shape[-1] == 1:  # Grayscale
                                        pil_img = Image.fromarray(img_array.squeeze(), mode='L')
                                    elif img_array.shape[-1] == 3:  # RGB
                                        pil_img = Image.fromarray(img_array, mode='RGB')
                                    elif img_array.shape[-1] == 4:  # RGBA
                                        pil_img = Image.fromarray(img_array, mode='RGBA')
                                    else:
                                        # Default to RGB by taking first 3 channels
                                        pil_img = Image.fromarray(img_array[:, :, :3], mode='RGB')

                                    # Generate unique filename to prevent overwrites
                                    import time
                                    base_name = filename_prefix.replace('/', '_')
                                    timestamp = int(time.time() * 1000)  # Millisecond timestamp for uniqueness

                                    # Try basic filename first
                                    base_filename = f"{base_name}_{i+1:05d}_{timestamp}.png"
                                    filepath = output_dir / base_filename

                                    # If file exists, increment counter until we find a unique name
                                    counter = 0
                                    while filepath.exists():
                                        counter += 1
                                        unique_filename = f"{base_name}_{i+1:05d}_{timestamp}_{counter:03d}.png"
                                        filepath = output_dir / unique_filename

                                    print(f"🔧 Saving to unique filename: {filepath.name}")

                                    # Save the image
                                    pil_img.save(filepath)
                                    saved_files.append(str(filepath))

                                print(f"📁 Images saved successfully via fallback method:")
                                for i, filepath in enumerate(saved_files, 1):
                                    print(f"   {i}. {filepath}")

                                return True

                            except Exception as fallback_error:
                                print(f"❌ Fallback image saving failed: {fallback_error}")
                                print(f"   Raw result available but not saved to disk")
                                print(f"   Result structure: {list(result.keys())}")
                                print(f"   Images tensor info: type={type(images)}, shape={getattr(images, 'shape', 'no shape attr')}")
                                return True  # Still return True since generation succeeded

                        except Exception as save_error:
                            print(f"⚠️ Image generation succeeded but saving failed: {save_error}")
                            print(f"   Raw result available but not saved to disk")
                            print(f"   Result structure: {list(result.keys())}")
                            return True  # Still return True since generation succeeded
                    else:
                        # Enhanced error reporting for SaveAsScript issues
                        available_keys = list(result.keys())
                        print(f"⚠️ No 'images' key found in result")
                        print(f"   Available keys: {available_keys}")
                        if 'ui' in available_keys:
                            print(f"   UI structure: {result['ui'] if isinstance(result.get('ui'), dict) else type(result.get('ui'))}")
                        print(f"   This may indicate a SaveAsScript compatibility issue")
                        return True  # Still consider it a success since script ran
                else:
                    print(f"❌ Expected dict result but got: {type(result)}")
                    print(f"   This indicates the script is not properly configured for module import")
                    return False

            except AttributeError as attr_error:
                print(f"❌ Script attribute error: {attr_error}")
                print(f"   This may indicate missing SaveAsScript export features")
                return False
            except TypeError as type_error:
                print(f"❌ Script type error: {type_error}")
                print(f"   This may indicate incorrect argument mapping")
                print(f"   Expected arguments: {list(execution_args.keys())}")
                return False
            except Exception as exec_error:
                print(f"❌ Script execution failed: {exec_error}")
                print(f"   Error type: {type(exec_error).__name__}")
                return False

        except FileNotFoundError as file_error:
            print(f"❌ File not found: {file_error}")
            return False
        except Exception as general_error:
            print(f"❌ Unexpected error executing ComfyUI script: {general_error}")
            print(f"   Error type: {type(general_error).__name__}")
            return False

    def create_comfyui_config_tab(self):
        """Create the ComfyUI configuration tab"""
        config_frame = ttk.Frame(self.notebook, style="Synthwave.TFrame")
        self.notebook.add(config_frame, text="COMFYUI CONFIG")

        # Main container
        main_container = tk.Frame(config_frame, bg=SynthwaveColors.BACKGROUND)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Top row: Script Selection and Model Selection (side by side)
        top_row_frame = tk.Frame(main_container, bg=SynthwaveColors.BACKGROUND)
        top_row_frame.pack(fill='x', pady=(0, 20))

        # Script Selection Section (left half)
        self.create_script_selection_section(top_row_frame)

        # Model Selection Section (right half)
        self.create_model_selection_section(top_row_frame)

        # Script Import Section
        self.create_script_import_section(main_container)

        # Prompt Argument Configuration Section
        self.create_prompt_config_section(main_container)

        # Script Preview Section
        self.create_script_preview_section(main_container)

    def create_script_selection_section(self, parent):
        """Create ComfyUI script selection section (left half)"""
        # Left half container
        left_container = tk.Frame(parent, bg=SynthwaveColors.BACKGROUND)
        left_container.pack(side='left', fill='both', expand=True, padx=(0, 10))

        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            left_container,
            text="┌─ SCRIPT SELECTION ─┐",
            font=header_font,
            fg=SynthwaveColors.PRIMARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        selection_container = tk.Frame(left_container, bg=SynthwaveColors.PANEL_BG, relief='solid', bd=3, highlightbackground=SynthwaveColors.NEON_PINK, highlightthickness=2)
        selection_container.pack(fill='both', expand=True)

        selection_frame = tk.Frame(selection_container, bg=SynthwaveColors.SECONDARY)
        selection_frame.pack(fill='x', padx=15, pady=15)

        label_font = font.Font(family="Courier New", size=10)
        button_font = font.Font(family="Courier New", size=10, weight="bold")

        # Current script display
        current_frame = tk.Frame(selection_frame, bg=SynthwaveColors.SECONDARY)
        current_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            current_frame,
            text="Current Script:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        ).pack(side='left')

        self.current_script_display = tk.Label(
            current_frame,
            text=self.selected_comfyui_script,
            font=font.Font(family="Courier New", size=10, weight="bold"),
            fg=SynthwaveColors.WARNING,
            bg=SynthwaveColors.SECONDARY
        )
        self.current_script_display.pack(side='left', padx=(10, 0))

        # Available scripts listbox
        scripts_label = tk.Label(
            selection_frame,
            text="Available Scripts:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        scripts_label.pack(anchor='w', pady=(0, 5))

        scripts_frame = tk.Frame(selection_frame, bg=SynthwaveColors.SECONDARY)
        scripts_frame.pack(fill='x', pady=(0, 15))

        self.scripts_listbox = tk.Listbox(
            scripts_frame,
            font=label_font,
            bg=SynthwaveColors.BACKGROUND,
            fg=SynthwaveColors.TEXT,
            selectbackground=SynthwaveColors.PRIMARY_ACCENT,
            selectforeground=SynthwaveColors.BACKGROUND,
            height=6
        )

        scripts_scrollbar = ttk.Scrollbar(scripts_frame, orient="vertical", command=self.scripts_listbox.yview)
        self.scripts_listbox.configure(yscrollcommand=scripts_scrollbar.set)

        self.scripts_listbox.pack(side="left", fill="both", expand=True)
        scripts_scrollbar.pack(side="right", fill="y")

        # Load available scripts
        self.refresh_scripts_list()

        # Script control buttons
        buttons_frame = tk.Frame(selection_frame, bg=SynthwaveColors.SECONDARY)
        buttons_frame.pack(fill='x')

        select_btn = tk.Button(
            buttons_frame,
            text="SELECT SCRIPT",
            font=button_font,
            bg=SynthwaveColors.SUCCESS,
            fg=SynthwaveColors.BACKGROUND,
            relief='flat',
            padx=15,
            pady=6,
            command=self.select_script
        )
        select_btn.pack(side='left')

    def create_model_selection_section(self, parent):
        """Create LMStudio model selection section (right half)"""
        # Right half container
        right_container = tk.Frame(parent, bg=SynthwaveColors.BACKGROUND)
        right_container.pack(side='right', fill='both', expand=True, padx=(10, 0))

        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            right_container,
            text="┌─ MODEL SELECTION ─┐",
            font=header_font,
            fg=SynthwaveColors.SECONDARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        model_container = tk.Frame(right_container, bg=SynthwaveColors.PANEL_BG, relief='solid', bd=3, highlightbackground=SynthwaveColors.NEON_CYAN, highlightthickness=2)
        model_container.pack(fill='both', expand=True)

        model_frame = tk.Frame(model_container, bg=SynthwaveColors.SECONDARY)
        model_frame.pack(fill='x', padx=15, pady=15)

        label_font = font.Font(family="Courier New", size=10)
        button_font = font.Font(family="Courier New", size=10, weight="bold")

        # Current model display
        current_model_frame = tk.Frame(model_frame, bg=SynthwaveColors.SECONDARY)
        current_model_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            current_model_frame,
            text="Current Model:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        ).pack(side='left')

        # Initialize current model variable with fallback
        self.current_model_var = tk.StringVar(value="qwen/qwen3-vl-30b@4bit")  # Default fallback

        self.current_model_display = tk.Label(
            current_model_frame,
            textvariable=self.current_model_var,
            font=font.Font(family="Courier New", size=10, weight="bold"),
            fg=SynthwaveColors.WARNING,
            bg=SynthwaveColors.SECONDARY
        )
        self.current_model_display.pack(side='left', padx=(10, 0))

        # Available models dropdown
        models_label = tk.Label(
            model_frame,
            text="Available Models:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        models_label.pack(anchor='w', pady=(0, 5))

        # Model selection frame
        select_model_frame = tk.Frame(model_frame, bg=SynthwaveColors.SECONDARY)
        select_model_frame.pack(fill='x', pady=(0, 15))

        # Initialize available models variable
        self.available_models_var = tk.StringVar()
        self.available_models = []

        # Model dropdown (Combobox)
        self.model_combobox = ttk.Combobox(
            select_model_frame,
            textvariable=self.available_models_var,
            font=label_font,
            state='readonly',
            width=35
        )
        self.model_combobox.pack(side='left', padx=(0, 10))

        # Load Model button
        load_model_btn = tk.Button(
            select_model_frame,
            text="Load Model",
            font=button_font,
            bg=SynthwaveColors.PRIMARY_ACCENT,
            fg=SynthwaveColors.BACKGROUND,
            activebackground=SynthwaveColors.NEON_CYAN,
            activeforeground=SynthwaveColors.BACKGROUND,
            relief='flat',
            padx=15,
            pady=6,
            command=self.load_selected_model
        )
        load_model_btn.pack(side='left', padx=(0, 10))

        # Refresh Models button
        refresh_models_btn = tk.Button(
            select_model_frame,
            text="Refresh",
            font=button_font,
            bg=SynthwaveColors.TERTIARY_ACCENT,
            fg=SynthwaveColors.BACKGROUND,
            activebackground=SynthwaveColors.NEON_PINK,
            activeforeground=SynthwaveColors.BACKGROUND,
            relief='flat',
            padx=15,
            pady=6,
            command=self.refresh_available_models
        )
        refresh_models_btn.pack(side='left')

        # Status display
        self.model_status_label = tk.Label(
            model_frame,
            text="Status: Ready to load models",
            font=font.Font(family="Courier New", size=9),
            fg=SynthwaveColors.SECONDARY_ACCENT,
            bg=SynthwaveColors.SECONDARY
        )
        self.model_status_label.pack(anchor='w', pady=(5, 0))

        # Initialize models on creation
        self.refresh_available_models()

    def create_script_import_section(self, parent):
        """Create script import section"""
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ IMPORT NEW SCRIPT ─┐",
            font=header_font,
            fg=SynthwaveColors.SECONDARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        import_container = tk.Frame(parent, bg=SynthwaveColors.SECONDARY, relief='ridge', bd=2)
        import_container.pack(fill='x', pady=(0, 20), padx=10)

        import_frame = tk.Frame(import_container, bg=SynthwaveColors.SECONDARY)
        import_frame.pack(fill='x', padx=15, pady=15)

        label_font = font.Font(family="Courier New", size=10)
        button_font = font.Font(family="Courier New", size=10, weight="bold")

        # Instructions
        instructions = tk.Label(
            import_frame,
            text="Import ComfyUI exported workflow scripts (.py files)",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        instructions.pack(anchor='w', pady=(0, 10))

        # File selection
        file_frame = tk.Frame(import_frame, bg=SynthwaveColors.SECONDARY)
        file_frame.pack(fill='x', pady=(0, 10))

        self.import_file_var = tk.StringVar()
        file_entry = tk.Entry(
            file_frame,
            textvariable=self.import_file_var,
            font=label_font,
            bg=SynthwaveColors.BACKGROUND,
            fg=SynthwaveColors.TEXT,
            insertbackground=SynthwaveColors.PRIMARY_ACCENT,
            width=50
        )
        file_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        browse_btn = tk.Button(
            file_frame,
            text="BROWSE",
            font=button_font,
            bg=SynthwaveColors.TERTIARY_ACCENT,
            fg=SynthwaveColors.BACKGROUND,
            relief='flat',
            padx=15,
            pady=6,
            command=self.browse_script_file
        )
        browse_btn.pack(side='right')

        # Import button
        import_btn = tk.Button(
            import_frame,
            text="📥 IMPORT SCRIPT",
            font=button_font,
            bg=SynthwaveColors.PRIMARY_ACCENT,
            fg=SynthwaveColors.BACKGROUND,
            relief='flat',
            padx=20,
            pady=8,
            command=self.import_script
        )
        import_btn.pack(anchor='w')

    def create_prompt_config_section(self, parent):
        """Create prompt argument configuration section"""
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ PROMPT ARGUMENT MAPPING ─┐",
            font=header_font,
            fg=SynthwaveColors.TERTIARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        config_container = tk.Frame(parent, bg=SynthwaveColors.SECONDARY, relief='ridge', bd=2)
        config_container.pack(fill='x', pady=(0, 20), padx=10)

        config_frame = tk.Frame(config_container, bg=SynthwaveColors.SECONDARY)
        config_frame.pack(fill='x', padx=15, pady=15)

        label_font = font.Font(family="Courier New", size=10)
        button_font = font.Font(family="Courier New", size=10, weight="bold")

        # Instructions
        instructions = tk.Label(
            config_frame,
            text="Arguments are auto-detected when importing scripts. Manual override available below.",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        instructions.pack(anchor='w', pady=(0, 10))

        # Status label for detection results (auto-updated on import)
        status_frame = tk.Frame(config_frame, bg=SynthwaveColors.SECONDARY)
        status_frame.pack(fill='x', pady=(0, 15))

        status_title = tk.Label(
            status_frame,
            text="Auto-Detection Status:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        status_title.pack(side='left')

        self.detection_status_label = tk.Label(
            status_frame,
            text="Import a script to auto-detect arguments",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        self.detection_status_label.pack(side='left', padx=(10, 0))

        # Argument selection controls
        selection_frame = tk.Frame(config_frame, bg=SynthwaveColors.SECONDARY)
        selection_frame.pack(fill='x', pady=(0, 15))

        # Main prompt argument
        main_prompt_frame = tk.Frame(selection_frame, bg=SynthwaveColors.SECONDARY)
        main_prompt_frame.pack(fill='x', pady=(0, 10))

        tk.Label(
            main_prompt_frame,
            text="Main Prompt Argument:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        ).pack(side='left')

        self.main_prompt_var = tk.StringVar()
        self.main_prompt_combo = ttk.Combobox(
            main_prompt_frame,
            textvariable=self.main_prompt_var,
            font=label_font,
            width=15,
            state="readonly"
        )
        self.main_prompt_combo.pack(side='left', padx=(10, 0))

        # Negative prompt argument
        neg_prompt_frame = tk.Frame(selection_frame, bg=SynthwaveColors.SECONDARY)
        neg_prompt_frame.pack(fill='x', pady=(0, 10))

        tk.Label(
            neg_prompt_frame,
            text="Negative Prompt Argument:",
            font=label_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        ).pack(side='left')

        self.neg_prompt_var = tk.StringVar()
        self.neg_prompt_combo = ttk.Combobox(
            neg_prompt_frame,
            textvariable=self.neg_prompt_var,
            font=label_font,
            width=15,
            state="readonly"
        )
        self.neg_prompt_combo.pack(side='left', padx=(10, 0))

        # Save configuration button
        save_frame = tk.Frame(config_frame, bg=SynthwaveColors.SECONDARY)
        save_frame.pack(fill='x')

        save_btn = tk.Button(
            save_frame,
            text="💾 SAVE MAPPING",
            font=button_font,
            bg=SynthwaveColors.SUCCESS,
            fg=SynthwaveColors.BACKGROUND,
            relief='flat',
            padx=15,
            pady=6,
            command=self.save_prompt_mapping
        )
        save_btn.pack(side='left')

        # Initialize script analyzer
        if ComfyUIScriptAnalyzer:
            self.script_analyzer = ComfyUIScriptAnalyzer()
        else:
            self.script_analyzer = None

    def create_script_preview_section(self, parent):
        """Create script preview section"""
        header_font = font.Font(family="Courier New", size=14, weight="bold")
        section_label = tk.Label(
            parent,
            text="┌─ SCRIPT PREVIEW ─┐",
            font=header_font,
            fg=SynthwaveColors.TERTIARY_ACCENT,
            bg=SynthwaveColors.BACKGROUND
        )
        section_label.pack(anchor='w', pady=(0, 10))

        preview_container = tk.Frame(parent, bg=SynthwaveColors.SECONDARY, relief='ridge', bd=2)
        preview_container.pack(fill='both', expand=True, padx=10)

        # Preview text widget
        preview_frame = tk.Frame(preview_container, bg=SynthwaveColors.SECONDARY)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.script_preview = tk.Text(
            preview_frame,
            font=font.Font(family="Courier New", size=9),
            bg=SynthwaveColors.BACKGROUND,
            fg=SynthwaveColors.TEXT,
            insertbackground=SynthwaveColors.PRIMARY_ACCENT,
            state='disabled',
            height=10,
            wrap='none'
        )

        preview_scroll_y = ttk.Scrollbar(preview_frame, orient="vertical", command=self.script_preview.yview)
        preview_scroll_x = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.script_preview.xview)
        self.script_preview.configure(yscrollcommand=preview_scroll_y.set, xscrollcommand=preview_scroll_x.set)

        self.script_preview.pack(side="left", fill="both", expand=True)
        preview_scroll_y.pack(side="right", fill="y")
        preview_scroll_x.pack(side="bottom", fill="x")

    def refresh_scripts_list(self):
        """Refresh the list of available ComfyUI scripts"""
        self.scripts_listbox.delete(0, tk.END)
        self.scan_comfyui_scripts()

        for script in self.available_scripts:
            self.scripts_listbox.insert(tk.END, script)

        # Auto-select current script
        try:
            current_index = self.available_scripts.index(self.selected_comfyui_script)
            self.scripts_listbox.selection_set(current_index)
            self.scripts_listbox.see(current_index)
        except ValueError:
            pass

    def auto_detect_arguments_for_script(self, script_name):
        """Auto-detect prompt arguments for a specific script and return result"""
        if not self.script_analyzer:
            return None

        try:
            # Analyze the specified script
            arguments, mapping = self.script_analyzer.analyze_script(script_name)

            # Extract text arguments for the combo boxes
            text_args = [arg.dest for arg in arguments if 'text' in arg.dest.lower()]
            text_args.sort()

            # Update combo box options
            self.main_prompt_combo['values'] = text_args
            self.neg_prompt_combo['values'] = text_args

            # Set suggested values
            if mapping.main_prompt:
                self.main_prompt_var.set(mapping.main_prompt)
            if mapping.negative_prompt:
                self.neg_prompt_var.set(mapping.negative_prompt)

            # Update status
            status = f"Found {len(arguments)} args, {len(text_args)} text args"
            if mapping.main_prompt:
                status += f" | Main: {mapping.main_prompt}"
            if mapping.negative_prompt:
                status += f" | Neg: {mapping.negative_prompt}"

            self.detection_status_label.config(
                text=status,
                fg=SynthwaveColors.SUCCESS
            )

            # Auto-save the mapping
            script_base = script_name.replace('.py', '')
            self.script_analyzer.save_mapping(script_base, mapping)

            # Return result for display in import message
            result = f"Main: {mapping.main_prompt or 'None'}, Neg: {mapping.negative_prompt or 'None'}"
            return result

        except Exception as e:
            self.detection_status_label.config(
                text=f"Error: {str(e)}",
                fg=SynthwaveColors.WARNING
            )
            return None


    def save_prompt_mapping(self):
        """Save the current prompt argument mapping"""
        if not self.script_analyzer:
            messagebox.showerror("Error", "Script analyzer not available")
            return

        if not self.selected_comfyui_script:
            messagebox.showwarning("Warning", "No script selected")
            return

        try:
            # Create mapping from current UI values
            from script_analyzer import PromptMapping
            mapping = PromptMapping(
                main_prompt=self.main_prompt_var.get() or None,
                negative_prompt=self.neg_prompt_var.get() or None
            )

            # Save the mapping
            script_name = self.selected_comfyui_script.replace('.py', '')
            self.script_analyzer.save_mapping(script_name, mapping)

            messagebox.showinfo("Success", f"Prompt mapping saved for {script_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save mapping: {e}")

    def load_prompt_mapping(self, script_name):
        """Load and display saved prompt mapping for a script"""
        if not self.script_analyzer:
            return

        try:
            mapping = self.script_analyzer.load_mapping(script_name)
            if mapping:
                self.main_prompt_var.set(mapping.main_prompt or "")
                self.neg_prompt_var.set(mapping.negative_prompt or "")

                status = "Loaded saved mapping"
                if mapping.main_prompt:
                    status += f" | Main: {mapping.main_prompt}"
                if mapping.negative_prompt:
                    status += f" | Neg: {mapping.negative_prompt}"

                self.detection_status_label.config(
                    text=status,
                    fg=SynthwaveColors.SUCCESS
                )
            else:
                # Clear UI if no mapping found
                self.main_prompt_var.set("")
                self.neg_prompt_var.set("")
                self.detection_status_label.config(
                    text="No saved mapping found",
                    fg=SynthwaveColors.TEXT
                )
        except Exception as e:
            print(f"Error loading mapping: {e}")

    def select_script(self):
        """Select a ComfyUI script from the list"""
        selection = self.scripts_listbox.curselection()
        if selection:
            selected_script = self.available_scripts[selection[0]]
            self.selected_comfyui_script = selected_script
            self.current_script_display.config(text=selected_script)
            self.current_script_label.config(text=f"Script: {selected_script}")

            # Load script preview
            self.load_script_preview(selected_script)

            # Load prompt mapping for this script
            script_name = selected_script.replace('.py', '')
            self.load_prompt_mapping(script_name)

            messagebox.showinfo("Success", f"Selected script: {selected_script}")
        else:
            messagebox.showwarning("Warning", "Please select a script from the list")

    def browse_script_file(self):
        """Browse for a ComfyUI script file to import"""
        file_path = filedialog.askopenfilename(
            title="Select ComfyUI Script",
            filetypes=[
                ("Python files", "*.py"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.import_file_var.set(file_path)

    def import_script(self):
        """Import a new ComfyUI script"""
        file_path = self.import_file_var.get().strip()
        if not file_path:
            messagebox.showerror("Error", "Please select a file to import")
            return

        try:
            import shutil
            source_path = Path(file_path)
            if not source_path.exists():
                messagebox.showerror("Error", "Selected file does not exist")
                return

            # Step 1: Validate script before importing
            is_valid, validation_message = self.validate_comfyui_script(source_path)
            if not is_valid:
                # Show validation warning but allow import anyway
                result = messagebox.askyesno(
                    "Script Validation Warning",
                    f"Script validation failed: {validation_message}\n\n"
                    "This script may not be compatible with SaveAsScript module import.\n"
                    "Do you want to import it anyway?"
                )
                if not result:
                    print(f"❌ Script import cancelled due to validation issues")
                    return

            # Copy to current directory
            destination = Path(source_path.name)
            shutil.copy2(source_path, destination)

            # Store the imported script name for auto-selection
            imported_script_name = source_path.name

            print(f"📥 Imported script: {imported_script_name}")
            print(f"📂 File exists at destination: {destination.exists()}")

            # Validate the copied script for final confirmation
            is_valid_copy, copy_validation_message = self.validate_comfyui_script(destination)
            if is_valid_copy:
                print(f"✅ Script validation passed: {copy_validation_message}")
            else:
                print(f"⚠️ Script validation warning: {copy_validation_message}")

            # Refresh scripts list
            self.refresh_scripts_list()

            print(f"📋 Available scripts after refresh: {self.available_scripts}")

            # Auto-select the newly imported script
            if imported_script_name in self.available_scripts:
                try:
                    script_index = self.available_scripts.index(imported_script_name)
                    self.scripts_listbox.selection_set(script_index)
                    self.scripts_listbox.see(script_index)

                    # Set as current script
                    self.selected_comfyui_script = imported_script_name
                    self.current_script_display.config(text=imported_script_name)
                    self.current_script_label.config(text=f"Script: {imported_script_name}")

                    # Load script preview
                    self.load_script_preview(imported_script_name)

                    # Auto-detect arguments for the imported script
                    detection_result = self.auto_detect_arguments_for_script(imported_script_name)

                    success_msg = f"✅ Imported and selected script: {imported_script_name}"
                    if is_valid_copy:
                        success_msg += f"\n✅ Validation: {copy_validation_message}"
                    else:
                        success_msg += f"\n⚠️ Validation: {copy_validation_message}"
                    if detection_result:
                        success_msg += f"\n🔍 Detected arguments: {detection_result}"

                    messagebox.showinfo("Success", success_msg)
                    print(f"✅ Successfully auto-selected: {imported_script_name}")
                except Exception as e:
                    print(f"❌ Error during auto-selection: {e}")
                    messagebox.showinfo("Success", f"✅ Imported script: {imported_script_name}\n⚠️ Auto-selection failed: {e}")
            else:
                # Script not detected by our filters - force add it
                print(f"⚠️ Script not detected by filters, force-adding: {imported_script_name}")
                self.available_scripts.append(imported_script_name)
                self.scripts_listbox.insert(tk.END, imported_script_name)

                # Now select it
                try:
                    script_index = len(self.available_scripts) - 1
                    self.scripts_listbox.selection_set(script_index)
                    self.scripts_listbox.see(script_index)

                    # Set as current script
                    self.selected_comfyui_script = imported_script_name
                    self.current_script_display.config(text=imported_script_name)
                    self.current_script_label.config(text=f"Script: {imported_script_name}")

                    # Load script preview
                    self.load_script_preview(imported_script_name)

                    # Auto-detect arguments for the imported script
                    detection_result = self.auto_detect_arguments_for_script(imported_script_name)

                    success_msg = f"✅ Imported and selected script: {imported_script_name}\n(Force-added to list)"
                    if is_valid_copy:
                        success_msg += f"\n✅ Validation: {copy_validation_message}"
                    else:
                        success_msg += f"\n⚠️ Validation: {copy_validation_message}"
                    if detection_result:
                        success_msg += f"\n🔍 Detected arguments: {detection_result}"

                    messagebox.showinfo("Success", success_msg)
                    print(f"✅ Force-added and selected: {imported_script_name}")
                except Exception as e:
                    print(f"❌ Error during force-selection: {e}")
                    messagebox.showwarning("Partial Success", f"✅ Imported script: {imported_script_name}\n❌ Could not auto-select: {e}")

            self.import_file_var.set("")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import script: {str(e)}")

    def load_script_preview(self, script_name):
        """Load preview of the selected script"""
        try:
            script_path = Path(script_name)
            if script_path.exists():
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.script_preview.config(state='normal')
                self.script_preview.delete(1.0, tk.END)

                # Show first 50 lines for preview
                lines = content.split('\n')
                preview_lines = lines[:50]
                if len(lines) > 50:
                    preview_lines.append("...")
                    preview_lines.append(f"[{len(lines) - 50} more lines]")

                self.script_preview.insert(1.0, '\n'.join(preview_lines))
                self.script_preview.config(state='disabled')
            else:
                self.script_preview.config(state='normal')
                self.script_preview.delete(1.0, tk.END)
                self.script_preview.insert(1.0, f"Script file '{script_name}' not found")
                self.script_preview.config(state='disabled')

        except Exception as e:
            self.script_preview.config(state='normal')
            self.script_preview.delete(1.0, tk.END)
            self.script_preview.insert(1.0, f"Error loading script: {str(e)}")
            self.script_preview.config(state='disabled')


    def process_queue(self):
        """Process messages from background threads"""
        try:
            while True:
                message = self.queue.get_nowait()
                self.handle_queue_message(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def handle_queue_message(self, message):
        """Handle messages from background threads"""
        msg_type = message.get('type')

        if msg_type == 'scan_progress':
            self.update_scan_progress(message)
        elif msg_type == 'scan_complete':
            self.handle_scan_complete(message)
        elif msg_type == 'transform_progress':
            self.update_transform_progress(message)
        elif msg_type == 'transform_complete':
            self.handle_transform_complete(message)
        elif msg_type == 'comfyui_progress':
            self.update_comfyui_progress(message)
        elif msg_type == 'comfyui_complete':
            self.handle_comfyui_complete(message)
        elif msg_type == 'error':
            self.handle_error(message)
        elif msg_type == 'log_message':
            self.handle_log_message(message)

    def handle_log_message(self, message):
        """Handle log messages by writing them to scan results"""
        log_text = message.get('message', 'Log message')
        self.write_to_scan_results(log_text)

    def update_scan_progress(self, message):
        """Update scan progress in GUI"""
        current = message.get('current', 0)
        total = message.get('total', 1)
        post_title = message.get('post_title', 'Scanning...')

        # Update progress bar
        self.scan_progress.config(value=current, maximum=total)

        # Update status (with safety check)
        if hasattr(self, 'current_operation_label'):
            self.current_operation_label.config(text=f"Scanning: {post_title[:50]}...")

        # Log message to console
        print(f"[INFO] Scanning post {current}/{total}: {post_title}")

    def handle_scan_complete(self, message):
        """Handle scan completion"""
        results = message.get('results', [])
        subreddit = message.get('subreddit', 'unknown')

        # Update UI
        self.start_scan_btn.config(state='normal', text="▶ START SCAN")
        self.scan_progress.stop()
        self.scan_progress.config(mode='determinate', value=100, maximum=100)

        # Update scan results display
        self.current_scan_results = results
        self.write_to_scan_results(f"✅ Scan completed! Found {len(results)} posts:")

        for post in results:
            title = post.get('title', 'Unknown Title')[:60]
            score = post.get('score', 0)
            self.write_to_scan_results(f"   [{score}] {title}")

        # Log success to console
        print(f"[SUCCESS] Scan complete: {len(results)} posts from r/{subreddit}")

        # Auto-transform if enabled
        if self.auto_transform_var.get() and results:
            print("[INFO] Auto-transformation enabled, starting AI processing...")
            self.start_transform_thread()

    def start_transform_thread(self):
        """Start transformation thread for all scan results"""
        if not self.current_scan_results:
            return

        print("[INFO] Starting AI transformation of Reddit posts to design prompts")

        self.transform_thread = threading.Thread(
            target=self.run_transform_all,
            daemon=True
        )
        self.transform_thread.start()

    def run_transform_all(self):
        """Transform all scan results to prompts in background thread"""
        try:
            # Perform model health check before starting batch transformation
            if not self.refresh_model_connection():
                # Try enhanced error recovery before giving up
                if not self.enhanced_model_error_recovery("transformation_start"):
                    self.queue.put({
                        'type': 'transform_complete',
                        'total_processed': 0,
                        'error': 'Model health check failed - cannot proceed with transformation'
                    })
                    return

            # Mark model as active for transformation batch
            self.set_model_state(ModelState.ACTIVE, "Processing transformation batch...")

            total_posts = len(self.current_scan_results)
            successful_transforms = 0

            for i, post in enumerate(self.current_scan_results):
                self.queue.put({
                    'type': 'transform_progress',
                    'current': i + 1,
                    'total': total_posts,
                    'post_title': post.get('title', 'Unknown')
                })

                # Ensure post has usable text content (use title if text_content is empty)
                if not post.get('text_content') or post['text_content'] == 'N/A':
                    post['text_content'] = post['title']

                # Transform post to prompt
                if self.llm_transformer:
                    try:
                        post_title = post.get('title', 'Unknown')[:40] + "..."
                        self.queue.put({
                            'type': 'log_message',
                            'message': f"🤖 Generating prompt for: {post_title}"
                        })

                        prompt_result = self.llm_transformer.transform_reddit_to_tshirt_prompt(post)
                        if prompt_result.get('success', False):
                            prompt_id = prompt_result.get('prompt_id', 'unknown')
                            self.queue.put({
                                'type': 'log_message',
                                'message': f"✅ Generated prompt: {prompt_id}"
                            })

                            # Add LLM-generated prompt to current session prompts
                            prompt_data = {
                                'file': Path(prompt_result['prompt_file']),
                                'reddit_id': post['id'],
                                'title': post['title'],
                                'score': str(post['score']),
                                'status': "⏳ Pending"
                            }
                            self.current_session_prompts.append(prompt_data)
                            successful_transforms += 1
                        else:
                            error_msg = prompt_result.get('error', 'Unknown error')
                            self.queue.put({
                                'type': 'log_message',
                                'message': f"❌ Failed to generate prompt: {error_msg}"
                            })
                    except Exception as e:
                        error_msg = f"Transform failed for post {post.get('id', 'unknown')}: {e}"
                        print(f"❌ {error_msg}")
                        self.queue.put({
                            'type': 'log_message',
                            'message': f"❌ {error_msg}"
                        })
                else:
                    # Create mock prompt for demo
                    self.create_mock_prompt(post)
                    successful_transforms += 1

                # Simulate processing time
                time.sleep(1)

            # Clean up model resources after batch completion
            self.cleanup_model_resources()

            self.queue.put({
                'type': 'transform_complete',
                'total_processed': successful_transforms
            })

        except Exception as e:
            # Clean up resources even on failure
            self.cleanup_model_resources()

            self.queue.put({
                'type': 'error',
                'error': f"Transformation failed: {str(e)}"
            })

    def create_mock_prompt(self, post):
        """Create a mock prompt file for demo purposes"""
        try:
            # Create prompts directory if it doesn't exist
            prompts_dir = Path("poc_output/prompts")
            prompts_dir.mkdir(parents=True, exist_ok=True)

            # Generate mock prompt content
            import datetime
            prompt_id = f"demo_prompt_{post['id']}"
            prompt_file = prompts_dir / f"{prompt_id}.md"

            mock_prompt = f"""Vector illustration of {post.get('text_content', 'trending meme concept')},
bold graphic design style, high contrast colors, minimalist composition,
suitable for t-shirt printing, 768x1024 pixels, 300 DPI, RGB, transparent background"""

            prompt_content = f"""# T-Shirt Design Prompt (Demo Mode)

## Source Information
- **Reddit ID**: {post['id']}
- **Original Title**: {post['title']}
- **Text Content**: {post.get('text_content', 'N/A')}
- **Popularity Score**: {post['score']}
- **Generated**: {datetime.datetime.now().isoformat()}
- **Generation Type**: Demo Mode

## ComfyUI Prompt

```
{mock_prompt}
```

## Technical Specifications
- **Dimensions**: 768x1024 pixels
- **Resolution**: 300 DPI
- **Color Mode**: RGB
- **Background**: Transparent
- **Format**: PNG
- **Design Type**: Demo visual graphic design

## Notes
- Demo mode prompt - LLM not available
- Generated for GUI demonstration purposes
"""

            # Save the mock prompt file
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt_content)

            # Add to current session prompts (for Results display)
            prompt_data = {
                'file': prompt_file,
                'reddit_id': post['id'],
                'title': post['title'],
                'score': str(post['score']),
                'status': "⏳ Pending"
            }
            self.current_session_prompts.append(prompt_data)

            print(f"✅ Created demo prompt: {prompt_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to create mock prompt: {e}")
            return False

    def update_transform_progress(self, message):
        """Update transformation progress"""
        current = message.get('current', 0)
        total = message.get('total', 1)
        post_title = message.get('post_title', 'Processing...')

        # Update progress (using scan_progress since operation_progress removed with Results tab)
        self.scan_progress.config(value=current, maximum=total)
        self.write_to_scan_results(f"🔄 Transforming: {current}/{total} - {post_title[:50]}...")

        # Update status (with safety check)
        if hasattr(self, 'current_operation_label'):
            self.current_operation_label.config(text=f"AI Processing: {post_title[:50]}...")

        # Log progress to console
        print(f"[INFO] Transforming {current}/{total}: {post_title}")

    def handle_transform_complete(self, message):
        """Handle transformation completion (Results tab removed - using consolidated interface)"""
        total_processed = message.get('total_processed', 0)

        # Log completion to scan results
        self.write_to_scan_results(f"🎉 AI transformation complete: {total_processed} prompts generated")

        # Refresh prompts (enables ComfyUI button if prompts exist)
        self.refresh_prompts()

        # Auto-execute ComfyUI if enabled
        if self.auto_execute_var.get() and total_processed > 0:
            self.write_to_scan_results("⚡ Auto-execution enabled, starting ComfyUI processing...")
            # Start ComfyUI execution directly (no tab switching needed)
            self.start_comfyui_execution()

    def update_comfyui_progress(self, message):
        """Update ComfyUI progress"""
        current = message.get('current', 0)
        total = message.get('total', 1)
        prompt_title = message.get('prompt_title', 'Processing...')

        # Update progress bars (using scan_progress since operation_progress removed with Results tab)
        self.scan_progress.config(value=current, maximum=total)
        self.write_to_scan_results(f"🎨 ComfyUI: {current}/{total} - {prompt_title[:50]}...")

        # Update status (with safety check)
        if hasattr(self, 'current_operation_label'):
            self.current_operation_label.config(text=f"Generating: {prompt_title[:50]}...")

        # Log progress to console
        print(f"[INFO] Generating design {current}/{total}: {prompt_title}")

    def handle_comfyui_complete(self, message):
        """Handle ComfyUI execution completion"""
        total_processed = message.get('total_processed', 0)

        # Reset UI state
        self.start_execution_btn.config(state='normal', text="▶ START COMFYUI")
        self.stop_execution_btn.config(state='disabled')

        # Update progress (using scan_progress since operation_progress removed with Results tab)
        self.scan_progress.config(value=100, maximum=100)
        self.write_to_scan_results(f"🎉 Complete: {total_processed}/{total_processed} operations finished")

        # Statistics would be updated in Monitor tab (removed)

        # Update status (with safety check)
        if hasattr(self, 'current_operation_label'):
            self.current_operation_label.config(text="Status: All designs generated successfully")

        # Log completion to console
        print(f"[SUCCESS] ComfyUI execution complete: {total_processed} designs generated")

        # Refresh prompts to show updated status
        self.refresh_prompts()

    def handle_error(self, message):
        """Handle error messages"""
        messagebox.showerror("Error", message.get('error', 'Unknown error occurred'))

    def create_gallery_tab(self):
        """Create the Gallery tab with file list and image viewer"""
        gallery_frame = ttk.Frame(self.notebook, style="Synthwave.TFrame")
        self.notebook.add(gallery_frame, text="GALLERY")

        # Main container
        main_container = tk.Frame(gallery_frame, bg=SynthwaveColors.BACKGROUND)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)

        # Create paned window for split layout
        paned_window = tk.PanedWindow(main_container, orient='horizontal', bg=SynthwaveColors.BACKGROUND, sashwidth=5, sashrelief='raised')
        paned_window.pack(fill='both', expand=True)

        # Left panel - File list
        self.create_file_list_panel(paned_window)

        # Right panel - Image viewer
        self.create_image_viewer_panel(paned_window)

        # Set initial pane sizes (30% for file list, 70% for image viewer)
        self.root.after(100, lambda: paned_window.sash_place(0, 300, 0))

        # Initialize gallery data
        self.output_folders = [
            "./output/synthwave_generated",
            "./poc_output/generated_designs"
        ]
        self.current_image_path = None
        self.gallery_images = []

        # Initial load of files
        self.refresh_gallery()

        # Set up auto-refresh (check for new files every 2 seconds)
        self.schedule_gallery_refresh()

    def create_file_list_panel(self, parent):
        """Create the left panel with file list"""
        # File list container
        list_container = tk.Frame(parent, bg=SynthwaveColors.PANEL_BG, relief='solid', bd=4, highlightbackground=SynthwaveColors.NEON_PURPLE, highlightthickness=3)
        parent.add(list_container, minsize=250)

        # Header
        header_font = font.Font(family="Courier New", size=12, weight="bold")
        header_label = tk.Label(
            list_container,
            text="📁 GENERATED IMAGES",
            font=header_font,
            fg=SynthwaveColors.PRIMARY_ACCENT,
            bg=SynthwaveColors.SECONDARY
        )
        header_label.pack(pady=(10, 5))

        # Refresh button with glow effect
        button_font = font.Font(family="Courier New", size=9, weight="bold")
        refresh_btn = tk.Button(
            list_container,
            text="🔄 REFRESH",
            font=button_font,
            bg=SynthwaveColors.PRIMARY_ACCENT,
            fg=SynthwaveColors.BACKGROUND,
            activebackground=SynthwaveColors.GLOW_PINK,
            relief='raised',
            bd=3,
            padx=15,
            pady=6,
            highlightbackground=SynthwaveColors.NEON_PINK,
            highlightthickness=1,
            command=self.refresh_gallery
        )
        refresh_btn.pack(pady=(0, 10))

        # File list with scrollbar
        list_frame = tk.Frame(list_container, bg=SynthwaveColors.SECONDARY)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Create listbox
        self.file_listbox = tk.Listbox(
            list_frame,
            font=font.Font(family="Courier New", size=9),
            bg=SynthwaveColors.BACKGROUND,
            fg=SynthwaveColors.TEXT,
            selectbackground=SynthwaveColors.PRIMARY_ACCENT,
            selectforeground=SynthwaveColors.BACKGROUND,
            relief='flat',
            bd=0,
            highlightthickness=0
        )

        # Scrollbar for listbox
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        # Pack listbox and scrollbar
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind events
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        # Cross-platform right-click bindings
        self.file_listbox.bind('<Button-3>', self.show_context_menu)        # Right-click (Linux/Windows)
        self.file_listbox.bind('<Button-2>', self.show_context_menu)        # Right-click (macOS)
        self.file_listbox.bind('<Control-Button-1>', self.show_context_menu)  # Ctrl+click (macOS)

    def create_image_viewer_panel(self, parent):
        """Create the right panel with image viewer"""
        # Image viewer container
        viewer_container = tk.Frame(parent, bg=SynthwaveColors.PANEL_BG, relief='solid', bd=4, highlightbackground=SynthwaveColors.NEON_CYAN, highlightthickness=3)
        parent.add(viewer_container, minsize=400)

        # Header
        header_font = font.Font(family="Courier New", size=12, weight="bold")
        self.image_header_label = tk.Label(
            viewer_container,
            text="🖼️ IMAGE VIEWER",
            font=header_font,
            fg=SynthwaveColors.SECONDARY_ACCENT,
            bg=SynthwaveColors.SECONDARY
        )
        self.image_header_label.pack(pady=(10, 5))

        # Image info label
        info_font = font.Font(family="Courier New", size=9)
        self.image_info_label = tk.Label(
            viewer_container,
            text="Select an image from the list to view",
            font=info_font,
            fg=SynthwaveColors.TEXT,
            bg=SynthwaveColors.SECONDARY
        )
        self.image_info_label.pack(pady=(0, 10))

        # Scrollable image canvas
        canvas_frame = tk.Frame(viewer_container, bg=SynthwaveColors.BACKGROUND)
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # Create canvas with scrollbars and explicit size
        self.image_canvas = tk.Canvas(
            canvas_frame,
            bg=SynthwaveColors.BACKGROUND,
            highlightthickness=0,
            width=800,
            height=600
        )

        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.image_canvas.yview)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=self.image_canvas.xview)

        self.image_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack canvas and scrollbars
        self.image_canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Bind canvas events for zooming/scrolling
        self.image_canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.image_canvas.bind('<Button-4>', self.on_mousewheel)
        self.image_canvas.bind('<Button-5>', self.on_mousewheel)

    def refresh_gallery(self, preserve_selection=False):
        """Refresh the file list with current images"""
        try:
            # Store current selection if preserving
            selected_file_path = None
            selected_index = None
            if preserve_selection:
                selection = self.file_listbox.curselection()
                if selection and selection[0] < len(self.gallery_images):
                    selected_index = selection[0]
                    selected_file_path = self.gallery_images[selected_index]['file_path']

            # Scan all output folders for images
            import os
            from pathlib import Path

            new_gallery_images = []

            for folder_path in self.output_folders:
                folder = Path(folder_path)
                if folder.exists():
                    # Find image files
                    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
                    for image_file in folder.iterdir():
                        if image_file.is_file() and image_file.suffix.lower() in image_extensions:
                            # Add to list with folder prefix for organization
                            folder_name = folder.name
                            display_name = f"[{folder_name}] {image_file.name}"

                            new_gallery_images.append({
                                'display_name': display_name,
                                'file_path': str(image_file),
                                'file_name': image_file.name,
                                'folder': folder_name,
                                'size': image_file.stat().st_size,
                                'modified': image_file.stat().st_mtime
                            })

            # Sort by modification time (newest first)
            new_gallery_images.sort(key=lambda x: x['modified'], reverse=True)

            # Check if anything actually changed (avoid unnecessary refresh)
            if preserve_selection and len(new_gallery_images) == len(self.gallery_images):
                # Quick check: same number of files with same paths
                old_paths = [img['file_path'] for img in self.gallery_images]
                new_paths = [img['file_path'] for img in new_gallery_images]
                if old_paths == new_paths:
                    # No changes, skip refresh to avoid disrupting user
                    return

            # Update gallery_images
            self.gallery_images = new_gallery_images
            print(f"[DEBUG] Gallery refresh found {len(self.gallery_images)} images")

            # Refresh listbox with new items
            self.file_listbox.delete(0, tk.END)
            for img_info in self.gallery_images:
                self.file_listbox.insert(tk.END, img_info['display_name'])

            # Restore selection if preserving
            if preserve_selection and selected_file_path:
                # Find the same file in the new list
                for i, img_info in enumerate(self.gallery_images):
                    if img_info['file_path'] == selected_file_path:
                        self.file_listbox.select_set(i)
                        self.file_listbox.see(i)  # Ensure it's visible
                        break

            # Update header with count
            count = len(self.gallery_images)
            self.image_header_label.config(text=f"🖼️ IMAGE VIEWER ({count} images)")

        except Exception as e:
            print(f"[ERROR] Gallery refresh failed: {e}")

    def schedule_gallery_refresh(self):
        """Schedule automatic gallery refresh"""
        # Refresh every 10 seconds to catch new generations (less disruptive)
        self.root.after(10000, self.auto_refresh_gallery)

    def auto_refresh_gallery(self):
        """Auto-refresh gallery and reschedule"""
        self.refresh_gallery(preserve_selection=True)
        self.schedule_gallery_refresh()

    def on_file_select(self, event):
        """Handle file selection from listbox"""
        try:
            selection = self.file_listbox.curselection()
            print(f"[DEBUG] File selection event triggered, selection: {selection}")

            if selection:
                index = selection[0]
                print(f"[DEBUG] Selected index: {index}, total images: {len(self.gallery_images)}")

                if index < len(self.gallery_images):
                    img_info = self.gallery_images[index]
                    print(f"[DEBUG] Attempting to display: {img_info['display_name']}")
                    self.display_image(img_info)
                else:
                    print(f"[WARNING] Index {index} out of range for {len(self.gallery_images)} images")
            else:
                print(f"[DEBUG] No file selected")

        except Exception as e:
            print(f"[ERROR] File selection failed: {e}")
            import traceback
            traceback.print_exc()

    def display_image(self, img_info):
        """Display the selected image in the viewer"""
        try:
            from PIL import Image, ImageTk
            import os

            file_path = img_info['file_path']
            print(f"[DEBUG] Attempting to display image: {file_path}")

            if not os.path.exists(file_path):
                error_msg = f"❌ Image file not found: {file_path}"
                print(f"[ERROR] {error_msg}")
                self.image_info_label.config(text=error_msg)
                return

            # Load and display image
            pil_image = Image.open(file_path)
            original_width, original_height = pil_image.size
            print(f"[DEBUG] Original image size: {original_width}x{original_height}")

            # Calculate display size (max 750x550 to fit in 800x600 canvas with padding)
            max_width, max_height = 750, 550

            ratio = min(max_width/original_width, max_height/original_height)
            if ratio < 1:
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                display_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"[DEBUG] Resized image to: {new_width}x{new_height}")
            else:
                display_image = pil_image
                new_width, new_height = original_width, original_height
                print(f"[DEBUG] Using original size: {new_width}x{new_height}")

            # Convert to PhotoImage and maintain reference
            self.current_photo = ImageTk.PhotoImage(display_image)
            print(f"[DEBUG] PhotoImage created successfully")

            # Clear canvas
            self.image_canvas.delete("all")

            # Center the image in the canvas
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()

            # If canvas hasn't been drawn yet, use the configured size
            if canvas_width <= 1:
                canvas_width = 800
            if canvas_height <= 1:
                canvas_height = 600

            x_center = canvas_width // 2
            y_center = canvas_height // 2

            # Place image at center
            self.image_canvas.create_image(x_center, y_center, anchor="center", image=self.current_photo)
            print(f"[DEBUG] Image placed at canvas center: ({x_center}, {y_center})")

            # Update canvas scroll region to accommodate the image
            bbox = self.image_canvas.bbox("all")
            if bbox:
                self.image_canvas.configure(scrollregion=bbox)
                print(f"[DEBUG] Canvas scroll region set to: {bbox}")

            # Update info label
            size_mb = img_info['size'] / (1024 * 1024)
            info_text = f"📏 {original_width}x{original_height} | 💾 {size_mb:.1f}MB | 📁 {img_info['folder']}"
            self.image_info_label.config(text=info_text)
            print(f"[DEBUG] Info updated: {info_text}")

            self.current_image_path = file_path
            print(f"[SUCCESS] Image displayed successfully: {os.path.basename(file_path)}")

        except Exception as e:
            error_msg = f"❌ Failed to load image: {str(e)}"
            print(f"[ERROR] Image display failed: {e}")
            import traceback
            traceback.print_exc()
            self.image_info_label.config(text=error_msg)

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling on image canvas"""
        if event.delta:
            self.image_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.image_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.image_canvas.yview_scroll(1, "units")

    def show_context_menu(self, event):
        """Show right-click context menu for file operations"""
        try:
            # Check if we have any images
            if not hasattr(self, 'gallery_images') or not self.gallery_images:
                # Show simple context menu to refresh
                context_menu = tk.Menu(self.root, tearoff=0, bg=SynthwaveColors.SECONDARY, fg=SynthwaveColors.TEXT)
                context_menu.add_command(
                    label="🔄 Refresh Gallery",
                    command=self.refresh_gallery
                )
                context_menu.post(event.x_root, event.y_root)
                return

            # Get selected item
            index = self.file_listbox.nearest(event.y)

            if index >= 0 and index < len(self.gallery_images):
                self.file_listbox.select_clear(0, tk.END)
                self.file_listbox.select_set(index)

                img_info = self.gallery_images[index]

                # Create context menu
                context_menu = tk.Menu(self.root, tearoff=0, bg=SynthwaveColors.SECONDARY, fg=SynthwaveColors.TEXT)

                context_menu.add_command(
                    label="🔍 Open With...",
                    command=lambda: self.open_with_dialog(img_info['file_path'])
                )
                context_menu.add_command(
                    label="🎨 Open with GIMP",
                    command=lambda: self.open_with_gimp(img_info['file_path'])
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="📂 Show in Finder/Explorer",
                    command=lambda: self.show_in_finder(img_info['file_path'])
                )
                context_menu.add_separator()
                context_menu.add_command(
                    label="📋 Copy Path",
                    command=lambda: self.copy_to_clipboard(img_info['file_path'])
                )
                context_menu.add_command(
                    label="ℹ️ Properties",
                    command=lambda: self.show_file_properties(img_info)
                )

                # Show menu at cursor
                context_menu.post(event.x_root, event.y_root)

        except Exception as e:
            print(f"[ERROR] Context menu failed: {e}")

    def open_with_dialog(self, file_path):
        """Open 'Open With' dialog for the selected file"""
        try:
            import subprocess
            import sys
            import os

            if sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', '-a', 'Preview', file_path])
            elif sys.platform.startswith('win'):   # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.run(['xdg-open', file_path])

        except Exception as e:
            print(f"[ERROR] Open with failed: {e}")
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def open_with_gimp(self, file_path):
        """Launch GIMP with the selected image file"""
        try:
            import subprocess
            import sys
            import os
            from pathlib import Path

            # Common GIMP executable names and paths by platform
            gimp_paths = []

            if sys.platform.startswith('darwin'):  # macOS
                gimp_paths = [
                    '/Volumes/Tikbalang2TB/Apps2/GIMP.app/Contents/MacOS/GIMP',
                    '/Volumes/Tikbalang2TB/Apps2/GIMP-2.10.app/Contents/MacOS/GIMP',
                    '/Applications/GIMP.app/Contents/MacOS/GIMP',
                    '/Applications/GIMP-2.10.app/Contents/MacOS/GIMP',
                    '/usr/local/bin/gimp',
                    'gimp'
                ]
            elif sys.platform.startswith('win'):   # Windows
                gimp_paths = [
                    'C:\\Program Files\\GIMP 2\\bin\\gimp-2.10.exe',
                    'C:\\Program Files (x86)\\GIMP 2\\bin\\gimp-2.10.exe',
                    'C:\\Program Files\\GIMP\\bin\\gimp.exe',
                    'C:\\Program Files (x86)\\GIMP\\bin\\gimp.exe',
                    'gimp'
                ]
            else:  # Linux
                gimp_paths = [
                    '/usr/bin/gimp',
                    '/usr/local/bin/gimp',
                    '/snap/bin/gimp',
                    '/usr/bin/gimp-2.10',
                    'gimp'
                ]

            # Try to find and launch GIMP (non-blocking)
            gimp_found = False
            for gimp_path in gimp_paths:
                try:
                    if gimp_path == 'gimp':
                        # Try system PATH - launch in background
                        subprocess.Popen([gimp_path, file_path], cwd=str(Path.home()))
                        gimp_found = True
                        print(f"[INFO] Launched GIMP from PATH: {file_path}")
                        break
                    elif Path(gimp_path).exists():
                        # Try specific path - launch in background
                        subprocess.Popen([gimp_path, file_path], cwd=str(Path.home()))
                        gimp_found = True
                        print(f"[INFO] Launched GIMP from {gimp_path}: {file_path}")
                        break
                except (subprocess.SubprocessError, FileNotFoundError, OSError):
                    continue

            if not gimp_found:
                # If GIMP not found, show helpful error message
                error_msg = f"""GIMP not found on your system.

Please install GIMP from: https://www.gimp.org/downloads/

Common installation locations:
• macOS: /Applications/GIMP.app
• Windows: C:\\Program Files\\GIMP 2\\
• Linux: /usr/bin/gimp

Or ensure GIMP is in your system PATH."""

                messagebox.showwarning("GIMP Not Found", error_msg)
                print(f"[WARNING] GIMP not found. Checked paths: {gimp_paths}")

        except Exception as e:
            print(f"[ERROR] GIMP launch failed: {e}")
            messagebox.showerror("Error", f"Failed to launch GIMP: {str(e)}")

    def show_in_finder(self, file_path):
        """Show file in Finder/Explorer"""
        try:
            import subprocess
            import sys
            import os

            if sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', '-R', file_path])
            elif sys.platform.startswith('win'):   # Windows
                subprocess.run(['explorer', '/select,', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', os.path.dirname(file_path)])

        except Exception as e:
            print(f"[ERROR] Show in finder failed: {e}")

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            print(f"[INFO] Copied to clipboard: {text}")
        except Exception as e:
            print(f"[ERROR] Clipboard copy failed: {e}")

    def show_file_properties(self, img_info):
        """Show file properties dialog"""
        try:
            import datetime

            # Format file size
            size_bytes = img_info['size']
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024*1024:
                size_str = f"{size_bytes/1024:.1f} KB"
            else:
                size_str = f"{size_bytes/(1024*1024):.1f} MB"

            # Format modification time
            mod_time = datetime.datetime.fromtimestamp(img_info['modified'])
            mod_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")

            # Show properties
            properties = f"""File Properties:

Name: {img_info['file_name']}
Folder: {img_info['folder']}
Path: {img_info['file_path']}
Size: {size_str}
Modified: {mod_str}"""

            messagebox.showinfo("File Properties", properties)

        except Exception as e:
            print(f"[ERROR] Properties dialog failed: {e}")

    def refresh_available_models(self):
        """Refresh the list of available models from LMStudio API"""
        try:
            self.model_status_label.config(text="Status: Loading models...", fg=SynthwaveColors.WARNING)
            self.root.update_idletasks()

            # Import lmstudio to get available models
            import lmstudio as lms

            # Get list of downloaded models
            downloaded_models = lms.list_downloaded_models()

            if downloaded_models:
                # Extract model keys/names
                model_names = []
                for model in downloaded_models:
                    # Handle different possible formats from the API
                    if isinstance(model, dict):
                        model_key = model.get('key', model.get('name', str(model)))
                    else:
                        # Try to extract model_key attribute if it exists (for DownloadedLlm objects)
                        if hasattr(model, 'model_key'):
                            model_key = model.model_key
                        else:
                            model_key = str(model)
                    model_names.append(model_key)

                # Update available models
                self.available_models = model_names
                self.model_combobox['values'] = self.available_models

                # Set current selection to fallback model if it exists in the list
                fallback_model = self.current_model_var.get()
                if fallback_model in self.available_models:
                    self.model_combobox.set(fallback_model)
                elif self.available_models:
                    # If fallback not available, use first available model
                    self.model_combobox.set(self.available_models[0])

                self.model_status_label.config(
                    text=f"Status: Found {len(self.available_models)} available models",
                    fg=SynthwaveColors.SUCCESS
                )
                print(f"[INFO] Loaded {len(self.available_models)} available models")

            else:
                self.available_models = []
                self.model_combobox['values'] = []
                self.model_status_label.config(
                    text="Status: No models found in LMStudio",
                    fg=SynthwaveColors.ERROR
                )
                print("[WARNING] No models found in LMStudio")

        except ImportError:
            self.model_status_label.config(
                text="Status: LMStudio not available (lmstudio package not found)",
                fg=SynthwaveColors.ERROR
            )
            print("[ERROR] lmstudio package not found. Please install: pip install lmstudio")

        except Exception as e:
            self.model_status_label.config(
                text=f"Status: Error loading models - {str(e)}",
                fg=SynthwaveColors.ERROR
            )
            print(f"[ERROR] Failed to refresh models: {e}")

    def load_selected_model(self):
        """Load the selected model in LMStudio"""
        try:
            selected_model = self.model_combobox.get()
            if not selected_model:
                self.model_status_label.config(
                    text="Status: No model selected",
                    fg=SynthwaveColors.WARNING
                )
                return

            # Set loading state
            self.set_model_state(ModelState.LOADING, f"Loading {selected_model}...")
            self.root.update_idletasks()

            # Import lmstudio to load the model
            import lmstudio as lms

            # Load the new model instance
            print(f"[INFO] Loading model: {selected_model}")
            model_instance = lms.llm(selected_model)

            # Store the model instance
            self.current_model_instance = model_instance

            # Update the current model display
            self.current_model_var.set(selected_model)

            # Update the transformer to use the new model instance
            if self.llm_transformer:
                self.llm_transformer.update_model(model_instance, selected_model)
                print(f"[INFO] Updated transformer with new model: {selected_model}")
            else:
                # Create new transformer with the model instance
                self.llm_transformer = TShirtPromptTransformer(model_instance=model_instance)
                print(f"[INFO] Created new transformer with model: {selected_model}")

            # Set loaded state
            self.set_model_state(ModelState.LOADED, f"Successfully loaded {selected_model}")

            print(f"[SUCCESS] Model loaded and transformer updated: {selected_model}")

        except ImportError:
            self.set_model_state(ModelState.FAILED, "LMStudio not available")
            print("[ERROR] lmstudio package not found")

            self.show_user_notification(
                "LMStudio Not Available",
                "LMStudio package not found. Please install it with:\npip install lmstudio",
                "error"
            )

        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Failed to load model {selected_model}: {e}")

            # Check if this is a recoverable error and attempt fallback
            if any(keyword in error_msg.lower() for keyword in ['model not found', 'connection', 'timeout', 'network']):
                print(f"[ERROR RECOVERY] Detected recoverable error, attempting fallback...")

                if not self.attempt_fallback_model():
                    # Fallback also failed
                    self.set_model_state(ModelState.FAILED, f"Failed to load {selected_model} and fallback failed")
            else:
                # Non-recoverable error
                self.set_model_state(ModelState.FAILED, f"Failed to load {selected_model} - {error_msg}")
                self.show_user_notification(
                    "Model Load Error",
                    f"Failed to load model: {selected_model}\nError: {error_msg}",
                    "error"
                )

    def set_model_state(self, state, message=None):
        """Update model state and display status

        Args:
            state: ModelState constant
            message: Optional custom message for status display
        """
        self.current_model_state = state

        # Update status display based on state
        if hasattr(self, 'model_status_label'):
            if message:
                status_text = f"Status: {message}"
            else:
                status_text = f"Status: {state.title()}"

            # Set color based on state
            if state == ModelState.LOADED:
                color = SynthwaveColors.SUCCESS
            elif state in [ModelState.LOADING, ModelState.RECONNECTING]:
                color = SynthwaveColors.WARNING
            elif state == ModelState.FAILED:
                color = SynthwaveColors.ERROR
            elif state == ModelState.ACTIVE:
                color = SynthwaveColors.NEON_CYAN
            else:
                color = SynthwaveColors.TEXT

            self.model_status_label.config(text=status_text, fg=color)

        print(f"[MODEL STATE] {state}: {message or 'State changed'}")

    def validate_model_health(self):
        """Perform health check on current model

        Returns:
            bool: True if model is healthy, False otherwise
        """
        if self.current_model_state == ModelState.UNLOADED:
            print("[MODEL HEALTH] No model loaded")
            return False

        if not self.current_model_instance:
            print("[MODEL HEALTH] No model instance available")
            self.set_model_state(ModelState.FAILED, "Model instance lost")
            return False

        try:
            if self.llm_transformer and hasattr(self.llm_transformer, 'validate_model'):
                is_valid = self.llm_transformer.validate_model()
                if not is_valid:
                    self.set_model_state(ModelState.FAILED, "Model validation failed")
                    return False
                else:
                    print("[MODEL HEALTH] Model validation passed")
                    return True
            else:
                print("[MODEL HEALTH] No transformer available for validation")
                return False
        except Exception as e:
            print(f"[MODEL HEALTH] Health check failed: {e}")
            self.set_model_state(ModelState.FAILED, f"Health check failed: {str(e)}")
            return False

    def cleanup_model_resources(self):
        """Clean up model resources after use"""
        try:
            if self.current_model_state == ModelState.ACTIVE:
                # Set back to loaded state after use
                self.set_model_state(ModelState.LOADED, "Model ready for next use")
                print("[MODEL LIFECYCLE] Model returned to ready state")

            # Note: We don't actually delete the model instance as it may be reused
            # Just mark it as no longer active
        except Exception as e:
            print(f"[MODEL LIFECYCLE] Cleanup warning: {e}")

    def refresh_model_connection(self):
        """Attempt to refresh/reconnect model if needed

        Returns:
            bool: True if model is ready, False if failed
        """
        try:
            # Check if we have a valid model
            if self.validate_model_health():
                return True

            # If validation failed, try to reconnect
            if self.llm_transformer and hasattr(self.llm_transformer, 'reconnect_model'):
                self.set_model_state(ModelState.RECONNECTING, "Attempting to reconnect model...")

                if self.llm_transformer.reconnect_model():
                    self.set_model_state(ModelState.LOADED, "Model reconnected successfully")
                    return True
                else:
                    self.set_model_state(ModelState.FAILED, "Model reconnection failed")
                    return False
            else:
                print("[MODEL REFRESH] No reconnection method available")
                return False

        except Exception as e:
            print(f"[MODEL REFRESH] Failed to refresh model connection: {e}")
            self.set_model_state(ModelState.FAILED, f"Refresh failed: {str(e)}")
            return False

    def attempt_fallback_model(self):
        """Attempt to load fallback model when selected model fails

        Returns:
            bool: True if fallback successful, False otherwise
        """
        try:
            if not self.default_fallback_model:
                print("[FALLBACK] No default fallback model configured")
                return False

            print(f"[FALLBACK] Attempting to load fallback model: {self.default_fallback_model}")
            self.set_model_state(ModelState.LOADING, f"Loading fallback model: {self.default_fallback_model}")

            # Import lmstudio to load the fallback model
            import lmstudio as lms

            # Load the fallback model instance
            fallback_instance = lms.llm(self.default_fallback_model)

            # Store the model instance
            self.current_model_instance = fallback_instance

            # Update the transformer to use the fallback model
            if self.llm_transformer:
                self.llm_transformer.update_model(fallback_instance, self.default_fallback_model)
            else:
                # Create new transformer with the fallback model
                self.llm_transformer = TShirtPromptTransformer(model_instance=fallback_instance)

            # Update the current model display to show fallback
            self.current_model_var.set(f"{self.default_fallback_model} (fallback)")

            # Set loaded state with fallback indication
            self.set_model_state(ModelState.LOADED, f"Fallback model loaded: {self.default_fallback_model}")

            print(f"[FALLBACK] Successfully loaded fallback model: {self.default_fallback_model}")

            # Show user notification about fallback
            self.show_user_notification(
                "Model Fallback",
                f"Selected model failed to load. Using fallback model:\n{self.default_fallback_model}",
                "warning"
            )

            return True

        except Exception as e:
            print(f"[FALLBACK] Failed to load fallback model: {e}")
            self.set_model_state(ModelState.FAILED, f"Fallback model failed: {str(e)}")

            # Show error notification
            self.show_user_notification(
                "Model Error",
                f"Both selected and fallback models failed to load.\nPlease check LMStudio status.",
                "error"
            )

            return False

    def show_user_notification(self, title, message, type="info"):
        """Show user notification with model state information

        Args:
            title: Notification title
            message: Notification message
            type: Notification type ("info", "warning", "error")
        """
        try:
            # Log to console
            print(f"[USER NOTIFICATION] {title}: {message}")

            # Log to scan results for user visibility
            if hasattr(self, 'write_to_scan_results'):
                icon = "ℹ️" if type == "info" else "⚠️" if type == "warning" else "❌"
                self.write_to_scan_results(f"{icon} {title}: {message}")

            # Show message box for important notifications
            if type == "error":
                messagebox.showerror(title, message)
            elif type == "warning":
                messagebox.showwarning(title, message)
            else:
                messagebox.showinfo(title, message)

        except Exception as e:
            print(f"[ERROR] Failed to show user notification: {e}")

    def enhanced_model_error_recovery(self, error_context="unknown"):
        """Enhanced error recovery with multiple fallback strategies

        Args:
            error_context: Context where the error occurred

        Returns:
            bool: True if recovery successful, False otherwise
        """
        print(f"[ERROR RECOVERY] Starting recovery for context: {error_context}")

        # Strategy 1: Try to refresh current model connection
        if self.refresh_model_connection():
            print("[ERROR RECOVERY] Recovery successful via model refresh")
            self.show_user_notification(
                "Model Recovery",
                "Model connection restored successfully.",
                "info"
            )
            return True

        # Strategy 2: Try fallback model
        if self.attempt_fallback_model():
            print("[ERROR RECOVERY] Recovery successful via fallback model")
            return True

        # Strategy 3: Reset to clean state and notify user
        print("[ERROR RECOVERY] All recovery strategies failed")
        self.set_model_state(ModelState.FAILED, "All recovery attempts failed")

        self.show_user_notification(
            "Model Recovery Failed",
            "Unable to recover model connection. Please:\n"
            "1. Check that LMStudio is running\n"
            "2. Verify models are available\n"
            "3. Try manually loading a model",
            "error"
        )

        return False


def main():
    """Main entry point"""
    app = SynthwaveGUI()


if __name__ == "__main__":
    main()