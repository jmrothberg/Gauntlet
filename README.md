# Gauntlet: The Third Encounter

A faithful recreation of the classic **Atari Lynx** game *Gauntlet: The Third Encounter* with both desktop (Python/Pygame) and web (HTML5 Canvas) versions.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![HTML5](https://img.shields.io/badge/HTML5-Canvas-orange.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Overview

This project recreates the legendary dungeon-crawling action of Gauntlet with:
- **8 Playable Character Classes** with unique stats
- **11 Enemy Types** with distinct behaviors
- **6 Progressive Levels** with procedural maze generation
- **Full Combat System** with melee and ranged attacks
- **Items & Power-ups** including keys, food, potions, and scrolls
- **Shop System** for purchasing upgrades
- **Save/Load System** for game persistence

## Quick Start

### Web Version (Easiest)
Simply open `Gauntlet_1FILE_Oct_29_25.html` in any modern web browser. No installation required!

### Desktop Version (Python)
```bash
# Install dependencies
pip install -r Gauntlet_requirements.txt

# Run the game
python Gauntlet_Oct_27_25.py
```

## Screenshots

Screenshots and reference images are available in the `Atari Gaunlet screen examples/` folder.

## Project Structure

```
Gauntlet/
├── README.md                       # This file - project overview
├── gauntlet_readme.md              # Detailed gameplay documentation
├── Gauntlet_requirements.txt       # Python dependencies
│
├── GAME FILES
│   ├── Gauntlet_Oct_27_25.py       # Main Python/Pygame game (desktop)
│   ├── Gauntlet_1FILE_Oct_29_25.html   # Standalone HTML5 game (web)
│   └── Gauntlet_Lynx_Edition.html  # Alternative web version
│
├── BUILD SYSTEM
│   ├── build_game.py               # Builds HTML game with generated assets
│   ├── build_real_game.py          # Builds HTML game with real Lynx assets
│   ├── game_logic_lynx.js          # JavaScript game logic (Lynx style)
│   └── real_logic.js               # JavaScript logic for real assets
│
├── ASSET GENERATION
│   ├── generate_lynx_assets.py     # Generates Lynx-style sprites
│   ├── extract_real_assets.py      # Extracts assets from screenshots
│   └── convert_sprites_gui.py      # GUI tool for sprite conversion
│
├── SPRITE ASSETS
│   ├── Gauntlet_sprites/           # Game sprite images
│   ├── converted_sprites/          # Processed sprite files
│   └── Atari Gaunlet screen examples/  # Reference screenshots
│
├── DOCUMENTATION
│   └── EMBEDDED_SPRITES_README.md  # Sprite converter documentation
│
└── SAVE DATA
    └── gauntlet_save.json          # Game save file
```

## File Descriptions

### Main Game Files

| File | Description |
|------|-------------|
| `Gauntlet_Oct_27_25.py` | Full-featured desktop game using Python/Pygame with procedural sound, save system, and complete gameplay |
| `Gauntlet_1FILE_Oct_29_25.html` | Self-contained HTML5 game with all assets embedded - just open in browser |
| `Gauntlet_Lynx_Edition.html` | Alternative HTML version with Lynx-style presentation |

### Build Tools

| File | Description |
|------|-------------|
| `build_game.py` | Combines generated assets + game logic into standalone HTML |
| `build_real_game.py` | Combines extracted real assets + game logic into standalone HTML |
| `game_logic_lynx.js` | Core JavaScript game engine with Lynx-style gameplay |
| `real_logic.js` | JavaScript game logic optimized for real Lynx assets |

### Asset Tools

| File | Description |
|------|-------------|
| `generate_lynx_assets.py` | Programmatically creates Lynx-style sprites using PIL |
| `extract_real_assets.py` | Extracts and encodes assets from Lynx screenshots |
| `convert_sprites_gui.py` | GUI application for converting images to game sprites |

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrow Keys | Move character |
| SPACE | Melee attack (near enemy) or shoot projectile |
| TAB / I | Open/close inventory |
| P | Pause game |
| S | Save game |
| C | Switch character class |
| H | Help screen |
| ESC | Close menus / Quit |

## Character Classes

| Class | HP | Speed | Strength | Magic |
|-------|---:|------:|---------:|------:|
| Android | 100 | 4 | 3 | 1 |
| Valkyrie | 100 | 4 | 4 | 3 |
| Gunfighter | 80 | 5 | 4 | 2 |
| Nerd | 60 | 3 | 2 | 5 |
| Pirate | 120 | 3 | 5 | 1 |
| Punkrocker | 90 | 4 | 4 | 2 |
| Samurai | 110 | 4 | 5 | 1 |
| Wizard | 70 | 3 | 2 | 6 |

## Dependencies

### Python/Desktop Version
```
pygame
numpy
```

Install with: `pip install -r Gauntlet_requirements.txt`

### Web Version
No dependencies - runs in any modern browser with JavaScript enabled.

### Asset Tools
```
Pillow (PIL)
tkinter (usually included with Python)
```

## Building from Source

### Build HTML Game with Generated Assets
```bash
# 1. Generate sprite assets
python generate_lynx_assets.py

# 2. Build the HTML game
python build_game.py
# Output: Gauntlet_Lynx_Reforged.html
```

### Build HTML Game with Real Lynx Assets
```bash
# 1. Extract assets from screenshots
python extract_real_assets.py

# 2. Build the HTML game
python build_real_game.py
# Output: Gauntlet_Lynx_Real.html
```

## Detailed Documentation

For comprehensive gameplay documentation including:
- All item descriptions and effects
- Enemy types and behaviors
- Level progression details
- Hazard mechanics
- Tips and strategies

See [gauntlet_readme.md](gauntlet_readme.md)

## Credits

Created by **Jonathan M. Rothberg (JMR)** - A tribute to the classic Atari Lynx game *Gauntlet: The Third Encounter*.

## License

This is an unofficial fan recreation for educational purposes. All rights to the original Gauntlet game belong to their respective owners.

---

*"Blue Warrior needs food badly!"*
