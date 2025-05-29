#!/usr/bin/env python3
"""
dreamnet - A dynamic symbolic generator

Refactored to be configuration-driven, modular, and efficient.
"""

import json
import subprocess
import sys
import os
from datetime import datetime
import re
import random
from pathlib import Path


class DreamConfig:
    """Configuration manager for Dreamnet"""
    
    def __init__(self, config_path=None):
        self.script_dir = Path(__file__).parent
        self.config_path = config_path or self.script_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def get(self, *keys, default=None):
        """Get nested configuration value"""
        current = self.config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current


class SymbolEngine:
    """Dynamic symbol and color selection engine"""
    
    def __init__(self, config):
        self.config = config
        self._symbol_cache = {}
        self._color_cache = {}
    
    def get_symbols_for_theme(self, theme_name):
        """Get symbols for a specific theme"""
        if theme_name in self._symbol_cache:
            return self._symbol_cache[theme_name]
        
        theme = self.config.get('themes', theme_name, default={})
        symbol_pools = theme.get('symbols', ['cosmic'])
        
        symbols = []
        for pool_name in symbol_pools:
            pool_chars = self.config.get('symbols', 'base_pools', pool_name, default="")
            symbols.extend(list(pool_chars))
        
        # Cache and return
        self._symbol_cache[theme_name] = symbols
        return symbols
    
    def get_colors_for_theme(self, theme_name):
        """Get colors for a specific theme"""
        if theme_name in self._color_cache:
            return self._color_cache[theme_name]
        
        theme = self.config.get('themes', theme_name, default={})
        color_palettes = theme.get('colors', ['cosmic'])
        
        colors = []
        for palette_name in color_palettes:
            palette = self.config.get('colors', 'base_palettes', palette_name, default=[])
            colors.extend(palette)
        
        # Cache and return
        self._color_cache[theme_name] = colors
        return colors
    
    def detect_theme(self, intent):
        """Detect theme from intent text"""
        intent_lower = intent.lower()
        
        # Score themes based on keyword matches
        theme_scores = {}
        for theme_name, theme_data in self.config.get('themes', default={}).items():
            keywords = theme_data.get('keywords', [])
            score = sum(1 for keyword in keywords if keyword in intent_lower)
            if score > 0:
                theme_scores[theme_name] = score
        
        # Return highest scoring theme or default
        if theme_scores:
            return max(theme_scores.items(), key=lambda x: x[1])[0]
        return 'wisdom'  # Default theme
    
    def select_symbol_and_color(self, intent):
        """Select symbol and color based on intent"""
        theme = self.detect_theme(intent)
        
        symbols = self.get_symbols_for_theme(theme)
        colors = self.get_colors_for_theme(theme)
        
        # Fallback to config defaults if empty
        if not symbols:
            symbols = list(self.config.get('symbols', 'fallback', default="∞"))
        if not colors:
            colors = [self.config.get('colors', 'fallback', default="#7f8c8d")]
        
        return random.choice(symbols), random.choice(colors), theme


class PromptGenerator:
    """Dynamic prompt generation"""
    
    def __init__(self, config):
        self.config = config
    
    def create_prompt(self, intent, style):
        """Create dynamic prompt from template"""
        base_template = self.config.get('prompts', 'base_template', default="")
        variations = self.config.get('prompts', 'variations', default=[])
        
        # Add variation if available
        if variations:
            variation = random.choice(variations)
            prompt = f"{variation}\n\n{base_template}"
        else:
            prompt = base_template
        
        return prompt.format(intent=intent, style=style)


class DreamAgent:
    """Main Dreamnet agent - now much simpler and configuration-driven"""
    
    def __init__(self, config_path=None):
        self.config = DreamConfig(config_path)
        self.symbol_engine = SymbolEngine(self.config)
        self.prompt_generator = PromptGenerator(self.config)
        
        # Setup paths
        self.script_dir = Path(__file__).parent
        self.brain_file = self.script_dir / "brain.json"
        self.output_file = self.script_dir / "output.json"
        self.logs_dir = self.script_dir / "logs"
        self.echoes_dir = self.script_dir / "echoes"
        
        # Create directories
        self.logs_dir.mkdir(exist_ok=True)
        self.echoes_dir.mkdir(exist_ok=True)
    
    def load_brain(self):
        """Load intent and style from brain.json"""
        try:
            with open(self.brain_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.brain_file} not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.brain_file}")
            sys.exit(1)
    
    def extract_concept(self, intent):
        """Extract main concept for echo file naming"""
        # Simple approach: look for theme keywords
        for theme_name, theme_data in self.config.get('themes', default={}).items():
            keywords = theme_data.get('keywords', [])
            if any(keyword in intent.lower() for keyword in keywords):
                return theme_name
        
        # Fallback: extract longest meaningful word
        words = re.findall(r'\b\w{4,}\b', intent.lower())
        stop_words = {'this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'explore', 'essence'}
        meaningful_words = [w for w in words if w not in stop_words]
        
        return meaningful_words[0] if meaningful_words else "dream"
    
    def call_ollama(self, prompt):
        """Call Ollama model"""
        try:
            model_name = self.config.get('model', 'name', default='qwen3:1.7b')
            timeout = self.config.get('model', 'timeout', default=60)
            
            cmd = ["ollama", "run", model_name, prompt]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            
            return result.stdout.strip() if result.returncode == 0 else None
                
        except subprocess.TimeoutExpired:
            print("Ollama call timed out")
            return None
        except FileNotFoundError:
            print("Error: Ollama not found. Please ensure Ollama is installed and in PATH")
            return None
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None
    
    def parse_response(self, response):
        """Parse model response and extract JSON"""
        if not response:
            return None
            
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        return None
    
    def get_fallback(self, intent):
        """Get enhanced fallback response"""
        fallbacks = self.config.get('fallbacks', default=[])
        if not fallbacks:
            # Ultimate fallback
            return {
                "symbol": "∞",
                "phrase": "The dream continues beyond understanding.",
                "color": "#7f8c8d",
                "reasoning": "When symbols fail, the infinite persists."
            }
        
        fallback = random.choice(fallbacks).copy()
        
        # Enhance with theme-specific symbol and color if possible
        symbol, color, theme = self.symbol_engine.select_symbol_and_color(intent)
        fallback['symbol'] = symbol
        fallback['color'] = color
        fallback['reasoning'] = f"Theme '{theme}' resonates through symbolic selection. {fallback['reasoning']}"
        
        return fallback
    
    def save_output(self, result):
        """Save result to output.json"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving output: {e}")
    
    def log_session(self, prompt, response, result, timestamp):
        """Save session log"""
        clean_timestamp = timestamp.replace(':', '').replace('T', '-')[:15]
        log_file = self.logs_dir / f"seed_{clean_timestamp}.log"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== DREAMNET SESSION LOG ===\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Model: {self.config.get('model', 'name', default='qwen3:1.7b')}\n\n")
                f.write(f"PROMPT:\n{prompt}\n\n")
                f.write(f"RESPONSE:\n{response or 'No response'}\n\n")
                f.write(f"RESULT:\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
        except Exception as e:
            print(f"Error saving log: {e}")
    
    def append_echo(self, result, concept, timestamp):
        """Append to echo file"""
        echo_file = self.echoes_dir / f"{concept}.md"
        display_time = timestamp.replace('T', '-').replace(':', '')[:13]
        
        entry = f"""## {display_time}
**Symbol**: {result['symbol']}  
**Phrase**: {result['phrase']}  
**Reasoning**: {result['reasoning']}

"""
        
        try:
            mode = 'a' if echo_file.exists() else 'w'
            with open(echo_file, mode, encoding='utf-8') as f:
                if mode == 'w':
                    f.write(f"# {concept.title()} Echoes\n\n")
                f.write(entry)
        except Exception as e:
            print(f"Error writing echo: {e}")
    
    def dream(self):
        """Main dreaming process - much simpler now"""
        print("🌙 Dreamnet awakening...")
        
        # Load configuration
        brain_data = self.load_brain()
        intent = brain_data.get('intent', '')
        style = brain_data.get('style', '')
        
        print(f"📖 Intent: {intent}")
        print(f"🎨 Style: {style}")
        
        # Extract concept and detect theme
        concept = self.extract_concept(intent)
        theme = self.symbol_engine.detect_theme(intent)
        print(f"💭 Concept: {concept} (Theme: {theme})")
        
        # Generate prompt and call model
        prompt = self.prompt_generator.create_prompt(intent, style)
        print("🔮 Consulting oracle...")
        
        response = self.call_ollama(prompt)
        result = self.parse_response(response) if response else None
        
        if result:
            print("✅ Oracle responded through the symbolic veil...")
            # Enhance with theme-based color if missing
            if not result.get('color'):
                _, color, _ = self.symbol_engine.select_symbol_and_color(intent)
                result['color'] = color
        else:
            print("⚠️ Model failed, using enhanced fallback...")
            result = self.get_fallback(intent)
        
        # Display results
        print(f"✨ Symbol: {result['symbol']}")
        print(f"📝 Phrase: {result['phrase']}")
        print(f"🎨 Color: {result.get('color', 'N/A')}")
        
        # Save everything
        timestamp = datetime.now().isoformat()
        self.save_output(result)
        self.log_session(prompt, response, result, timestamp)
        self.append_echo(result, concept, timestamp)
        
        print(f"💾 Results saved")
        print("🌟 Dream complete.")


def main():
    """Main entry point"""
    agent = DreamAgent()
    agent.dream()


if __name__ == "__main__":
    main()
