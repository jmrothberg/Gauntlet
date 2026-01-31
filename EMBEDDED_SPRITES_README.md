# Image to Sprite Converter

A comprehensive utility for converting images to game sprites with transparency control. Supports both command-line and graphical interfaces.

## Features

- **Command Line Interface**: For automated/scripted conversions (`sprite_converter.py`)
- **Graphical User Interface**: Point-and-click interface (`convert_sprites_gui.py`)
- **Flexible Input**: Convert entire folders or single image files (PNG, JPG, BMP, GIF, TIFF)
- **Smart Transparency**: Automatically makes white backgrounds transparent
- **Dual Output Formats**: Generate PNG sprites or embedded JavaScript files
- **Batch Processing**: Convert multiple images at once
- **Transparency Control**: Toggle transparency on/off

## Installation

No additional dependencies required - uses only Python standard library.

## Usage

### GUI Version (Recommended for beginners)

Run the graphical interface:

```bash
python3 convert_sprites_gui.py
```

**GUI Features:**
- **Select Input**: Choose a folder with images or a single image file
- **Transparency Control**: Check/uncheck "Make white backgrounds transparent"
- **Output Format**: Choose PNG sprite or JavaScript embedded format
- **Auto-suggest**: Output filename is automatically suggested based on input
- **One-click conversion**: Click "🚀 Convert Sprites" to process

### Command Line Version

```bash
python3 sprite_converter.py <input_path> [-o output_file] [--no-transparent]
```

**Arguments:**
- `input_path`: Path to folder containing images or single image file
- `-o, --output`: Output file (PNG or JS)
- `--no-transparent`: Keep white backgrounds instead of making them transparent

### Command Line Version

```bash
python3 convert_sprites.py <input_path> [-o output_file]
```

**Arguments:**
- `input_path`: Path to folder containing PNG files or single PNG file
- `-o, --output`: Output JavaScript file (default: `embedded_sprites.js`)

**Examples:**

```bash
# Convert all PNGs in a folder
python3 convert_sprites.py Gauntlet_sprites/

# Convert single PNG file
python3 convert_sprites.py Gauntlet_sprites/gold.png

# Specify custom output file
python3 convert_sprites.py Gauntlet_sprites/ -o my_sprites.js
```

## Special Key Mappings

The converter automatically maps filenames to proper sprite keys used in the game:

| Filename | Sprite Key |
|----------|------------|
| `sumurai.png` | `samurai` |
| `red_demon_1.png` | `enemy_demon` |
| `red_demon_2.png` | `enemy_demon2` |
| `red_orge.png` | `enemy_orge` |
| `red_cyclops.png` | `enemy_cyclops` |
| `red_chimera_1.png` | `enemy_chimera1` |
| `red_chimera_2.png` | `enemy_chimera2` |
| `red_chimera_3.png` | `enemy_chimera3` |
| `Scorpion.png` | `enemy_scorpion` |
| `Skeleton.png` | `enemy_skeleton` |
| `small_ghost.png` | `enemy_ghost` |
| `Apple.png` | `item_apple` |
| `potion.png` | `item_potion` |
| `gold.png` | `item_gold` |
| `key.png` | `item_key` |
| `Scroll.png` | `item_scroll` |
| `doom_wall_texture.png` | `tile_wall` |

## Output Format

Generates a JavaScript file with embedded base64-encoded sprites:

```javascript
// Embedded sprite data
const embeddedSprites = {
    "samurai": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "enemy_demon": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    // ... more sprites
};
```

## Integration with Gauntlet

1. Convert your PNG sprites using either GUI or CLI
2. The generated JavaScript file can be included in your HTML
3. Access sprites in your game code using the embeddedSprites object

## Error Handling

- Validates input paths (must be directory or .png file)
- Shows clear error messages for invalid inputs
- GUI provides user-friendly error dialogs
- CLI provides console error messages

## Files

- `convert_sprites.py` - Command line version with reusable functions
- `convert_sprites_gui.py` - Graphical user interface
- `embedded_sprites.js` - Generated output file (created by converter)</content>
</xai:function_call">Write contents to /Users/jonathanrothberg/Gauntlet/EMBEDDED_SPRITES_README.md
