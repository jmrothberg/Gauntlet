# JMR's Gauntlet: The Third Encounter - Game Documentation

A complete recreation of the classic Atari Lynx game *Gauntlet: The Third Encounter* with both desktop (Python/Pygame) and web (HTML5 Canvas) versions.

> **Note:** This file contains detailed gameplay documentation. For project overview and setup, see the main [README.md](README.md).

## Overview

This implementation faithfully recreates the original Gauntlet gameplay experience with modern code structure and cross-platform compatibility. Choose between running the game as a desktop application or directly in your web browser.

## Play In Browser

These HTML versions are served by GitHub Pages, GitHub's built-in static web hosting for this repository:

- [Gauntlet: Best Of](https://jmrothberg.github.io/Gauntlet/Gauntlet_bestof.html) - recommended browser/iPad/iPhone version with mobile controls, cleaned-up sprites, slime splitting, and best-of gameplay updates.
- [Gauntlet Oct 29 Single File](https://jmrothberg.github.io/Gauntlet/Gauntlet_1FILE_Oct_29_25.html) - newer of the two older HTML builds, with richer embedded bitmap sprites plus mobile/touch updates. It supersedes `Gauntlet_Lynx_Edition.html`.

## Features

### Core Gameplay
- **8 Character Classes**: Android, Valkyrie, Gunfighter, Nerd, Pirate, Punkrocker, Samurai, Wizard - each with unique stats
- **Real-time Combat**: Melee attacks and projectile shooting
- **11 Enemy Types**: Slime, Spider, Ghost, Frog, Scorpion, Skeleton, Demon variants, Orge, Cyclops, Chimera variants
- **6 Progressive Levels**: Increasing difficulty with procedural maze generation
- **Large Scrolling World**: 3072x3072 pixel world with interconnected rooms

### Items & Power-ups
- **Keys**: Unlock doors to progress through levels
- **Food**: Restores 10 HP immediately
- **Gold**: Collectible currency for shopping
- **Potions**: Speed (+40% movement), Strength (+2 melee damage), Missiles (+2 projectile damage)
- **Scrolls**: Invisibility, Farsee (minimap), Revive (auto-resurrection), Blast (kill all enemies)

### Game Systems
- **Shop System**: Terminal-based shops for purchasing items
- **Save/Load System**: Complete game state preservation
- **Inventory Management**: TAB to open/close, navigate with arrows, ENTER to use, D to drop
- **Difficulty Levels**: WOKE (easy), MEDIUM (medium), BASED (hard)
- **Status Effects**: Various timed effects that enhance gameplay

### Technical Features
- Procedural level generation with room-based maze layout
- Real-time game loop with delta time
- Collision detection with wall sliding
- Camera following within world bounds
- Comprehensive sound effects and visual effects
- Sprite-based rendering with fallback graphics

## Requirements

### Desktop Version (Python)
```
pygame
numpy
```
Python 3.6 or higher recommended.

### Web Version (HTML5)
No installation required - runs directly in modern web browsers with JavaScript enabled.

## Installation & Running

### Desktop Version

1. Install dependencies:
   ```bash
   pip install -r Gauntlet_requirements.txt
   ```

2. Run the game:
   ```bash
   python Gauntlet_Oct_27_25.py
   ```

### Web Version

1. Open one of the playable browser links above, or open the matching `.html` file locally.
2. For iPad/iPhone, use `Gauntlet_bestof.html` for the best touch controls.

## Controls

### Movement
- **WASD** or **Arrow Keys**: Move character
- **Mouse**: Aim (web version only)

### Combat
- **SPACE**: Melee attack (when near enemy) or shoot projectile

### Game Management
- **TAB** or **I**: Open/close inventory
- **P**: Pause/unpause game
- **S**: Save game (during gameplay)
- **C**: Switch character class (preserves stats)
- **H**: Help screen

### Menu Navigation
- **Arrow Keys**: Navigate menus
- **ENTER**: Select option
- **ESC**: Close menus or quit from main menu

## Gameplay Guide

### Objective
Collect all keys in each level to unlock doors and progress. Survive as long as possible while managing your health and resources.

### Character Classes
- **Android**: Balanced stats
- **Valkyrie**: High speed, medium strength
- **Gunfighter**: High missile damage
- **Nerd**: Low stats but can be fun
- **Pirate**: Balanced with pirate flair
- **Punkrocker**: High strength, low speed
- **Samurai**: Very high strength
- **Wizard**: Special abilities

### Hazards
- **Spikes**: Deal 10 damage/second on contact
- **Poison**: Deal 4 damage/second + slow movement
- **Slime**: Brief movement reduction on contact

### Tips
- Food restores health immediately - use it wisely
- Potions provide temporary boosts - timing matters
- Invisibility helps avoid enemies while collecting items
- Save frequently using the 'S' key
- Use the minimap (Farsee scroll) to plan your route

## Save Files

The game automatically saves to `gauntlet_save.json` when you save during gameplay. This preserves:
- Current level and position
- Character stats and inventory
- Active status effects
- Collected gold and items

## Technical Details

### Desktop Version
- Built with Pygame for cross-platform desktop gaming
- Uses numpy for mathematical operations
- Procedural sound generation for all game events
- Sprite-based rendering with animation frames

### Web Version
- Pure HTML5 Canvas implementation
- JavaScript port of the Python game logic
- Pixel-perfect rendering with crisp edges
- Touch/mobile friendly controls

### Architecture
- Real-time game loop with delta time calculations
- Room-based maze generation algorithm
- Collision detection system with wall sliding
- Camera system that follows player within world bounds

## Development Notes

This is a complete, faithful recreation of the original Gauntlet gameplay experience. The code is structured for maintainability and includes comprehensive documentation within the source files.

## Credits

Created by JMR - A tribute to the classic Atari Lynx game *Gauntlet: The Third Encounter*.

---

*Note: This is an unofficial fan recreation. All rights to the original Gauntlet game belong to their respective owners.*
