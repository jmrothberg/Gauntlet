"""
JMR's Gauntlet: The Third Encounter (Atari Lynx) – Complete recreation in Pygame and HTML5.

CORE GAME FEATURES IMPLEMENTED:
===============================

1. MENU SYSTEM:
   - Main menu with options: New Game, Load Game, Level Select, Help
   - Difficulty selection (WOKE=easy, MEDIUM=medium, BASED=hard)
   - Character selection with 8 classes (Android, Valkyrie, Gunfighter, Nerd, Pirate, Punkrocker, Samurai, Wizard)
   - Each character has unique speed/strength/missiles stats

2. GAME WORLD:
   - Large scrolling world (3072x3072 pixels) with procedural room-based maze generation
   - Rooms connected by corridors with locked doors requiring keys
   - Multiple interconnected rooms per level, each with enemies and items
   - World margins prevent spawning at edges

3. COMBAT SYSTEM:
   - Real-time combat with melee (SPACE when near enemy) and ranged attacks (SPACE to shoot)
   - 11 enemy types: Slime, Spider, Ghost, Frog, Scorpion, Skeleton, Demon variants, Orge, Cyclops, Chimera variants
   - Enemies chase player (unless invisible), have different speeds and behaviors
   - Slime enemies split into smaller versions when killed
   - Projectile system with cooldowns

4. ITEMS & POWER-UPS:
   - Keys: Unlock doors to progress through levels
   - Food: Restores 10 HP immediately
   - Gold: Collectible currency for shopping
   - Potions: Speed (+40% movement), Strength (+2 melee damage), Missiles (+2 projectile damage)
   - Scrolls: Invisibility (enemies can't see player), Farsee (shows minimap), Revive (auto-resurrect), Blast (kill all enemies)

5. SHOP SYSTEM:
   - Terminal-based shops in dungeon rooms
   - Buy food, keys, potions, scrolls with gold
   - Shop interface with arrow key navigation

6. PROGRESSION & DIFFICULTY:
   - 6 levels with increasing difficulty
   - Difficulty affects enemy count and potion duration
   - Life drain over time (0.5 HP/second)
   - Level completion when all keys collected and doors opened

7. HAZARDS & ENVIRONMENTAL EFFECTS:
   - Spikes: Deal 10 damage/second on contact
   - Poison: Deal 4 damage/second + slow movement
   - Runes: Visual effect only
   - Slime slow: Brief movement reduction on contact

8. STATUS EFFECTS & TIMERS:
   - Speed potions: 40% movement bonus (duration based on difficulty)
   - Strength potions: +2 melee damage
   - Missile potions: +2 projectile damage
   - Invisibility: Enemies can't target player
   - Farsee: Shows full level minimap
   - Revive: Auto-resurrection on death

9. SAVE/LOAD SYSTEM:
   - Save game state to JSON file
   - Preserves level, score, difficulty, character, player stats, inventory, status effects
   - Load game restores complete state

10. HUD & UI:
    - Split-screen HUD: Left panel (life bar + status effects), Right panel (stats + inventory)
    - Big icon slot shows last pickup or enemy portrait
    - UI message log in bottom-right
    - Inventory management (TAB to open, arrows to navigate, ENTER to use, D to drop)
    - Farsee minimap when active

11. SOUND & VISUAL EFFECTS:
    - Procedural sound generation for all game events
    - Visual effects for potion usage, enemy hits, sword swings
    - Sprite-based rendering with fallbacks for all characters and enemies
    - Animation frames for walking characters

12. CONTROLS:
    - WASD/Arrow keys: Movement
    - SPACE: Melee attack (near enemy) or shoot projectile
    - TAB/I: Open/close inventory
    - P: Pause/unpause
    - S: Save game (in-game)
    - C: Switch character class (preserves stats)
    - H: Help screen
    - ESC: Close menus, quit from main menu

TECHNICAL IMPLEMENTATION:
=========================
- Pygame for desktop version, HTML5 Canvas for web version
- Procedural level generation with room-based maze layout
- Real-time game loop with delta time
- Collision detection with wall sliding
- Camera following player within world bounds
- Sprite loading with fallback graphics
- JSON save system with error handling
- Comprehensive input handling with key debouncing

This implementation faithfully recreates the classic Gauntlet gameplay experience
with modern code structure and cross-platform compatibility.
"""

import pygame
import sys
import math
import random
import time
import numpy as np
import os
import json
from enum import Enum

# Game Constants
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
GAME_WIDTH = 480    # Portrait game world width (viewport width)
# ADDED: Adjusted play/UI split to ~1/3 HUD, aligned to 32px tiles
GAME_HEIGHT = 544   # Viewport height (top play area)
UI_HEIGHT = 256     # Bottom HUD height
# Scrolling world (larger than viewport)
WORLD_WIDTH = 3072   # 96 tiles wide (doubled from 48)
WORLD_HEIGHT = 3072  # 96 tiles tall (doubled from 48)
WORLD_MARGIN = 128   # keep rooms away from world edges

# Colors (Atari Lynx palette approximation)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)

# Item Values & Effects
FOOD_VALUE = 10
POTION_SPEED_VALUE = 0.5
POTION_STRENGTH_VALUE = 1
POTION_MISSILES_VALUE = 1
REVIVE_VALUE = 0.5
STRENGTH_DAMAGE = 5
GOLD_VALUE = 100

# Player Stats
PLAYER_MAX_LIFE = 100
PLAYER_STARTING_GOLD = 500
PLAYER_MAX_INVENTORY = 12

# Shop Costs
KEY_COST = 150
POTION_COST = 100
SCROLL_COST = 150

# Enemy Spawning
ENEMY_CAP = 200
MIN_ENEMIES_PER_ROOM = 2
MAX_ENEMIES_PER_ROOM = 10

# Level Item Generation
BASE_CORRIDOR_FOOD = 20         # Minimum food in corridors
FOOD_PER_ROOM_MULTIPLIER = 2    # Additional corridor food per room
MIN_FOOD_PER_ROOM = 0           # Minimum food items per room
MAX_FOOD_PER_ROOM = 2           # Maximum food items per room
TERMINAL_CHANCE_PER_ROOM = 1.0  # Probability (0.0-1.0) of terminal in each room (1.0 = all rooms, 0.5 = half)

# Gold Generation
BASE_CORRIDOR_GOLD = 15         # Minimum gold in corridors
GOLD_PER_ROOM_MULTIPLIER = 1    # Additional corridor gold per room
GOLD_CHANCE_PER_ROOM = 0.5      # Probability (0.0-1.0) of gold in each room

# Key Generation
BASE_CORRIDOR_KEYS = 2          # Minimum keys in corridors
KEYS_PER_ROOM_MULTIPLIER = 0.5  # Additional corridor keys per room (0.5 = half as many as rooms)

# Damage & Health
LIFE_DRAIN_RATE = 0.5  # per second

# Hazard Damage (per second)
SPIKES_DAMAGE_RATE = 10.0
POISON_DAMAGE_RATE = 4.0

# Enemy Stats
ENEMY_MAX_LIFE = 10
ENEMY_BASE_SPEED = 0.5

# Status Effects & Timing
SLIME_SLOW_DURATION = 1.0  # seconds
POTION_DURATION = 20.0  # seconds
ENEMY_PORTRAIT_DURATION = 8.0  # seconds

# Scoring
ENEMY_KILL_SCORE = 100

# Animation & Timing
ANIMATION_FRAME_TIME = 0.1
SHOT_COOLDOWN = 0.18
MELEE_COOLDOWN = 1.0
KEY_DELAY = 0.2

# Character Classes - Each with unique stat balance for different playstyles
class CharacterClass:
    def __init__(self, name, speed, strength, missiles):
        self.name = name
        self.speed = speed          # Movement speed (higher = faster)
        self.strength = strength    # Melee damage bonus
        self.missiles = missiles    # Base projectile damage

# 8 playable character classes with distinct stat distributions
CHARACTER_CLASSES = {
    'android': CharacterClass('Android', 24, 7, 9),     # Balanced high missiles, good strength
    'valkyrie': CharacterClass('Valkyrie', 40, 3, 5),   # Highest speed, low defense (glass cannon)
    'gunfighter': CharacterClass('Gunfighter', 32, 4, 7), # Good speed + missiles (ranged focus)
    'nerd': CharacterClass('Nerd', 26, 2, 4),           # Lowest stats overall (challenge character)
    'pirate': CharacterClass('Pirate', 28, 5, 5),       # Balanced physical fighter
    'punkrocker': CharacterClass('Punkrocker', 29, 5, 6), # Good all-around stats
    'samurai': CharacterClass('Samurai', 34, 6, 5),     # High strength + speed (melee focus)
    'wizard': CharacterClass('Wizard', 28, 3, 8)        # Highest missiles, low defense (magic focus)
}

# Game State Management - Controls which screen/menu is active
class GameState(Enum):
    MENU = 0              # Main menu screen
    DIFFICULTY_SELECT = 1  # Difficulty selection (WOKE/MEDIUM/BASED)
    CHARACTER_SELECT = 2   # Character class selection (8 classes)
    PLAYING = 3           # Active gameplay
    PAUSED = 8            # Game paused (P key)
    GAME_OVER = 4         # Player died
    LEVEL_COMPLETE = 5    # All keys collected, level finished
    SHOP = 6              # Shop interface (at terminals)
    LEVEL_SELECT = 7      # Debug level selector
    HELP = 9              # Help/controls screen

# Movement Directions - Used for player, enemies, projectiles
class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

# Item Types - All collectible/power-up items in the game
class ItemType(Enum):
    FOOD = 0              # Restores 10 HP immediately
    KEY = 1               # Unlocks doors (required for progression)
    GOLD = 2              # Currency for shopping
    POTION_SPEED = 3      # +40% movement speed for duration
    POTION_STRENGTH = 4   # +2 melee damage
    POTION_MISSILES = 5   # +2 projectile damage
    SCROLL_INVISIBILITY = 6 # Enemies can't see/target player
    SCROLL_FARSEE = 7     # Shows full level minimap
    SCROLL_REVIVE = 8     # Auto-resurrection on death
    SCROLL_BLAST = 9      # Kill all enemies on screen

# Enemy Types - 11 different enemy varieties with unique behaviors
class EnemyType(Enum):
    SLIME = 0      # Splits when killed, slow movement, poison effect
    SPIDER = 1     # Fast, aggressive
    GHOST = 2      # Semi-transparent, floats through some terrain
    FROG = 3       # Demon-like enemy
    SCORPION = 4   # Poison stinger, armored
    SKELETON = 5   # Undead warrior
    DEMON2 = 6     # Two-headed demon
    ORGE = 7       # Large brutish enemy
    CYCLOPS = 8    # One-eyed giant
    CHIMERA1 = 9   # Three-headed beast variant 1
    CHIMERA2 = 10  # Three-headed beast variant 2
    CHIMERA3 = 11  # Three-headed beast variant 3

# Environmental Hazards - Damage zones in dungeon rooms
class HazardType(Enum):
    SPIKES = 0     # Deals 10 damage/second on contact
    RUNE = 1       # Visual effect only (aesthetic)
    POISON = 2     # Deals 4 damage/second + movement slow

# Difficulty Levels - Affects enemy count and potion duration
class Difficulty(Enum):
    WOKE = 0      # Easy: 6x potion time, 1/6 monsters
    MEDIUM = 1    # Medium: 3x potion time, 1/3 monsters
    BASED = 2     # Hard: 1x potion time, 1x monsters (normal)

# Difficulty scaling multipliers applied to gameplay
DIFFICULTY_MULTIPLIERS = {
    Difficulty.WOKE: {'potion': 6.0, 'monsters': 1/6.0},    # Very easy - long power-ups, few enemies
    Difficulty.MEDIUM: {'potion': 3.0, 'monsters': 1/3.0},  # Moderate challenge
    Difficulty.BASED: {'potion': 1.0, 'monsters': 1.0}      # Normal difficulty (original Gauntlet)
}

# Main Game Class - Manages all game state, rendering, and logic
class GauntletGame:
    def __init__(self):
        # Initialize Pygame subsystems
        pygame.init()
        pygame.mixer.init()

        # Set up display window (portrait orientation for mobile-like feel)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("JMR's Gauntlet: The Third Encounter")

        # Core game state variables
        self.state = GameState.MENU  # Start at main menu
        self.current_level = 1       # Current dungeon level (1-6)
        self.score = 0               # Player score (enemy kills)
        self.difficulty = Difficulty.BASED  # Default to hard difficulty
        self.player = None           # Player character instance
        self.enemies = []            # List of active enemies
        self.items = []              # List of items on ground
        self.level_data = None       # Current level layout data

        # Menu state tracking
        self.selected_character_index = 0
        self.character_keys = list(CHARACTER_CLASSES.keys())

        # Combat system state
        self.projectiles = []        # Active projectile shots

        # Visual effects system
        self.effects = []            # Temporary visual effects (auras, sword swings)
        self.last_pickup_type = None # Last item collected (for HUD icon)
        self.last_enemy_hit = None   # Last enemy damaged (for portrait display)
        self.enemy_portrait_timer = 0.0  # How long to show enemy portrait

        # Sprite management
        self.sprites = {}            # Loaded sprite images
        self._load_sprites()         # Load all game sprites

        # Sprite key mappings for easy item rendering
        self._common_sprites = {
            ItemType.KEY: 'item_key',
            ItemType.FOOD: 'item_apple',
            ItemType.GOLD: 'item_gold',
            ItemType.POTION_SPEED: 'item_potion',
            ItemType.POTION_STRENGTH: 'item_potion',
            ItemType.POTION_MISSILES: 'item_potion',
        }

        # UI font system (monospace for retro feel)
        self.font_tiny = pygame.font.SysFont("Courier", 16)     # HUD messages
        self.font_mini = pygame.font.SysFont("Courier", 14)     # Help screen (compact)
        self.font_small = pygame.font.SysFont("Courier", 18)    # Menu text
        self.font_medium = pygame.font.SysFont("Courier", 24)   # Titles
        self.font_large = pygame.font.SysFont("Courier", 32)    # Main headings

        # Timing and performance
        self.clock = pygame.time.Clock()          # Frame rate control
        self.last_update = time.time()            # For delta time calculation

        # Input system with debouncing
        self.keys_pressed = {}                    # Currently held keys
        self.shop_block_until_exit = False        # Prevents shop spam
        self.help_entered_this_frame = False      # Help screen state
        self.shop_cooldown = 0                    # Shop interaction cooldown
        self.last_key_time = 0.0                  # Menu navigation debounce
        self.key_delay = 0.2                      # 200ms debounce for menus

        # Audio system (procedural sound generation)
        self.sound_manager = SoundManager()

        # UI messaging system (bottom-right HUD messages)
        self.ui_messages = []  # List of [message, timestamp] pairs

        # Environmental effects
        self.player_slow_timer = 0.0  # Slime contact slow effect

        # Graphics initialization
        self._init_retro_tiles()  # Generate tile textures
        self._init_sprites()       # Initialize sprite surfaces

        # Camera system (follows player in large world)
        self.camera_x = 0
        self.camera_y = 0

        # Welcome message
        self.add_ui_message("Gauntlet initialized!")

        # Inventory system
        self.inventory_open = False
        self.inventory_cursor = 0

        # Status effects tracking (potions, scrolls, etc.)
        self.status_effects = {
            'speed': 0.0,      # Movement speed bonus timer
            'strength': 0.0,   # Melee damage bonus timer
            'missiles': 0.0,   # Projectile damage bonus timer
            'shield': 0.0,     # Damage reduction timer
            'invis': 0.0,      # Invisibility timer
            'revive': 0,       # Number of revive charges
        }
        self.farsee_timer = 0.0  # Farsee scroll minimap timer

    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Always set key state for all states to ensure proper handling
                    self.keys_pressed[event.key] = True

                    # Global ESC handling - only quit from menu or game over
                    if event.key == pygame.K_ESCAPE:
                        if self.state in [GameState.MENU, GameState.GAME_OVER]:
                            running = False
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING  # Unpause with ESC

                    # Pause/unpause with P key during gameplay
                    elif event.key == pygame.K_p:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.PAUSED
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING

                elif event.type == pygame.KEYUP:
                    # Clear key state when released
                    if event.key in self.keys_pressed:
                        del self.keys_pressed[event.key]

            # Update game state
            self.update(dt)

            # Render
            self.render()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def update(self, dt):
        """Update game logic"""
        if self.state == GameState.MENU:
            self.update_menu()
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.update_difficulty_select()
        elif self.state == GameState.CHARACTER_SELECT:
            self.update_character_select()
        elif self.state == GameState.PLAYING:
            self.update_playing(dt)
        elif self.state == GameState.PAUSED:
            self.update_paused()
        elif self.state == GameState.GAME_OVER:
            self.update_game_over()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.update_level_complete()
        elif self.state == GameState.SHOP:
            self.update_shop()
        elif self.state == GameState.LEVEL_SELECT:
            self.update_level_select()
        elif self.state == GameState.HELP:
            self.update_help()

    def render(self):
        """Render the current game state"""
        # Don't fill screen with black for help screen to prevent flashing
        if self.state != GameState.HELP:
            self.screen.fill(BLACK)

        if self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.DIFFICULTY_SELECT:
            self.render_difficulty_select()
        elif self.state == GameState.CHARACTER_SELECT:
            self.render_character_select()
        elif self.state == GameState.PLAYING:
            self.render_playing()
        elif self.state == GameState.PAUSED:
            self.render_paused()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.render_level_complete()
        elif self.state == GameState.SHOP:
            self.render_shop()
        elif self.state == GameState.LEVEL_SELECT:
            self.render_level_select()
        elif self.state == GameState.HELP:
            self.render_help()

        # FIX: render transient UI messages on top of HUD in bottom-right
        # Don't show messages during pause, help, inventory, or when Farsee is active
        show_messages = (
            self.state not in [GameState.PAUSED, GameState.HELP] and 
            not (hasattr(self, 'inventory_open') and self.inventory_open) and
            not (hasattr(self, 'farsee_timer') and self.farsee_timer > 0)
        )
        if show_messages:
            self._render_ui_messages()

    def add_ui_message(self, text):
        """Add a short HUD message to display in bottom-right; keep last 6."""
        if not hasattr(self, 'ui_messages'):
            self.ui_messages = []
        timestamp = time.time()
        self.ui_messages.append((text, timestamp))
        # Keep only the last 6 messages
        if len(self.ui_messages) > 6:
            self.ui_messages = self.ui_messages[-6:]

    def _render_ui_messages(self):
        """Draw recent UI messages in the bottom-right over the HUD."""
        if not hasattr(self, 'ui_messages') or not self.ui_messages:
            return
        # Keep only the last 6 messages (no time-based expiration)
        if len(self.ui_messages) > 6:
            self.ui_messages = self.ui_messages[-6:]
        if not self.ui_messages:
            return
        # Bottom-right origin inside HUD right panel
        left_w = SCREEN_WIDTH // 2
        bottom_y = GAME_HEIGHT
        padding = 8
        x = left_w + padding
        y = bottom_y + UI_HEIGHT - padding
        # Draw from newest upward
        for text, _ in reversed(self.ui_messages):
            surf = self.font_tiny.render(text, True, (255, 255, 0))
            y -= surf.get_height() + 2
            # Simple shadow for readability
            self.screen.blit(self.font_tiny.render(text, True, (0, 0, 0)), (x+1, y+1))
            self.screen.blit(surf, (x, y))

    def update_menu(self):
        """Update main menu logic"""
        if pygame.K_RETURN in self.keys_pressed:
            self.state = GameState.DIFFICULTY_SELECT
            self.keys_pressed[pygame.K_RETURN] = False
            self.last_key_time = pygame.time.get_ticks() / 1000.0  # Reset debounce timer
        elif pygame.K_l in self.keys_pressed:  # L key for level select
            self.state = GameState.LEVEL_SELECT
            self.selected_level = 1
            self.keys_pressed[pygame.K_l] = False
        elif pygame.K_s in self.keys_pressed:  # S key for load saved game
            self.load_game()
            self.keys_pressed[pygame.K_s] = False
            self.last_key_time = pygame.time.get_ticks() / 1000.0
        elif pygame.K_h in self.keys_pressed:  # H key for help
            self.help_previous_state = self.state  # Remember where we came from
            self.state = GameState.HELP
            self.help_entered_this_frame = True
            self.help_ignore_h_until_release = True  # Ignore H until released
            self.keys_pressed[pygame.K_h] = False
        elif pygame.K_ESCAPE in self.keys_pressed:
            # ESC in menu quits the game
            import sys
            pygame.quit()
            sys.exit()

    def render_menu(self):
        """Render main menu"""
        title_text = self.font_large.render("JMR's GAUNTLET", True, YELLOW)
        subtitle_text = self.font_medium.render("The Third Encounter", True, GREEN)
        start_text = self.font_small.render("ENTER: Start New Game", True, WHITE)
        load_text = self.font_small.render("S: Load Saved Game", True, GREEN)
        level_text = self.font_small.render("L: Level Select", True, CYAN)
        help_text = self.font_small.render("H: Help/Controls", True, ORANGE)

        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 80))
        self.screen.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, 140))
        self.screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 260))
        self.screen.blit(load_text, (SCREEN_WIDTH//2 - load_text.get_width()//2, 300))
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 340))
        self.screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, 380))

        # Character selection
        self.selected_character_index = 0
        self.character_keys = list(CHARACTER_CLASSES.keys())

        # Shop cooldown to prevent flashing
        self.shop_cooldown = 0
        # Key handling for shop
        self.last_key_time = 0
        self.key_delay = 0.2  # 200ms delay between key presses
        # Help screen state management
        self.help_entered_this_frame = False
        self.help_previous_state = None
        self.help_ignore_h_until_release = False

    def update_character_select(self):
        """Update character selection logic (with simple debounce)."""
        now = pygame.time.get_ticks() / 1000.0
        if now - self.last_key_time < 0.15:
            return
        if pygame.K_UP in self.keys_pressed:
            self.selected_character_index = (self.selected_character_index - 1) % len(CHARACTER_CLASSES)
            self.keys_pressed[pygame.K_UP] = False
            self.last_key_time = now
        elif pygame.K_DOWN in self.keys_pressed:
            self.selected_character_index = (self.selected_character_index + 1) % len(CHARACTER_CLASSES)
            self.keys_pressed[pygame.K_DOWN] = False
            self.last_key_time = now
        elif pygame.K_RETURN in self.keys_pressed:
            selected_class = self.character_keys[self.selected_character_index]
            self.start_game(selected_class)
            self.keys_pressed[pygame.K_RETURN] = False
            self.last_key_time = now
        elif pygame.K_ESCAPE in self.keys_pressed:
            self.state = GameState.MENU
            self.keys_pressed[pygame.K_ESCAPE] = False
            self.last_key_time = now

    def render_character_select(self):
        """Render character selection screen"""
        select_text = self.font_large.render("Select Character", True, YELLOW)
        self.screen.blit(select_text, (SCREEN_WIDTH//2 - select_text.get_width()//2, 50))

       
        y_pos = 96
        line_step = 42
        for i, (key, char_class) in enumerate(CHARACTER_CLASSES.items()):
            color = GREEN if i == self.selected_character_index else WHITE
            arrow = ">" if i == self.selected_character_index else " "
            class_text = self.font_medium.render(
                f"{arrow} {char_class.name}", True, color
            )
            stats_text = self.font_small.render(
                f"   Spd:{char_class.speed} Str:{char_class.strength} Msl:{char_class.missiles}",
                True, GRAY
            )
            self.screen.blit(class_text, (50, y_pos))
            self.screen.blit(stats_text, (50, y_pos + 28))

            

            y_pos += line_step

        # Character description placed above instructions
        selected_class = CHARACTER_CLASSES[self.character_keys[self.selected_character_index]]
        desc = ""
        if selected_class.name == "Android":
            desc = "Balanced stats, reliable choice"
        elif selected_class.name == "Valkyrie":
            desc = "Highest speed, low defense"
        elif selected_class.name == "Gunfighter":
            desc = "Good speed and missiles"
        elif selected_class.name == "Nerd":
            desc = "Lowest stats, challenge mode"
        elif selected_class.name == "Pirate":
            desc = "Balanced physical fighter"
        elif selected_class.name == "Punkrocker":
            desc = "Good all-around stats"
        elif selected_class.name == "Samurai":
            desc = "High strength and speed"
        elif selected_class.name == "Wizard":
            desc = "Highest missiles, low defense"
        desc_y = GAME_HEIGHT - 92
        if desc:
            desc_text = self.font_medium.render(desc, True, CYAN)
            self.screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, desc_y))

        # Instructions pinned to very bottom (two lines, narrower)
        nav = self.font_small.render("UP/DOWN: Navigate", True, WHITE)
        act = self.font_small.render("ENTER: Select    ESC: Back", True, WHITE)
        self.screen.blit(nav, (SCREEN_WIDTH//2 - nav.get_width()//2, GAME_HEIGHT - 44))
        self.screen.blit(act, (SCREEN_WIDTH//2 - act.get_width()//2, GAME_HEIGHT - 24))

    def update_difficulty_select(self):
        """Update difficulty selection logic"""
        now = pygame.time.get_ticks() / 1000.0
        if now - self.last_key_time < 0.15:
            return
        if pygame.K_UP in self.keys_pressed:
            # Cycle difficulty backward
            difficulties = list(Difficulty)
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index - 1) % len(difficulties)]
            self.keys_pressed[pygame.K_UP] = False
            self.last_key_time = now
        elif pygame.K_LEFT in self.keys_pressed:
            # Cycle difficulty backward (alternative)
            difficulties = list(Difficulty)
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index - 1) % len(difficulties)]
            self.keys_pressed[pygame.K_LEFT] = False
            self.last_key_time = now
        elif pygame.K_DOWN in self.keys_pressed:
            # Cycle difficulty forward
            difficulties = list(Difficulty)
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
            self.keys_pressed[pygame.K_DOWN] = False
            self.last_key_time = now
        elif pygame.K_RIGHT in self.keys_pressed:
            # Cycle difficulty forward (alternative)
            difficulties = list(Difficulty)
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
            self.keys_pressed[pygame.K_RIGHT] = False
            self.last_key_time = now
        elif pygame.K_RETURN in self.keys_pressed:
            self.state = GameState.CHARACTER_SELECT
            self.keys_pressed[pygame.K_RETURN] = False
            self.last_key_time = now
        elif pygame.K_ESCAPE in self.keys_pressed:
            self.state = GameState.MENU
            self.keys_pressed[pygame.K_ESCAPE] = False
            self.last_key_time = now

    def render_difficulty_select(self):
        """Render difficulty selection screen"""
        title_text = self.font_large.render("Select Difficulty", True, YELLOW)
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))

        difficulties = [
            ("WOKE", "Easy - 6x potions, 1/6 monsters", Difficulty.WOKE),
            ("MEDIUM", "Medium - 3x potions, 1/3 monsters", Difficulty.MEDIUM),
            ("BASED", "Hard - Normal difficulty", Difficulty.BASED)
        ]

        y_pos = 120
        for name, desc, diff_enum in difficulties:
            if diff_enum == self.difficulty:
                color = GREEN
                arrow = ">"
                name_color = YELLOW
            else:
                color = WHITE
                arrow = " "
                name_color = WHITE

            name_text = self.font_large.render(f"{arrow} {name}", True, name_color)
            desc_text = self.font_small.render(desc, True, color)

            self.screen.blit(name_text, (100, y_pos))
            self.screen.blit(desc_text, (120, y_pos + 32))
            y_pos += 80

        # Instructions
        nav = self.font_small.render("UP/DOWN or LEFT/RIGHT: Change Difficulty", True, WHITE)
        act = self.font_small.render("ENTER: Continue    ESC: Back", True, WHITE)
        self.screen.blit(nav, (SCREEN_WIDTH//2 - nav.get_width()//2, GAME_HEIGHT - 44))
        self.screen.blit(act, (SCREEN_WIDTH//2 - act.get_width()//2, GAME_HEIGHT - 24))

    def start_game(self, character_class):
        """Initialize game with selected character"""
        self.current_character_key = character_class  # Track key to avoid KeyError on level advance
        self.player = Player(character_class, 1)  # Start at level 1
        self.player.game = self
        self.state = GameState.PLAYING
        self.load_level(1)
        print(f"Starting game with {character_class}")

    def save_game(self):
        """Save current game state to file"""
        try:
            # Check if we have a valid game state to save
            if not hasattr(self, 'player') or not self.player:
                self.add_ui_message("No active game to save!")
                return

            if not hasattr(self, 'current_level'):
                self.add_ui_message("Game not properly initialized!")
                return

            # Ensure all required attributes exist with defaults
            current_level = getattr(self, 'current_level', 1)
            score = getattr(self, 'score', 0)
            difficulty_name = getattr(self.difficulty, 'name', 'BASED') if hasattr(self, 'difficulty') and self.difficulty else 'BASED'
            character_key = getattr(self, 'current_character_key', 'android')

            # Build save data with safe attribute access
            save_data = {
                'current_level': current_level,
                'score': score,
                'difficulty': difficulty_name,
                'character_class': character_key,
                'player_data': {
                    'life': getattr(self.player, 'life', 100),
                    'max_life': getattr(self.player, 'max_life', 100),
                    'gold': getattr(self.player, 'gold', 0),
                    'keys_collected': getattr(self.player, 'keys_collected', 0),
                    'inventory': [],
                    'speed': getattr(self.player, 'speed', 1.0),
                    'strength': getattr(self.player, 'strength', 1.0),
                    'missiles': getattr(self.player, 'missiles', 1.0)
                },
                'status_effects': getattr(self, 'status_effects', {}),
                'farsee_timer': getattr(self, 'farsee_timer', 0.0),
                'timestamp': time.time()
            }

            # Safely handle inventory
            if hasattr(self.player, 'inventory') and self.player.inventory:
                try:
                    save_data['player_data']['inventory'] = [
                        {'type': getattr(item.type, 'name', 'unknown'), 'x': getattr(item, 'x', 0), 'y': getattr(item, 'y', 0)}
                        for item in self.player.inventory
                        if hasattr(item, 'type')
                    ]
                except Exception:
                    save_data['player_data']['inventory'] = []

            # Save to file
            with open('gauntlet_save.json', 'w') as f:
                json.dump(save_data, f, indent=2)
            self.add_ui_message("Game saved successfully!")

        except Exception as e:
            print(f"Save error: {str(e)}")  # Debug output
            self.add_ui_message(f"Save failed: {str(e)[:50]}...")

    def load_game(self):
        """Load game state from file"""
        try:
            with open('gauntlet_save.json', 'r') as f:
                save_data = json.load(f)

            # Restore game state with safe defaults
            self.current_level = save_data.get('current_level', 1)
            self.score = save_data.get('score', 0)

            # Safely handle difficulty
            try:
                self.difficulty = Difficulty[save_data.get('difficulty', 'BASED')]
            except (KeyError, ValueError):
                self.difficulty = Difficulty.BASED

            self.current_character_key = save_data.get('character_class', 'android')

            # Recreate player
            try:
                self.player = Player(self.current_character_key, self.current_level)
                self.player.game = self
            except Exception as e:
                print(f"Player creation error: {e}")
                self.add_ui_message("Failed to create player character!")
                return False

            # Restore player stats with safe defaults
            player_data = save_data.get('player_data', {})
            self.player.life = player_data.get('life', 100)
            self.player.max_life = player_data.get('max_life', 100)
            self.player.gold = player_data.get('gold', 0)
            self.player.keys_collected = player_data.get('keys_collected', 0)
            self.player.speed = player_data.get('speed', 1.0)
            self.player.strength = player_data.get('strength', 1.0)
            self.player.missiles = player_data.get('missiles', 1.0)

            # Restore inventory safely
            self.player.inventory = []
            inventory_data = player_data.get('inventory', [])
            for item_data in inventory_data:
                try:
                    item_type_name = item_data.get('type', 'unknown')
                    if hasattr(ItemType, item_type_name.upper()):
                        item_type = getattr(ItemType, item_type_name.upper())
                        item = Item(item_data.get('x', 0), item_data.get('y', 0), item_type)
                        self.player.inventory.append(item)
                except Exception as e:
                    print(f"Failed to load item {item_data}: {e}")
                    continue

            # Restore status effects
            self.status_effects = save_data.get('status_effects', {})
            self.farsee_timer = save_data.get('farsee_timer', 0.0)

            # Reload the current level
            try:
                self.load_level(self.current_level)
            except Exception as e:
                print(f"Level loading error: {e}")
                self.load_level(1)  # Fallback to level 1

            self.state = GameState.PLAYING
            self.add_ui_message("Game loaded successfully!")
            return True

        except FileNotFoundError:
            self.add_ui_message("No saved game found!")
            return False
        except json.JSONDecodeError:
            self.add_ui_message("Save file is corrupted!")
            return False
        except Exception as e:
            print(f"Load error: {str(e)}")
            self.add_ui_message(f"Load failed: {str(e)[:50]}...")
            return False

    def switch_character(self):
        """Switch to next character class, preserving stats"""
        if not self.player:
            return

        # Get current character index
        character_keys = list(CHARACTER_CLASSES.keys())
        try:
            current_index = character_keys.index(self.current_character_key)
        except ValueError:
            current_index = 0

        # Cycle to next character
        next_index = (current_index + 1) % len(character_keys)
        next_character_key = character_keys[next_index]

        # Preserve current player stats
        current_life = self.player.life
        current_max_life = self.player.max_life
        current_gold = self.player.gold
        current_keys = self.player.keys_collected
        current_inventory = self.player.inventory.copy()
        current_x, current_y = self.player.x, self.player.y

        # Create new player with new character class
        self.player = Player(next_character_key, self.current_level)
        self.player.game = self

        # Restore preserved stats
        self.player.life = current_life
        self.player.max_life = current_max_life
        self.player.gold = current_gold
        self.player.keys_collected = current_keys
        self.player.inventory = current_inventory
        self.player.x, self.player.y = current_x, current_y

        # Update character key tracking
        self.current_character_key = next_character_key

        # Get character name for message
        char_class = CHARACTER_CLASSES[next_character_key]
        self.add_ui_message(f"Switched to {char_class.name}!")

    def load_level(self, level_num):
        """Load and generate a complete dungeon level with rooms, enemies, items, and hazards"""
        self.current_level = level_num
        self.enemies = []      # Clear previous level enemies
        self.items = []        # Clear previous level items
        self.hazards = []      # Reset environmental hazards

        # LEVEL GENERATION PIPELINE (8-step process):

        # 1. Generate maze layout - creates interconnected rooms and corridors
        self.generate_level_layout(level_num)

        # 2. Place key locations in open spaces (30 keys for large world)
        rng = random.Random(level_num * 911)  # Seeded for consistent level design
        for i in range(30):
            kx = rng.randint(WORLD_MARGIN + 64, WORLD_WIDTH - WORLD_MARGIN - 64)
            ky = rng.randint(WORLD_MARGIN + 64, WORLD_HEIGHT - WORLD_MARGIN - 64)
            if not self.check_wall_collision(kx, ky):
                self.keys_needed.append((kx, ky))

        # 3. Ensure every room has at least one door for connectivity
        self.ensure_room_doors()

        # 4. Spawn enemies in rooms (difficulty affects count)
        self.spawn_enemies(level_num)

        # 5. Place all items including keys, food, gold, potions
        self.place_items()

        # 6. Add environmental hazards (spikes, poison, runes)
        self.place_hazards()

        # 7. Ensure player has space to move and doors function properly
        self.ensure_spawn_space()
        self.ensure_door_blockers()

        # 8. Position player in first room and guarantee progression path
        if self.player and self.rooms:
            rx, ry, rw, rh = self.rooms[0]
            self.player.x = rx + rw // 2
            self.player.y = ry + rh // 2
            
            # CRITICAL: Always place a key in the starting room
            start_key_x = rx + rw // 4  # Offset from center so visible
            start_key_y = ry + rh // 4
            self.items.append(Item(start_key_x, start_key_y, ItemType.KEY))
            print(f"Placed starting key at ({start_key_x}, {start_key_y}) in room ({rx}, {ry}, {rw}, {rh})")
            
            # ALSO: Make sure starting room has at least one door that's already open
            # Find doors ON the walls of the starting room
            starting_room_doors = []
            for door_x, door_y in self.doors:
                # Check if door is on the perimeter of starting room
                on_room_wall = False
                # Top or bottom wall
                if ((door_x >= rx and door_x <= rx + rw) and (door_y == ry or door_y == ry + rh - 32)):
                    on_room_wall = True
                # Left or right wall  
                elif ((door_y >= ry and door_y <= ry + rh) and (door_x == rx or door_x == rx + rw - 32)):
                    on_room_wall = True
                
                if on_room_wall:
                    starting_room_doors.append((door_x, door_y))
            
            if starting_room_doors:
                # Remove one door to make it permanently open (no key needed)
                door_to_open = starting_room_doors[0]
                if door_to_open in self.doors:
                    self.doors.remove(door_to_open)
                print(f"Made starting room door permanently open at {door_to_open}")
            else:
                # Fallback: carve a new door on the top wall center
                door_x = rx + (rw // 2 // 32) * 32
                door_y = ry
                if (door_x, door_y) in self.walls:
                    self.walls.remove((door_x, door_y))
                self.doors.append((door_x, door_y))
                print("Created fallback door for starting room at", (door_x, door_y))

        # Always ensure at least as many keys as doors
        if len(self.keys_needed) < len(self.doors):
            add = len(self.doors) - len(self.keys_needed)
            for _ in range(add):
                while True:
                    kx = rng.randint(WORLD_MARGIN + 64, WORLD_WIDTH - WORLD_MARGIN - 64)
                    ky = rng.randint(WORLD_MARGIN + 64, WORLD_HEIGHT - WORLD_MARGIN - 64)
                    if not self.check_wall_collision(kx, ky):
                        self.keys_needed.append((kx, ky))
                        break

        # Center camera on player
        if self.player:
            self.camera_x = max(0, min(WORLD_WIDTH - GAME_WIDTH, int(self.player.x) - GAME_WIDTH // 2))
            self.camera_y = max(0, min(WORLD_HEIGHT - GAME_HEIGHT, int(self.player.y) - GAME_HEIGHT // 2))

        print(f"Loading level {level_num}")

    def generate_level_layout(self, level_num):
        """Generate maze-based level with large rooms carved into it"""
        self.walls = []
        self.doors = []
        self.keys_needed = []
        self.terminals = []
        self.rooms = []

        wall_size = 32
        
        # Create maze grid 
        maze_width = WORLD_WIDTH // wall_size
        maze_height = WORLD_HEIGHT // wall_size
        
        # Create proper room-based layout like original Gauntlet
        rnd = random.Random(level_num * 137)
        
        # Start with empty world (no walls initially)
        
        # Generate many interconnected rooms like original Gauntlet
        room_grid_size = 6  # Smaller rooms so we can fit more
        
        # Create a grid for room placement
        rooms_per_row = maze_width // (room_grid_size + 2)  # +2 for corridor space
        rooms_per_col = maze_height // (room_grid_size + 2)
        
        print(f"Grid capacity: {rooms_per_row} x {rooms_per_col} = {rooms_per_row * rooms_per_col} rooms")
        
        # Place rooms in ALL grid positions (fill the entire world)
        for grid_row in range(rooms_per_col):
            for grid_col in range(rooms_per_row):
                
                # Calculate room position
                room_grid_x = grid_col * (room_grid_size + 2) + 1
                room_grid_y = grid_row * (room_grid_size + 2) + 1
                
                # Convert to pixel coordinates
                room_x = room_grid_x * wall_size
                room_y = room_grid_y * wall_size
                room_w = room_grid_size * wall_size
                room_h = room_grid_size * wall_size
                
                # Add some randomness to room size
                if rnd.random() < 0.3:  # 30% chance for larger room
                    room_w += wall_size * rnd.randint(1, 3)
                    room_h += wall_size * rnd.randint(1, 3)
                
                self.rooms.append((room_x, room_y, room_w, room_h))
                
                # Create walls around the room (room boundaries)
                for rx in range(room_grid_x, room_grid_x + room_w // wall_size):
                    for ry in range(room_grid_y, room_grid_y + room_h // wall_size):
                        # Only add walls on the perimeter
                        if (rx == room_grid_x or rx == room_grid_x + room_w // wall_size - 1 or
                            ry == room_grid_y or ry == room_grid_y + room_h // wall_size - 1):
                            if 0 <= rx < maze_width and 0 <= ry < maze_height:
                                wall_x = rx * wall_size
                                wall_y = ry * wall_size
                                self.walls.append((wall_x, wall_y))
        
        # Create single door entrances for each room (like original Gauntlet)
        for room_idx, (rx, ry, rw, rh) in enumerate(self.rooms):
            # Each room gets 1-2 doors maximum
            doors_for_room = rnd.randint(1, 2)
            
            for door_num in range(doors_for_room):
                # Choose a random wall side for the door
                side = rnd.choice(['top', 'bottom', 'left', 'right'])

                # IMPORTANT: Align door to wall grid so it matches a wall tile
                room_grid_x = rx // wall_size
                room_grid_y = ry // wall_size
                room_tiles_w = rw // wall_size
                room_tiles_h = rh // wall_size

                if side == 'top':
                    door_tile_x = room_grid_x + rnd.randint(1, max(1, room_tiles_w - 2))
                    door_tile_y = room_grid_y
                elif side == 'bottom':
                    door_tile_x = room_grid_x + rnd.randint(1, max(1, room_tiles_w - 2))
                    door_tile_y = room_grid_y + room_tiles_h - 1
                elif side == 'left':
                    door_tile_x = room_grid_x
                    door_tile_y = room_grid_y + rnd.randint(1, max(1, room_tiles_h - 2))
                else:  # right
                    door_tile_x = room_grid_x + room_tiles_w - 1
                    door_tile_y = room_grid_y + rnd.randint(1, max(1, room_tiles_h - 2))

                door_x = door_tile_x * wall_size
                door_y = door_tile_y * wall_size

                # Remove the wall tile to create a door (if it exists) and always record the door
                if (door_x, door_y) in self.walls:
                    self.walls.remove((door_x, door_y))
                self.doors.append((door_x, door_y))

                # Create a short corridor stub (just 1-2 tiles) to connect to adjacent areas
                if side == 'top' and door_y - wall_size >= 0:
                    self.walls = [(wx, wy) for (wx, wy) in self.walls if not (wx == door_x and wy == door_y - wall_size)]
                elif side == 'bottom' and door_y + wall_size < WORLD_HEIGHT:
                    self.walls = [(wx, wy) for (wx, wy) in self.walls if not (wx == door_x and wy == door_y + wall_size)]
                elif side == 'left' and door_x - wall_size >= 0:
                    self.walls = [(wx, wy) for (wx, wy) in self.walls if not (wx == door_x - wall_size and wy == door_y)]
                elif side == 'right' and door_x + wall_size < WORLD_WIDTH:
                    self.walls = [(wx, wy) for (wx, wy) in self.walls if not (wx == door_x + wall_size and wy == door_y)]

        # Place terminals in rooms
        if self.rooms:
            cx, cy, cw, ch = self.rooms[0]
            self.terminals.append((cx + 32, cy + 32))

    
    def ensure_room_doors(self):
        """Rooms are already connected via maze - place terminals based on probability"""
        rng = random.Random(self.current_level * 31337 + 42)  # Use consistent seed
        for (rx, ry, rw, rh) in self.rooms:
            if rng.random() < TERMINAL_CHANCE_PER_ROOM:
                term_pos = (rx + 32, ry + 32)
                if term_pos not in self.terminals:
                    self.terminals.append(term_pos)
        """Ensure every generated room has at least one door placed on a wall opening.
        We replace one wall tile with a door and clear one approach tile outside."""
        for (rx, ry, rw, rh) in self.rooms:
            # Check if a door already exists on this room's walls
            has_door = False
            for (dx, dy) in self.doors:
                on_horizontal = (rx <= dx <= rx + rw - 32) and (dy in (ry, ry + rh - 16))
                on_vertical = (ry <= dy <= ry + rh - 16) and (dx in (rx, rx + rw - 32))
                if on_horizontal or on_vertical:
                    has_door = True
                    break
            if has_door:
                continue

            # Candidate wall tiles where we can replace with a door (prefer non-borders)
            wall_candidates = []
            # Right wall strip
            wx = rx + rw - 32
            for wy in range(ry + 32, ry + rh - 32, 32):
                if (wx, wy) in self.walls and wx + 32 < WORLD_WIDTH:
                    wall_candidates.append((wx, wy, 'R'))
            # Left wall strip
            wx = rx
            for wy in range(ry + 32, ry + rh - 32, 32):
                if (wx, wy) in self.walls and wx - 32 > 0:
                    wall_candidates.append((wx, wy, 'L'))
            # Top wall strip
            wy = ry
            for wx in range(rx + 32, rx + rw - 32, 32):
                if (wx, wy) in self.walls and wy - 32 > 0:
                    wall_candidates.append((wx, wy, 'T'))
            # Bottom wall strip
            wy = ry + rh - 32
            for wx in range(rx + 32, rx + rw - 32, 32):
                if (wx, wy) in self.walls and wy + 32 < WORLD_HEIGHT:
                    wall_candidates.append((wx, wy, 'B'))

            if not wall_candidates:
                continue

            # Use first candidate: remove wall, add door, clear approach
            wx, wy, side = wall_candidates[0]
            if (wx, wy) in self.walls:
                self.walls.remove((wx, wy))
            door_x, door_y = wx, wy
            self.doors.append((door_x, door_y))

            # Clear approach tile just outside the wall
            if side == 'R' and door_x + 32 < WORLD_WIDTH:
                self.walls = [(x, y) for (x, y) in self.walls if not (x == door_x + 32 and y == door_y)]
            elif side == 'L' and door_x - 32 > 0:
                self.walls = [(x, y) for (x, y) in self.walls if not (x == door_x - 32 and y == door_y)]
            elif side == 'T' and door_y - 32 > 0:
                self.walls = [(x, y) for (x, y) in self.walls if not (x == door_x and y == door_y - 32)]
            elif side == 'B' and door_y + 32 < WORLD_HEIGHT:
                self.walls = [(x, y) for (x, y) in self.walls if not (x == door_x and y == door_y + 32)]

    def spawn_enemies(self, level_num):
        """Spawn enemies for the level"""
        # Spawn enemies INSIDE rooms so they are unleashed when doors open
        if not self.rooms:
            return

        rnd = random.Random(level_num * 777)
        total_cap = ENEMY_CAP  # higher overall density
        spawned = 0

        # Shuffle rooms so population is evenly distributed across the map
        room_order = list(self.rooms)
        rnd.shuffle(room_order)

        # Enemies per room scales with level, clamped, and difficulty
        base_per_room = MIN_ENEMIES_PER_ROOM + level_num // 2
        per_room = max(MIN_ENEMIES_PER_ROOM, min(MAX_ENEMIES_PER_ROOM, base_per_room))
        # Apply difficulty multiplier to monster count
        monster_multiplier = DIFFICULTY_MULTIPLIERS[self.difficulty]['monsters']
        per_room = max(1, int(per_room * monster_multiplier))  # Ensure at least 1 enemy per room

        for (rx, ry, rw, rh) in room_order:
            # Interior bounds (avoid walls/doors)
            min_x = rx + 56
            max_x = rx + rw - 56
            min_y = ry + 56
            max_y = ry + rh - 56
            if min_x >= max_x or min_y >= max_y:
                continue

            for _ in range(per_room):
                if spawned >= total_cap:
                    break
                enemy_type = random.choice(list(EnemyType))
                attempts = 0
                placed = False
                while attempts < 30 and not placed:
                    x = rnd.randint(min_x, max_x)
                    y = rnd.randint(min_y, max_y)
                    if self.is_free_of_walls(x, y):
                        self.enemies.append(Enemy(x, y, enemy_type, self))
                        spawned += 1
                        placed = True
                    attempts += 1
            if spawned >= total_cap:
                break

    def place_items(self):
        """Place items randomly throughout the level"""
        rng = random.Random(getattr(self, 'current_level', 1) * 919)

        def is_inside_any_room(px: int, py: int) -> bool:
            for (rx, ry, rw, rh) in self.rooms:
                if rx <= px <= rx + rw and ry <= py <= ry + rh:
                    return True
            return False

        # Corridor health (outside rooms)
        corridor_health = max(BASE_CORRIDOR_FOOD, len(self.rooms) * FOOD_PER_ROOM_MULTIPLIER)
        placed = 0
        attempts = 0
        while placed < corridor_health and attempts < corridor_health * 20:
            x = rng.randint(WORLD_MARGIN, WORLD_WIDTH - WORLD_MARGIN)
            y = rng.randint(WORLD_MARGIN, WORLD_HEIGHT - WORLD_MARGIN)
            if not self.check_wall_collision(x, y) and not is_inside_any_room(x, y):
                self.items.append(Item(x, y, ItemType.FOOD))
                placed += 1
            attempts += 1

        # Room health (MIN_FOOD_PER_ROOM–MAX_FOOD_PER_ROOM per room)
        for (rx, ry, rw, rh) in self.rooms:
            for _ in range(rng.randint(MIN_FOOD_PER_ROOM, MAX_FOOD_PER_ROOM)):
                hx = rng.randint(rx + 40, rx + rw - 40)
                hy = rng.randint(ry + 40, ry + rh - 40)
                if not self.check_wall_collision(hx, hy):
                    self.items.append(Item(hx, hy, ItemType.FOOD))

        # Place keys in valid locations - force placement!
        keys_placed = 0
        for key_pos in self.keys_needed:
            key_x, key_y = key_pos
            # Make sure key position is valid
            if not self.check_wall_collision(key_x, key_y):
                self.items.append(Item(key_x, key_y, ItemType.KEY))
                keys_placed += 1
            else:
                # Find a nearby valid position - expanded search
                valid_position = False
                attempts = 0
                while not valid_position and attempts < 100:  # More attempts
                    offset_x = random.randint(-96, 96)  # Larger search radius
                    offset_y = random.randint(-96, 96)
                    test_x = max(WORLD_MARGIN, min(WORLD_WIDTH - WORLD_MARGIN, key_x + offset_x))
                    test_y = max(WORLD_MARGIN, min(WORLD_HEIGHT - WORLD_MARGIN, key_y + offset_y))
                    if not self.check_wall_collision(test_x, test_y):
                        self.items.append(Item(test_x, test_y, ItemType.KEY))
                        keys_placed += 1
                        valid_position = True
                    attempts += 1
        
        print(f"DEBUG: Placed {keys_placed} keys out of {len(self.keys_needed)} needed")
        
        # If we couldn't place enough keys, add them in room centers (guaranteed open space)
        if keys_placed < len(self.keys_needed) // 2:  # If less than half placed
            for i, (rx, ry, rw, rh) in enumerate(self.rooms):
                if keys_placed >= len(self.keys_needed):
                    break
                # Place key in center of room
                key_x = rx + rw // 2
                key_y = ry + rh // 2
                self.items.append(Item(key_x, key_y, ItemType.KEY))
                keys_placed += 1
            print(f"DEBUG: Added keys in room centers, total keys now: {keys_placed}")

        # Corridor items (keys and gold outside rooms)
        corridor_keys = max(BASE_CORRIDOR_KEYS, int(len(self.rooms) * KEYS_PER_ROOM_MULTIPLIER))
        corridor_gold = max(BASE_CORRIDOR_GOLD, len(self.rooms) * GOLD_PER_ROOM_MULTIPLIER)
        total_corridor_items = corridor_keys + corridor_gold
        placed = 0
        attempts = 0
        while placed < total_corridor_items and attempts < total_corridor_items * 20:
            x = rng.randint(WORLD_MARGIN, WORLD_WIDTH - WORLD_MARGIN)
            y = rng.randint(WORLD_MARGIN, WORLD_HEIGHT - WORLD_MARGIN)
            if not self.check_wall_collision(x, y) and not is_inside_any_room(x, y):
                # Place keys first, then gold
                if placed < corridor_keys:
                    self.items.append(Item(x, y, ItemType.KEY))
                else:
                    self.items.append(Item(x, y, ItemType.GOLD))
                placed += 1
            attempts += 1

        # Room gold (chance per room)
        for (rx, ry, rw, rh) in self.rooms:
            if rng.random() < GOLD_CHANCE_PER_ROOM:
                gx = rng.randint(rx + 40, rx + rw - 40)
                gy = rng.randint(ry + 40, ry + rh - 40)
                if not self.check_wall_collision(gx, gy):
                    self.items.append(Item(gx, gy, ItemType.GOLD))

    def update_playing(self, dt):
        """Update gameplay logic"""
        # Update portrait timer
        if self.enemy_portrait_timer > 0:
            self.enemy_portrait_timer -= dt
        # Update status effect timers
        if hasattr(self, 'status_effects'):
            for key in ('speed', 'strength', 'missiles', 'shield', 'invis'):
                if self.status_effects.get(key, 0) > 0:
                    self.status_effects[key] = max(0.0, self.status_effects[key] - dt)
        if hasattr(self, 'farsee_timer') and self.farsee_timer > 0:
            self.farsee_timer = max(0.0, self.farsee_timer - dt)
            
        if self.player:
            old_x, old_y = self.player.x, self.player.y
            self.player.update(dt, self.keys_pressed)
            # FIX: resolve collisions per-axis to avoid corner-sticking
            new_x, new_y = self.player.x, self.player.y
            if self.check_wall_collision(new_x, new_y):
                # Try allowing X movement only (only if X actually changed)
                if new_x != old_x and not self.check_wall_collision(new_x, old_y):
                    self.player.y = old_y
                # Else try allowing Y movement only (only if Y actually changed)
                elif new_y != old_y and not self.check_wall_collision(old_x, new_y):
                    self.player.x = old_x
                else:
                    # Neither axis is free; revert move
                    self.player.x, self.player.y = old_x, old_y

            # FIX: update melee cooldown timer here to avoid adding new loops
            if hasattr(self, 'melee_cooldown') and self.melee_cooldown > 0:
                self.melee_cooldown = max(0.0, self.melee_cooldown - dt)

            # SPACE: Contextual action handled by terminal check before shooting
            # Defer to check_terminal_collisions to open shop when colliding with a terminal.
            # If not at a terminal, the shooting block below will fire the missile.
            if pygame.K_SPACE in self.keys_pressed:
                pass

            # Open help screen
            if pygame.K_h in self.keys_pressed:
                self.help_previous_state = self.state  # Remember where we came from
                self.state = GameState.HELP
                self.help_entered_this_frame = True
                self.help_ignore_h_until_release = True  # Ignore H until released
                self.keys_pressed.pop(pygame.K_h, None)

            # Save game (F5 or S)
            if pygame.K_F5 in self.keys_pressed:
                self.save_game()
                self.keys_pressed.pop(pygame.K_F5, None)
            elif pygame.K_s in self.keys_pressed and self.state == GameState.PLAYING:
                self.save_game()
                self.keys_pressed.pop(pygame.K_s, None)

            # Character switch (C key)
            if pygame.K_c in self.keys_pressed:
                self.switch_character()
                self.keys_pressed.pop(pygame.K_c, None)

            # Camera follows player within world
            self.camera_x = max(0, min(WORLD_WIDTH - GAME_WIDTH, int(self.player.x) - GAME_WIDTH // 2))
            self.camera_y = max(0, min(WORLD_HEIGHT - GAME_HEIGHT, int(self.player.y) - GAME_HEIGHT // 2))

            self.check_item_collisions()
            self.check_enemy_collisions()
            self.check_terminal_collisions()
            self.check_door_collisions()
            # Inventory open/close
            if pygame.K_TAB in self.keys_pressed or pygame.K_i in self.keys_pressed:
                self.inventory_open = not self.inventory_open
                self.keys_pressed.pop(pygame.K_TAB, None)
                self.keys_pressed.pop(pygame.K_i, None)
            elif pygame.K_ESCAPE in self.keys_pressed and self.inventory_open:
                self.inventory_open = False
                self.keys_pressed.pop(pygame.K_ESCAPE, None)
            # Inventory handling
            if self.inventory_open:
                if pygame.K_LEFT in self.keys_pressed or pygame.K_UP in self.keys_pressed:
                    if self.player.inventory:
                        self.inventory_cursor = max(0, self.inventory_cursor - 1)
                    self.keys_pressed.pop(pygame.K_LEFT, None)
                    self.keys_pressed.pop(pygame.K_UP, None)
                if pygame.K_RIGHT in self.keys_pressed or pygame.K_DOWN in self.keys_pressed:
                    if self.player.inventory:
                        self.inventory_cursor = min(len(self.player.inventory) - 1, self.inventory_cursor + 1)
                    self.keys_pressed.pop(pygame.K_RIGHT, None)
                    self.keys_pressed.pop(pygame.K_DOWN, None)
                if pygame.K_RETURN in self.keys_pressed and self.player.inventory:
                    self.use_inventory_item(self.inventory_cursor)
                    self.keys_pressed.pop(pygame.K_RETURN, None)
                if pygame.K_d in self.keys_pressed and self.player.inventory:
                    self.drop_inventory_item(self.inventory_cursor)
                    self.keys_pressed.pop(pygame.K_d, None)
                return

            # SPACE bar handling now done in check_terminal_collisions() with distance-based priority
            self.update_projectiles(dt)
            # ADDED: hazards apply damage/slow/effects on contact
            self.check_hazard_collisions(dt)
            if len(self.doors) == 0 and len(self.keys_needed) == 0:
                self.complete_level()

            # Slower life drain
            self.player.life -= dt * LIFE_DRAIN_RATE
            if self.player.life <= 0:
                # Check for revive scroll
                if self.status_effects.get('revive', 0) > 0:
                    self.status_effects['revive'] -= 1
                    self.player.life = self.player.max_life * REVIVE_VALUE
                    self.add_ui_message("Revived!")
                else:
                    self.sound_manager.play_death()
                    self.state = GameState.GAME_OVER

        # Update enemies
        for enemy in self.enemies:
            # Save old position
            old_x, old_y = enemy.x, enemy.y
            enemy.update(dt)
            # Prevent clipping into walls (strict check)
            if not self.is_free_of_walls(enemy.x, enemy.y):
                enemy.x, enemy.y = old_x, old_y

        # Update items
        for item in self.items:
            item.update(dt)

    def check_wall_collision(self, x, y):
        """Check if position collides with walls"""
        # FIX: use symmetric 24x24 rect to avoid right-side gap while keeping logic below
        player_rect = pygame.Rect(x - 12, y - 12, 24, 24)

        # Doors now block movement until opened with space bar

        for wall_x, wall_y in self.walls:
            wall_rect = pygame.Rect(wall_x, wall_y, 32, 32)
            if player_rect.colliderect(wall_rect):
                # Allow slight overlap tolerance on right side to reach doors on right walls
                if player_rect.right > wall_rect.left and player_rect.right - wall_rect.left <= 4:
                    # ignore tiny right overlap (increased from 2 to 4 for consistency)
                    continue
                # FIX: allow tiny bottom overlap so player can get flush with bottom walls
                if player_rect.bottom > wall_rect.top and player_rect.bottom - wall_rect.top <= 4:
                    # ignore tiny bottom overlap (increased to 4 for consistency)
                    continue
                # FIX: allow tiny left overlap so player can get flush with left walls
                if player_rect.left < wall_rect.right and wall_rect.right - player_rect.left <= 4:
                    # ignore tiny left overlap (increased to 4 for consistency)
                    continue
                # FIX: allow tiny top overlap so player can get flush with top walls
                if player_rect.top < wall_rect.bottom and wall_rect.bottom - player_rect.top <= 4:
                    # ignore tiny top overlap (increased to 4 for consistency)
                    continue
                return True

        # Check unopened doors (they act as walls)
        for door_x, door_y in self.doors:
            door_rect = pygame.Rect(door_x, door_y, 32, 16)  # Match HTML version door size
            if player_rect.colliderect(door_rect):
                return True  # Block movement at doors without keys

        return False

    def is_free_of_walls(self, x: int, y: int) -> bool:
        """Strict wall collision test for spawning/movement of NPCs and projectiles."""
        rect = pygame.Rect(x - 12, y - 12, 24, 24)
        for wx, wy in self.walls:
            if rect.colliderect(pygame.Rect(wx, wy, 32, 32)):
                return False
        return True

    def check_item_collisions(self):
        """Check for player-item collisions and collect items"""
        if not self.player:
            return

        player_rect = pygame.Rect(self.player.x - 12, self.player.y - 12, 24, 24)

        for item in self.items[:]:  # Copy list to avoid modification during iteration
            if item.collected:
                continue

            item_rect = pygame.Rect(item.x - 12, item.y - 12, 24, 24)  # Larger item hitbox
            if player_rect.colliderect(item_rect):
                self.collect_item(item)

    def collect_item(self, item):
        """Handle item collection"""
        # Health (apples) apply immediately and never use inventory
        if item.type == ItemType.FOOD:
            item.collected = True
            self.player.life = min(self.player.max_life, self.player.life + FOOD_VALUE)
            self.sound_manager.play_food_eat()
            self.last_action = 'FOOD'
            self.last_pickup_type = item.type
            # FIX: route message to HUD instead of console
            self.add_ui_message(f"Ate, gained {FOOD_VALUE} life")
            return

        # Keys and Gold apply immediately and do NOT occupy inventory
        if item.type == ItemType.KEY:
            item.collected = True
            self.player.keys_collected += 1
            # Remove this key from the keys_needed list
            item_pos = (item.x, item.y)
            if item_pos in self.keys_needed:
                self.keys_needed.remove(item_pos)
            self.sound_manager.play_item_collect()
            self.last_action = 'KEY'
            self.last_pickup_type = item.type
            self.add_ui_message(f"Collected key!")
            self.add_ui_message(f"Keys needed: {len(self.keys_needed)}")
            return

        if item.type == ItemType.GOLD:
            item.collected = True
            self.player.gold += GOLD_VALUE
            self.sound_manager.play_gold_collect()
            self.last_pickup_type = item.type
            self.add_ui_message(f"+{GOLD_VALUE} gold!")
            return

        # Potions and scrolls go to inventory (consumables)
        if item.type in (ItemType.POTION_SPEED, ItemType.POTION_STRENGTH, ItemType.POTION_MISSILES,
                         ItemType.SCROLL_INVISIBILITY, ItemType.SCROLL_FARSEE, ItemType.SCROLL_REVIVE, ItemType.SCROLL_BLAST):
            if len(self.player.inventory) >= self.player.max_inventory:
                self.add_ui_message("Inventory full!")
                return
            item.collected = True
            self.player.inventory.append(item)
            self.sound_manager.play_item_collect()
            self.last_pickup_type = item.type
            self.add_ui_message("Picked up " + str(item.type).split('.')[-1])
            return

        if len(self.player.inventory) >= self.player.max_inventory:
            # FIX: route message to HUD instead of console
            self.add_ui_message("Inventory full!")
            return

        item.collected = True
        self.player.inventory.append(item)

        # Apply item effects and play sounds
        if item.type == ItemType.FOOD:
            self.player.life = min(self.player.max_life, self.player.life + FOOD_VALUE)
            self.sound_manager.play_food_eat()
            self.last_action = 'FOOD'
            # ADDED: remember for HUD big icon
            self.last_pickup_type = item.type
            # FIX: route message to HUD instead of console
            self.add_ui_message("Ate, gained " + str(FOOD_VALUE) + " life")
        elif item.type == ItemType.KEY:
            self.player.keys_collected += 1
            # Remove this key from the keys_needed list
            item_pos = (item.x, item.y)
            if item_pos in self.keys_needed:
                self.keys_needed.remove(item_pos)
            self.sound_manager.play_item_collect()
            self.last_action = 'KEY'
            self.last_pickup_type = item.type
            # FIX: route message to HUD instead of console
            self.add_ui_message(f"Collected key! Keys: {self.player.keys_collected}, Keys needed: {len(self.keys_needed)}")
        elif item.type == ItemType.GOLD:
            self.player.gold += GOLD_VALUE
            self.sound_manager.play_gold_collect()
            self.last_pickup_type = item.type
            # FIX: route message to HUD instead of console
            self.add_ui_message(f"Collected gold, +{GOLD_VALUE} gold! Total: {self.player.gold}")
        elif item.type == ItemType.POTION_SPEED:
            self.player.speed += POTION_SPEED_VALUE
            self.sound_manager.play_item_collect()
            self.effects.append({"type": "aura", "color": (50, 150, 255), "timer": 0.35})
            self.last_pickup_type = item.type
            # FIX: route message to HUD instead of console
            self.add_ui_message("Speed potion!")
        elif item.type == ItemType.POTION_STRENGTH:
            self.player.strength += POTION_STRENGTH_VALUE
            self.sound_manager.play_item_collect()
            self.effects.append({"type": "aura", "color": (255, 220, 50), "timer": 0.35})
            self.last_pickup_type = item.type
            # FIX: route message to HUD instead of console
            self.add_ui_message("Strength potion!")
        elif item.type == ItemType.POTION_MISSILES:
            self.player.missiles += POTION_MISSILES_VALUE
            self.sound_manager.play_item_collect()
            self.effects.append({"type": "aura", "color": (50, 255, 120), "timer": 0.35})
            self.last_pickup_type = item.type
            # FIX: route message to HUD instead of console
            self.add_ui_message("Missiles potion!")

    def check_enemy_collisions(self):
        """Check for player-enemy collisions"""
        if not self.player:
            return

        player_rect = pygame.Rect(self.player.x - 12, self.player.y - 12, 24, 24)

        for enemy in self.enemies[:]:  # Copy list to avoid modification during iteration
            enemy_rect = pygame.Rect(enemy.x - 12, enemy.y - 12, 24, 24)  # Larger enemy hitbox
            if player_rect.colliderect(enemy_rect):
                # Player takes damage from contact
                base = max(1, STRENGTH_DAMAGE - self.player.strength)
                # Shield halves damage
                if self.status_effects.get('shield', 0) > 0:
                    base *= 0.5
                damage = base
                self.player.life -= damage
                self.sound_manager.play_damage()
                self.last_action = 'COMBAT'
                # Add HUD feedback for enemy collision
                enemy_name = str(enemy.type).replace('EnemyType.', '').title()
                self.add_ui_message(f"Hit by {enemy_name}! -{int(damage)} HP")
                # FIX: slime contact slow - reduce move speed briefly
                if enemy.type == EnemyType.SLIME:
                    self.player_slow_timer = SLIME_SLOW_DURATION  # seconds of slow
                # Show enemy portrait
                self.last_enemy_hit = enemy.type
                self.enemy_portrait_timer = ENEMY_PORTRAIT_DURATION
                # FIX: route message to HUD instead of console
                self.add_ui_message(f"Hit! -{damage} life")

                # Enemies no longer die from contact - only from SPACE melee attacks

                # Check if player died
                if self.player.life <= 0:
                    # Revive scroll auto-activates
                    if self.status_effects.get('revive', 0) > 0:
                        self.status_effects['revive'] -= 1
                        self.player.life = self.player.max_life * REVIVE_VALUE
                        self.add_ui_message("Revived!")
                    else:
                        self.sound_manager.play_death()
                        self.state = GameState.GAME_OVER

    def check_terminal_collisions(self):
        """Check for player-terminal collisions and handle T/D/space interactions"""
        if not self.player:
            return

        # Update shop cooldown
        if self.shop_cooldown > 0:
            self.shop_cooldown -= 1

        # Handle T key for terminal interaction
        if pygame.K_t in self.keys_pressed:
            px, py = self.player.x, self.player.y

            # Check if near a terminal
            for term_x, term_y in self.terminals:
                dist = math.sqrt((px - term_x) ** 2 + (py - term_y) ** 2)
                if dist < 40:  # Reasonable proximity
                    if not self.shop_block_until_exit and self.state != GameState.SHOP and self.shop_cooldown == 0:
                        self.enter_shop()
                    break

            self.keys_pressed.pop(pygame.K_t, None)

        # Handle D key for door interaction
        if pygame.K_d in self.keys_pressed:
            px, py = self.player.x, self.player.y

            # Check if near a door
            door_found = False
            for door_x, door_y in self.doors:
                # Use center of door tile for proximity check (more intuitive for side doors)
                door_center_x = door_x + 16
                door_center_y = door_y + 16
                dist = math.sqrt((px - door_center_x) ** 2 + (py - door_center_y) ** 2)
                if dist < 48:  # Increased proximity for easier door opening
                    door_found = True
                    if self.player.keys_collected > 0:
                        self.player.keys_collected -= 1
                        if (door_x, door_y) in self.doors:
                            self.doors.remove((door_x, door_y))
                            self.add_ui_message("Door unlocked!")
                    else:
                        self.add_ui_message("Need a key to open this door!")
                    break

            if not door_found:
                self.add_ui_message(f"No door nearby (keys: {self.player.keys_collected})")

            self.keys_pressed.pop(pygame.K_d, None)

        # Handle space bar for combat only
        if pygame.K_SPACE in self.keys_pressed:
            # Check if enemy is in melee range
            px, py = self.player.x, self.player.y
            enemy_in_range = False

            for enemy in self.enemies:
                dist = math.sqrt((px - enemy.x) ** 2 + (py - enemy.y) ** 2)
                if dist < 12:  # Melee range
                    enemy_in_range = True
                    break

            if enemy_in_range and getattr(self, 'melee_cooldown', 0) <= 0:
                self.try_melee_attack()
            else:
                self.fire_projectile()

            self.keys_pressed.pop(pygame.K_SPACE, None)

        # Handle shop blocking logic
        player_rect = pygame.Rect(self.player.x - 12, self.player.y - 12, 24, 24)
        colliding_any_terminal = False
        for term_x, term_y in self.terminals:
            term_rect = pygame.Rect(term_x - 4, term_y - 4, 32, 32)
            if player_rect.colliderect(term_rect):
                colliding_any_terminal = True
                break

        # Unblock re-entry only after leaving the terminal area fully
        if self.shop_block_until_exit and not colliding_any_terminal:
            self.shop_block_until_exit = False

    def check_door_collisions(self):
        """Door interactions now handled in check_terminal_collisions() with space bar"""
        # This function is kept for compatibility but does nothing
        pass

    def enter_shop(self):
        """Enter shop interface"""
        # Do not modify current level or regenerate map here
        self.state = GameState.SHOP
        self.shop_selection = 0  # Start with first item selected
        if not hasattr(self, 'shop_items') or not self.shop_items:
            self.shop_items = [
                {"name": "Food", "type": ItemType.FOOD, "cost": FOOD_VALUE},
                {"name": "Key", "type": ItemType.KEY, "cost": KEY_COST},
                {"name": "Speed Potion", "type": ItemType.POTION_SPEED, "cost": POTION_COST},
                {"name": "Strength Potion", "type": ItemType.POTION_STRENGTH, "cost": POTION_COST},
                {"name": "Missiles Potion", "type": ItemType.POTION_MISSILES, "cost": POTION_COST},
                {"name": "Invisibility", "type": ItemType.SCROLL_INVISIBILITY, "cost": SCROLL_COST},
                {"name": "Farsee", "type": ItemType.SCROLL_FARSEE, "cost": SCROLL_COST},
                {"name": "Revive", "type": ItemType.SCROLL_REVIVE, "cost": SCROLL_COST},
                {"name": "Blast", "type": ItemType.SCROLL_BLAST, "cost": SCROLL_COST},
            ]

    def render_playing(self):
        """Render gameplay"""
        game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        # Draw grass everywhere first
        for x in range(self.camera_x - (self.camera_x % 32), self.camera_x + GAME_WIDTH, 32):
            for y in range(self.camera_y - (self.camera_y % 32), self.camera_y + GAME_HEIGHT, 32):
                game_surface.blit(self.tile_grass, (x - self.camera_x, y - self.camera_y))

        # Draw grey cobble floor inside rooms only
        if hasattr(self, 'rooms'):
            for rx, ry, rw, rh in self.rooms:
                for x in range(rx, rx + rw, 32):
                    for y in range(ry, ry + rh, 32):
                        sx = x - self.camera_x
                        sy = y - self.camera_y
                        if -32 <= sx < GAME_WIDTH and -32 <= sy < GAME_HEIGHT:
                            game_surface.blit(self.tile_cobble, (sx, sy))

        # Walls
        if hasattr(self, 'walls') and self.walls:
            for wall_x, wall_y in self.walls:
                sx = wall_x - self.camera_x
                sy = wall_y - self.camera_y
                if -32 <= sx < GAME_WIDTH and -32 <= sy < GAME_HEIGHT:
                    game_surface.blit(self.tile_wall, (sx, sy))

        # Doors (dark gap with iron bars)
        if hasattr(self, 'doors') and self.doors:
            for door_x, door_y in self.doors:
                sx = door_x - self.camera_x
                sy = door_y - self.camera_y
                if -32 <= sx < GAME_WIDTH and -32 <= sy < GAME_HEIGHT:
                    pygame.draw.rect(game_surface, (60, 40, 20), (sx, sy, 32, 32))  # Make doors 32x32 for easier passage
                    for bx in (6, 16, 26):
                        pygame.draw.rect(game_surface, (140, 140, 140), (sx + bx - 1, sy + 1, 2, 30))  # Extend bars to full height

        # Terminals
        if hasattr(self, 'terminals') and self.terminals:
            for term_x, term_y in self.terminals:
                sx = term_x - self.camera_x
                sy = term_y - self.camera_y
                if -24 <= sx < GAME_WIDTH and -24 <= sy < GAME_HEIGHT:
                    pygame.draw.rect(game_surface, (0, 255, 255), (sx, sy, 24, 24))
                    pygame.draw.rect(game_surface, (0, 0, 0), (sx+4, sy+4, 16, 12))
                    pygame.draw.rect(game_surface, (0, 255, 0), (sx+6, sy+6, 12, 8))

        # Hazards
        if hasattr(self, 'hazards'):
            for (hx, hy, htype, phase) in self.hazards:
                sx = int(hx - self.camera_x)
                sy = int(hy - self.camera_y)
                if -24 <= sx < GAME_WIDTH and -24 <= sy < GAME_HEIGHT:
                    if htype == HazardType.SPIKES:
                        pygame.draw.polygon(game_surface, (180, 180, 180), [(sx-12, sy+8), (sx, sy-10), (sx+12, sy+8)])
                        pygame.draw.line(game_surface, (60, 60, 60), (sx-12, sy+8), (sx+12, sy+8), 2)
                    elif htype == HazardType.RUNE:
                        color = (80, 140, 255)
                        pygame.draw.circle(game_surface, color, (sx, sy), 12, 2)
                        pygame.draw.line(game_surface, color, (sx-7, sy), (sx+7, sy), 2)
                        pygame.draw.line(game_surface, color, (sx, sy-7), (sx, sy+7), 2)
                    elif htype == HazardType.POISON:
                        pygame.draw.ellipse(game_surface, (20, 160, 40), (sx-14, sy-9, 28, 18))
                        pygame.draw.ellipse(game_surface, (80, 220, 100), (sx-10, sy-6, 20, 12))

        # Player (class-aware silhouette)
        if self.player:
            px = int(self.player.x - self.camera_x)
            py = int(self.player.y - self.camera_y)
            if -16 <= px < GAME_WIDTH and -16 <= py < GAME_HEIGHT:
                self._draw_player(game_surface, px, py)
                # ADDED: clear facing indicator arrow
                self._draw_facing_indicator(game_surface, px, py)

        # Enemies and items
        for enemy in self.enemies:
            ex = int(enemy.x - self.camera_x)
            ey = int(enemy.y - self.camera_y)
            if -20 <= ex < GAME_WIDTH and -20 <= ey < GAME_HEIGHT:
                self._draw_enemy(game_surface, enemy, ex, ey)

        # ADDED: Projectiles rendering (bright bolts)
        for p in self.projectiles:
            sx = int(p.x - self.camera_x)
            sy = int(p.y - self.camera_y)
            if -8 <= sx < GAME_WIDTH and -8 <= sy < GAME_HEIGHT:
                pygame.draw.circle(game_surface, (255, 240, 120), (sx, sy), 3)

        for item in self.items:
            if not item.collected:
                ix = int(item.x - self.camera_x)
                iy = int(item.y - self.camera_y)
                if -20 <= ix < GAME_WIDTH and -20 <= iy < GAME_HEIGHT:
                    # Use sprites for items if available (simplified)
                    sprite_key = self._common_sprites.get(item.type)

                    def _draw_item_fallback(surface, x, y):
                        """Fallback drawing for items when sprites aren't available"""
                        if item.type == ItemType.KEY:
                            pygame.draw.rect(surface, GOLD, (x - 8, y - 4, 16, 8), border_radius=2)
                            pygame.draw.rect(surface, GOLD, (x + 6, y - 6, 4, 12))
                            pygame.draw.rect(surface, GOLD, (x + 8, y - 4, 8, 4))
                        elif item.type == ItemType.FOOD:
                            pygame.draw.circle(surface, RED, (x, y), 6)
                            pygame.draw.circle(surface, GREEN, (x - 2, y - 4), 3)
                        elif item.type == ItemType.GOLD:
                            pygame.draw.circle(surface, GOLD, (x, y), 8)
                            pygame.draw.circle(surface, YELLOW, (x, y), 6)
                        elif item.type in [ItemType.POTION_SPEED, ItemType.POTION_STRENGTH, ItemType.POTION_MISSILES]:
                            pygame.draw.rect(surface, (100, 100, 100), (x - 4, y - 8, 8, 12), border_radius=2)
                            pygame.draw.circle(surface, (150, 150, 150), (x, y - 6), 3)

                    self._try_draw_sprite(game_surface, sprite_key, ix, iy, size=(24, 24), fallback_func=_draw_item_fallback)

        self.screen.blit(game_surface, (0, 0))

        # HUD split: big icon + LIFE left; stats/score right (monospace)
        # Hide UI when inventory is open
        if not self.inventory_open:
            left_w = SCREEN_WIDTH // 2
            right_w = SCREEN_WIDTH - left_w
            bottom_y = GAME_HEIGHT

            left_panel = pygame.Surface((left_w, UI_HEIGHT))
            left_panel.fill((10, 10, 10))
            # LIFE bar + numeric
            life_val = int(self.player.life) if self.player else 0
            pygame.draw.rect(left_panel, (255, 255, 255), (8, 8, left_w - 16, 28), 2)
            max_bar = left_w - 20
            filled = int(max_bar * max(0, life_val) / max(1, (self.player.max_life if self.player else 100)))
            pygame.draw.rect(left_panel, (100, 0, 0), (10, 10, max_bar, 24))
            pygame.draw.rect(left_panel, (0, 220, 0), (10, 10, filled, 24))
            life_text = self.font_small.render("LIFE", True, (0, 0, 0))
            left_panel.blit(life_text, (12, 10))
            
            # POTION/SCROLL TIMER BAR - between life bar and icon
            if hasattr(self, 'status_effects'):
                # Find ALL active effects (potions, scrolls, including farsee)
                active_effects = []
                
                # Check status_effects dictionary
                for effect, time_left in self.status_effects.items():
                    if time_left > 0 and effect in ['speed', 'strength', 'missiles', 'shield', 'invis']:
                        active_effects.append((effect, time_left))
                
                # Check farsee_timer separately (it's not in status_effects)
                if hasattr(self, 'farsee_timer') and self.farsee_timer > 0:
                    active_effects.append(('farsee', self.farsee_timer))
                
                # ALWAYS show timer bar area - exact same style as LIFE bar
                pygame.draw.rect(left_panel, (255, 255, 255), (8, 70, left_w - 16, 28), 2)  # White border like LIFE bar
                pygame.draw.rect(left_panel, (100, 0, 0), (10, 72, max_bar, 24))  # Dark background like LIFE bar
                
                if active_effects:
                    # If multiple effects, cycle through them every 2 seconds
                    if len(active_effects) > 1:
                        cycle_index = int(pygame.time.get_ticks() / 2000) % len(active_effects)
                        effect_name, time_left = active_effects[cycle_index]
                        # Show count of total active effects
                        effect_text = self.font_small.render(f"{effect_name.upper()}: {time_left:.1f}s ({len(active_effects)} active)", True, (0, 0, 0))
                    else:
                        # Single effect - show normally
                        effect_name, time_left = active_effects[0]
                        effect_text = self.font_small.render(f"{effect_name.upper()}: {time_left:.1f}s", True, (0, 0, 0))
                    
                    # Calculate scaling based on maximum possible duration for this effect type
                    if effect_name == 'farsee':
                        # Farsee is always 30 seconds maximum
                        max_effect_duration = 30.0
                    else:
                        # Potions scale up to WOKE difficulty (6x multiplier)
                        max_effect_duration = POTION_DURATION * 6.0  # Always use maximum possible

                    # Scale the bar based on remaining time vs maximum duration
                    effect_percent = time_left / max_effect_duration
                    effect_percent = max(0.0, min(1.0, effect_percent))  # Clamp to 0-1

                    # Yellow fill - same position as background
                    pygame.draw.rect(left_panel, (255, 255, 0), (10, 72, int(max_bar * effect_percent), 24))
                    
                    # Draw the text
                    left_panel.blit(effect_text, (15, 74))
                else:
                    # Show "No Active Effects" when empty
                    no_effect_text = self.font_small.render("NO ACTIVE EFFECTS", True, (0, 0, 0))
                    left_panel.blit(no_effect_text, (15, 74))
            
            # Big Icon Slot - shows enemy when hit, otherwise last pickup (moved down 70px for potion timer)
            pygame.draw.rect(left_panel, (255, 255, 255), (12, 140, 88, 88), 2)
            cx, cy = 12 + 44,140 + 44

            # Priority: 1. Enemy portrait, 2. Active status effects, 3. Last pickup
            if self.enemy_portrait_timer > 0 and self.last_enemy_hit is not None:
                self._draw_enemy_portrait_hud(left_panel, self.last_enemy_hit, cx, cy)
            elif self.status_effects.get('speed', 0) > 0:
                # Show speed potion sprite
                if 'item_potion' in self.sprites and self.sprites['item_potion'] is not None:
                    sprite = self.sprites['item_potion']
                    scaled = pygame.transform.scale(sprite, (60, 60))
                    scaled.fill((100, 100, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
                    left_panel.blit(scaled, (cx - 30, cy - 30))
            elif self.status_effects.get('strength', 0) > 0:
                # Show strength potion sprite
                if 'item_potion' in self.sprites and self.sprites['item_potion'] is not None:
                    sprite = self.sprites['item_potion']
                    scaled = pygame.transform.scale(sprite, (60, 60))
                    scaled.fill((255, 200, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
                    left_panel.blit(scaled, (cx - 30, cy - 30))
            elif self.status_effects.get('missiles', 0) > 0:
                # Show missiles potion sprite
                if 'item_potion' in self.sprites and self.sprites['item_potion'] is not None:
                    sprite = self.sprites['item_potion']
                scaled = pygame.transform.scale(sprite, (60, 60))
                scaled.fill((100, 255, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
                left_panel.blit(scaled, (cx - 30, cy - 30))
            elif self.status_effects.get('invis', 0) > 0:
                # Show invisibility scroll sprite (if it exists)
                if 'item_scroll' in self.sprites and self.sprites['item_scroll'] is not None:
                    sprite = self.sprites['item_scroll']
                    scaled = pygame.transform.scale(sprite, (60, 60))
                    left_panel.blit(scaled, (cx - 30, cy - 30))
                else:
                    # Fallback: render scroll graphics
                    try:
                        # Draw a simple scroll graphic
                        pygame.draw.rect(left_panel, (255, 255, 200), (cx - 20, cy - 15, 40, 30))
                        pygame.draw.rect(left_panel, (200, 200, 150), (cx - 20, cy - 15, 40, 30), 2)
                        # Scroll ends
                        pygame.draw.circle(left_panel, (139, 69, 19), (cx - 20, cy), 3)
                        pygame.draw.circle(left_panel, (139, 69, 19), (cx + 20, cy), 3)

                    except:
                        #
                        pygame.draw.circle(left_panel, (255, 255, 0), (cx, cy), 20)
            elif hasattr(self, 'last_pickup_type') and self.last_pickup_type is not None:
                # Show last pickup item
                sprite_key = None
                if self.last_pickup_type == ItemType.KEY:
                    sprite_key = 'item_key'
                elif self.last_pickup_type == ItemType.FOOD:
                    sprite_key = 'item_apple'
                elif self.last_pickup_type == ItemType.GOLD:
                    sprite_key = 'item_gold'

                if sprite_key and sprite_key in self.sprites and self.sprites[sprite_key] is not None:
                    sprite = self.sprites[sprite_key]
                    scaled = pygame.transform.scale(sprite, (60, 60))
                    left_panel.blit(scaled, (cx - 30, cy - 30))
                else:
                    # Fallback to original drawing
                    if self.last_pickup_type == ItemType.KEY:
                        # Draw key with hazard symbols
                        pygame.draw.rect(left_panel, (230, 200, 40), (cx-14, cy-3, 28, 6))
                        pygame.draw.rect(left_panel, (230, 200, 40), (cx+14, cy-10, 6, 22))
                        pygame.draw.circle(left_panel, (255, 230, 90), (cx+10, cy), 6)

                        # Add hazard symbols around the key
                        # Triangle (spikes) - top left
                        pygame.draw.polygon(left_panel, (180, 180, 180), [(cx-25, cy-15+5), (cx-20, cy-25), (cx-15, cy-15+5)])
                        # Plus sign (rune) - top right
                        pygame.draw.line(left_panel, (80, 140, 255), (cx+25-5, cy-20), (cx+25+5, cy-20), 2)
                        pygame.draw.line(left_panel, (80, 140, 255), (cx+25, cy-20-5), (cx+25, cy-20+5), 2)
                        # Green blob (poison) - bottom
                        pygame.draw.ellipse(left_panel, (20, 160, 40), (cx-8, cy+15, 16, 10))
                        pygame.draw.ellipse(left_panel, (80, 220, 100), (cx-5, cy+16, 10, 6))
                    elif self.last_pickup_type == ItemType.FOOD:
                        pygame.draw.circle(left_panel, (230, 20, 20), (cx, cy), 18)
                        pygame.draw.circle(left_panel, (255, 120, 120), (cx-5, cy-5), 8)
                    elif self.last_pickup_type == ItemType.GOLD:
                        pygame.draw.circle(left_panel, (235, 200, 0), (cx, cy), 18)
                        pygame.draw.circle(left_panel, (255, 230, 80), (cx, cy), 18, 3)
                    else:
                        pygame.draw.ellipse(left_panel, (60, 140, 255), (cx-14, cy-20, 28, 36))
            self.screen.blit(left_panel, (0, bottom_y))

            right_panel = pygame.Surface((right_w, UI_HEIGHT))
            right_panel.fill((0, 0, 0))
            pygame.draw.rect(right_panel, (255, 255, 255), (0, 0, right_w, UI_HEIGHT), 2)
            def t(txt):
                return self.font_small.render(txt, True, (255, 255, 255))
            if self.player:
                right_panel.blit(t(f"SCORE {self.score:5d}"), (10, 8))
                right_panel.blit(t(f"SPEED    {self.player.character_class.speed:2d}"), (10, 28))
                right_panel.blit(t(f"STRENGTH {self.player.character_class.strength:2d}"), (10, 48))
                right_panel.blit(t(f"MISSILES {self.player.character_class.missiles:2d}"), (10, 68))
                right_panel.blit(t(f"GOLD {self.player.gold:2d}"), (10, 88))
                right_panel.blit(t(f"KEYS     {self.player.keys_collected:2d}"), (10, 108))
            right_panel.blit(t(f"LEVEL {self.current_level}"), (150, 8))
            self.screen.blit(right_panel, (left_w, bottom_y))

            # Farsee mini-map (only show when NOT in inventory)
            if hasattr(self, 'farsee_timer') and self.farsee_timer > 0 and not self.inventory_open:
                self._render_farsee_minimap()

        # Inventory overlay (readable grid) - positioned higher for more rows
        if self.inventory_open:
            inv_w, inv_h = SCREEN_WIDTH - 40, 220  # Increased height for more rows
            inv = pygame.Surface((inv_w, inv_h), pygame.SRCALPHA)
            inv.fill((0, 0, 0, 210))
            x0, y0 = 20, GAME_HEIGHT + 10  # Position higher in bottom area
            # Title (smaller, high-contrast)
            title = self.font_small.render("INVENTORY(Enter=Use, D=Drop, ESC=Close)", True, YELLOW)
            inv.blit(title, (10, 6))
            # Slots grid - fixed 4 columns for better layout
            slot_w, slot_h, pad = 80, 32, 8  # Slightly smaller slots for 4 columns
            cols = 4  # Fixed 4 columns
            # Abbreviations for compact labels
            def abbr(t):
                n = str(t).split('.')[-1]
                return {
                    'POTION_SPEED': 'SPEED',
                    'POTION_STRENGTH': 'STRENGTH',
                    'POTION_MISSILES': 'MISSILE',
                    'SCROLL_BLAST': 'BLAST',
                    'SCROLL_FARSEE': 'FARSEE',
                    'SCROLL_INVISIBILITY': 'INVIS',
                    'SCROLL_REVIVE': 'REVIVE',
                }.get(n, n)
            for i, item in enumerate(self.player.inventory):
                row = i // cols
                col = i % cols
                sx = 10 + col * (slot_w + pad)
                sy = 30 + row * (slot_h + pad)
                # Slot background
                pygame.draw.rect(inv, (30, 30, 30), (sx, sy, slot_w, slot_h))
                border_color = CYAN if i == self.inventory_cursor else (200, 200, 200)
                pygame.draw.rect(inv, border_color, (sx, sy, slot_w, slot_h), 2)
                # Label centered
                label = self.font_small.render(abbr(item.type), True, WHITE)
                inv.blit(label, (sx + (slot_w - label.get_width()) // 2, sy + (slot_h - label.get_height()) // 2))
            self.screen.blit(inv, (x0, y0))

        # ADDED: short lived aura effects around player
        self._render_effects_overlay()

        # DO NOT render UI messages here - they're rendered in render() method conditionally

    # ADDED: draw player with class-specific look and animation
    def _draw_player(self, surf, x, y):
        cls_name = self.player.character_class.name.lower()
        # Walking animation offset - MORE VISIBLE
        bob = 0
        if self.player.anim_frame == 1:
            bob = -3  # Even more visible bob
        
        # Try to use loaded sprites first
        sprite_key = None
        if 'wizard' in cls_name:
            sprite_key = 'wizard'
        elif 'gunfighter' in cls_name:
            sprite_key = 'gunfighter'
        elif 'valkyrie' in cls_name:
            sprite_key = 'valkyrie'
        elif 'android' in cls_name:
            sprite_key = 'android'
        elif 'pirate' in cls_name:
            sprite_key = 'pirate'
        elif 'punkrocker' in cls_name:
            sprite_key = 'punkrocker'
        elif 'nerd' in cls_name:
            sprite_key = 'nerd'
        else:
            sprite_key = 'samurai'
            
        if sprite_key in self.sprites:
            sprite = self.sprites[sprite_key]
            # Scale sprite to appropriate size (32x32)
            scaled = pygame.transform.scale(sprite, (32, 32))
            # Load sprites as-is without shading (fixed for all classes like wizard)
            # Wizard sprite used as-is without tinting
            surf.blit(scaled, (x - 16, y - 16 + bob))
        else:
            # Fallback: use graphics instead of emojis (emojis don't work in pygame)
            self._draw_character_fallback_original(surf, x, y + bob, cls_name)

    # ADDED: original character fallback graphics
    def _draw_character_fallback_original(self, surf, x, y, cls_name):
    
        bob = 0  # No animation bob for fallbacks
        if 'wizard' in cls_name:
            # Blue robe with pointy hat
            robe_color = (50, 80, 200)
            pygame.draw.circle(surf, robe_color, (x, y + bob), 10)
            # Pointy hat
            pygame.draw.polygon(surf, (50, 80, 200), [(x-5, y-8+bob), (x+5, y-8+bob), (x, y-14+bob)])
            # Staff
            pygame.draw.line(surf, (160, 120, 60), (x+6, y-6+bob), (x+6, y+8+bob), 2)
        elif 'valkyrie' in cls_name:
            body_color = (180, 200, 220)
            pygame.draw.circle(surf, body_color, (x, y + bob), 10)
            # Winged helmet
            pygame.draw.arc(surf, (220, 220, 220), (x-12, y-10+bob, 24, 12), 0, 3.14, 2)
            # Shield
            pygame.draw.circle(surf, (200, 200, 200), (x-8, y+bob), 5, 2)
        elif 'samurai' in cls_name:
            body_color = (180, 40, 40)
            pygame.draw.circle(surf, body_color, (x, y + bob), 10)
            # Topknot
            pygame.draw.circle(surf, (20, 20, 20), (x, y-10+bob), 3)
            # Katana
            pygame.draw.line(surf, (240, 240, 240), (x+6, y-8+bob), (x+14, y+8+bob), 2)
        elif 'pirate' in cls_name:
            body_color = (139, 69, 19)  # Brown
            pygame.draw.circle(surf, body_color, (x, y + bob), 10)
            # Pirate hat
            pygame.draw.polygon(surf, (0, 0, 0), [(x-8, y-10+bob), (x+8, y-10+bob), (x+6, y-6+bob), (x-6, y-6+bob)])
            # Eye patch
            pygame.draw.circle(surf, (0, 0, 0), (x-3, y-2+bob), 2)
        elif 'punk' in cls_name or 'punkrocker' in cls_name:
            body_color = (255, 105, 180)
            pygame.draw.circle(surf, body_color, (x, y + bob), 10)
            # Mohawk
            pygame.draw.rect(surf, (255, 20, 147), (x-2, y-12+bob, 4, 6))
        elif 'android' in cls_name:
            body_color = (192, 192, 192)  # Silver
            pygame.draw.circle(surf, body_color, (x, y + bob), 10)
            # Robot eyes
            pygame.draw.circle(surf, (255, 0, 0), (x-3, y-2+bob), 2)
            pygame.draw.circle(surf, (255, 0, 0), (x+3, y-2+bob), 2)
        else:
            # Default character
            body_color = (240, 230, 140)
            pygame.draw.circle(surf, body_color, (x, y + bob), 10)

        # Dark outline for all
        pygame.draw.circle(surf, (0, 0, 0), (x, y + bob), 10, 2)

   
    def _render_character_emoji_preview(self, character_key, x, y):
       

        try:
            # Use homemade character graphics instead of emojis
            self._render_character_fallback_small(self.screen, x + 12, y + 12, character_key)

        except Exception as e:
            # Fallback: render simple character graphics
            self._render_character_fallback_small(self.screen, x + 12, y + 12, character_key)

    # ADDED: small character fallback for previews
    def _render_character_fallback_small(self, surf, x, y, character_key):
       
        if character_key == 'wizard':
            pygame.draw.circle(surf, (50, 80, 200), (x, y), 8)
            pygame.draw.polygon(surf, (50, 80, 200), [(x-4, y-6), (x+4, y-6), (x, y-10)])
        elif character_key == 'valkyrie':
            pygame.draw.circle(surf, (180, 200, 220), (x, y), 8)
            pygame.draw.arc(surf, (220, 220, 220), (x-8, y-8, 16, 8), 0, 3.14, 1)
        elif character_key == 'samurai':
            pygame.draw.circle(surf, (180, 40, 40), (x, y), 8)
            pygame.draw.circle(surf, (20, 20, 20), (x, y-8), 2)
        elif character_key == 'pirate':
            pygame.draw.circle(surf, (139, 69, 19), (x, y), 8)
            pygame.draw.polygon(surf, (0, 0, 0), [(x-6, y-8), (x+6, y-8), (x+4, y-4), (x-4, y-4)])
        elif character_key == 'android':
            pygame.draw.circle(surf, (192, 192, 192), (x, y), 8)
            pygame.draw.circle(surf, (255, 0, 0), (x-2, y-2), 1)
            pygame.draw.circle(surf, (255, 0, 0), (x+2, y-2), 1)
        elif character_key == 'punkrocker':
            pygame.draw.circle(surf, (255, 105, 180), (x, y), 8)
            pygame.draw.rect(surf, (255, 20, 147), (x-2, y-10, 4, 4))
        elif character_key == 'gunfighter':
            pygame.draw.circle(surf, (200, 150, 100), (x, y), 8)
            pygame.draw.line(surf, (100, 50, 0), (x-4, y), (x+4, y), 2)
        elif character_key == 'nerd':
            pygame.draw.circle(surf, (200, 200, 150), (x, y), 8)
            pygame.draw.rect(surf, (0, 0, 0), (x-3, y-3, 6, 2))  # Glasses
        else:
            pygame.draw.circle(surf, (240, 230, 140), (x, y), 8)

        # Small outline for all
        pygame.draw.circle(surf, (0, 0, 0), (x, y), 8, 1)

    # ADDED: facing direction indicator (small arrow)
    def _draw_facing_indicator(self, surf, x, y):
        color = (255, 255, 255)
        if self.player.direction == Direction.UP:
            pygame.draw.polygon(surf, color, [(x, y-14), (x-4, y-6), (x+4, y-6)])
        elif self.player.direction == Direction.DOWN:
            pygame.draw.polygon(surf, color, [(x, y+14), (x-4, y+6), (x+4, y+6)])
        elif self.player.direction == Direction.LEFT:
            pygame.draw.polygon(surf, color, [(x-14, y), (x-6, y-4), (x-6, y+4)])
        elif self.player.direction == Direction.RIGHT:
            pygame.draw.polygon(surf, color, [(x+14, y), (x+6, y-4), (x+6, y+4)])


    # ADDED: Draw enemy portrait in HUD using sprites
    def _draw_enemy_portrait_hud(self, surf, enemy_type, x, y):
        """Draw large enemy portrait for HUD using sprites"""
        sprite_key = None
        
        # Map enemy types to loaded sprites
        if enemy_type == EnemyType.SLIME:
            sprite_key = 'enemy_slime'
        elif enemy_type == EnemyType.SPIDER:
            sprite_key = 'enemy_spider'
        elif enemy_type == EnemyType.GHOST:
            sprite_key = 'enemy_ghost'
        elif enemy_type == EnemyType.FROG:
            sprite_key = 'enemy_demon'
        elif enemy_type == EnemyType.SCORPION:
            sprite_key = 'enemy_scorpion'
        elif enemy_type == EnemyType.SKELETON:
            sprite_key = 'enemy_skeleton'
        elif enemy_type == EnemyType.DEMON2:
            sprite_key = 'enemy_demon2'
        elif enemy_type == EnemyType.ORGE:
            sprite_key = 'enemy_orge'
        elif enemy_type == EnemyType.CYCLOPS:
            sprite_key = 'enemy_cyclops'
        elif enemy_type == EnemyType.CHIMERA1:
            sprite_key = 'enemy_chimera1'
        elif enemy_type == EnemyType.CHIMERA2:
            sprite_key = 'enemy_chimera2'
        elif enemy_type == EnemyType.CHIMERA3:
            sprite_key = 'enemy_chimera3'
            
        if sprite_key and sprite_key in self.sprites and self.sprites[sprite_key] is not None:
            sprite = self.sprites[sprite_key]
            # Scale sprite for HUD display (larger)
            scaled = pygame.transform.scale(sprite, (70, 70))
            surf.blit(scaled, (x - 35, y - 35))
        else:
            # Fallback to original portrait drawing
            self._draw_enemy_portrait_fallback(surf, enemy_type, x, y)

    def _draw_enemy_portrait_fallback(self, surf, enemy_type, x, y):
        """Draw large enemy portrait for HUD using emojis"""
       

        try:
            
            self._draw_enemy_fallback_graphics(surf, enemy_type, x, y)

        except Exception as e:
            # Ultimate fallback if emoji rendering fails
            pygame.draw.circle(surf, (255, 0, 0), (x, y), 25)
            pygame.draw.circle(surf, (0, 0, 0), (x-8, y), 5)
            pygame.draw.circle(surf, (0, 0, 0), (x+8, y), 5)

    def _draw_enemy_fallback_graphics(self, surf, enemy_type, x, y):
        """Draw homemade enemy graphics for HUD portraits"""
        if enemy_type == EnemyType.SLIME:
            # Green slime blob
            pygame.draw.circle(surf, (0, 255, 0), (x, y), 25)
            pygame.draw.circle(surf, (0, 200, 0), (x, y), 20)
            pygame.draw.circle(surf, (0, 0, 0), (x-8, y-5), 3)
            pygame.draw.circle(surf, (0, 0, 0), (x+8, y-5), 3)
        elif enemy_type == EnemyType.GHOST:
            # White ghost shape
            pygame.draw.circle(surf, (255, 255, 255), (x, y-5), 20)
            pygame.draw.polygon(surf, (255, 255, 255), [(x-20, y+15), (x-10, y+5), (x, y+15), (x+10, y+5), (x+20, y+15)])
            pygame.draw.circle(surf, (0, 0, 0), (x-6, y-8), 3)
            pygame.draw.circle(surf, (0, 0, 0), (x+6, y-8), 3)
        elif enemy_type == EnemyType.SCORPION:
            # Brown scorpion
            pygame.draw.ellipse(surf, (139, 69, 19), (x-15, y-8, 30, 16))
            pygame.draw.circle(surf, (139, 69, 19), (x+20, y-15), 8)  # Tail
            pygame.draw.circle(surf, (255, 0, 0), (x+20, y-15), 3)    # Stinger
            pygame.draw.circle(surf, (0, 0, 0), (x-5, y-3), 2)
            pygame.draw.circle(surf, (0, 0, 0), (x+5, y-3), 2)
        elif enemy_type == EnemyType.SKELETON:
            # White skull
            pygame.draw.circle(surf, (255, 255, 255), (x, y), 20)
            pygame.draw.circle(surf, (0, 0, 0), (x-8, y-5), 4)  # Eye sockets
            pygame.draw.circle(surf, (0, 0, 0), (x+8, y-5), 4)
            pygame.draw.polygon(surf, (0, 0, 0), [(x-3, y+5), (x, y+15), (x+3, y+5)])  # Nasal cavity
        else:
            # Default red monster
            pygame.draw.circle(surf, (255, 0, 0), (x, y), 25)
            pygame.draw.circle(surf, (0, 0, 0), (x-8, y), 5)
            pygame.draw.circle(surf, (0, 0, 0), (x+8, y), 5)
    
    # ADDED: enemy sprites matching original Gauntlet monsters
    def _draw_enemy(self, surf, enemy, x, y):
        sprite_key = None
        wobble = 0
        
        # Map enemy types to loaded sprites
        if enemy.type == EnemyType.SLIME:
            sprite_key = 'enemy_slime'
            wobble = 2 * math.sin(enemy.anim_t * 6.0)
        elif enemy.type == EnemyType.SPIDER:
            sprite_key = 'enemy_spider'
        elif enemy.type == EnemyType.GHOST:
            sprite_key = 'enemy_ghost'
        elif enemy.type == EnemyType.FROG:
            sprite_key = 'enemy_demon'
        elif enemy.type == EnemyType.SCORPION:
            sprite_key = 'enemy_scorpion'
        elif enemy.type == EnemyType.SKELETON:
            sprite_key = 'enemy_skeleton'
        elif enemy.type == EnemyType.DEMON2:
            sprite_key = 'enemy_demon2'
        elif enemy.type == EnemyType.ORGE:
            sprite_key = 'enemy_orge'
        elif enemy.type == EnemyType.CYCLOPS:
            sprite_key = 'enemy_cyclops'
        elif enemy.type == EnemyType.CHIMERA1:
            sprite_key = 'enemy_chimera1'
        elif enemy.type == EnemyType.CHIMERA2:
            sprite_key = 'enemy_chimera2'
        elif enemy.type == EnemyType.CHIMERA3:
            sprite_key = 'enemy_chimera3'
            
        if sprite_key and sprite_key in self.sprites and self.sprites[sprite_key] is not None:
            sprite = self.sprites[sprite_key]
            # Scale sprite to appropriate size
            scaled = pygame.transform.scale(sprite, (32, 32))
            # Apply hit flash
            if enemy.hit_timer > 0:
                scaled.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(scaled, (x - 16, y - 16 + int(wobble)))
        else:
            # Fallback to original drawing code
            if enemy.type == EnemyType.SLIME:
                # Green blob that wobbles (OOZE from original)
                wobble = 2 * math.sin(enemy.anim_t * 6.0)
                pygame.draw.ellipse(surf, (20, 180, 60), (x - 12, y - 8 + int(wobble), 24, 16))
                pygame.draw.ellipse(surf, (40, 220, 80), (x - 8, y - 5 + int(wobble), 16, 10))
                # Eyes
                pygame.draw.circle(surf, (255, 255, 255), (x-3, y-2+int(wobble)), 2)
                pygame.draw.circle(surf, (255, 255, 255), (x+3, y-2+int(wobble)), 2)
                pygame.draw.circle(surf, (0, 0, 0), (x-3, y-2+int(wobble)), 1)
                pygame.draw.circle(surf, (0, 0, 0), (x+3, y-2+int(wobble)), 1)
            elif enemy.type == EnemyType.SPIDER:
                # Black spider with red markings
                pygame.draw.ellipse(surf, (40, 40, 40), (x-8, y-6, 16, 12))
                # Red hourglass
                pygame.draw.polygon(surf, (255, 0, 0), [(x, y-4), (x-3, y), (x, y+4), (x+3, y)])
                # Legs
                for dx, dy in [(-12, -2), (-10, 2), (10, -2), (12, 2)]:
                    pygame.draw.line(surf, (20, 20, 20), (x, y), (x+dx, y+dy), 2)
            elif enemy.type == EnemyType.GHOST:
                # Semi-transparent ghost with flickering
                ghost = pygame.Surface((30, 30), pygame.SRCALPHA)
                alpha = 140 + int(40 * math.sin(enemy.anim_t * 8.0))
                # Ghost body
                pygame.draw.circle(ghost, (200, 200, 255, alpha), (15, 12), 10)
                # Wavy bottom
                for i in range(3):
                    wx = 8 + i * 7
                    wy = 20 + int(2 * math.sin(enemy.anim_t * 4 + i))
                    pygame.draw.circle(ghost, (200, 200, 255, alpha), (wx, wy), 4)
                # Eyes
                pygame.draw.circle(ghost, (0, 0, 0, 255), (11, 10), 2)
                pygame.draw.circle(ghost, (0, 0, 0, 255), (19, 10), 2)
                surf.blit(ghost, (x - 15, y - 12))
            elif enemy.type == EnemyType.FROG:
                # Demon (red horned creature from original)
                pygame.draw.ellipse(surf, (180, 20, 20), (x-10, y-8, 20, 16))
                # Horns
                pygame.draw.polygon(surf, (120, 0, 0), [(x-8, y-8), (x-10, y-14), (x-6, y-8)])
                pygame.draw.polygon(surf, (120, 0, 0), [(x+6, y-8), (x+10, y-14), (x+8, y-8)])
                # Eyes
                pygame.draw.circle(surf, (255, 255, 0), (x-4, y-2), 2)
                pygame.draw.circle(surf, (255, 255, 0), (x+4, y-2), 2)
            elif enemy.type == EnemyType.SCORPION:
                # Yellow/gold scorpion with tail
                body = (220, 170, 40)
                # Body segments
                pygame.draw.ellipse(surf, body, (x-8, y-6, 16, 12))
                # Claws
                pygame.draw.circle(surf, body, (x-10, y-4), 4)
                pygame.draw.circle(surf, body, (x+10, y-4), 4)
                pygame.draw.arc(surf, (180, 140, 30), (x-14, y-8, 8, 8), 0, 3.14, 2)
                pygame.draw.arc(surf, (180, 140, 30), (x+6, y-8, 8, 8), 0, 3.14, 2)
                # Tail with stinger
                pygame.draw.lines(surf, body, False, [(x, y), (x-8, y-8), (x-12, y-14), (x-10, y-18)], 3)
                pygame.draw.circle(surf, (255, 0, 0), (x-10, y-18), 2)
            elif enemy.type == EnemyType.SKELETON:
                # White bony skeleton
                bone_color = (240, 240, 240)
                # Skull
                pygame.draw.circle(surf, bone_color, (x, y-4), 6)
                # Eye sockets
                pygame.draw.circle(surf, (0, 0, 0), (x-2, y-5), 1)
                pygame.draw.circle(surf, (0, 0, 0), (x+2, y-5), 1)
                # Jaw
                pygame.draw.arc(surf, bone_color, (x-4, y-2, 8, 6), 0, 3.14, 2)
                # Spine
                pygame.draw.lines(surf, bone_color, False, [(x, y+2), (x, y+8), (x, y+14)], 3)
                # Ribs
                for i in range(3):
                    ry = y + 4 + i * 3
                    pygame.draw.line(surf, bone_color, (x-4, ry), (x+4, ry), 2)
                # Arms
                pygame.draw.line(surf, bone_color, (x, y+4), (x-6, y+8), 2)
                pygame.draw.line(surf, bone_color, (x, y+4), (x+6, y+8), 2)
            else:
                # Generic grunt
                pygame.draw.circle(surf, (160, 80, 40), (x, y), 10)
                pygame.draw.circle(surf, (255, 255, 255), (x-3, y-2), 2)
                pygame.draw.circle(surf, (255, 255, 255), (x+3, y-2), 2)
            
            # Hit flash
            if enemy.hit_timer > 0:
                pygame.draw.circle(surf, (255, 255, 255), (x, y), 12, 2)

    def render_ui(self):
        """Render the UI/stats area"""
        # Position UI at the bottom of the game area
        ui_y_position = GAME_HEIGHT

        ui_surface = pygame.Surface((SCREEN_WIDTH, UI_HEIGHT))
        ui_surface.fill(DARK_GRAY)

        # Draw UI border
        pygame.draw.rect(ui_surface, WHITE, (0, 0, SCREEN_WIDTH, UI_HEIGHT), 2)

        if self.player:
            # Life bar
            life_percent = max(0, self.player.life / self.player.max_life)
            pygame.draw.rect(ui_surface, RED, (30, 20, 250, 25))
            pygame.draw.rect(ui_surface, GREEN, (30, 20, int(250 * life_percent), 25))

            # Life text
            life_text = self.font_medium.render(f"LIFE: {int(self.player.life)}", True, (0, 0, 0))
            ui_surface.blit(life_text, (300, 20))

            # Potion timer bar (below life bar)
            if hasattr(self, 'status_effects') and self.status_effects:
                # Find active potion effects
                active_effects = []
                for effect, time_left in self.status_effects.items():
                    if time_left > 0 and effect in ['speed', 'strength', 'missiles', 'shield', 'invis']:
                        active_effects.append((effect, time_left))

                if active_effects:
                    # Show the first active effect (or could cycle through them)
                    effect_name, time_left = active_effects[0]

                    # Calculate scaling based on maximum possible duration for this effect type
                    if effect_name == 'farsee':
                        # Farsee is always 30 seconds maximum
                        max_effect_duration = 30.0
                    else:
                        # Potions scale up to WOKE difficulty (6x multiplier)
                        max_effect_duration = POTION_DURATION * 6.0  # Always use maximum possible

                    # Scale the bar based on remaining time vs maximum duration
                    effect_percent = time_left / max_effect_duration
                    effect_percent = max(0.0, min(1.0, effect_percent))  # Clamp to 0-1

                    # Timer bar background and fill (same style as LIFE bar)
                    pygame.draw.rect(ui_surface, RED, (30, 50, 250, 25))  # Same red background as LIFE bar
                    pygame.draw.rect(ui_surface, (255, 255, 0), (30, 50, int(250 * effect_percent), 25))  # Yellow fill

                    # Effect name and time
                    effect_text = self.font_small.render(f"{effect_name.upper()}: {time_left:.1f}s", True, (0, 0, 0))
                    ui_surface.blit(effect_text, (300, 45))

            # Stats display
            stats_text = self.font_small.render(
                f"SPEED:{self.player.character_class.speed} STRENGTH:{self.player.character_class.strength}  MISSILES:{self.player.character_class.missiles}",
                True, CYAN
            )
            ui_surface.blit(stats_text, (30, 60))

            # Level, gold, and keys
            level_text = self.font_medium.render(f"LEVEL {self.current_level}", True, CYAN)
            ui_surface.blit(level_text, (300, 100))

            # Inventory display
            inv_x = 30
            inv_y = 100
            inv_text = self.font_medium.render("INVENTORY:", True, WHITE)
            ui_surface.blit(inv_text, (inv_x, inv_y))

            # Count quantities of each item type
            item_counts = {}
            for item in self.player.inventory:
                item_type = item.type
                item_counts[item_type] = item_counts.get(item_type, 0) + 1

            # Add keys count (keys are tracked separately, not in inventory)
            if self.player.keys_collected > 0:
                item_counts[ItemType.KEY] = self.player.keys_collected

            # Show inventory items in column format with quantities
            visible_types = list(item_counts.keys())[-6:] if len(item_counts) > 6 else list(item_counts.keys())
            for i, item_type in enumerate(visible_types):
                # Use full names instead of abbreviations
                if item_type == ItemType.FOOD:
                    item_name = "Food"
                elif item_type == ItemType.KEY:
                    item_name = "Key"
                elif item_type == ItemType.GOLD:
                    item_name = "Gold"
                elif item_type == ItemType.POTION_SPEED:
                    item_name = "Speed Potion"
                elif item_type == ItemType.POTION_STRENGTH:
                    item_name = "Strength Potion"
                elif item_type == ItemType.POTION_MISSILES:
                    item_name = "Missiles Potion"
                elif item_type == ItemType.SCROLL_INVISIBILITY:
                    item_name = "Invisibility Scroll"
                elif item_type == ItemType.SCROLL_FARSEE:
                    item_name = "Farsee Scroll"
                elif item_type == ItemType.SCROLL_REVIVE:
                    item_name = "Revive Scroll"
                elif item_type == ItemType.SCROLL_BLAST:
                    item_name = "Blast Scroll"
                else:
                    item_name = str(item_type).replace('ItemType.', '').replace('_', ' ').title()

                # Add quantity
                quantity = item_counts[item_type]
                if quantity > 1:
                    item_name = f"{item_name} x{quantity}"

                item_text = self.font_small.render(item_name, True, GREEN)
                ui_surface.blit(item_text, (inv_x, inv_y + 25 + i * 20))

            # Show inventory count if more than 6 item types
            if len(item_counts) > 6:
                count_text = self.font_small.render(f"+{len(item_counts)-6} more types", True, YELLOW)
                ui_surface.blit(count_text, (inv_x , inv_y + 25 + 6 * 20))

        self.screen.blit(ui_surface, (0, ui_y_position))

    def update_game_over(self):
        """Update game over logic"""
        if pygame.K_r in self.keys_pressed:
            self.reset_game()
            self.keys_pressed[pygame.K_r] = False

    def render_game_over(self):
        """Render game over screen"""
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        restart_text = self.font_medium.render("Press R to Restart", True, WHITE)

        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 150))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 250))

    def update_level_complete(self):
        """Update level complete logic"""
        pass

    def render_level_complete(self):
        """Render level complete screen"""
        pass

    def update_shop(self):
        """Update shop logic"""
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_key_time < self.key_delay:
            return

        if pygame.K_UP in self.keys_pressed:
            self.shop_selection = (self.shop_selection - 1) % len(self.shop_items)
            self.last_key_time = current_time
        elif pygame.K_DOWN in self.keys_pressed:
            self.shop_selection = (self.shop_selection + 1) % len(self.shop_items)
            self.last_key_time = current_time
        elif pygame.K_RETURN in self.keys_pressed:
            self.purchase_item(self.shop_selection)
            self.last_key_time = current_time
        elif pygame.K_ESCAPE in self.keys_pressed:
            self.state = GameState.PLAYING
            self.shop_cooldown = 30
            self.shop_block_until_exit = True
            self.last_key_time = current_time

        # Clear keys after handling
        self.keys_pressed.clear()

    def render_shop(self):
        """Render shop interface overlaid on current game state"""
        # First render the current game state (map + HUD)
        if hasattr(self, 'render_playing'):
            self.render_playing()
        if hasattr(self, 'render_ui'):
            self.render_ui()

        # Now overlay shop interface elements on top
        # Semi-transparent background for shop area only
        shop_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        shop_bg.fill((0, 0, 0))  # Black background
        shop_bg.set_alpha(180)  # Semi-transparent (0-255, 180 = ~70% opacity)
        self.screen.blit(shop_bg, (0, 0))

        # Shop title
        shop_title = self.font_large.render("COMPUTER TERMINAL", True, GREEN)
        self.screen.blit(shop_title, (SCREEN_WIDTH//2 - shop_title.get_width()//2, 50))

        # Player gold display
        if self.player:
            gold_text = self.font_medium.render(f"GOLD: {self.player.gold}", True, YELLOW)
            self.screen.blit(gold_text, (80, 100))
        else:
            gold_text = self.font_medium.render("GOLD: 0", True, YELLOW)
            self.screen.blit(gold_text, (80, 100))

        # Display shop items with clear selection indicator
        y_pos = 150
        for i, item in enumerate(self.shop_items):
            if i == self.shop_selection:
                # Highlighted selection
                bg_color = (50, 50, 100)  # Dark blue background
                pygame.draw.rect(self.screen, bg_color, (60, y_pos - 6, 420, 36))
                arrow = ">>>"
                color = YELLOW
            else:
                arrow = "   "
                color = WHITE

            item_text = self.font_small.render(
                f"{arrow} {item['name']} - {item['cost']} GOLD",
                True, color
            )
            self.screen.blit(item_text, (80, y_pos))
            y_pos += 30

        # Instructions overlaid on game area
        instructions = [
            "ARROW KEYS: Navigate items",
            "ENTER: Purchase selected item",
            "ESC: Exit shop"
        ]

        y_pos = GAME_HEIGHT - 60  # Position instructions near bottom of game area
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, CYAN)
            self.screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, y_pos))
            y_pos += 18

    def purchase_item(self, item_index):
        """Purchase an item from the shop"""
        if not self.player:
            return

        item = self.shop_items[item_index]

        if self.player.gold >= item['cost']:
            if len(self.player.inventory) < self.player.max_inventory:
                self.player.gold -= item['cost']
                # Keys and food apply immediately. Other items go to inventory.
                if item['type'] == ItemType.KEY:
                    self.player.keys_collected += 1
                    self.sound_manager.play_item_collect()
                    # FIX: HUD message instead of console
                    self.add_ui_message("Bought KEY.")
                    
                elif item['type'] == ItemType.FOOD:
                    self.player.life = min(self.player.max_life, self.player.life + 25)
                    self.sound_manager.play_food_eat()
                    # FIX: HUD message instead of console
                    self.add_ui_message("Bought FOOD.")
                    
                else:
                    new_item = Item(0, 0, item['type'])
                    self.player.inventory.append(new_item)
                    self.sound_manager.play_item_collect()
                    # FIX: HUD message instead of console
                    self.add_ui_message(f"Bought {item['name']}.")
                    
                    
            else:
                # Allow stacking FOOD and GOLD even if inventory area is full (quality-of-life)
                if item['type'] == ItemType.FOOD:
                    self.player.gold -= item['cost']
                    self.player.life = min(self.player.max_life, self.player.life + 25)
                    self.sound_manager.play_food_eat()
                    # FIX: HUD message instead of console
                    self.add_ui_message("Inventory full; Ate FOOD")
                elif item['type'] == ItemType.GOLD:
                    self.player.gold -= item['cost']
                    self.player.gold += GOLD_VALUE
                    self.sound_manager.play_gold_collect()
                    # FIX: HUD message instead of console
                    self.add_ui_message("Inventory full; Collected GOLD")
                else:
                    # FIX: HUD message instead of console
                    self.add_ui_message("INVENTORY FULL!")
        else:
            # FIX: HUD message instead of console
            self.add_ui_message("NOT ENOUGH GOLD!")
            self.add_ui_message(f"Need {item['cost']} gold")

    def update_help(self):
        """Update help screen logic"""
        # Prevent immediate exit if we just entered this frame
        if self.help_entered_this_frame:
            self.help_entered_this_frame = False
            return

        # If we're ignoring H until release, check if H has been released
        if self.help_ignore_h_until_release:
            if pygame.K_h not in self.keys_pressed:
                self.help_ignore_h_until_release = False  # H has been released, stop ignoring
            # Don't process exit logic while ignoring H
            return

        # Exit on ESC or H (only if H is not being ignored)
        if pygame.K_ESCAPE in self.keys_pressed or pygame.K_h in self.keys_pressed:
            # Return to the previous state (where we came from)
            if self.help_previous_state is not None:
                self.state = self.help_previous_state
                self.help_previous_state = None  # Clear it after use
            else:
                # Fallback to playing state if no previous state was stored
                self.state = GameState.PLAYING
            self.keys_pressed.pop(pygame.K_ESCAPE, None)
            self.keys_pressed.pop(pygame.K_h, None)
            self.help_ignore_h_until_release = False  # Clear the ignore flag

    def complete_level(self):
        """Advance to the next level"""
        self.current_level += 1
        if self.current_level > 6:
            self.current_level = 6  # Max level

        # FIX: HUD message instead of console
        self.add_ui_message(f"Level {self.current_level - 1} complete → L{self.current_level}")

        # Reset player position for new level, preserve chosen character class key
        character_key = getattr(self, 'current_character_key', None)
        if not character_key and self.player:
            # Fallback: derive key from current class name
            for k, cls in CHARACTER_CLASSES.items():
                if cls.name == self.player.character_class.name:
                    character_key = k
                    break
        if not character_key:
            character_key = 'android'

        self.player = Player(character_key, self.current_level)
        self.player.game = self
        self.load_level(self.current_level)

    def render_help(self):
        """Render help screen - completely covers the entire screen"""
        # Fill entire screen with solid background to cover everything
        help_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        help_bg.fill((0, 0, 0))  # Solid black background
        self.screen.blit(help_bg, (0, 0))

        help_lines = [
            "CONTROLS:",
            "Arrow Keys / WASD; Move character",
            "SPACE; Fire missiles or melee attack",
            "T; Access terminals/shops",
            "D; Open doors (requires keys)",
            "TAB/I; Open/Close Inventory",
            "INVENTORY; ENTER=Use, D=Drop, ESC=Close",
            "CONSOLE; ARROW KEYS=Navigate, ENTER=Buy",
            "P; Pause/Unpause Game",
            "H; Open Help Screen",
            "S; SAVE GAME",
            "C; SWITCH CHARACTER",
            "ESC; Close Console/Inventory/Help",
            "",
            "GAMEPLAY:",
            "Fire missiles at enemies to defeat them",
            "Collect FOOD restores 10 life immediately",
            "Collect KEYS to unlock doors",
            "Defeat enemies for points",
            "",
            "OBJECTIVE:",
            "Navigate connected dungeon rooms",
            "Find keys to unlock doors",
            "Use shops to buy items,potions,scrolls",
            "Survive as long as possible!",
            "",
            "ITEMS:",
            "Potions; SPEED/STRENGTH/MISSILES",
            "Scrolls; BLAST/FARSEE/REVIVE/INVISIBILITY",
            "Gold; 100; Keys; auto-use on doors",
            "",
            "ENEMIES:",
            "Slime,Ghost,Scorpion,Skeleton",
           
            "",
            "CHARACTERS:",
            "ANDROID : Balanced stats",
            "VALKYRIE : Highest speed",
            "GUNFIGHTER : Good speed + missiles",
            "NERD : Lowest stats (challenge)",
            "PIRATE : Balanced fighter",
            "PUNKROCKER: Good all-around",
            "SAMURAI: High strength + speed",
            "WIZARD: Highest missiles",
            "",
            "SAVE/LOAD:",
            "S; Save game during play",
            "MAIN MENU > S; Load saved game",
            "Saves: level, score, stats, inventory",
            "",
            "CHARACTER SWITCHING:",
            "C; Cycle through characters",
            "Preserves: HP, gold, inventory, position",
            "",
            "DIFFICULTY LEVELS:",
            "WOKE: 6x potions, 1/6 monsters (Easy)",
            "MEDIUM: 3x potions, 1/3 monsters",
            "BASED: Normal difficulty (Hard)",
            "",
            "MENU FLOW:",
            "Main Menu > Difficulty > Character > Game",
            "",
        ]

        y_pos = 20
        for line in help_lines:
            if line == "":
                y_pos += 6
            else:
                color = GREEN if ":" in line else WHITE
                if "Press" in line:
                    color = CYAN
                elif "OBJECTIVE" in line:
                    color = YELLOW
                elif any(char_class in line for char_class in ["ANDROID", "VALKYRIE", "GUNFIGHTER", "NERD", "PIRATE", "PUNKROCKER", "SAMURAI", "WIZARD"]):
                    color = CYAN

                help_text = self.font_mini.render(line, True, color)
                self.screen.blit(help_text, (30, y_pos))
                y_pos += 14

    def render_paused(self):
        """Render paused game state"""
        # First render the current game
        self.render_playing()

        # Overlay pause message
        pause_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pause_bg.fill((0, 0, 0))
        pause_bg.set_alpha(150)  # Semi-transparent overlay
        self.screen.blit(pause_bg, (0, 0))

        # Pause text
        pause_text = self.font_large.render("PAUSED", True, YELLOW)
        self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50))

        # Instructions
        resume_text = self.font_medium.render("Press P or ESC to Resume", True, WHITE)
        self.screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 10))

    def update_paused(self):
        """Update paused game state - no updates while paused"""
        pass

    def update_level_select(self):
        """Update level select logic"""
        if pygame.K_LEFT in self.keys_pressed:
            self.selected_level = max(1, self.selected_level - 1)
            self.keys_pressed[pygame.K_LEFT] = False
        elif pygame.K_RIGHT in self.keys_pressed:
            self.selected_level = min(6, self.selected_level + 1)
            self.keys_pressed[pygame.K_RIGHT] = False
        elif pygame.K_RETURN in self.keys_pressed:
            self.start_game_at_level('valkyrie', self.selected_level)  # Default to Valkyrie
            self.keys_pressed[pygame.K_RETURN] = False
        elif pygame.K_ESCAPE in self.keys_pressed:
            self.state = GameState.MENU
            self.keys_pressed[pygame.K_ESCAPE] = False
            # Clear any other keys that might interfere
            self.keys_pressed.clear()

    def render_level_select(self):
        """Render level select screen"""
        select_text = self.font_large.render("Level Select", True, YELLOW)
        self.screen.blit(select_text, (SCREEN_WIDTH//2 - select_text.get_width()//2, 80))

        level_text = self.font_large.render(f"Level {self.selected_level}", True, GREEN)
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 160))

        # Instructions
        left_text = self.font_medium.render("LEFT/RIGHT: Change Level", True, WHITE)
        self.screen.blit(left_text, (SCREEN_WIDTH//2 - left_text.get_width()//2, 280))

        enter_text = self.font_medium.render("ENTER: Start   ESC: Back", True, WHITE)
        self.screen.blit(enter_text, (SCREEN_WIDTH//2 - enter_text.get_width()//2, 340))

    def start_game_at_level(self, character_class, level):
        """Start game with selected character at specific level"""
        self.current_character_key = character_class  # Track key for consistent class across levels
        self.player = Player(character_class, level)
        self.player.game = self
        self.current_level = level
        self.state = GameState.PLAYING
        self.load_level(level)
        print(f"Starting game with {character_class} at level {level}")

    def reset_game(self):
        """Reset game to initial state"""
        self.state = GameState.MENU
        self.current_level = 1
        self.score = 0
        self.player = None
        self.enemies = []
        self.items = []
        self.ui_messages = []  # Clear HUD messages when resetting

    def ensure_spawn_space(self):
        """Guarantee the player can move at level start by clearing nearby walls."""
        if not self.player:
            return
        safe_rect = pygame.Rect(int(self.player.x) - 24, int(self.player.y) - 24, 48, 48)
        new_walls = []
        for wx, wy in self.walls:
            # Never remove border walls
            if wx in (0, GAME_WIDTH - 32) or wy in (0, GAME_HEIGHT - 32):
                new_walls.append((wx, wy))
                continue
            wall_rect = pygame.Rect(wx, wy, 32, 32)
            if wall_rect.colliderect(safe_rect):
                continue  # clear very close tiles only
            new_walls.append((wx, wy))
        self.walls = new_walls

    def ensure_door_blockers(self):
        """Ensure one tile of approach space on the outside of each door.
        Doors are already openings in walls - do not place wall tiles at door positions."""
        approach_clear = []
        for door_x, door_y in self.doors:
            block_y = (int(door_y) // 32) * 32  # align to grid row nearest door
            # Decide orientation by proximity to room walls: carve approach tile outside
            left_tile = (door_x - 32, block_y)
            right_tile = (door_x + 32, block_y)
            top_tile = (door_x, block_y - 32)
            bottom_tile = (door_x, block_y + 32)
            # Choose an approach tile that is inside bounds and not border
            for tx, ty in (right_tile, left_tile, bottom_tile, top_tile):
                if 0 < tx < GAME_WIDTH - 32 and 0 < ty < GAME_HEIGHT - 32:
                    approach_clear.append((tx, ty))
                    break
        # Carve approach space (remove walls at approach tiles) - doors remain as wall openings
        self.walls = [(wx, wy) for (wx, wy) in self.walls if (wx, wy) not in set(approach_clear)]

    def _init_sprites(self):
        """Initialize pixel art sprites for characters and enemies"""
        # Create wizard sprite (16x16 scaled to 32x32)
        self.wizard_sprite = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Blue robe pixels
        pixels = [
            "....BBBB....",
            "...BBBBBB...",
            "..BBBPPBBB..",
            ".BBPPPPPPBB.",
            ".BPWWPPWWPB.",
            ".BPKKPPKKPB.",
            ".BPPPPPPPPB.",
            ".BBPPPPPPBB.",
            "..BBBBBBBB..",
            "..BBBBBBBB..",
            "..BB.BB.BB..",
            "..BB.BB.BB..",
        ]
        colors = {'B': (50, 80, 200), 'P': (255, 220, 190), 'W': (255, 255, 255), 
                  'K': (0, 0, 0), '.': None}
        
        for y, row in enumerate(pixels):
            for x, char in enumerate(row):
                if colors.get(char):
                    # Scale up 2x for visibility
                    pygame.draw.rect(self.wizard_sprite, colors[char], 
                                   (x*2 + 4, y*2 + 4, 2, 2))
    
    def _init_retro_tiles(self):
        """Create simple retro-looking tiles (grass, cobble, stone wall)."""
        tile = 32
        rnd = random.Random(1337)

        # Try to load wall texture if available
        if 'tile_wall' in self.sprites:
            self.tile_wall = pygame.transform.scale(self.sprites['tile_wall'], (tile, tile))
        else:
            # Enhanced stone wall tile fallback - create more realistic wall texture
            self.tile_wall = pygame.Surface((tile, tile))
            # Base stone color
            base_color = (120, 110, 100)

            # Fill with base stone color
            self.tile_wall.fill(base_color)

            # Add stone texture variation
            for _ in range(25):
                x = rnd.randint(0, tile-1)
                y = rnd.randint(0, tile-1)
                variation = rnd.randint(-20, 20)
                stone_color = (
                    max(80, min(160, base_color[0] + variation)),
                    max(70, min(140, base_color[1] + variation)),
                    max(60, min(130, base_color[2] + variation))
                )
                self.tile_wall.set_at((x, y), stone_color)

            # Add mortar lines (darker lines between stones)
            mortar_color = (80, 75, 70)
            # Horizontal mortar lines
            for y in [8, 16, 24]:
                pygame.draw.line(self.tile_wall, mortar_color, (0, y), (tile-1, y), 2)
            # Vertical mortar lines
            for x in [8, 16, 24]:
                pygame.draw.line(self.tile_wall, mortar_color, (x, 0), (x, tile-1), 2)

            # Add some random cracks and imperfections
            for _ in range(8):
                x1 = rnd.randint(0, tile-1)
                y1 = rnd.randint(0, tile-1)
                x2 = x1 + rnd.randint(-3, 3)
                y2 = y1 + rnd.randint(-3, 3)
                crack_color = (60, 55, 50)
                if 0 <= x2 < tile and 0 <= y2 < tile:
                    pygame.draw.line(self.tile_wall, crack_color, (x1, y1), (x2, y2), 1)

        # Grass tile
        self.tile_grass = pygame.Surface((tile, tile))
        self.tile_grass.fill((22, 120, 22))
        for _ in range(35):
            x = rnd.randint(0, tile-1)
            y = rnd.randint(0, tile-1)
            color = (rnd.randint(20, 40), rnd.randint(140, 190), rnd.randint(20, 40))
            self.tile_grass.set_at((x, y), color)

        # Cobblestone tile
        self.tile_cobble = pygame.Surface((tile, tile))
        self.tile_cobble.fill((110, 110, 110))
        for _ in range(12):
            cx = rnd.randint(4, tile-4)
            cy = rnd.randint(4, tile-4)
            r = rnd.randint(4, 7)
            pygame.draw.ellipse(self.tile_cobble, (150, 150, 150), (cx-r, cy-r+1, 2*r, 2*r-2))
            pygame.draw.ellipse(self.tile_cobble, (80, 80, 80), (cx-r, cy-r+1, 2*r, 2*r), 1)

    # ADDED: place a few hazards in rooms
    def place_hazards(self):
        if not hasattr(self, 'rooms'):
            return
        rnd = random.Random(self.current_level * 31337)
        self.hazards = []
        for (rx, ry, rw, rh) in self.rooms:
            for _ in range(rnd.randint(0, 2)):
                hx = rnd.randint(rx + 32, rx + rw - 32)
                hy = rnd.randint(ry + 32, ry + rh - 32)
                if self.check_wall_collision(hx, hy):
                    continue
                htype = rnd.choice([HazardType.SPIKES, HazardType.RUNE, HazardType.POISON])
                self.hazards.append((hx, hy, htype, 0.0))

    # ADDED: apply hazard effects
    def check_hazard_collisions(self, dt):
        if not self.player or not hasattr(self, 'hazards'):
            return
        pre_speed = self.player.speed
        slowed = False
        p_rect = pygame.Rect(self.player.x - 10, self.player.y - 10, 20, 20)
        for i, (hx, hy, htype, phase) in enumerate(self.hazards):
            h_rect = pygame.Rect(hx - 12, hy - 12, 24, 24)
            if p_rect.colliderect(h_rect):
                if htype == HazardType.SPIKES:
                    damage = SPIKES_DAMAGE_RATE * dt
                    self.player.life -= damage
                    self.add_ui_message(f"Hit by spikes! -{int(damage)} HP")
                elif htype == HazardType.RUNE:
                    # visual pulse only
                    self.effects.append({"type": "aura", "color": (80, 140, 255), "timer": 0.2})
                    self.add_ui_message("Activated rune!")
                elif htype == HazardType.POISON:
                    damage = POISON_DAMAGE_RATE * dt
                    self.player.life -= damage
                    slowed = True
                    self.add_ui_message(f"Poison damage! -{int(damage)} HP")
        # Apply brief slow in poison
        if slowed:
            self.player.speed = max(0.5, pre_speed * 0.9)
        else:
            self.player.speed = pre_speed

    # ADDED: effects overlay renderer
    def _render_effects_overlay(self):
        if not self.player or not self.effects:
            return
        next_effects = []
        for e in self.effects:
            timer = e.get('timer', 0.0)
            if timer <= 0:
                continue

            effect_type = e.get('type', 'aura')

            if effect_type == 'sword_sprite':
                # Render sword swing sprite
                sprite = e.get('sprite')
                x = e.get('x', 0) - self.camera_x
                y = e.get('y', 0) - self.camera_y
                direction = e.get('direction', Direction.DOWN)

                # Rotate sprite based on direction
                if direction == Direction.LEFT:
                    rotated = pygame.transform.rotate(sprite, 90)
                elif direction == Direction.RIGHT:
                    rotated = pygame.transform.rotate(sprite, -90)
                elif direction == Direction.UP:
                    rotated = pygame.transform.rotate(sprite, 180)
                else:  # DOWN
                    rotated = sprite

                self.screen.blit(rotated, (x - 16, y - 16))

            elif effect_type == 'sword_arc':
                # Render fallback sword arc animation
                x = e.get('x', 0) - self.camera_x
                y = e.get('y', 0) - self.camera_y
                direction = e.get('direction', Direction.DOWN)

                # Draw a simple sword arc
                if direction == Direction.RIGHT:
                    pygame.draw.arc(self.screen, (255, 255, 255), (x-10, y-10, 20, 20), 0, 1.57, 3)
                elif direction == Direction.LEFT:
                    pygame.draw.arc(self.screen, (255, 255, 255), (x-10, y-10, 20, 20), 1.57, 3.14, 3)
                elif direction == Direction.UP:
                    pygame.draw.arc(self.screen, (255, 255, 255), (x-10, y-10, 20, 20), 3.14, 4.71, 3)
                else:  # DOWN
                    pygame.draw.arc(self.screen, (255, 255, 255), (x-10, y-10, 20, 20), 4.71, 6.28, 3)

            else:
                # Original aura effect
                color = e.get('color', (255, 255, 255))
                px = int(self.player.x - self.camera_x)
                py = int(self.player.y - self.camera_y)
                pygame.draw.circle(self.screen, color, (px, py), 18, 2)

            e['timer'] = timer - 1/60.0
            if e['timer'] > 0:
                next_effects.append(e)
        self.effects = next_effects

    def _render_farsee_minimap(self):
        """Render Farsee mini-map showing entire level"""
        # Mini-map dimensions and position
        map_size = SCREEN_WIDTH/2 - 20
        map_x = SCREEN_WIDTH - map_size - 10
        map_y = SCREEN_HEIGHT - map_size - 10

        # Create mini-map surface
        minimap = pygame.Surface((map_size, map_size))
        minimap.fill((0, 0, 0))
        pygame.draw.rect(minimap, (255, 255, 255), (0, 0, map_size, map_size), 1)

        # Calculate scale factors
        scale_x = map_size / WORLD_WIDTH
        scale_y = map_size / WORLD_HEIGHT

        # Draw walls (scaled down)
        for wall_x, wall_y in self.walls:
            mx = int(wall_x * scale_x)
            my = int(wall_y * scale_y)
            if 0 <= mx < map_size and 0 <= my < map_size:
                minimap.set_at((mx, my), (128, 128, 128))

        # Draw doors
        for door_x, door_y in self.doors:
            mx = int(door_x * scale_x)
            my = int(door_y * scale_y)
            if 0 <= mx < map_size and 0 <= my < map_size:
                minimap.set_at((mx, my), (255, 255, 0))  # Yellow for doors

        # Draw items (KEYS with BIG gold highlighting)
        for item in self.items:
            if not item.collected:
                ix = int(item.x * scale_x)
                iy = int(item.y * scale_y)
                if 0 <= ix < map_size and 0 <= iy < map_size:
                    if item.type == ItemType.KEY:
                        # BIG gold highlighting for keys - draw a cross pattern
                        gold_color = (255, 215, 0)  # Bright gold
                        # Draw a larger cross pattern for keys
                        for dx in range(-2, 3):
                            for dy in range(-2, 3):
                                if abs(dx) == abs(dy) or dx == 0 or dy == 0:  # Cross pattern
                                    mx, my = ix + dx, iy + dy
                                    if 0 <= mx < map_size and 0 <= my < map_size:
                                        minimap.set_at((mx, my), gold_color)
                    else:
                        # Other items in white
                        minimap.set_at((ix, iy), (255, 255, 255))

        # Draw enemies
        for enemy in self.enemies:
            mx = int(enemy.x * scale_x)
            my = int(enemy.y * scale_y)
            if 0 <= mx < map_size and 0 <= my < map_size:
                minimap.set_at((mx, my), (255, 0, 0))  # Red for enemies

        # Draw player position
        if self.player:
            px = int(self.player.x * scale_x)
            py = int(self.player.y * scale_y)
            if 0 <= px < map_size and 0 <= py < map_size:
                # Draw player as a small white square
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        mx, my = px + dx, py + dy
                        if 0 <= mx < map_size and 0 <= my < map_size:
                            minimap.set_at((mx, my), (255, 255, 255))

        # Draw current viewport rectangle
        view_left = int(self.camera_x * scale_x)
        view_top = int(self.camera_y * scale_y)
        view_width = int(GAME_WIDTH * scale_x)
        view_height = int(GAME_HEIGHT * scale_y)
        pygame.draw.rect(minimap, (0, 255, 0), (view_left, view_top, view_width, view_height), 1)

        # Add "FARSEE" label
        font = pygame.font.Font(None, 16)
        label = font.render("FARSEE", True, (255, 255, 255))
        minimap.blit(label, (map_size//2 - label.get_width()//2, map_size - 15))

        # Blit to screen
        self.screen.blit(minimap, (map_x, map_y))

    def fire_projectile(self):
        if not self.player:
            return
        # Missiles stat scales damage; limit rate of fire by a brief cooldown
        if getattr(self, 'shot_cooldown', 0) > 0:
            return
        self.shot_cooldown = SHOT_COOLDOWN  # ~5-6 shots/second
        damage = max(1, self.player.missiles)
        # Strength/missiles buffs
        if hasattr(self, 'status_effects'):
            if self.status_effects.get('missiles', 0) > 0:
                damage += 2
        if hasattr(self, 'status_effects'):
            if self.status_effects.get('strength', 0) > 0:
                damage += 0  # strength affects melee; leave missiles unchanged
        proj = Projectile(self.player.x, self.player.y, self.player.direction, 6.0, damage)
        self.projectiles.append(proj)
        # DEBUG: confirm missile fired
        print("MISSILE FIRED")
        # HUD cue
        self.add_ui_message("Missile!")

    def update_projectiles(self, dt):
        # Move and resolve hits
        # Update firing cooldown
        if hasattr(self, 'shot_cooldown') and self.shot_cooldown > 0:
            self.shot_cooldown = max(0.0, self.shot_cooldown - dt)

        for p in self.projectiles:
            if not p.alive:
                continue
            p.update(dt)
            # Collide with walls
            # Use a smaller rect for projectile-wall test to avoid premature collision near right walls
            proj_rect = pygame.Rect(p.x - 2, p.y - 2, 4, 4)
            hit_wall = False
            for wx, wy in self.walls:
                if proj_rect.colliderect(pygame.Rect(wx, wy, 32, 32)):
                    hit_wall = True
                    break
            if hit_wall:
                p.alive = False
            # Collide with enemies (only if not already hit wall)
            elif not hit_wall:
                for e in self.enemies[:]:
                    if abs(e.x - p.x) < 12 and abs(e.y - p.y) < 12:
                        # ADDED: use take_damage for slime split and add hit flash
                        e.hit_timer = 0.15
                        split = e.take_damage(p.damage)
                        p.alive = False
                        # Track enemy hit for portrait
                        self.last_enemy_hit = e.type
                        self.enemy_portrait_timer = 8.0  # Show enemy portrait for 8 seconds instead of 2
                        if e.life <= 0:
                            if e.type == EnemyType.SLIME and split:
                                for dx in (-8, 8):
                                    ns = Enemy(e.x + dx, e.y, EnemyType.SLIME)
                                    ns.max_life = 6
                                    ns.life = 6
                                    ns.speed = 0.7
                                    self.enemies.append(ns)
                            self.enemies.remove(e)
                            self.sound_manager.play_item_collect()
                            self.score += 100
                        break
        # Keep alive projectiles only
        self.projectiles = [p for p in self.projectiles if p.alive]

    def try_melee_attack(self):
        """Perform melee sword attack in facing direction if enemies are within range.

        MELEE COMBAT SYSTEM:
        - Only activates when enemies are within close range (12 pixels)
        - Creates a small rectangular hitbox in facing direction
        - 0.25 second cooldown between swings to prevent spam
        - Damage = base strength + 2 if strength potion active
        - Slime enemies split into smaller versions when killed
        - Returns True if attack executed, False if no valid targets

        This creates a tactical choice between melee (high damage, close range)
        and ranged attacks (safe distance, but lower damage per shot).
        """
        if not self.player:
            return False

        # Prevent spam attacks with cooldown system
        if getattr(self, 'melee_cooldown', 0) > 0:
            return False

        # Define melee attack area based on player facing direction
        px, py = self.player.x, self.player.y
        reach = 12      # Attack reach distance
        w, h = 18, 18   # Attack area dimensions

        # Create attack hitbox in facing direction
        if self.player.direction == Direction.RIGHT:
            swing_rect = pygame.Rect(px, py - h//2, reach, h)
        elif self.player.direction == Direction.LEFT:
            swing_rect = pygame.Rect(px - reach, py - h//2, reach, h)
        elif self.player.direction == Direction.UP:
            swing_rect = pygame.Rect(px - h//2, py - reach, h, reach)
        else:  # DOWN
            swing_rect = pygame.Rect(px - h//2, py, h, reach)

        # Check for valid targets before committing to attack
        any_target = False
        for e in self.enemies:
            enemy_rect = pygame.Rect(e.x - 12, e.y - 12, 24, 24)
            if swing_rect.colliderect(enemy_rect):
                any_target = True
                break

        # No enemies in range - don't consume the attack input
        if not any_target:
            return False

        # Execute attack: damage all enemies in range
        self.melee_cooldown = 0.25  # 0.25 second cooldown
        damage = max(1, self.player.strength + (2 if self.status_effects.get('strength', 0) > 0 else 0))

        for e in self.enemies[:]:  # Copy list to avoid modification during iteration
            enemy_rect = pygame.Rect(e.x - 12, e.y - 12, 24, 24)
            if swing_rect.colliderect(enemy_rect):
                e.hit_timer = 0.12  # Visual hit flash
                split = e.take_damage(damage)

                # Handle enemy death and special effects
                if e.life <= 0:
                    # Slime splitting mechanic - creates tactical challenge
                    if e.type == EnemyType.SLIME and split:
                        # Create two smaller slime enemies
                        for dx in (-8, 8):
                            ns = Enemy(e.x + dx, e.y, EnemyType.SLIME)
                            ns.max_life = 6  # Smaller health
                            ns.life = 6
                            ns.speed = 0.7  # Slower than original
                            self.enemies.append(ns)

                    # Remove dead enemy and award points
                    self.enemies.remove(e)
                    self.sound_manager.play_item_collect()
                    self.score += ENEMY_KILL_SCORE  # 100 points per kill

        # Audio and visual feedback
        self.sound_manager.play_melee()
        self.add_ui_message("Sword!")

        # Sword swing animation effect
        if 'sword_swing' in self.sprites:
            # Use sword swing sprite if available
            swing_sprite = self.sprites['sword_swing']
            scaled = pygame.transform.scale(swing_sprite, (32, 32))
            self.effects.append({"type": "sword_sprite", "sprite": scaled, "timer": 0.2, "x": px, "y": py, "direction": self.player.direction})
        else:
            # Fallback animation - draw a simple sword arc
            self.effects.append({"type": "sword_arc", "timer": 0.2, "x": px, "y": py, "direction": self.player.direction})

        return True

    def use_inventory_item(self, index):
        """Use/consume an item from the player's inventory.

        ITEM EFFECTS SYSTEM:
        - Potions: Temporary stat boosts (duration affected by difficulty)
        - Scrolls: Instant or temporary special effects
        - Items are removed from inventory after use
        - Effects provide strategic gameplay choices

        Potions (temporary buffs):
        - Speed: +40% movement speed
        - Strength: +2 melee damage
        - Missiles: +2 projectile damage

        Scrolls (special abilities):
        - Blast: Kill all enemies on screen (emergency clear)
        - Farsee: Show full level minimap (30s, difficulty scaled)
        - Invisibility: Enemies can't target player (15s, difficulty scaled)
        - Revive: Auto-resurrection on death (stacks charges)
        """
        if index < 0 or index >= len(self.player.inventory):
            return

        item = self.player.inventory[index]
        t = item.type

        # Calculate potion duration based on difficulty level
        potion_multiplier = DIFFICULTY_MULTIPLIERS[self.difficulty]['potion']
        potion_duration = POTION_DURATION * potion_multiplier  # Base 20s * difficulty multiplier

        # POTION EFFECTS - Temporary stat boosts
        if t == ItemType.POTION_SPEED:
            self.status_effects['speed'] = potion_duration
            self.add_ui_message(f"Speed + ({potion_duration:.1f}s)")
        elif t == ItemType.POTION_STRENGTH:
            self.status_effects['strength'] = potion_duration
            self.add_ui_message(f"Strength + ({potion_duration:.1f}s)")
        elif t == ItemType.POTION_MISSILES:
            self.status_effects['missiles'] = potion_duration
            self.add_ui_message(f"Missiles + ({potion_duration:.1f}s)")

        # SCROLL EFFECTS - Instant or special abilities
        elif t == ItemType.SCROLL_BLAST:
            # Emergency clear: kill all enemies on screen
            killed = 0
            for e in self.enemies[:]:
                self.enemies.remove(e)
                killed += 1
            if killed > 0:
                self.sound_manager.play_item_collect()
                self.score += ENEMY_KILL_SCORE * killed
            self.add_ui_message("BLAST!")

        elif t == ItemType.SCROLL_FARSEE:
            # Strategic map reveal
            farsee_duration = 30.0 * potion_multiplier  # 30 second base duration
            self.farsee_timer = farsee_duration
            self.add_ui_message(f"FARSEE ({farsee_duration:.1f}s)")

        elif t == ItemType.SCROLL_INVISIBILITY:
            # Stealth ability - enemies can't see player
            invis_duration = 15.0 * potion_multiplier  # 15 second base duration
            self.status_effects['invis'] = invis_duration
            self.add_ui_message(f"Invisibility ({invis_duration:.1f}s)")

        elif t == ItemType.SCROLL_REVIVE:
            # Insurance against death - can stack multiple charges
            self.status_effects['revive'] = self.status_effects.get('revive', 0) + 1
            self.add_ui_message("Revive ready")

        # Remove used item from inventory
        del self.player.inventory[index]

        # Adjust cursor position if necessary
        if self.inventory_cursor >= len(self.player.inventory):
            self.inventory_cursor = max(0, len(self.player.inventory) - 1)

    def drop_inventory_item(self, index):
        if index < 0 or index >= len(self.player.inventory):
            return
        item = self.player.inventory[index]
        self.items.append(Item(int(self.player.x), int(self.player.y), item.type))
        del self.player.inventory[index]
        self.add_ui_message("Dropped " + str(item.type).split('.')[-1])
        if self.inventory_cursor >= len(self.player.inventory):
            self.inventory_cursor = max(0, len(self.player.inventory) - 1)

    def _load_sprites(self):
        """Load sprite images from the Gauntlet_sprites folder and other sources"""
        base_path = os.path.dirname(os.path.abspath(__file__))
        sprites_path = os.path.join(base_path, 'Gauntlet_sprites')
        
        # Define sprite mappings - all sprites should be in Gauntlet_sprites/ directory
        sprite_files = {
            # Player sprites (from Gauntlet_sprites/)
            'wizard': 'Wizard.png',
            'valkyrie': 'valkyrie.png',
            'samurai': 'sumurai.png',
            'pirate': 'pirate.png',
            'punkrocker': 'punkrocker.png',
            'gunfighter': 'gunfighter.png',
            'nerd': 'nerd.png',
            'android': 'android.png',

            # Enemy sprites (from Gauntlet_sprites/)
            'enemy_slime': 'slime.png',
            'enemy_demon': 'red_demon_1.png',
            'enemy_demon2': 'red_demon_2.png',
            'enemy_orge': 'red_orge.png',
            'enemy_cyclops': 'red_cyclops.png',
            'enemy_chimera1': 'red_chimera_1.png',
            'enemy_chimera2': 'red_chimera_2.png',
            'enemy_chimera3': 'red_chimera_3.png',
           
            'enemy_scorpion': 'Scorpion.png',
            'enemy_skeleton': 'Skeleton.png',
            'enemy_ghost': 'small_ghost.png',

            # Item sprites (from Gauntlet_sprites/)
            'item_apple': 'Apple.png',        # Food/health item
            'item_potion': 'potion.png',      # Health potion
            
            'item_gold': 'gold.png',          # Gold/treasure
            'item_key': 'key.png',            # Door key
            'item_scroll': 'Scroll.png',      # Magic scroll

            # Environment (from Gauntlet_sprites/)
            'tile_wall': 'doom_wall_texture.png',  # Doom-style wall texture
        }
        
        # Load sprites with fallback to placeholder
        for key, filename in sprite_files.items():
            # Handle relative paths (like ../doom_sprites/)
            if filename.startswith('../'):
                full_path = os.path.join(base_path, filename[3:])  # Remove '../' prefix
            else:
                full_path = os.path.join(sprites_path, filename)
            try:
                if os.path.exists(full_path):
                    sprite = pygame.image.load(full_path).convert_alpha()
                    self.sprites[key] = sprite
                    print(f"Loaded sprite: {key} from {filename} (size: {sprite.get_size()})")
                else:
                    print(f"Sprite file not found: {filename} for key {key}")
            except Exception as e:
                print(f"Could not load sprite {filename}: {e}")
        
        # Note: Extra sprites from main directory removed - all sprites should be in Gauntlet_sprites/
        # If you need additional sprites, add them to the sprite_files dictionary above
        
        # All sprites are now loaded directly into self.sprites in the loop above
        # No additional mapping needed - sprites are accessed by their keys directly

    def _try_draw_sprite(self, surface, sprite_key, x, y, size=(24, 24), fallback_func=None):
        """Simple helper to draw sprite if available, or use fallback function if provided"""
        if sprite_key and sprite_key in self.sprites and self.sprites[sprite_key] is not None:
            sprite = self.sprites[sprite_key]
            scaled = pygame.transform.scale(sprite, size)
            surface.blit(scaled, (x - size[0]//2, y - size[1]//2))
            return True
        elif fallback_func:
            fallback_func(surface, x, y)
            return False
        return False

class Player:
    def __init__(self, character_class, level_num=1):
        self.character_class = CHARACTER_CLASSES[character_class]
        # World spawn defaults (will be adjusted by game after level generation)
        self.x = WORLD_WIDTH // 2
        self.y = WORLD_HEIGHT // 2
        # Movement and stats
        self.max_life = PLAYER_MAX_LIFE
        self.life = self.max_life
        self.inventory = []
        self.max_inventory = PLAYER_MAX_INVENTORY  # Slightly larger inventory to reduce 'full' cases
        self.speed = self.character_class.speed / 10  # Half speed for smaller movement increments
        self.strength = self.character_class.strength
        self.missiles = self.character_class.missiles
        self.direction = Direction.DOWN
        self.keys_collected = 0
        self.gold = PLAYER_STARTING_GOLD  # Start with plenty of gold for shopping
        # ADDED: animation timer for walk/attack
        self.anim_frame = 0
        self.anim_timer = 0.0
        # Link back to game for status effects (set by GauntletGame after create)
        self.game = None

    def update(self, dt, keys_pressed):
        """Update player logic"""
        dx, dy = 0, 0
        moving = False
        if pygame.K_LEFT in keys_pressed or pygame.K_a in keys_pressed:
            dx = -self.speed * dt * 60
            self.direction = Direction.LEFT
            moving = True
        if pygame.K_RIGHT in keys_pressed or pygame.K_d in keys_pressed:
            dx = self.speed * dt * 60
            self.direction = Direction.RIGHT
            moving = True
        if pygame.K_UP in keys_pressed or pygame.K_w in keys_pressed:
            dy = -self.speed * dt * 60
            self.direction = Direction.UP
            moving = True
        if pygame.K_DOWN in keys_pressed or pygame.K_s in keys_pressed:
            dy = self.speed * dt * 60
            self.direction = Direction.DOWN
            moving = True
        # Apply temporary slow if slimed and speed potion boost if active
        speed_multiplier = 1.0
        if getattr(self, 'game', None):
            if getattr(self.game, 'player_slow_timer', 0) > 0:
                speed_multiplier *= 0.6
            if hasattr(self.game, 'status_effects') and self.game.status_effects.get('speed', 0) > 0:
                speed_multiplier *= 1.4
        if getattr(self, 'game', None) and getattr(self.game, 'player_slow_timer', 0) > 0:
            self.game.player_slow_timer = max(0.0, self.game.player_slow_timer - dt)

        # Update position within world bounds
        self.x = max(4, min(WORLD_WIDTH - 4, self.x + dx * speed_multiplier))
        self.y = max(4, min(WORLD_HEIGHT - 4, self.y + dy * speed_multiplier))
        # ADDED: animate when moving
        if moving:
            self.anim_timer += dt
            if self.anim_timer > ANIMATION_FRAME_TIME:  # Faster animation
                self.anim_frame = (self.anim_frame + 1) % 2
                self.anim_timer = 0.0
        else:
            # Reset to standing frame when stopped
            self.anim_frame = 0
            self.anim_timer = 0.0

    # ADDED: minimal top-down silhouettes for classes
    # Note: helper lives on GauntletGame, not Player; this is a placeholder for clarity

class Enemy:
    def __init__(self, x, y, enemy_type, game=None):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.max_life = ENEMY_MAX_LIFE
        self.life = self.max_life
        # Add speed variation to prevent piling up
        self.speed = ENEMY_BASE_SPEED * random.uniform(0.7, 1.3)  # 70-130% of base speed
        self.direction = Direction.DOWN
        # Add random direction change timing to prevent synchronized movement
        self.last_direction_change = random.uniform(0, 1.0)  # Start with random timing
        self.direction_change_interval = random.uniform(0.8, 1.4)  # Random change intervals
        # ADDED: simple animation/hit tracking
        self.anim_t = 0.0
        self.hit_timer = 0.0
        self.game = game  # Reference to game for wall collision checking

    def update(self, dt):
        """Update enemy logic"""
        # Simple AI - move randomly
        self.last_direction_change += dt
        self.anim_t += dt
        if self.hit_timer > 0:
            self.hit_timer -= dt

        if self.last_direction_change > self.direction_change_interval:  # Random change intervals
            # Check if player is invisible
            player_invisible = self.game and hasattr(self.game, 'status_effects') and self.game.status_effects.get('invis', 0) > 0

            if player_invisible:
                # Random movement when player is invisible
                self.direction = random.choice(list(Direction))
            else:
                # Move toward player when visible
                if self.game and self.game.player:
                    player = self.game.player
                    dx_to_player = player.x - self.x
                    dy_to_player = player.y - self.y

                    # Add some randomness to prevent perfect synchronization
                    if random.random() < 0.3:  # 30% chance for random movement even when chasing
                        self.direction = random.choice(list(Direction))
                    else:
                        # Determine primary direction toward player
                        if abs(dx_to_player) > abs(dy_to_player):
                            # Move horizontally toward player
                            self.direction = Direction.RIGHT if dx_to_player > 0 else Direction.LEFT
                        else:
                            # Move vertically toward player
                            self.direction = Direction.DOWN if dy_to_player > 0 else Direction.UP
                else:
                    # Fallback to random if no player
                    self.direction = random.choice(list(Direction))

            self.last_direction_change = 0

        # Move based on direction
        dx, dy = 0, 0
        if self.direction == Direction.LEFT:
            dx = -self.speed * dt * 60
        elif self.direction == Direction.RIGHT:
            dx = self.speed * dt * 60
        elif self.direction == Direction.UP:
            dy = -self.speed * dt * 60
        elif self.direction == Direction.DOWN:
            dy = self.speed * dt * 60

        # Update position with wall collision checking
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check wall collision for new position
        if self.game and hasattr(self.game, 'check_wall_collision'):
            # Check if new position would collide with walls
            if not self.game.check_wall_collision(new_x, new_y):
                self.x = new_x
                self.y = new_y
            else:
                # Hit a wall, change direction
                self.direction = random.choice(list(Direction))
                self.last_direction_change = 0
        else:
            # Fallback to bounds checking only
            self.x = max(32, min(WORLD_WIDTH - 32, new_x))
            self.y = max(32, min(WORLD_HEIGHT - 32, new_y))

    def take_damage(self, damage):
        """Take damage and potentially split"""
        self.life -= damage
        if self.life <= 0:
            if self.type == EnemyType.SLIME:
                # Slime splits into two smaller slimes
                return True  # Signal to create new slimes
        return False

class Projectile:
    def __init__(self, x, y, direction, speed, damage):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.alive = True

    def update(self, dt):
        if self.direction == Direction.LEFT:
            self.x -= self.speed * dt * 60
        elif self.direction == Direction.RIGHT:
            self.x += self.speed * dt * 60
        elif self.direction == Direction.UP:
            self.y -= self.speed * dt * 60
        elif self.direction == Direction.DOWN:
            self.y += self.speed * dt * 60

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.collected = False

    def update(self, dt):
        """Update item logic"""
        # Items don't move, but could have animations
        pass

class SoundManager:
    def __init__(self):
        self.sample_rate = 44100
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2)  # Stereo

    def generate_tone(self, frequency, duration, volume=0.3):
        """Generate a simple tone"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # Create mono tone
        tone_mono = np.sin(frequency * 2 * np.pi * t) * volume
        # Convert to stereo by duplicating the mono channel
        tone_stereo = np.column_stack((tone_mono, tone_mono))
        # Convert to 16-bit signed integers
        tone_stereo = (tone_stereo * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(tone_stereo)

    def play_item_collect(self):
        """Play item collection sound"""
        sound = self.generate_tone(800, 0.1)
        sound.play()

    def play_gold_collect(self):
        """Play gold collection sound"""
        sound = self.generate_tone(1000, 0.15)
        sound.play()

    def play_food_eat(self):
        """Play food eating sound"""
        sound = self.generate_tone(600, 0.2)
        sound.play()

    def play_damage(self):
        """Play damage sound"""
        # Descending tone
        sound = self.generate_tone(400, 0.3)
        sound.play()

    def play_death(self):
        """Play death sound"""
        # Multiple descending tones
        for freq in [300, 250, 200]:
            sound = self.generate_tone(freq, 0.2)
            sound.play()
            time.sleep(0.1)

    def play_melee(self):
        """Play melee swing sound (use existing file if present, else tone)."""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            candidate = os.path.join(base_path, 'sounds', 'thrust.wav')
            if os.path.exists(candidate):
                pygame.mixer.Sound(candidate).play()
                return
        except Exception:
            pass
        # Fallback: brief whoosh tone
        self.generate_tone(200, 0.08, volume=0.25).play()

def main():
    """Main entry point"""
    game = GauntletGame()
    game.run()

if __name__ == "__main__":
    main()
