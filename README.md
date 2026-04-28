# JMR's Gauntlet

A browser-playable tribute to *Gauntlet: The Third Encounter* — top-down dungeon-crawl with eight character classes, procedural levels, and touch controls for mobile.

## Play online

Hosted on GitHub Pages from the `main` branch:

- **[Gauntlet: Best Of](https://jmrothberg.github.io/Gauntlet/Gauntlet_bestof.html)** — recommended for desktop, iPad, and iPhone. Procedural pixel-art dungeons, Star Gem quest, mobile touch controls.
- **[Gauntlet (single-file)](https://jmrothberg.github.io/Gauntlet/Gauntlet_1FILE_Oct_29_25.html)** — same world with richer illustrative sprites and the full eight-class roster.

Either file also opens directly in any modern browser. No install required.

## What's in it

- **8 character classes** — Wizard, Valkyrie, Gunfighter, Android, Pirate, Punkrocker, Samurai, Nerd. Each has an idle pose and an attack pose that plays while firing or swinging.
- **Procedurally generated rooms, doors, and corridors** with wall-sliding collision and a camera that follows the player.
- **Combat** — melee when adjacent to an enemy, ranged projectiles otherwise. Hit-flash on damage.
- **Items** — apples and turkeys (heal), gold, keys, potions (speed, strength, missile boost), scrolls (blast, shield, revive, far-see, invisibility), and amulets.
- **Enemies** — slimes, spiders, scorpions, skeletons, ghosts, demons, ogres, gargoyles, orcs, beholders, sorcerers, and a stable of bosses available in `Graphics/sprites/unused/` for future levels (dragon, lich, succubus, dark knight, ice/lava elementals, …).
- **Mobile-first** — swipe to steer, on-screen MELEE/SHOOT/INV/START buttons.

## Controls

| Input | Action |
|---|---|
| Arrow keys / WASD | Move |
| Space | Melee (when adjacent) or shoot |
| Tab or I | Open / close inventory |
| P | Pause |
| Touch swipe | Move |
| On-screen buttons | Melee, shoot, inventory, start |

## Repo layout

```
Gauntlet/
├── Gauntlet_bestof.html             # procedural pixel-art build
├── Gauntlet_1FILE_Oct_29_25.html    # illustrative-sprite build
├── index.html                       # GitHub Pages entry
├── Gauntlet.png                     # social-card preview image
├── Graphics/
│   ├── *.png                        # 5 source sprite sheets (1254×1254 each)
│   └── sprites/
│       ├── *.png                    # 40 sprites used by both games
│       └── unused/*.png             # 40 spare sprites available for future use
├── tools/
│   ├── slice_sheets.py              # cuts sheets into named transparent PNGs
│   ├── wire_1file_sprites.py        # idempotent migration for the single-file build
│   └── wire_bestof_sprites.py       # idempotent migration for the best-of build
└── Atari Gaunlet screen examples/   # reference screenshots
```

## Updating sprites

Both games load `./Graphics/sprites/<name>.png` at runtime, so swapping or adding a sprite file is enough — no rebuild required.

To re-slice the source sheets after editing them:

```bash
python3 -m pip install pillow numpy scipy
python3 tools/slice_sheets.py
```

The slicer writes 80 named PNGs with transparent backgrounds into `Graphics/sprites/`. Any sprites that the games don't currently reference belong in `Graphics/sprites/unused/`.

## Credits

Created by **Jonathan M. Rothberg (JMR)** — a tribute to *Gauntlet: The Third Encounter*.

Unofficial fan recreation. All rights to the original Gauntlet game belong to their respective owners.
