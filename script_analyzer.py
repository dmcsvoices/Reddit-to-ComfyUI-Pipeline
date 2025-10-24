"""
ComfyUI Script Analyzer
Intelligently detects prompt arguments in imported ComfyUI scripts
"""

import ast
import re
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class ArgumentInfo:
    """Information about a script argument"""
    name: str
    dest: str  # The actual argument name without dashes
    default: Any
    help_text: str
    arg_type: str  # 'str', 'int', 'float', etc.
    score: float  # Confidence score for being a prompt argument


@dataclass
class PromptMapping:
    """Mapping of prompt types to argument names"""
    main_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    steps: Optional[str] = None
    seed: Optional[str] = None


class ComfyUIScriptAnalyzer:
    """Analyzes ComfyUI scripts to detect argument patterns"""

    def __init__(self):
        self.config_dir = Path("script_configs")
        self.config_dir.mkdir(exist_ok=True)

    def analyze_script(self, script_path: str) -> Tuple[List[ArgumentInfo], PromptMapping]:
        """
        Analyze a ComfyUI script to detect arguments and suggest prompt mappings

        Returns:
            Tuple of (all_arguments, suggested_mapping)
        """
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the script for argument definitions
            arguments = self._parse_arguments(content)

            # Score arguments and suggest prompt mapping
            suggested_mapping = self._suggest_prompt_mapping(arguments)

            return arguments, suggested_mapping

        except Exception as e:
            print(f"Error analyzing script {script_path}: {e}")
            return [], PromptMapping()

    def _parse_arguments(self, content: str) -> List[ArgumentInfo]:
        """Parse add_argument calls from script content"""
        arguments = []

        # Improved regex to find complete add_argument calls including multiline strings
        # This pattern captures the full argument block by finding the opening parenthesis
        # and matching to the corresponding closing parenthesis
        pattern = r'parser\.add_argument\(\s*([^)]+)\)'

        # Find each add_argument call
        pos = 0
        while True:
            start_match = re.search(r'parser\.add_argument\(', content[pos:])
            if not start_match:
                break

            start_pos = pos + start_match.start()
            paren_pos = pos + start_match.end() - 1  # Position of opening parenthesis

            # Find the matching closing parenthesis
            paren_count = 1
            i = paren_pos + 1
            while i < len(content) and paren_count > 0:
                if content[i] == '(':
                    paren_count += 1
                elif content[i] == ')':
                    paren_count -= 1
                i += 1

            if paren_count == 0:
                # Extract the complete argument call
                full_call = content[start_pos:i]
                arg_info = self._parse_full_argument_call(full_call)
                if arg_info:
                    arguments.append(arg_info)

            pos = i

        return arguments

    def _parse_full_argument_call(self, full_call: str) -> Optional[ArgumentInfo]:
        """Parse a complete add_argument call"""
        try:
            # Extract argument name (first parameter)
            arg_name_match = re.search(r'parser\.add_argument\(\s*["\']([^"\']+)["\']', full_call)
            if not arg_name_match:
                return None

            arg_name = arg_name_match.group(1)
            dest = arg_name.lstrip('-')

            # Initialize defaults
            default = None
            help_text = ""
            arg_type = "str"

            # Extract default value - handle multiline strings
            default_match = re.search(r'default\s*=\s*([\'"][^\'\"]*[\'"]|[\']{3}.*?[\']{3}|[\"]{3}.*?[\"]{3})',
                                    full_call, re.DOTALL)
            if default_match:
                default_str = default_match.group(1)
                try:
                    # Try to evaluate as Python literal
                    default = ast.literal_eval(default_str)
                except:
                    # If it fails, strip quotes manually
                    if default_str.startswith('"""') or default_str.startswith("'''"):
                        default = default_str[3:-3]
                    elif default_str.startswith('"') or default_str.startswith("'"):
                        default = default_str[1:-1]
                    else:
                        default = default_str

            # Extract help text
            help_match = re.search(r'help\s*=\s*["\']([^"\']*)["\']', full_call, re.DOTALL)
            if help_match:
                help_text = help_match.group(1)

            # Infer type from default or parameter
            if isinstance(default, int):
                arg_type = "int"
            elif isinstance(default, float):
                arg_type = "float"
            elif isinstance(default, bool):
                arg_type = "bool"

            # Score this argument for prompt likelihood
            score = self._score_argument(dest, default, help_text)

            return ArgumentInfo(
                name=arg_name,
                dest=dest,
                default=default,
                help_text=help_text,
                arg_type=arg_type,
                score=score
            )

        except Exception as e:
            print(f"Error parsing argument call: {e}")
            return None


    def _score_argument(self, dest: str, default: Any, help_text: str) -> float:
        """Score an argument for likelihood of being a prompt"""
        score = 0.0

        # Name-based scoring
        if 'text' in dest.lower():
            score += 0.4
        if 'prompt' in dest.lower():
            score += 0.5
        if 'positive' in dest.lower():
            score += 0.3
        if 'negative' in dest.lower():
            score += 0.2

        # Help text scoring
        if help_text:
            help_lower = help_text.lower()
            if 'clip text encode' in help_lower:
                score += 0.3
            if 'positive prompt' in help_lower:
                score += 0.4
            if 'negative prompt' in help_lower:
                score += 0.3
            if 'prompt' in help_lower:
                score += 0.2

        # Default value scoring
        if isinstance(default, str):
            if len(default) > 50:  # Long defaults likely main prompts
                score += 0.3
            elif len(default) == 0:  # Empty defaults likely negative prompts
                score += 0.1

        return min(score, 1.0)  # Cap at 1.0

    def _suggest_prompt_mapping(self, arguments: List[ArgumentInfo]) -> PromptMapping:
        """Suggest prompt mapping based on argument analysis"""
        # Find prompt-related arguments (text or prompt in name)
        prompt_args = [arg for arg in arguments if
                      'text' in arg.dest.lower() or 'prompt' in arg.dest.lower()]
        prompt_args.sort(key=lambda x: x.score, reverse=True)

        mapping = PromptMapping()

        # First pass: look for explicit prompt names
        for arg in prompt_args:
            if 'main_prompt' in arg.dest.lower() or 'positive_prompt' in arg.dest.lower():
                mapping.main_prompt = arg.dest
            elif 'negative_prompt' in arg.dest.lower() or 'neg_prompt' in arg.dest.lower():
                mapping.negative_prompt = arg.dest

        # Second pass: if not found, use scoring for text arguments
        if not mapping.main_prompt and prompt_args:
            # Find main prompt (highest scoring with substantial default)
            for arg in prompt_args:
                if (arg.score > 0.3 and
                    isinstance(arg.default, str) and
                    len(arg.default) > 20):
                    mapping.main_prompt = arg.dest
                    break

        # Third pass: find negative prompt
        if not mapping.negative_prompt and prompt_args:
            # Find negative prompt (empty default or "negative" in name/help)
            for arg in prompt_args:
                if (arg.dest != mapping.main_prompt and
                    ('negative' in arg.dest.lower() or
                     (isinstance(arg.default, str) and len(arg.default) == 0) or
                     'negative' in arg.help_text.lower())):
                    mapping.negative_prompt = arg.dest
                    break

        # Find other common arguments
        for arg in arguments:
            if 'width' in arg.dest.lower() and arg.arg_type in ['int', 'float']:
                mapping.width = arg.dest
            elif 'height' in arg.dest.lower() and arg.arg_type in ['int', 'float']:
                mapping.height = arg.dest
            elif 'steps' in arg.dest.lower() and arg.arg_type == 'int':
                mapping.steps = arg.dest
            elif 'seed' in arg.dest.lower() and arg.arg_type == 'int':
                mapping.seed = arg.dest

        return mapping

    def save_mapping(self, script_name: str, mapping: PromptMapping) -> None:
        """Save prompt mapping configuration for a script"""
        config_file = self.config_dir / f"{script_name}.json"

        mapping_dict = {
            'main_prompt': mapping.main_prompt,
            'negative_prompt': mapping.negative_prompt,
            'width': mapping.width,
            'height': mapping.height,
            'steps': mapping.steps,
            'seed': mapping.seed
        }

        with open(config_file, 'w') as f:
            json.dump(mapping_dict, f, indent=2)

    def load_mapping(self, script_name: str) -> Optional[PromptMapping]:
        """Load saved prompt mapping for a script"""
        config_file = self.config_dir / f"{script_name}.json"

        if not config_file.exists():
            return None

        try:
            with open(config_file, 'r') as f:
                data = json.load(f)

            return PromptMapping(
                main_prompt=data.get('main_prompt'),
                negative_prompt=data.get('negative_prompt'),
                width=data.get('width'),
                height=data.get('height'),
                steps=data.get('steps'),
                seed=data.get('seed')
            )
        except Exception as e:
            print(f"Error loading mapping for {script_name}: {e}")
            return None

    def get_execution_args(self, script_name: str, prompt_text: str,
                          negative_prompt: str = "", **kwargs) -> Dict[str, Any]:
        """
        Get execution arguments for a script based on saved mapping

        Args:
            script_name: Name of the script
            prompt_text: Main prompt text
            negative_prompt: Negative prompt text
            **kwargs: Additional arguments (width, height, steps, seed, etc.)

        Returns:
            Dictionary of argument names to values
        """
        mapping = self.load_mapping(script_name)
        if not mapping:
            # Fallback to default naming
            return {
                'text4': prompt_text,  # Common default
                'text5': negative_prompt,
                **kwargs
            }

        args = {}

        if mapping.main_prompt:
            args[mapping.main_prompt] = prompt_text

        if mapping.negative_prompt:
            args[mapping.negative_prompt] = negative_prompt

        # Add other mapped arguments if provided
        for key, value in kwargs.items():
            if key == 'width' and mapping.width:
                args[mapping.width] = value
            elif key == 'height' and mapping.height:
                args[mapping.height] = value
            elif key == 'steps' and mapping.steps:
                args[mapping.steps] = value
            elif key == 'seed' and mapping.seed:
                args[mapping.seed] = value
            else:
                # Pass through unmapped arguments
                args[key] = value

        return args


# Convenience functions for easy integration
def analyze_comfyui_script(script_path: str) -> Tuple[List[ArgumentInfo], PromptMapping]:
    """Analyze a ComfyUI script and return argument info and suggested mapping"""
    analyzer = ComfyUIScriptAnalyzer()
    return analyzer.analyze_script(script_path)


def get_script_execution_args(script_name: str, prompt_text: str, **kwargs) -> Dict[str, Any]:
    """Get execution arguments for a script"""
    analyzer = ComfyUIScriptAnalyzer()
    return analyzer.get_execution_args(script_name, prompt_text, **kwargs)