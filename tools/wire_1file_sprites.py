#!/usr/bin/env python3
"""Rewrite the embeddedSprites map in Gauntlet_1FILE_Oct_29_25.html and apply
the small companion edits (smoothing, attack-frame state, sprite_key updates).

Idempotent: detects whether the file is already in the new state by looking
for an "./Graphics/sprites/" path in the embeddedSprites block.
"""

from pathlib import Path
import re
import sys

GAME = Path(__file__).resolve().parent.parent / "Gauntlet_1FILE_Oct_29_25.html"

# New map. Each key here is a string that the game references as a sprite key.
# tile_wall stays as the existing data URI (preserved verbatim) because we have
# no equivalent in the new sheets and the procedural fallback differs.
NEW_MAP_BODY = """    // Players (idle frame + attack frame)
    "Wizard":              "./Graphics/sprites/player_wizard.png",
    "Wizard_attack":       "./Graphics/sprites/player_wizard_attack.png",
    "valkyrie":            "./Graphics/sprites/player_valkyrie.png",
    "valkyrie_attack":     "./Graphics/sprites/player_valkyrie_attack.png",
    "gunfighter":          "./Graphics/sprites/player_gunfighter.png",
    "gunfighter_attack":   "./Graphics/sprites/player_gunfighter_attack.png",
    "android":             "./Graphics/sprites/player_android.png",
    "android_attack":      "./Graphics/sprites/player_android_attack.png",
    "pirate":              "./Graphics/sprites/player_pirate.png",
    "pirate_attack":       "./Graphics/sprites/player_pirate_attack.png",
    "punkrocker":          "./Graphics/sprites/player_punkrocker.png",
    "punkrocker_attack":   "./Graphics/sprites/player_punkrocker_attack.png",
    "samurai":             "./Graphics/sprites/player_samurai.png",
    "samurai_attack":      "./Graphics/sprites/player_samurai_attack.png",
    "nerd":                "./Graphics/sprites/player_nerd.png",
    "nerd_attack":         "./Graphics/sprites/player_nerd_attack.png",
    // Enemies
    "slime":               "./Graphics/sprites/enemy_slime_green.png",
    "enemy_spider":        "./Graphics/sprites/enemy_spider.png",
    "enemy_ghost":         "./Graphics/sprites/enemy_ghost.png",
    "enemy_scorpion":      "./Graphics/sprites/enemy_scorpion.png",
    "enemy_skeleton":      "./Graphics/sprites/enemy_skeleton.png",
    "enemy_demon":         "./Graphics/sprites/enemy_demon.png",
    "enemy_demon2":        "./Graphics/sprites/enemy_dark_sorcerer.png",
    "enemy_orge":          "./Graphics/sprites/enemy_ogre.png",
    "enemy_cyclops":       "./Graphics/sprites/enemy_beholder.png",
    "enemy_chimera1":      "./Graphics/sprites/enemy_gargoyle.png",
    "enemy_chimera2":      "./Graphics/sprites/enemy_orc.png",
    "enemy_chimera3":      "./Graphics/sprites/enemy_minotaur.png",
    // Items (per-type for variety)
    "item_apple":          "./Graphics/sprites/item_apple.png",
    "item_gold":           "./Graphics/sprites/item_gold_sack.png",
    "item_key":            "./Graphics/sprites/item_key_silver.png",
    "item_potion_speed":   "./Graphics/sprites/item_potion_blue.png",
    "item_potion_strength":"./Graphics/sprites/item_potion_red.png",
    "item_potion_missiles":"./Graphics/sprites/item_potion_green.png",
    "item_scroll_invisibility":"./Graphics/sprites/item_scroll_shield.png",
    "item_scroll_farsee":  "./Graphics/sprites/item_amulet_star.png",
    "item_potion_revive":  "./Graphics/sprites/item_scroll_revive.png",
    "item_scroll_blast":   "./Graphics/sprites/item_scroll_blast.png",
    // Backwards-compatible aliases for existing code paths
    "item_potion":         "./Graphics/sprites/item_potion_blue.png",
    "item_scroll":         "./Graphics/sprites/item_scroll_blast.png",
"""


def replace_embedded_sprites(text: str) -> str:
    """Replace the entire embeddedSprites block, preserving the tile_wall entry."""
    # Match: const embeddedSprites = { ... };  spanning multiple lines
    pattern = re.compile(
        r"(const embeddedSprites = \{)(.*?)(\n\s*\};)",
        re.DOTALL,
    )
    m = pattern.search(text)
    if m is None:
        sys.exit("Could not find embeddedSprites block")
    body = m.group(2)
    # Find the tile_wall line inside the body (it's a single line ending with a comma).
    tw_match = re.search(r'\n\s*"tile_wall":\s*"data:image[^\n]*?,?\s*(?=\n)', body)
    if tw_match is None:
        sys.exit("Could not find tile_wall entry")
    tile_wall_line = tw_match.group(0).strip().rstrip(",") + ","
    new_body = "\n" + NEW_MAP_BODY + "    " + tile_wall_line + "\n"
    return text[: m.start(2)] + new_body + text[m.end(2) :]


def add_image_smoothing(text: str) -> str:
    """After getContext('2d'), set image smoothing flags."""
    needle = "ctx = canvas.getContext('2d');"
    if needle not in text:
        sys.exit("Could not find getContext line")
    addition = (
        "ctx = canvas.getContext('2d');\n"
        "            ctx.imageSmoothingEnabled = true;\n"
        "            ctx.imageSmoothingQuality = 'high';"
    )
    if "ctx.imageSmoothingQuality" in text:
        return text  # idempotent
    return text.replace(needle, addition, 1)


def fix_spider_sprite(text: str) -> str:
    """SPIDER currently maps to enemy_scorpion; we now have a real spider sprite."""
    needle = (
        "} else if (enemy.type == EnemyType.SPIDER) {\n"
        "                    sprite_key = 'enemy_scorpion'; // Use scorpion sprite for spider"
    )
    fixed = (
        "} else if (enemy.type == EnemyType.SPIDER) {\n"
        "                    sprite_key = 'enemy_spider';"
    )
    return text.replace(needle, fixed, 1)


def differentiate_items(text: str) -> str:
    """Give each potion/scroll its own sprite instead of one-for-all."""
    old = """                if (item.type == ItemType.FOOD) {
                    sprite_key = 'item_apple';
                } else if (item.type == ItemType.GOLD) {
                    sprite_key = 'item_gold';
                } else if (item.type == ItemType.KEY) {
                    sprite_key = 'item_key';
                } else if (item.type == ItemType.POTION_SPEED || item.type == ItemType.POTION_STRENGTH || item.type == ItemType.POTION_MISSILES) {
                    sprite_key = 'item_potion';
                } else if (item.type == ItemType.SCROLL_INVISIBILITY || item.type == ItemType.SCROLL_FARSEE || item.type == ItemType.POTION_REVIVE || item.type == ItemType.SCROLL_BLAST) {
                    sprite_key = 'item_scroll';
                }"""
    new = """                if (item.type == ItemType.FOOD) {
                    sprite_key = 'item_apple';
                } else if (item.type == ItemType.GOLD) {
                    sprite_key = 'item_gold';
                } else if (item.type == ItemType.KEY) {
                    sprite_key = 'item_key';
                } else if (item.type == ItemType.POTION_SPEED) {
                    sprite_key = 'item_potion_speed';
                } else if (item.type == ItemType.POTION_STRENGTH) {
                    sprite_key = 'item_potion_strength';
                } else if (item.type == ItemType.POTION_MISSILES) {
                    sprite_key = 'item_potion_missiles';
                } else if (item.type == ItemType.SCROLL_INVISIBILITY) {
                    sprite_key = 'item_scroll_invisibility';
                } else if (item.type == ItemType.SCROLL_FARSEE) {
                    sprite_key = 'item_scroll_farsee';
                } else if (item.type == ItemType.POTION_REVIVE) {
                    sprite_key = 'item_potion_revive';
                } else if (item.type == ItemType.SCROLL_BLAST) {
                    sprite_key = 'item_scroll_blast';
                }"""
    if old not in text:
        if "sprite_key = 'item_potion_speed'" in text:
            return text  # already migrated
        sys.exit("Could not find item-mapping block to differentiate")
    return text.replace(old, new, 1)


def add_attack_frame_to_player_draw(text: str) -> str:
    """Make the player draw branch consult player.attack_anim_timer."""
    old = """            _draw_player(x, y) {
                const cls_name = this.player.character_class.name.toLowerCase();
                let bob = 0;
                if (this.player.anim_frame == 1) {
                    bob = -3;
                }

                // Try to use loaded sprites first
                let sprite_key = null;
                if (cls_name.includes('wizard')) {
                    sprite_key = 'Wizard'; // Capital W matches embedded_sprites.js
                } else if (cls_name.includes('gunfighter')) {
                    sprite_key = 'gunfighter';
                } else if (cls_name.includes('valkyrie')) {
                    sprite_key = 'valkyrie';
                } else if (cls_name.includes('android')) {
                    sprite_key = 'android';
                } else if (cls_name.includes('pirate')) {
                    sprite_key = 'pirate';
                } else if (cls_name.includes('punk')) {
                    sprite_key = 'punkrocker';
                } else if (cls_name.includes('nerd')) {
                    sprite_key = 'nerd';
                } else {
                    sprite_key = 'samurai';
                }

                // Always draw fallback for now to ensure visibility
                this._draw_character_fallback(x, y + bob, cls_name);

                // Try to draw sprite on top if available
                tryDrawSprite(sprite_key, x, y + bob, 32);"""

    new = """            _draw_player(x, y) {
                const cls_name = this.player.character_class.name.toLowerCase();
                let bob = 0;
                if (this.player.anim_frame == 1) {
                    bob = -3;
                }

                // Try to use loaded sprites first
                let sprite_key = null;
                if (cls_name.includes('wizard')) {
                    sprite_key = 'Wizard'; // Capital W matches embedded_sprites.js
                } else if (cls_name.includes('gunfighter')) {
                    sprite_key = 'gunfighter';
                } else if (cls_name.includes('valkyrie')) {
                    sprite_key = 'valkyrie';
                } else if (cls_name.includes('android')) {
                    sprite_key = 'android';
                } else if (cls_name.includes('pirate')) {
                    sprite_key = 'pirate';
                } else if (cls_name.includes('punk')) {
                    sprite_key = 'punkrocker';
                } else if (cls_name.includes('nerd')) {
                    sprite_key = 'nerd';
                } else {
                    sprite_key = 'samurai';
                }

                // Show attack frame briefly after firing/melee
                if ((this.player.attack_anim_timer || 0) > 0 && sprites[sprite_key + '_attack']) {
                    sprite_key = sprite_key + '_attack';
                }

                // Sprite-first; fall back to procedural shapes only if image missing
                if (!tryDrawSprite(sprite_key, x, y + bob, 32)) {
                    this._draw_character_fallback(x, y + bob, cls_name);
                }"""

    if old not in text:
        if "attack_anim_timer" in text:
            return text  # already migrated
        sys.exit("Could not find _draw_player to patch")
    return text.replace(old, new, 1)


def add_attack_timer_state(text: str) -> str:
    """Initialise attack_anim_timer on the player object and decay it per tick."""
    # Player init: missiles is a known Python-port field. Find a player-init block.
    # The simplest stable anchor is the player.missiles assignment around line 1955
    # within reset_level / resurrect:  this.player.missiles = ...
    # Instead we hook into update() near the projectile cooldown decay.
    old = """            update_projectiles(dt) {
                // Update firing cooldown
                if (this.shot_cooldown > 0) {
                    this.shot_cooldown = Math.max(0, this.shot_cooldown - dt);
                }"""
    new = """            update_projectiles(dt) {
                // Update firing cooldown
                if (this.shot_cooldown > 0) {
                    this.shot_cooldown = Math.max(0, this.shot_cooldown - dt);
                }
                // Attack-animation frame timer
                if (this.player && this.player.attack_anim_timer > 0) {
                    this.player.attack_anim_timer = Math.max(0, this.player.attack_anim_timer - dt);
                }"""
    if old not in text:
        if "attack_anim_timer = Math.max" in text:
            return text  # idempotent
        sys.exit("Could not find update_projectiles to patch")
    return text.replace(old, new, 1)


def trigger_attack_anim(text: str) -> str:
    """Set the attack anim timer when the player fires or attacks."""
    # Two trigger sites: play_attack() (melee) at ~3835 and play_shoot() (missile) at ~3954.
    # Add a single line right after each play_*() call.
    triggers = [
        ("                this.sound_manager.play_attack();\n",
         "                this.sound_manager.play_attack();\n                if (this.player) this.player.attack_anim_timer = 0.18;\n"),
        ("                // Play shooting sound\n                this.sound_manager.play_shoot();\n",
         "                // Play shooting sound\n                this.sound_manager.play_shoot();\n                if (this.player) this.player.attack_anim_timer = 0.18;\n"),
    ]
    for old, new in triggers:
        if new in text:
            continue  # already migrated this site
        if old not in text:
            sys.exit(f"Could not find attack trigger site: {old[:60]}...")
        text = text.replace(old, new, 1)
    return text


def main() -> None:
    text = GAME.read_text()
    original = text

    text = replace_embedded_sprites(text)
    text = add_image_smoothing(text)
    text = fix_spider_sprite(text)
    text = differentiate_items(text)
    text = add_attack_frame_to_player_draw(text)
    text = add_attack_timer_state(text)
    text = trigger_attack_anim(text)

    if text == original:
        print("No changes (already migrated).")
        return
    GAME.write_text(text)
    delta = len(text) - len(original)
    print(f"Updated {GAME.name}: size delta = {delta:+,} bytes")


if __name__ == "__main__":
    main()
