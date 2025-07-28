"""
Game Configuration and Constants
"""
import os
from pathlib import Path

# Screen settings
SCREEN_WIDTH = 750
SCREEN_HEIGHT = 950
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# UI Colors
UI_GREEN = (23, 204, 58)
UI_DARK = (28, 28, 28)
HP_GREEN = (0, 205, 0)
HP_RED = (255, 0, 0)
SCORE_BLUE = (34, 101, 217)
SCORE_RED = (255, 48, 48)

# Game balance
PLAYER_SPEED = 6
BULLET_SPEED = 10
MOB_SPEED_RANGE = (1, 3)
DAMAGE_BASE = 5
HP_BASE = 100

# Paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images" 
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"
DATA_DIR = BASE_DIR / "data"

# Create directories if they don't exist
for directory in [ASSETS_DIR, IMAGES_DIR, SOUNDS_DIR, FONTS_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# Audio settings
MASTER_VOLUME = 0.7
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.3

# Game settings
MAX_MOBS = 10
BONUS_DROP_CHANCE = 30
LEVEL_SCORE_MULTIPLIER = 1.2