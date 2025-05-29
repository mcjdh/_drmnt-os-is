# 🌙 Dreamnet - Enhanced Symbolic Generator

A mystical local-first symbolic generator that transforms intent into profound symbols, poetic wisdom, and reasoned insights using a local LLM with enhanced diversity and thematic resonance.

## ✨ Overview

Dreamnet runs an enhanced dream agent that:
- Reads intent and style from `brain.json` 
- Calls local Ollama model (`qwen3:1.7b`) with enhanced Unicode support
- Generates diverse symbolic output using thematic symbol pools
- Creates profound phrases through mystical prompt templates
- Uses intelligent color selection based on intent themes
- Archives results with full session logs
- Creates conceptual echoes organized by extracted themes

## 🎨 Enhanced Features

### 🔮 Diverse Symbol Generation
- **Sacred Symbols**: ☯, 🕉, ✡, ☪, ⚛, ♱, ☥, 🔯
- **Cosmic Symbols**: ∞, ✦, ✧, ⭐, 🌟, 💫, 🌙, ☽, ☾
- **Geometric Forms**: ◊, ▲, ∆, ◈, ⟁, ⬟, ⬢, ⬡, ⧫, ◇
- **Elemental Powers**: 🔥, 💧, 🌍, 💨, ⚡, ❄, 🌊, 🍃
- **Mystical Essence**: 🔮, 🌺, 🦋, 🕊, 🐉, 🌸, 🍄, 🌿
- **Ancient Glyphs**: 𓂀, 𓅃, 𓇯, 𓈖, ⚜, ☬, ◉, ⚫, ⚪

### 🎭 Thematic Intelligence
The system now intelligently selects symbols and colors based on intent themes:
- **Love/Forgiveness**: Mystical symbols with warm colors
- **Wisdom/Knowledge**: Cosmic and ancient symbols with ethereal tones
- **Peace/Balance**: Sacred symbols with cool, nature colors
- **Transformation**: Elemental symbols with vibrant energy colors

### 🌈 Enhanced Color Palettes
- **Cosmic**: Deep space purples and midnight blues
- **Mystical**: Enchanted violets and magical purples  
- **Nature**: Earth greens and golden ambers
- **Warm**: Passionate reds and sunset oranges
- **Cool**: Ocean blues and mountain grays
- **Ethereal**: Celestial whites and silver mists

## 🏗️ Structure

```
dreamnet/
├── dream.py              ← main executable script
├── brain.json            ← symbolic intent and style configuration
├── output.json           ← latest generated result
├── logs/
│   └── seed_YYYYMMDD-HHMMSS.log  ← timestamped session logs
├── echoes/
│   └── forgiveness.md    ← concept-based output collections
└── README.md             ← this file
```

## 🚀 Quick Start

### Prerequisites
1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)
2. **Pull the model**: `ollama pull qwen3:1.7b`
3. **Verify Ollama**: `ollama run qwen3:1.7b "Hello"`

### Running Dreamnet
```bash
cd dreamnet
python dream.py
```

## 📝 Configuration

Edit `brain.json` to set your symbolic intent:

```json
{
  "intent": "Your symbolic exploration or question",
  "style": "mystical, contemplative, ancient wisdom"
}
```

## 📤 Output Format

### output.json
```json
{
  "symbol": "☯",
  "phrase": "Balance dissolves all wounds into wisdom.",
  "color": "#8e7cc3",
  "reasoning": "Symbolic explanation of choices made"
}
```

### Echo Files (echoes/{concept}.md)
```markdown
# Concept Echoes

## 20250528-1845
**Symbol**: ☯  
**Phrase**: Balance dissolves all wounds into wisdom.  
**Reasoning**: Forgiveness represents the balance...
```

## 🔧 Architecture

- **Modular Design**: Single-file executable with clear separation of concerns
- **Graceful Fallbacks**: Built-in fallback responses if model fails
- **Local-First**: No external dependencies beyond Ollama
- **Session Logging**: Complete prompt/response archival
- **Concept Tracking**: Automatic categorization by intent themes

## 🌟 Example Session

```bash
$ python dream.py
🌙 Dreamnet awakening...
📖 Intent: Explore the essence of forgiveness...
🎨 Style: mystical, contemplative, with gentle wisdom
💭 Concept: forgiveness
🔮 Consulting the oracle...
✨ Generated symbol: ☯
📝 Phrase: Balance dissolves all wounds into wisdom.
🎨 Color: #8e7cc3
💾 Results saved to output.json
📋 Session logged to logs/seed_20250528-184523.log
🌊 Echo added to echoes/forgiveness.md
🌟 Dream complete.
```

## 🔮 Purpose

This prototype represents the first crystal of a larger dream architecture — a symbolic seed that will later scale into a network of agents, drift models, and recursive constellation renderings.

*Built with poetic grace and modular clarity.*
