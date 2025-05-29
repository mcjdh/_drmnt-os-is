#!/usr/bin/env python3
"""
Test script for dreamnet with different themes
"""

import json
import os
import shutil
import time
import sys

# Enhanced test brains with diverse themes
test_brains = [
    {
        "intent": "Explore the depths of inner wisdom and ancient knowledge",
        "style": "ancient, profound, cosmic wisdom"
    },
    {
        "intent": "Channel the raw power of elemental transformation",
        "style": "fierce, elemental, primal energy"
    },
    {
        "intent": "Discover the gentle flow of peace and harmony",
        "style": "serene, flowing, tranquil wisdom"
    },
    {
        "intent": "Embrace the sacred geometry of divine love",
        "style": "sacred, geometric, divine resonance"
    },
    {
        "intent": "Navigate the quantum mysteries of consciousness",
        "style": "quantum mysticism, scientific spirituality"
    },
    {
        "intent": "Transform shadow into light through alchemical wisdom",
        "style": "alchemical, transformative, shadow work"
    },
    {
        "intent": "Connect with the ocean of universal compassion",
        "style": "oceanic, flowing, boundless love"
    },
    {
        "intent": "Ignite the fire of creative manifestation",
        "style": "fiery, creative, passionate expression"
    }
]

def test_theme(brain_data, theme_name):
    """Test a specific theme configuration"""
    print(f"\n{'='*60}")
    print(f"🌟 Testing: {theme_name}")
    print(f"{'='*60}")
    print(f"📖 Intent: {brain_data['intent']}")
    print(f"🎨 Style: {brain_data['style']}")
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    brain_path = os.path.join(script_dir, "brain.json")
    brain_backup_path = os.path.join(script_dir, "brain_backup.json")
    output_path = os.path.join(script_dir, "output.json")
    dream_script = os.path.join(script_dir, "dream.py")
    
    # Save current brain.json
    if os.path.exists(brain_path):
        shutil.copy(brain_path, brain_backup_path)
    
    # Write test brain
    with open(brain_path, 'w') as f:
        json.dump(brain_data, f, indent=2)
    
    # Run dreamnet with proper path
    print("🔮 Generating...")
    os.system(f"{sys.executable} {dream_script}")
    
    # Small delay to ensure file is written
    time.sleep(0.5)
    
    # Read result
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        print(f"\n✨ Symbol: {result['symbol']}")
        print(f"📝 Phrase: {result['phrase']}")
        print(f"🎨 Color: {result.get('color', 'N/A')}")
        print(f"💭 Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
    except Exception as e:
        print(f"❌ Error reading result: {e}")
    
    # Restore original brain
    if os.path.exists(brain_backup_path):
        shutil.move(brain_backup_path, brain_path)

if __name__ == "__main__":
    print("🌙 Dreamnet Theme Tester")
    print("Testing enhanced symbolic generation across multiple themes...")
    
    for i, brain in enumerate(test_brains):
        test_theme(brain, f"Theme {i+1}: {brain['intent'][:30]}...")
    
    print(f"\n{'='*60}")
    print("🌟 Theme testing complete!")
    print(f"{'='*60}")
