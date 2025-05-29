#!/usr/bin/env python3
"""
Test script for dreamnet with different themes
"""

import json
import os
import shutil

# Different brain configurations to test
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
    }
]

def test_theme(brain_data, theme_name):
    """Test a specific theme configuration"""
    print(f"\n🌟 Testing theme: {theme_name}")
    
    # Save current brain.json
    if os.path.exists("brain.json"):
        shutil.copy("brain.json", "brain_backup.json")
    
    # Write test brain
    with open("brain.json", 'w') as f:
        json.dump(brain_data, f, indent=2)
    
    # Run dreamnet
    os.system("python dream.py")
    
    # Read result
    with open("output.json", 'r') as f:
        result = json.load(f)
    
    print(f"✨ Result: {result['symbol']} | {result['phrase'][:50]}...")
    
    # Restore original brain
    if os.path.exists("brain_backup.json"):
        shutil.move("brain_backup.json", "brain.json")

if __name__ == "__main__":
    print("🌙 Dreamnet Theme Tester")
    
    for i, brain in enumerate(test_brains):
        test_theme(brain, f"Theme {i+1}")
    
    print("\n🌟 Theme testing complete!")
