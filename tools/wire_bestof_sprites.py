#!/usr/bin/env python3
"""Rewrite the BESTOF_EMBEDDED_SPRITES map in Gauntlet_bestof.html to load
sprites from ./Graphics/sprites/, expand mappings to use the full new sprite
set, and wire up player attack-frame animation.

Idempotent.
"""

from pathlib import Path
import re
import sys

GAME = Path(__file__).resolve().parent.parent / "Gauntlet_bestof.html"

NEW_MAP_BODY = """  // Players (idle + attack)
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
  // Enemies (basic + boss-tier)
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
  "enemy_sorcerer_red":  "./Graphics/sprites/enemy_sorcerer_red.png",
  "enemy_orc":           "./Graphics/sprites/enemy_orc.png",
  "enemy_beholder":      "./Graphics/sprites/enemy_beholder.png",
  "enemy_death":         "./Graphics/sprites/enemy_death.png",
  // Items
  "item_apple":          "./Graphics/sprites/item_apple.png",
  "item_gold":           "./Graphics/sprites/item_gold_sack.png",
  "item_key":            "./Graphics/sprites/item_key_silver.png",
  "item_potion":         "./Graphics/sprites/item_potion_blue.png",
  "item_scroll":         "./Graphics/sprites/item_scroll_blast.png",
"""


def replace_embedded_sprites(text: str) -> str:
    pattern = re.compile(
        r"(const BESTOF_EMBEDDED_SPRITES = \{)(.*?)(\n\s*\};)",
        re.DOTALL,
    )
    m = pattern.search(text)
    if m is None:
        sys.exit("Could not find BESTOF_EMBEDDED_SPRITES block")
    body = m.group(2)
    tw_match = re.search(r'\n\s*"tile_wall":\s*"data:image[^\n]*?,?\s*(?=\n)', body)
    if tw_match is None:
        sys.exit("Could not find tile_wall entry in BESTOF map")
    tile_wall_line = tw_match.group(0).strip().rstrip(",") + ","
    new_body = "\n" + NEW_MAP_BODY + "  " + tile_wall_line + "\n"
    return text[: m.start(2)] + new_body + text[m.end(2) :]


def upgrade_mappings(text: str) -> str:
    """Replace installBestOfSpriteMappings with a richer mapping that:
       - exposes per-class _attack sprites (e.g. wizard_s_attack)
       - uses better matched art for sorcerer/lobber/death enemies
    """
    old = """function installBestOfSpriteMappings() {
  // Classes: keep gameplay names, but draw richer Oct 29 character art.
  useBestOfAnim('warrior_s_0', 'warrior_s_1', 'nerd');
  useBestOfAnim('warrior_n_0', 'warrior_n_1', 'nerd');
  useBestOfAnim('warrior_e_0', 'warrior_e_1', 'nerd');
  useBestOfAnim('warrior_w_0', 'warrior_w_1', 'nerd');
  useBestOfAnim('valkyrie_s_0', 'valkyrie_s_1', 'valkyrie');
  useBestOfAnim('wizard_s_0', 'wizard_s_1', 'Wizard');
  useBestOfAnim('archer_s_0', 'archer_s_1', 'gunfighter');
  useBestOfAnim('android_s_0', 'android_s_1', 'android');
  useBestOfAnim('samurai_s_0', 'samurai_s_1', 'samurai');
  useBestOfAnim('pirate_s_0', 'pirate_s_1', 'pirate');
  useBestOfAnim('punk_s_0', 'punk_s_1', 'punkrocker');

  // Enemies: map Oct 29 monster art to the active enemy IDs in this build.
  useBestOfAnim('scorpion_0', 'scorpion_1', 'enemy_scorpion');
  useBestOfAnim('slime_0', 'slime_1', 'slime');
  useBestOfAnim('skeleton_0', 'skeleton_1', 'enemy_skeleton');
  useBestOfAnim('ghost_0', 'ghost_1', 'enemy_ghost');
  useBestOfAnim('grunt_0', 'grunt_1', 'enemy_orge');
  useBestOfAnim('demon_0', 'demon_1', 'enemy_demon');
  useBestOfAnim('sorcerer_0', 'sorcerer_1', 'enemy_chimera1');
  useBestOfAnim('lobber_0', 'lobber_1', 'enemy_cyclops');
  useBestOfAnim('death_0', 'death_1', 'enemy_chimera3');

  // Items and wall tile: these are the clearest visual upgrades from Oct 29.
  useBestOfSprite('wall', 'tile_wall');
  // Keep wallOut procedural so grass biomes retain the green edge from the
  // original screenshots; dungeon biomes use the richer stone bitmap.
  useBestOfSprite('apple', 'item_apple');
  useBestOfSprite('key', 'item_key');
  useBestOfSprite('potion', 'item_potion');
  useBestOfSprite('gold', 'item_gold');
  useBestOfSprite('scroll', 'item_scroll');
  useBestOfSprite('treasure', 'item_gold');
}"""

    new = """function installBestOfSpriteMappings() {
  // Classes: idle in all directions, plus a per-class attack frame.
  // (Bestof has no per-direction art for these enemies, so all 4 dirs share.)
  const classes = [
    ['warrior', 'nerd'],
    ['valkyrie', 'valkyrie'],
    ['wizard', 'Wizard'],
    ['archer', 'gunfighter'],
    ['android', 'android'],
    ['samurai', 'samurai'],
    ['pirate', 'pirate'],
    ['punk', 'punkrocker'],
  ];
  for (const [name, key] of classes) {
    useBestOfSprite(name + '_s_0', key);
    useBestOfSprite(name + '_s_1', key);
    useBestOfSprite(name + '_n_0', key);
    useBestOfSprite(name + '_n_1', key);
    useBestOfSprite(name + '_e_0', key);
    useBestOfSprite(name + '_e_1', key);
    useBestOfSprite(name + '_w_0', key);
    useBestOfSprite(name + '_w_1', key);
    useBestOfSprite(name + '_attack', key + '_attack');
  }

  // Enemies: map Oct 29 monster art to the active enemy IDs in this build.
  useBestOfAnim('scorpion_0', 'scorpion_1', 'enemy_scorpion');
  useBestOfAnim('slime_0', 'slime_1', 'slime');
  useBestOfAnim('skeleton_0', 'skeleton_1', 'enemy_skeleton');
  useBestOfAnim('ghost_0', 'ghost_1', 'enemy_ghost');
  useBestOfAnim('grunt_0', 'grunt_1', 'enemy_orc');
  useBestOfAnim('demon_0', 'demon_1', 'enemy_demon');
  useBestOfAnim('sorcerer_0', 'sorcerer_1', 'enemy_sorcerer_red');
  useBestOfAnim('lobber_0', 'lobber_1', 'enemy_beholder');
  useBestOfAnim('death_0', 'death_1', 'enemy_death');

  // Items and wall tile.
  useBestOfSprite('wall', 'tile_wall');
  useBestOfSprite('apple', 'item_apple');
  useBestOfSprite('key', 'item_key');
  useBestOfSprite('potion', 'item_potion');
  useBestOfSprite('gold', 'item_gold');
  useBestOfSprite('scroll', 'item_scroll');
  useBestOfSprite('treasure', 'item_gold');
}"""
    if old not in text:
        if "useBestOfSprite(name + '_attack'" in text:
            return text  # already migrated
        sys.exit("Could not find installBestOfSpriteMappings to upgrade")
    return text.replace(old, new, 1)


def add_attack_anim_to_player(text: str) -> str:
    """Add an attackAnim timer that's set on shoot+melee, and use the attack
    sprite in drawPlayer when it's active."""

    # 1) Init the field on the player object literal (it has shootCd:0 line).
    init_old = "  shootCd: 0,"
    init_new = "  shootCd: 0,\n  attackAnim: 0,"
    if "attackAnim: 0," not in text:
        if init_old not in text:
            sys.exit("Could not find player.shootCd init line")
        text = text.replace(init_old, init_new, 1)

    # 2) Bump it on melee.
    melee_old = (
        "  if (inputMelee() && player.meleeCd <= 0) {\n"
        "    player.meleeCd = 0.3;\n"
        "    player.attacking = 0.15;\n"
        "    sfx('melee');\n"
        "    meleeAttack();\n"
        "  }"
    )
    melee_new = (
        "  if (inputMelee() && player.meleeCd <= 0) {\n"
        "    player.meleeCd = 0.3;\n"
        "    player.attacking = 0.15;\n"
        "    player.attackAnim = 0.18;\n"
        "    sfx('melee');\n"
        "    meleeAttack();\n"
        "  }"
    )
    if "player.attackAnim = 0.18" not in text:
        if melee_old not in text:
            sys.exit("Could not find melee block to add attackAnim")
        text = text.replace(melee_old, melee_new, 1)

    # 3) Bump it on shoot.
    shoot_old = (
        "  if (inputShoot() && player.shootCd <= 0 && player.missiles > 0) {\n"
        "    player.shootCd = 0.4;\n"
        "    if (!player.cheat) player.missiles--;\n"
        "    shootMissile();\n"
        "    sfx('shoot');\n"
        "  }"
    )
    shoot_new = (
        "  if (inputShoot() && player.shootCd <= 0 && player.missiles > 0) {\n"
        "    player.shootCd = 0.4;\n"
        "    player.attackAnim = 0.18;\n"
        "    if (!player.cheat) player.missiles--;\n"
        "    shootMissile();\n"
        "    sfx('shoot');\n"
        "  }"
    )
    if shoot_new not in text:
        if shoot_old not in text:
            sys.exit("Could not find shoot block to add attackAnim")
        text = text.replace(shoot_old, shoot_new, 1)

    # 4) Decay it.
    decay_old = "  player.shootCd = Math.max(0, player.shootCd - dt);"
    decay_new = (
        "  player.shootCd = Math.max(0, player.shootCd - dt);\n"
        "  player.attackAnim = Math.max(0, player.attackAnim - dt);"
    )
    if "player.attackAnim = Math.max" not in text:
        if decay_old not in text:
            sys.exit("Could not find shootCd decay line")
        text = text.replace(decay_old, decay_new, 1)

    # 5) Use _attack sprite when active in drawPlayer.
    draw_old = """  const f = player.frame;
  const cls = player.cls;
  let spr;
  // Warrior has full 4-dir sprites; other classes fall back to S-facing.
  if (cls === 'warrior') {
    if (player.facing === 's') spr = f ? SPR.warrior_s_1 : SPR.warrior_s_0;
    else if (player.facing === 'n') spr = f ? SPR.warrior_n_1 : SPR.warrior_n_0;
    else if (player.facing === 'e') spr = f ? SPR.warrior_e_1 : SPR.warrior_e_0;
    else spr = f ? SPR.warrior_w_1 : SPR.warrior_w_0;
  } else {
    spr = SPR[cls + '_s_' + f] || SPR.warrior_s_0;
  }
  drawSpriteAt(spr, player.x, player.y);"""

    draw_new = """  const f = player.frame;
  const cls = player.cls;
  let spr;
  // Show class-specific attack frame briefly after firing/melee.
  if (player.attackAnim > 0 && SPR[cls + '_attack']) {
    spr = SPR[cls + '_attack'];
  } else if (cls === 'warrior') {
    if (player.facing === 's') spr = f ? SPR.warrior_s_1 : SPR.warrior_s_0;
    else if (player.facing === 'n') spr = f ? SPR.warrior_n_1 : SPR.warrior_n_0;
    else if (player.facing === 'e') spr = f ? SPR.warrior_e_1 : SPR.warrior_e_0;
    else spr = f ? SPR.warrior_w_1 : SPR.warrior_w_0;
  } else {
    spr = SPR[cls + '_s_' + f] || SPR.warrior_s_0;
  }
  drawSpriteAt(spr, player.x, player.y);"""

    if "SPR[cls + '_attack']" not in text:
        if draw_old not in text:
            sys.exit("Could not find drawPlayer body to patch")
        text = text.replace(draw_old, draw_new, 1)

    return text


def main() -> None:
    text = GAME.read_text()
    original = text
    text = replace_embedded_sprites(text)
    text = upgrade_mappings(text)
    text = add_attack_anim_to_player(text)
    if text == original:
        print("No changes (already migrated).")
        return
    GAME.write_text(text)
    delta = len(text) - len(original)
    print(f"Updated {GAME.name}: size delta = {delta:+,} bytes")


if __name__ == "__main__":
    main()
