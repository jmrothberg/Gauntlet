#!/usr/bin/env python3
"""Slice the 5 Gauntlet sprite sheets into named, transparent-background PNGs.

Each sheet is 1254x1254, a 4x4 grid of cells (~313x313 each), with a uniform
grey gutter between cells. We slice on the grid, flood-fill the gutter from
the corners (so background-colored pixels INSIDE a sprite are preserved),
auto-crop to the sprite's bounding box, and save with descriptive names.
"""

from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SHEETS_DIR = ROOT / "Graphics"
OUT_DIR = SHEETS_DIR / "sprites"

# Cell layouts: { sheet_filename: { (col, row): output_name } }
LAYOUTS = {
    "003E5BD6-97D7-4C19-915B-AD517A7128D6.png": {
        (0, 0): "object_door_locked",
        (1, 0): "object_gate",
        (2, 0): "object_portal",
        (3, 0): "object_trapdoor",
        (0, 1): "object_generator",
        (1, 1): "object_plate_pressure",
        (2, 1): "object_torch_wall",
        (3, 1): "object_altar_skull",
        (0, 2): "object_spikes",
        (1, 2): "object_sawblade",
        (2, 2): "object_barrel",
        (3, 2): "object_crystal",
        (0, 3): "object_fountain",
        (1, 3): "object_statue",
        (2, 3): "object_rune_circle",
        (3, 3): "object_amulet_winged",
    },
    "1933436F-7F26-467E-B31B-47E7B106C2B1.png": {
        (0, 0): "enemy_slime_green",
        (1, 0): "enemy_slime_blue",
        (2, 0): "enemy_spider",
        (3, 0): "enemy_ghost",
        (0, 1): "enemy_scorpion",
        (1, 1): "enemy_skeleton",
        (2, 1): "enemy_demon",
        (3, 1): "enemy_sorcerer_red",
        (0, 2): "enemy_gargoyle",
        (1, 2): "enemy_orc",
        (2, 2): "enemy_beholder",
        (3, 2): "enemy_snake",
        (0, 3): "enemy_zombie",
        (1, 3): "enemy_ogre",
        (2, 3): "enemy_flame_skull",
        (3, 3): "enemy_blob",
    },
    "73A9BCD2-755B-4717-B087-8F0A458CC963.png": {
        (0, 0): "player_wizard",
        (1, 0): "player_wizard_attack",
        (2, 0): "player_valkyrie",
        (3, 0): "player_valkyrie_attack",
        (0, 1): "player_pirate",
        (1, 1): "player_pirate_attack",
        (2, 1): "player_gunfighter",
        (3, 1): "player_gunfighter_attack",
        (0, 2): "player_samurai",
        (1, 2): "player_samurai_attack",
        (2, 2): "player_android",
        (3, 2): "player_android_attack",
        (0, 3): "player_nerd",
        (1, 3): "player_nerd_attack",
        (2, 3): "player_punkrocker",
        (3, 3): "player_punkrocker_attack",
    },
    "9B3FCA69-5EA7-4ED0-9947-0FA52348A87A.png": {
        (0, 0): "enemy_death",
        (1, 0): "enemy_dark_sorcerer",
        (2, 0): "enemy_dragon",
        (3, 0): "enemy_golem_stone",
        (0, 1): "enemy_spider_queen",
        (1, 1): "enemy_minotaur",
        (2, 1): "enemy_mech",
        (3, 1): "enemy_lizardman",
        (0, 2): "enemy_lava_elemental",
        (1, 2): "enemy_ice_elemental",
        (2, 2): "enemy_swamp_horror",
        (3, 2): "enemy_dark_knight",
        (0, 3): "enemy_mech_scorpion",
        (1, 3): "enemy_succubus",
        (2, 3): "enemy_eye_of_doom",
        (3, 3): "enemy_lich",
    },
    "E464CCD0-247F-4495-A0DF-78BD60FE5A87.png": {
        (0, 0): "item_apple",
        (1, 0): "item_turkey",
        (2, 0): "item_gold_sack",
        (3, 0): "item_treasure_chest",
        (0, 1): "item_key_silver",
        (1, 1): "item_key_gold",
        (2, 1): "item_potion_blue",
        (3, 1): "item_potion_red",
        (0, 2): "item_potion_green",
        (1, 2): "item_potion_yellow",
        (2, 2): "item_scroll_speed",
        (3, 2): "item_scroll_strength",
        (0, 3): "item_scroll_blast",
        (1, 3): "item_scroll_shield",
        (2, 3): "item_scroll_revive",
        (3, 3): "item_amulet_star",
    },
}

# Cells per side; sheet is exactly cell_size * GRID
GRID = 4
# Each cell is built up of: thin dark outer border, then a hard jump to a
# light/white panel, then the sprite. We sample those background colors from
# fixed cell positions (corners + 12px insets), then clear ANY opaque pixel
# whose color is within COLOR_TOLERANCE of one of those samples — including
# enclosed panel pockets between sprite limbs that a flood-fill can't reach.
COLOR_TOLERANCE = 24  # how close to a sampled bg color to be considered bg
EDGE_PADDING = 4      # pixels added around the auto-cropped bounding box


def remove_background(cell_rgba: np.ndarray) -> np.ndarray:
    """Clear every pixel matching a sampled background color.

    Sample positions:
      - 4 corners of the cell    → outer dark border / gutter
      - 4 corners 12 px inset    → inner light panel
      - 4 mid-edge 12 px inset   → catches panel regions when corners sit on
                                   decorative frame elements

    Then for any pixel whose color is within COLOR_TOLERANCE of any sampled
    background color, set alpha=0. This handles enclosed panel pockets that
    a flood-fill couldn't reach (e.g. between a skeleton's legs).

    Tradeoff: a sprite pixel that happens to match the panel color exactly
    will also be cleared. The tolerance is kept moderate (24/255) so this is
    rare — sprite pixels typically have anti-aliased borders or saturation
    that distinguishes them from the flat panel grey.
    """
    h, w = cell_rgba.shape[:2]
    out = cell_rgba.copy()
    rgb = out[..., :3].astype(np.int16)

    inset = 12
    sample_positions = [
        (0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1),
        (inset, inset),
        (inset, w - 1 - inset),
        (h - 1 - inset, inset),
        (h - 1 - inset, w - 1 - inset),
        (inset, w // 2),
        (h - 1 - inset, w // 2),
        (h // 2, inset),
        (h // 2, w - 1 - inset),
    ]

    # Collect distinct background colors (dedupe similar ones)
    bg_colors: list[np.ndarray] = []
    for sy, sx in sample_positions:
        c = rgb[sy, sx]
        if any(np.max(np.abs(c - bc)) <= COLOR_TOLERANCE for bc in bg_colors):
            continue
        bg_colors.append(c)

    bg_mask = np.zeros((h, w), dtype=bool)
    for bc in bg_colors:
        dist = np.max(np.abs(rgb - bc), axis=2)
        bg_mask |= dist <= COLOR_TOLERANCE

    out[bg_mask, 3] = 0
    return out


def autocrop(rgba: np.ndarray) -> np.ndarray:
    """Crop to the bounding box of non-transparent pixels, plus padding."""
    alpha = rgba[..., 3]
    nonzero = np.argwhere(alpha > 0)
    if nonzero.size == 0:
        return rgba
    y0, x0 = nonzero.min(axis=0)
    y1, x1 = nonzero.max(axis=0) + 1
    h, w = rgba.shape[:2]
    y0 = max(0, y0 - EDGE_PADDING)
    x0 = max(0, x0 - EDGE_PADDING)
    y1 = min(h, y1 + EDGE_PADDING)
    x1 = min(w, x1 + EDGE_PADDING)
    return rgba[y0:y1, x0:x1]


def slice_sheet(sheet_path: Path, layout: dict[tuple[int, int], str]) -> int:
    img = Image.open(sheet_path).convert("RGBA")
    w, h = img.size
    cell_w = w // GRID
    cell_h = h // GRID
    arr = np.array(img)

    saved = 0
    for (col, row), name in layout.items():
        x0 = col * cell_w
        y0 = row * cell_h
        x1 = x0 + cell_w
        y1 = y0 + cell_h
        cell = arr[y0:y1, x0:x1].copy()
        cleaned = remove_background(cell)
        cropped = autocrop(cleaned)
        out_path = OUT_DIR / f"{name}.png"
        Image.fromarray(cropped, "RGBA").save(out_path, "PNG", optimize=True)
        saved += 1
    return saved


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for filename, layout in LAYOUTS.items():
        sheet = SHEETS_DIR / filename
        if not sheet.exists():
            print(f"  MISSING: {filename}")
            continue
        n = slice_sheet(sheet, layout)
        print(f"  {filename}: {n} sprites")
        total += n
    print(f"Wrote {total} sprites to {OUT_DIR}")


if __name__ == "__main__":
    main()
