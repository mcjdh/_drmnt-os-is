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
        # Get the directory where this script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.model_name = "qwen3:1.7b"
        self.brain_file = os.path.join(self.script_dir, "brain.json")
        self.output_file = os.path.join(self.script_dir, "output.json")
        self.logs_dir = os.path.join(self.script_dir, "logs")
        self.echoes_dir = os.path.join(self.script_dir, "echoes")
        
        # Create directories if they don't exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.echoes_dir, exist_ok=True)
        
        # Enhanced symbol pools with expanded mystical vocabulary
        self.symbol_pools = {
            'sacred': ['☯', '🕉', '✡', '☪', '⚛', '♱', '☥', '🔯', '☸', '✝', '☦', '☩'],
            'cosmic': ['∞', '✦', '✧', '⭐', '🌟', '💫', '🌙', '☽', '☾', '◯', '⭕', '☉', '✯', '✰', '✱'],
            'geometric': ['◊', '▲', '∆', '◈', '⟁', '⬟', '⬢', '⬡', '⧫', '◇', '⬠', '⬣', '⬦', '⬧'],
            'elemental': ['🔥', '💧', '🌍', '💨', '⚡', '❄', '🌊', '🍃', '🌋', '🌪', '☄', '🌈'],
            'mystical': ['🔮', '🌺', '🦋', '🕊', '🐉', '🌸', '🍄', '🌿', '🔯', '✨', '🦚', '🦢', '🌹'],
            'ancient': ['𓂀', '𓅃', '𓇯', '𓈖', '⚜', '☬', '◉', '⚫', '⚪', '𓁿', '𓀠', '𓆃'],
            'energy': ['⚡', '💥', '🌊', '🔥', '💫', '✨', '⭐', '🌟', '💖', '💎', '💠', '🔆'],
            'celestial': ['☄', '🌌', '🌠', '💫', '🌃', '🌆', '🌇', '🌉', '☀', '🌞', '🌝', '🌛'],
            'nature': ['🌲', '🌳', '🌴', '🌵', '🌷', '🌻', '🌼', '🏵', '🥀', '🌾', '🌱', '🍀'],
            'transformation': ['🦋', '🐛', '🦅', '🕊', '🦉', '🦆', '🐍', '🦎', '🐲', '🦄', '🦃', '🦚'],
            'quantum': ['⟨', '⟩', '∴', '∵', '∀', '∃', '⊗', '⊕', '⊙', '⊚', '⊛', '⊜'],
            'flow': ['∞', '∿', '〰', '≈', '⤙', '⤜', '⤛', '⟁', '⟐', '≋', '〜', '∼', '≀', '≁'],
            'ethereal': ['※', '⁂', '⁎', '⁕', '⁜', '⁝', '⁞', '⁺', '⁻', '°', '˚', '∘', '∙', '⊹', '✧']
        }
        
        # Enhanced color palettes with more nuanced selections
        self.color_palettes = {
            'cosmic': ['#1a1a2e', '#16213e', '#0f3460', '#533483', '#7209b7', '#2d1b69', '#4a0e4e', '#81689d'],
            'mystical': ['#8e7cc3', '#9b59b6', '#663399', '#4a154b', '#6a0572', '#ab83a1', '#ce93d8', '#ba68c8'],
            'nature': ['#27ae60', '#2ecc71', '#1abc9c', '#16a085', '#f39c12', '#e67e22', '#52b788', '#74c69d'],
            'warm': ['#e74c3c', '#c0392b', '#d35400', '#e67e22', '#f39c12', '#f1c40f', '#ff6b6b', '#ee6c4d'],
            'cool': ['#3498db', '#2980b9', '#34495e', '#2c3e50', '#1abc9c', '#16a085', '#4ecdc4', '#45b7d1'],
            'ethereal': ['#ecf0f1', '#bdc3c7', '#95a5a6', '#7f8c8d', '#34495e', '#2c3e50', '#dfe7fd', '#c7ceea'],
            'twilight': ['#5f27cd', '#341f97', '#2e86ab', '#48466d', '#3d3d3d', '#718093', '#4834d4', '#686de0'],
            'aurora': ['#f8b195', '#f67280', '#c06c84', '#6c5ce7', '#a29bfe', '#74b9ff', '#a29bfe', '#6c5ce7'],
            'earth': ['#d4a574', '#a68a64', '#936639', '#7f5539', '#582f0e', '#6f4e37', '#8b5a3c', '#a0522d'],
            'ocean': ['#006ba6', '#0496ff', '#3a86ff', '#7209b7', '#560bad', '#3f37c9', '#4361ee', '#4895ef'],
            'fire': ['#ff006e', '#fb5607', '#ffbe0b', '#fb8500', '#ff4800', '#ff0000', '#dc2f02', '#e85d04'],
            'spirit': ['#e0aaff', '#c77dff', '#9d4edd', '#7209b7', '#560bad', '#3c096c', '#240046', '#10002b']
        }
        
        # Enhanced fallback responses with more variety
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
            },
            {
                "symbol": "🌙",
                "phrase": "In lunar cycles, transformation finds its rhythm.",
                "color": "#6c5ce7",
                "reasoning": "The moon guides those who journey through darkness."
            },
            {
                "symbol": "☯",
                "phrase": "Balance dissolves all boundaries into unity.",
                "color": "#2c3e50",
                "reasoning": "Duality merges in the dance of opposites."
            },
            {
                "symbol": "🔮",
                "phrase": "The crystal sphere reflects infinite possibilities.",
                "color": "#a29bfe",
                "reasoning": "Vision clarifies when we gaze beyond the veil."
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
        # Enhanced concept extraction with weighted keywords
        words = re.findall(r'\b\w+\b', intent.lower())
        
        # Expanded stop words for better concept extraction
        stop_words = {
            'this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 
            'the', 'and', 'or', 'but', 'for', 'nor', 'yet', 'so', 'a', 'an',
            'how', 'what', 'when', 'where', 'why', 'who', 'which', 'both',
            'giver', 'receiver', 'explore', 'essence', 'transforms', 'between',
            'through', 'within', 'without', 'beyond', 'above', 'below'
        }
        
        # Priority concepts (weighted selection)
        priority_concepts = {
            'love': 10, 'wisdom': 10, 'peace': 10, 'harmony': 10,
            'forgiveness': 9, 'transformation': 9, 'balance': 9, 'energy': 9,
            'healing': 8, 'growth': 8, 'journey': 8, 'power': 8,
            'light': 7, 'shadow': 7, 'dream': 7, 'spirit': 7,
            'consciousness': 6, 'awareness': 6, 'presence': 6, 'flow': 6
        }
        
        # Score words based on priority
        scored_words = []
        for word in words:
            if word in priority_concepts:
                scored_words.append((word, priority_concepts[word]))
            elif len(word) > 4 and word not in stop_words:
                scored_words.append((word, 5))
            elif len(word) > 3 and word not in stop_words:
                scored_words.append((word, 3))
        
        # Sort by score and return highest
        if scored_words:
            scored_words.sort(key=lambda x: x[1], reverse=True)
            return scored_words[0][0]
        
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
        
        # Analyze intent for prompt customization
        intent_lower = intent.lower()
        
        # Enhanced prompt templates with more variety
        cosmic_prompts = [
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

            f"""Greetings, cosmic weaver of symbolic reality. The universe speaks through you.

Sacred Quest: {intent}
Vibrational Style: {style}

Transmit your wisdom as pure JSON:
{{
  "symbol": "single cosmic glyph that embodies this truth",
  "phrase": "profound wisdom crystallized in one sentence",
  "color": "hex frequency of this cosmic vibration #rrggbb",
  "reasoning": "the sacred geometry behind your selection"
}}

Let the stars guide your symbolic choice."""
        ]
        
        mystical_prompts = [
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

            f"""O keeper of mysteries, channel the ineffable through sacred forms.

Divine Purpose: {intent}
Sacred Resonance: {style}

Manifest as JSON only:
{{
  "symbol": "mystical unicode symbol of power",
  "phrase": "one sentence containing eternal wisdom",
  "color": "the color of this truth in hex #rrggbb",
  "reasoning": "mystical insight into your symbolic choice"
}}

Let ancient wisdom flow through modern forms."""
        ]
        
        geometric_prompts = [
            f"""Sacred geometer, divine the patterns within this intent.

Quest: {intent}
Resonance: {style}

Manifest as JSON only:
{{
  "symbol": "profound unicode symbol that embodies this essence",
  "phrase": "one luminous sentence of distilled wisdom",
  "color": "hex frequency of this vibrational truth #rrggbb",
  "reasoning": "mystical insight into the symbolic choice"
}}

Let the universe speak through your selection of forms.""",

            f"""Divine mathematician of symbolic reality, calculate the essence.

Equation: {intent}
Variables: {style}

Solve for wisdom in JSON:
{{
  "symbol": "geometric symbol of profound meaning",
  "phrase": "the solution expressed in one poetic sentence",
  "color": "chromatic frequency in hex #rrggbb",
  "reasoning": "the sacred mathematics behind your choice"
}}

Let phi and pi guide your symbolic selection."""
        ]
        
        elemental_prompts = [
            f"""Elemental oracle, channel the primal forces through symbols.

Elemental Intent: {intent}
Force Style: {style}

Manifest the elements as JSON:
{{
  "symbol": "elemental symbol of transformation",
  "phrase": "raw wisdom distilled into one sentence",
  "color": "the hue of this elemental truth #rrggbb",
  "reasoning": "how the elements converge in this symbol"
}}

Let fire, water, earth, and air speak through you."""
        ]
        
        # Select prompt based on intent analysis
        if any(word in intent_lower for word in ['cosmic', 'universe', 'stars', 'infinity']):
            selected_prompts = cosmic_prompts
        elif any(word in intent_lower for word in ['sacred', 'divine', 'spiritual', 'mystic']):
            selected_prompts = mystical_prompts
        elif any(word in intent_lower for word in ['geometry', 'pattern', 'structure', 'form']):
            selected_prompts = geometric_prompts
        elif any(word in intent_lower for word in ['element', 'fire', 'water', 'earth', 'energy']):
            selected_prompts = elemental_prompts
        else:
            # Combine all prompts for general use
            selected_prompts = cosmic_prompts + mystical_prompts + geometric_prompts
        
        return random.choice(selected_prompts)
    
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
        """Generate enhanced fallback based on intent analysis with weighted selection"""
        intent_lower = intent.lower()
        
        # Enhanced thematic mapping with weighted symbol selection
        theme_weights = {}
        
        # Analyze intent and build weighted pools
        if any(word in intent_lower for word in ['love', 'heart', 'compassion', 'kindness', 'forgiveness']):
            theme_weights['mystical'] = 3
            theme_weights['sacred'] = 2
            theme_symbols = (self.symbol_pools['mystical'] * 3 + 
                           self.symbol_pools['sacred'] * 2 + 
                           ['💖', '♥', '❤', '💕', '💗', '💝'] * 4)
            theme_colors = self.color_palettes['warm'] + self.color_palettes['spirit']
        elif any(word in intent_lower for word in ['wisdom', 'knowledge', 'understanding', 'learning', 'truth']):
            theme_weights['cosmic'] = 3
            theme_weights['ancient'] = 3
            theme_symbols = (self.symbol_pools['cosmic'] * 3 + 
                           self.symbol_pools['ancient'] * 3 +
                           self.symbol_pools['ethereal'] * 2)
            theme_colors = self.color_palettes['cosmic'] + self.color_palettes['twilight']
        elif any(word in intent_lower for word in ['peace', 'calm', 'balance', 'harmony', 'stillness']):
            theme_weights['sacred'] = 3
            theme_weights['flow'] = 2
            theme_symbols = (self.symbol_pools['sacred'] * 3 + 
                           self.symbol_pools['flow'] * 2 +
                           ['☯', '◎', '○', '☮', '🕊'] * 4)
            theme_colors = self.color_palettes['cool'] + self.color_palettes['ethereal']
        elif any(word in intent_lower for word in ['growth', 'change', 'transformation', 'journey', 'evolution']):
            theme_weights['transformation'] = 4
            theme_weights['nature'] = 2
            theme_symbols = (self.symbol_pools['transformation'] * 4 + 
                           self.symbol_pools['nature'] * 2 +
                           self.symbol_pools['elemental'])
            theme_colors = self.color_palettes['nature'] + self.color_palettes['aurora']
        elif any(word in intent_lower for word in ['power', 'strength', 'energy', 'force', 'intensity']):
            theme_weights['energy'] = 4
            theme_weights['elemental'] = 3
            theme_symbols = (self.symbol_pools['energy'] * 4 + 
                           self.symbol_pools['elemental'] * 3)
            theme_colors = self.color_palettes['fire'] + self.color_palettes['warm']
        elif any(word in intent_lower for word in ['mystery', 'unknown', 'hidden', 'secret', 'veil']):
            theme_weights['mystical'] = 3
            theme_weights['celestial'] = 2
            theme_symbols = (self.symbol_pools['mystical'] * 3 + 
                           self.symbol_pools['celestial'] * 2 +
                           self.symbol_pools['cosmic'])
            theme_colors = self.color_palettes['twilight'] + self.color_palettes['mystical']
        elif any(word in intent_lower for word in ['quantum', 'science', 'mathematics', 'logic']):
            theme_weights['quantum'] = 4
            theme_weights['geometric'] = 2
            theme_symbols = (self.symbol_pools['quantum'] * 4 + 
                           self.symbol_pools['geometric'] * 2)
            theme_colors = self.color_palettes['cosmic'] + self.color_palettes['cool']
        else:
            # Default balanced selection
            theme_symbols = (self.symbol_pools['cosmic'] + 
                           self.symbol_pools['geometric'] + 
                           self.symbol_pools['mystical'])
            theme_colors = self.color_palettes['cosmic'] + self.color_palettes['ethereal']
        
        # Create enhanced fallback
        selected_symbol = random.choice(theme_symbols)
        selected_color = random.choice(theme_colors)
        
        # Enhanced contextual phrases based on intent
        if 'love' in intent_lower or 'heart' in intent_lower:
            phrases = [
                "Love transcends all boundaries, weaving souls into one tapestry.",
                "In the heart's chamber, all beings find their home.",
                "Compassion flows like rivers returning to the ocean.",
                "The heart knows truths the mind cannot fathom.",
                "Love is the force that binds the universe in sacred unity."
            ]
        elif 'wisdom' in intent_lower or 'knowledge' in intent_lower:
            phrases = [
                "Wisdom emerges from the silence between thoughts.",
                "In the library of the cosmos, all truths are written.",
                "Knowledge flows through those who empty themselves to receive.",
                "The wise see patterns where others see chaos.",
                "Understanding dawns when the mind becomes still water."
            ]
        elif 'peace' in intent_lower or 'balance' in intent_lower:
            phrases = [
                "In perfect stillness, the universe reveals its rhythm.",
                "Balance is the dance between holding and releasing.",
                "Peace flows from accepting what is while creating what could be.",
                "Harmony emerges when all voices sing as one.",
                "In the center of the storm lies perfect calm."
            ]
        elif 'transformation' in intent_lower or 'change' in intent_lower:
            phrases = [
                "Every ending births a new beginning in the cosmic dance.",
                "Transformation requires the courage to release the familiar.",
                "Change is the universe expressing its infinite creativity.",
                "In metamorphosis, we discover who we truly are.",
                "The butterfly remembers being a caterpillar in its dreams."
            ]
        else:
            phrases = [
                "In the silence between thoughts, wisdom emerges.",
                "The universe whispers through symbols ancient and true.",
                "Sacred geometry unfolds in the dance of consciousness.",
                "Light bends around the corners of understanding.",
                "In the void, all possibilities crystallize into being.",
                "The eternal speaks through forms beyond language.",
                "Patterns emerge where chaos once seemed absolute.",
                "Divine mathematics governs the flow of dreams.",
                "Mystery and clarity dance together in eternal balance.",
                "The cosmic web connects all things in sacred resonance."
            ]
        
        selected_phrase = random.choice(phrases)
        
        return {
            "symbol": selected_symbol,
            "phrase": selected_phrase,
            "color": selected_color,
            "reasoning": f"When direct communion fails, the {selected_symbol} emerges as a beacon through the symbolic realm, chosen for its resonance with the essence of {concept if (concept := self.extract_concept(intent)) != 'dream' else 'the eternal mystery'}."
        }

    def enhance_model_response(self, result, intent=""):
        """Enhance model response with additional symbolic resonance"""
        if not result:
            return None
            
        # Add color if missing, using weighted thematic selection
        if not result.get('color'):
            intent_lower = intent.lower()
            
            # Build weighted color selection based on multiple themes
            color_weights = []
            
            if any(word in intent_lower for word in ['love', 'heart', 'warm', 'passion']):
                color_weights.extend(self.color_palettes['warm'] * 3)
                color_weights.extend(self.color_palettes['spirit'] * 2)
            if any(word in intent_lower for word in ['peace', 'calm', 'cool', 'serene']):
                color_weights.extend(self.color_palettes['cool'] * 3)
                color_weights.extend(self.color_palettes['ethereal'] * 2)
            if any(word in intent_lower for word in ['nature', 'growth', 'earth', 'organic']):
                color_weights.extend(self.color_palettes['nature'] * 3)
                color_weights.extend(self.color_palettes['earth'] * 2)
            if any(word in intent_lower for word in ['cosmic', 'space', 'universe', 'stars']):
                color_weights.extend(self.color_palettes['cosmic'] * 3)
                color_weights.extend(self.color_palettes['twilight'] * 2)
            if any(word in intent_lower for word in ['mystery', 'magic', 'mystical', 'spiritual']):
                color_weights.extend(self.color_palettes['mystical'] * 3)
                color_weights.extend(self.color_palettes['spirit'] * 2)
            if any(word in intent_lower for word in ['ocean', 'water', 'flow', 'wave']):
                color_weights.extend(self.color_palettes['ocean'] * 3)
                color_weights.extend(self.color_palettes['cool'] * 2)
            if any(word in intent_lower for word in ['fire', 'energy', 'power', 'strength']):
                color_weights.extend(self.color_palettes['fire'] * 3)
                color_weights.extend(self.color_palettes['warm'] * 2)
            
            # Default if no specific themes detected
            if not color_weights:
                color_weights = (self.color_palettes['mystical'] + 
                               self.color_palettes['cosmic'] + 
                               self.color_palettes['ethereal'])
            
            result['color'] = random.choice(color_weights)
        
        # Enhance reasoning if too short
        if result.get('reasoning') and len(result['reasoning']) < 50:
            concept = self.extract_concept(intent)
            result['reasoning'] = f"{result['reasoning']} This symbol resonates with the deep currents of {concept}, bridging the seen and unseen realms."
        
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
