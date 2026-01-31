#!/usr/bin/env python3
"""
generate_lynx_assets.py - Programmatic Lynx-Style Asset Generator

This script generates game sprites programmatically using PIL/Pillow,
creating assets that mimic the Atari Lynx Gauntlet visual style.

Generated Assets:
  - Environment: Wall tiles (cobblestone), Floor tiles (stippled grey)
  - Characters: 8 playable classes (Android, Gunfighter, Nerd, Pirate,
                Punkrocker, Samurai, Valkyrie, Wizard)
  - Items: Gold coins, Food (apple), Potions, Keys
  - Enemies: Ghost, Demon

All sprites are converted to base64 data URLs and saved to a JavaScript
file (gauntlet_assets.js) for embedding in the HTML game.

Usage:
    python generate_lynx_assets.py

Prerequisites:
    - PIL (Pillow) library: pip install Pillow
    - Optional: gauntlet.png logo in "Atari Gaunlet screen examples/"

Output:
    - gauntlet_assets.js - JavaScript object with base64 sprite data

Author: JMR
"""

import base64
import json
import os
from PIL import Image, ImageDraw


def create_solid_sprite(width, height, color):
    """
    Creates a solid-colored sprite image.
    
    Args:
        width: Sprite width in pixels
        height: Sprite height in pixels
        color: RGBA tuple (r, g, b, a) for fill color
        
    Returns:
        PIL Image with solid color fill
    """
    img = Image.new('RGBA', (width, height), color)
    return img

def create_wall_sprite():
    """
    Creates a Lynx-style wall tile with cobblestone pattern.
    
    The wall features:
      - 4 stone blocks in 2x2 grid
      - Dark grout lines between stones
      - 3D effect with highlights and shadows on each stone
    
    Returns:
        PIL Image (40x40 RGBA) of the wall tile
    """
    # Lynx style: White/Grey cobble stones with black grout
    w, h = 40, 40
    img = Image.new('RGBA', (w, h), (20, 20, 20, 255)) # Dark grout
    draw = ImageDraw.Draw(img)
    
    # Draw stones
    stones = [
        (2, 2, 18, 18), (20, 2, 38, 18),
        (2, 20, 18, 38), (20, 20, 38, 38)
    ]
    for x1, y1, x2, y2 in stones:
        # Stone base
        draw.rectangle([x1, y1, x2, y2], fill=(180, 180, 180, 255))
        # Highlight
        draw.line([x1, y1, x2, y1], fill=(255, 255, 255, 255))
        draw.line([x1, y1, x1, y2], fill=(255, 255, 255, 255))
        # Shadow
        draw.line([x2, y1, x2, y2], fill=(100, 100, 100, 255))
        draw.line([x1, y2, x2, y2], fill=(100, 100, 100, 255))
        
    return img

def create_floor_sprite():
    """
    Creates a Lynx-style floor tile with stippled pattern.
    
    The floor features a dark grey base with lighter stipple dots
    arranged in a diagonal pattern for visual texture.
    
    Returns:
        PIL Image (40x40 RGBA) of the floor tile
    """
    # Stippled grey floor
    w, h = 40, 40
    img = Image.new('RGBA', (w, h), (50, 50, 50, 255))
    draw = ImageDraw.Draw(img)
    for i in range(0, w, 4):
        for j in range(0, h, 4):
            if (i+j)%8 == 0:
                draw.point((i, j), fill=(80, 80, 80, 255))
    return img

def create_char_sprite(color, shape_type):
    """
    Creates a character sprite with body, head, and optional headgear.
    
    Args:
        color: RGBA tuple for the body/clothing color
        shape_type: Type of headgear - 'helmet', 'hat', or 'none'
        
    Returns:
        PIL Image (32x32 RGBA) of the character sprite
    """
    # 32x32 Character Sprite
    img = Image.new('RGBA', (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Body
    draw.rectangle([8, 8, 24, 28], fill=color)
    # Head
    draw.rectangle([10, 2, 22, 10], fill=(255, 220, 180, 255)) # Skin
    
    if shape_type == 'helmet':
        draw.rectangle([9, 1, 23, 6], fill=(200, 200, 200, 255))
    elif shape_type == 'hat':
        draw.polygon([(16,0), (26,10), (6,10)], fill=color)
        
    # Eyes
    draw.point((12, 5), fill=(0,0,0,255))
    draw.point((19, 5), fill=(0,0,0,255))
    
    return img

def create_item_sprite(type):
    """
    Creates an item sprite based on item type.
    
    Args:
        type: Item type string - 'gold', 'food', 'potion', or 'key'
        
    Returns:
        PIL Image (24x24 RGBA) of the item sprite
    """
    img = Image.new('RGBA', (24, 24), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    if type == 'gold':
        draw.ellipse([2, 4, 22, 20], fill=(255, 215, 0, 255), outline=(200, 150, 0, 255))
        draw.text((8, 6), "$", fill=(50, 50, 0, 255))
    elif type == 'food':
        draw.ellipse([4, 8, 20, 22], fill=(200, 50, 50, 255)) # Apple
        draw.line([12, 8, 12, 2], fill=(0, 100, 0, 255), width=2)
    elif type == 'potion':
        draw.polygon([(8, 4), (16, 4), (20, 20), (4, 20)], fill=(50, 100, 200, 255), outline=(200, 200, 255, 255))
    elif type == 'key':
        draw.line([12, 4, 12, 20], fill=(200, 200, 50, 255), width=3)
        draw.rectangle([10, 4, 14, 8], fill=(200, 200, 50, 255))
        draw.rectangle([10, 16, 16, 20], fill=(200, 200, 50, 255))
        
    return img

def img_to_b64(img):
    """
    Converts a PIL Image to a base64 data URL string.
    
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

# 1. Generate Environment
assets['wall'] = img_to_b64(create_wall_sprite())
assets['floor'] = img_to_b64(create_floor_sprite())

# 2. Generate Characters (Lynx Classes)
# Android, Gunfighter, Nerd, Pirate, Punkrocker, Samurai, Valkyrie, Wizard
assets['android'] = img_to_b64(create_char_sprite((150, 150, 180, 255), 'helmet'))
assets['gunfighter'] = img_to_b64(create_char_sprite((100, 80, 50, 255), 'hat'))
assets['nerd'] = img_to_b64(create_char_sprite((50, 200, 50, 255), 'none'))
assets['pirate'] = img_to_b64(create_char_sprite((200, 50, 50, 255), 'hat'))
assets['punkrocker'] = img_to_b64(create_char_sprite((200, 50, 150, 255), 'none')) # Pink mohawk implied
assets['samurai'] = img_to_b64(create_char_sprite((200, 20, 20, 255), 'helmet'))
assets['valkyrie'] = img_to_b64(create_char_sprite((100, 100, 200, 255), 'helmet'))
assets['wizard'] = img_to_b64(create_char_sprite((50, 50, 150, 255), 'hat'))

# 3. Generate Items
for t in ['gold', 'food', 'potion', 'key']:
    assets[t] = img_to_b64(create_item_sprite(t))

# 4. Load Logo if available
logo_path = "Atari Gaunlet screen examples/gauntlet.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        assets['logo'] = "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
else:
    print("Logo not found, skipping")

# 5. Enemies
assets['ghost'] = img_to_b64(create_char_sprite((200, 200, 200, 150), 'none')) # Translucent
assets['demon'] = img_to_b64(create_char_sprite((200, 0, 0, 255), 'none'))

# Write
with open('gauntlet_assets.js', 'w') as f:
    f.write("const GAME_ASSETS = ")
    json.dump(assets, f, indent=4)
    f.write(";")
    
print("Assets generated.")

