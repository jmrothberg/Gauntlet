#!/usr/bin/env python3
"""
extract_real_assets.py - Asset Extractor from Lynx Screenshots

This script extracts game assets from real Atari Lynx Gauntlet screenshots
and encodes them as base64 data URLs for embedding in HTML/JavaScript.

The script:
  1. Loads a Lynx Gauntlet screenshot image
  2. Crops various regions (player, floor, walls, etc.)
  3. Converts each crop to a base64-encoded PNG data URL
  4. Saves all assets to a JavaScript file (extracted_assets.js)

This allows the web game to use visuals derived from the original
Lynx game without needing separate image files.

Usage:
    python extract_real_assets.py

Prerequisites:
    - PIL (Pillow) library: pip install Pillow
    - Screenshot images in "Atari Gaunlet screen examples/" folder

Output:
    - extracted_assets.js - JavaScript object with base64 image data

Author: JMR
"""

from PIL import Image
import os
import base64
import json


def encode_img(img):
    """
    Encodes a PIL Image as a base64 data URL string.
    
    Args:
        img: PIL Image object to encode
        
    Returns:
        str: Data URL string in format "data:image/png;base64,..."
    """
    import io
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode('utf-8')

assets = {}

# Paths
screenshot_path = "Atari Gaunlet screen examples/Screenshot 2025-09-05 at 10.31.25 AM.png"
logo_path = "Atari Gaunlet screen examples/gauntlet.png"

if os.path.exists(screenshot_path):
    print(f"Processing {screenshot_path}...")
    try:
        ss = Image.open(screenshot_path)
        w, h = ss.size
        
        # Assuming the screenshot is a vertical gameplay capture
        # Center should be the player
        # We'll try to grab a 64x64 box from the center for the player
        cx, cy = w // 2, h // 2
        player_crop = ss.crop((cx - 30, cy - 30, cx + 30, cy + 30))
        assets['player_extracted'] = encode_img(player_crop)
        
        # Try to grab a floor tile. Usually near the player but not ON the player.
        # Let's try a bit to the left
        floor_crop = ss.crop((cx - 100, cy, cx - 60, cy + 40))
        assets['floor_extracted'] = encode_img(floor_crop)
        
        # Try to grab a wall tile. Walls are often high contrast.
        # This is a guess. We'll take a sample from the top left area which might be UI or Wall.
        # Actually, in Lynx Gauntlet, UI is often at the side or bottom.
        # Let's grab a few samples
        assets['sample_1'] = encode_img(ss.crop((100, 100, 140, 140)))
        assets['sample_2'] = encode_img(ss.crop((w-140, 100, w-100, 140)))
        
    except Exception as e:
        print(f"Error processing screenshot: {e}")

if os.path.exists(logo_path):
    print(f"Processing logo...")
    assets['logo'] = encode_img(Image.open(logo_path))

# Save to JS
with open('extracted_assets.js', 'w') as f:
    f.write("const EXTRACTED_ASSETS = ")
    json.dump(assets, f, indent=4)
    f.write(";")

print("Extraction complete.")

