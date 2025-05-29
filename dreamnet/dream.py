#!/usr/bin/env python3
"""
dreamnet - A minimal local-first symbolic generator

This script reads intent and style from brain.json, calls a local LLM via Ollama,
and generates symbolic output with reasoning.
"""

import json
import subprocess
import sys
import os
from datetime import datetime
import re
import random


class DreamAgent:
    def __init__(self):
        self.model_name = "qwen3:1.7b"
        self.brain_file = "brain.json"
        self.output_file = "output.json"
        self.logs_dir = "logs"
        self.echoes_dir = "echoes"
        
        # Enhanced symbol pools for diverse generation
        self.symbol_pools = {
            'cosmic': ['☉', '☽', '✦', '✧', '✯', '⟐', '⬟', '◎', '◉', '◌', '○', '●', '◯'],
            'mystical': ['☯', '⚡', '🔮', '🌙', '⭐', '💫', '✨', '🌟', '🔯', '☪', '☸', '༄'],
            'geometric': ['△', '▲', '▽', '▼', '◊', '◈', '◇', '□', '■', '▢', '▣', '◦', '⬢', '⬡'],
            'flow': ['∞', '∿', '〰', '≈', '⤙', '⤜', '⤛', '⟁', '⟐', '≋', '〜', '∼'],
            'nature': ['🌿', '🍃', '🌱', '🌾', '🌸', '🌺', '🌻', '🌷', '🌹', '🏔', '🌊', '⚘'],
            'ethereal': ['※', '⁂', '⁎', '⁕', '⁜', '⁝', '⁞', '⁺', '⁻', '°', '˚', '∘', '∙']
        }
        
        # Enhanced color palettes
        self.color_palettes = {
            'cosmic': ['#1a1a2e', '#16213e', '#0f3460', '#533483', '#7209b7', '#2d1b69'],
            'mystical': ['#8e7cc3', '#9b59b6', '#663399', '#4a154b', '#6a0572', '#ab83a1'],
            'nature': ['#27ae60', '#2ecc71', '#1abc9c', '#16a085', '#f39c12', '#e67e22'],
            'warm': ['#e74c3c', '#c0392b', '#d35400', '#e67e22', '#f39c12', '#f1c40f'],
            'cool': ['#3498db', '#2980b9', '#34495e', '#2c3e50', '#1abc9c', '#16a085'],
            'ethereal': ['#ecf0f1', '#bdc3c7', '#95a5a6', '#7f8c8d', '#34495e', '#2c3e50']        }
        
        # Enhanced mystical symbol pools for thematic generation
        self.symbol_pools = {
            'sacred': ['☯', '🕉', '✡', '☪', '⚛', '♱', '☥', '🔯'],
            'cosmic': ['∞', '✦', '✧', '⭐', '🌟', '💫', '🌙', '☽', '☾', '◯', '⭕'],
            'geometric': ['◊', '▲', '∆', '◈', '⟁', '⬟', '⬢', '⬡', '⧫', '◇'],
            'elemental': ['🔥', '💧', '🌍', '💨', '⚡', '❄', '🌊', '🍃'],
            'mystical': ['🔮', '🌺', '🦋', '🕊', '🐉', '🌸', '🍄', '🌿', '🔯', '✨'],
            'ancient': ['𓂀', '𓅃', '𓇯', '𓈖', '⚜', '☬', '◉', '⚫', '⚪'],
            'energy': ['⚡', '💥', '🌊', '🔥', '💫', '✨', '⭐', '🌟', '💖', '💎']
        }
        
        # Enhanced fallback responses with variety
        self.fallback_responses = [
            {
                "symbol": "∞",
                "phrase": "The dream continues beyond understanding.",
                "color": "#7f8c8d",
                "reasoning": "When symbols fail, the infinite persists."
            },
            {
                "symbol": "◎",
                "phrase": "In silence, all answers emerge.",
                "color": "#9b59b6",
                "reasoning": "The centered circle represents completeness in the void."
            },
            {
                "symbol": "✧",
                "phrase": "Stars whisper secrets to those who listen.",
                "color": "#3498db",
                "reasoning": "Light pierces through when words cannot reach."
            },
            {
                "symbol": "≋",
                "phrase": "Waves of possibility flow through consciousness.",
                "color": "#1abc9c",
                "reasoning": "Movement reveals truth in its flowing essence."
            },
            {
                "symbol": "⬢",
                "phrase": "Sacred geometry holds the universe's blueprint.",
                "color": "#e67e22",
                "reasoning": "Perfect forms echo the divine mathematical order."
            }
        ]
    
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
        """Extract main concept from intent for echo file naming"""
        # Enhanced concept extraction with better filtering
        words = re.findall(r'\b\w+\b', intent.lower())
        
        # Expanded stop words for better concept extraction
        stop_words = {
            'this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 
            'the', 'and', 'or', 'but', 'for', 'nor', 'yet', 'so', 'a', 'an',
            'how', 'what', 'when', 'where', 'why', 'who', 'which', 'both',
            'giver', 'receiver', 'explore', 'essence', 'transforms'
        }
        
        # Look for meaningful concepts (longer words, not in stop list)
        meaningful_words = [w for w in words if len(w) > 4 and w not in stop_words]
          # If no long words, try shorter meaningful ones
        if not meaningful_words:
            meaningful_words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        if meaningful_words:
            return meaningful_words[0]
        return "dream"
    
    def call_ollama(self, prompt):
        """Call Ollama model and return response with enhanced Unicode support"""
        try:
            cmd = ["ollama", "run", self.model_name, prompt]
            # Enhanced encoding handling for Windows Unicode support
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Ollama error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("Ollama call timed out")
            return None
        except FileNotFoundError:
            print("Error: Ollama not found. Please ensure Ollama is installed and in PATH")
            return None
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None
    
    def parse_model_response(self, response):
        """Parse model response and extract JSON"""
        if not response:
            return None
            
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # If no JSON found, return None
                return None
        except json.JSONDecodeError:
            return None
    
    def create_prompt(self, brain_data):
        """Create enhanced, diverse prompt for the LLM"""
        intent = brain_data.get("intent", "")
        style = brain_data.get("style", "")
        
        # Enhanced prompt templates for variety
        prompt_templates = [
            f"""You are an ancient symbolic oracle dwelling between dimensions. 

Intent: {intent}
Style: {style}

Channel the cosmic wisdom and respond with ONLY valid JSON:
{{
  "symbol": "mystical unicode symbol (☯, ∞, ⟁, ◊, ∆, ✧, ⬢, ≋, ◎, ※)",
  "phrase": "one ethereal sentence that captures the soul of this intent",
  "color": "hex color reflecting the vibrational frequency #rrggbb",
  "reasoning": "brief mystical explanation of the symbolic convergence"
}}

Let the symbols flow through you like starlight through crystal.""",

            f"""Ancient dreamweaver, you speak in symbols that dance between worlds.

Sacred Intent: {intent}
Essence Style: {style}

Weave your response as pure JSON:
{{
  "symbol": "single sacred glyph (cosmic, geometric, or ethereal)",
  "phrase": "poetic wisdom in one flowing sentence",
  "color": "hex embodiment of this truth #rrggbb", 
  "reasoning": "the hidden meaning behind your choices"
}}

Choose symbols that resonate with the deeper currents of existence.""",

            f"""Greetings, keeper of the symbolic realm. Divine this intent through sacred geometry.

Quest: {intent}
Resonance: {style}

Manifest as JSON only:
{{
  "symbol": "profound unicode symbol that embodies this essence",
  "phrase": "one luminous sentence of distilled wisdom",
  "color": "hex frequency of this vibrational truth #rrggbb",
  "reasoning": "mystical insight into the symbolic choice"
}}

Let the universe speak through your selection of forms."""
        ]
        
        # Randomly select a template for diversity
        selected_template = random.choice(prompt_templates)
        return selected_template
    
    def save_output(self, result):
        """Save result to output.json"""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving output: {e}")
    
    def log_session(self, prompt, response, result, timestamp):
        """Save full session to timestamped log file"""
        # Clean timestamp for Windows filename compatibility
        clean_timestamp = timestamp.replace(':', '').replace('T', '-')[:15]
        log_filename = f"seed_{clean_timestamp}.log"
        log_path = os.path.join(self.logs_dir, log_filename)
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"=== DREAMNET SESSION LOG ===\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Model: {self.model_name}\n\n")
                f.write(f"PROMPT SENT:\n{prompt}\n\n")
                f.write(f"RAW RESPONSE:\n{response}\n\n")
                f.write(f"PARSED RESULT:\n{json.dumps(result, indent=2, ensure_ascii=False)}\n")
        except Exception as e:
            print(f"Error saving log: {e}")
    
    def append_to_echo(self, result, concept, timestamp):
        """Append result to echoes/{concept}.md"""
        echo_file = os.path.join(self.echoes_dir, f"{concept}.md")
        
        # Format timestamp for display
        display_time = timestamp.replace('T', '-').replace(':', '')[:13]
        
        entry = f"""## {display_time}
**Symbol**: {result['symbol']}  
**Phrase**: {result['phrase']}  
**Reasoning**: {result['reasoning']}

"""
        
        try:
            # Create file if it doesn't exist or append to existing
            mode = 'a' if os.path.exists(echo_file) else 'w'
            with open(echo_file, mode, encoding='utf-8') as f:
                if mode == 'w':
                    f.write(f"# {concept.title()} Echoes\n\n")
                f.write(entry)
        except Exception as e:
            print(f"Error writing to echo file: {e}")
    
    def get_enhanced_fallback(self, intent=""):
        """Generate enhanced fallback based on intent analysis"""
        # Analyze intent for thematic fallback selection
        intent_lower = intent.lower()
          # Select fallback based on intent themes
        if any(word in intent_lower for word in ['love', 'heart', 'compassion', 'kindness', 'forgiveness']):
            theme_symbols = self.symbol_pools['mystical'] + ['💖', '♥', '❤', '☯']
            theme_colors = self.color_palettes['warm']
        elif any(word in intent_lower for word in ['wisdom', 'knowledge', 'understanding', 'learning']):
            theme_symbols = self.symbol_pools['cosmic'] + self.symbol_pools['ancient']
            theme_colors = self.color_palettes['cosmic'] + self.color_palettes['ethereal']
        elif any(word in intent_lower for word in ['peace', 'calm', 'balance', 'harmony']):
            theme_symbols = self.symbol_pools['sacred'] + ['☯', '◎', '○']
            theme_colors = self.color_palettes['cool'] + self.color_palettes['nature']
        elif any(word in intent_lower for word in ['growth', 'change', 'transformation', 'journey']):
            theme_symbols = self.symbol_pools['elemental'] + self.symbol_pools['energy']
            theme_colors = self.color_palettes['nature'] + self.color_palettes['warm']
        elif any(word in intent_lower for word in ['power', 'strength', 'energy', 'force']):
            theme_symbols = self.symbol_pools['energy'] + self.symbol_pools['elemental']
            theme_colors = self.color_palettes['vibrant']
        else:
            # Default to cosmic theme with geometric elements
            theme_symbols = self.symbol_pools['cosmic'] + self.symbol_pools['geometric']
            theme_colors = self.color_palettes['cosmic']
        
        # Create enhanced fallback
        selected_symbol = random.choice(theme_symbols)
        selected_color = random.choice(theme_colors)
        
        # Enhanced fallback phrases
        mystical_phrases = [
            "In the silence between thoughts, wisdom emerges.",
            "The universe whispers through symbols ancient and true.",
            "Sacred geometry unfolds in the dance of consciousness.",
            "Light bends around the corners of understanding.",
            "In the void, all possibilities crystallize into being.",
            "The eternal speaks through forms beyond language.",
            "Patterns emerge where chaos once seemed absolute.",
            "Divine mathematics governs the flow of dreams."
        ]
        
        selected_phrase = random.choice(mystical_phrases)
        
        return {
            "symbol": selected_symbol,
            "phrase": selected_phrase,
            "color": selected_color,
            "reasoning": f"When direct communion fails, the {selected_symbol} emerges as a beacon through the symbolic realm."
        }

    def enhance_model_response(self, result, intent=""):
        """Enhance model response with additional symbolic resonance"""
        if not result:
            return None
            
        # Add color if missing, using thematic selection
        if not result.get('color'):
            intent_lower = intent.lower()
            if any(word in intent_lower for word in ['love', 'heart', 'warm']):
                result['color'] = random.choice(self.color_palettes['warm'])
            elif any(word in intent_lower for word in ['peace', 'calm', 'cool']):
                result['color'] = random.choice(self.color_palettes['cool'])
            elif any(word in intent_lower for word in ['nature', 'growth', 'earth']):
                result['color'] = random.choice(self.color_palettes['nature'])
            else:
                result['color'] = random.choice(self.color_palettes['mystical'])
        
        return result
    
    def dream(self):
        """Main dreaming process"""
        print("🌙 Dreamnet awakening...")
        
        # Load brain configuration
        brain_data = self.load_brain()
        print(f"📖 Intent: {brain_data.get('intent', 'Unknown')}")
        print(f"🎨 Style: {brain_data.get('style', 'Unknown')}")
        
        # Extract concept for echo file
        concept = self.extract_concept(brain_data.get('intent', ''))
        print(f"💭 Concept: {concept}")
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Generate prompt
        prompt = self.create_prompt(brain_data)
        
        # Call model
        print("🔮 Consulting the oracle...")
        response = self.call_ollama(prompt)
          # Parse response
        result = self.parse_model_response(response) if response else None
        
        if result:
            # Enhance the model response with additional symbolic resonance
            result = self.enhance_model_response(result, brain_data.get('intent', ''))
            print("✅ Oracle has spoken through the symbolic veil...")
        else:
            print("⚠️  Model response invalid, using enhanced fallback...")
            result = self.get_enhanced_fallback(brain_data.get('intent', ''))
        
        print(f"✨ Generated symbol: {result['symbol']}")
        print(f"📝 Phrase: {result['phrase']}")
        print(f"🎨 Color: {result.get('color', 'N/A')}")
        print(f"🔍 Reasoning: {result.get('reasoning', 'Mystery flows through silence')}")
        
        # Save outputs
        self.save_output(result)
        self.log_session(prompt, response or "No response", result, timestamp)
        self.append_to_echo(result, concept, timestamp)
        
        print(f"💾 Results saved to {self.output_file}")
        print(f"📋 Session logged to logs/seed_{timestamp.replace(':', '').replace('T', '-')[:15]}.log")
        print(f"🌊 Echo added to echoes/{concept}.md")
        print("🌟 Dream complete.")


def main():
    """Main entry point"""
    agent = DreamAgent()
    agent.dream()


if __name__ == "__main__":
    main()
