"""
Resource Manager for efficient asset loading and caching
"""
import pygame
from pathlib import Path
from typing import Dict, Optional
import json
from utils.logger import logger
import config


class ResourceManager:
    """Manages game assets including images, sounds, and fonts"""
    
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.music_loaded = False
        
    def load_image(self, name: str, path: Optional[Path] = None, scale: Optional[tuple] = None) -> pygame.Surface:
        """Load and cache an image"""
        if name in self.images:
            return self.images[name]
            
        try:
            if path is None:
                # Try to find in Png directory first (backward compatibility)
                png_path = Path("Png") / f"{name}.png"
                if png_path.exists():
                    path = png_path
                else:
                    path = config.IMAGES_DIR / f"{name}.png"
            
            if not path.exists():
                logger.error(f"Image file not found: {path}")
                # Create a placeholder surface
                surface = pygame.Surface((32, 32))
                surface.fill(config.RED)
                self.images[name] = surface
                return surface
                
            image = pygame.image.load(str(path)).convert_alpha()
            
            if scale:
                image = pygame.transform.scale(image, scale)
                
            self.images[name] = image
            logger.info(f"Loaded image: {name}")
            return image
            
        except pygame.error as e:
            logger.error(f"Failed to load image {name}: {e}")
            # Create a placeholder surface
            surface = pygame.Surface((32, 32))
            surface.fill(config.RED)
            self.images[name] = surface
            return surface
    
    def load_sound(self, name: str, path: Optional[Path] = None, volume: float = 1.0) -> pygame.mixer.Sound:
        """Load and cache a sound"""
        if name in self.sounds:
            return self.sounds[name]
            
        try:
            if path is None:
                # Try to find in Sound directory first (backward compatibility)
                sound_path = None
                for ext in ['.ogg', '.mp3', '.wav']:
                    test_path = Path("Sound") / f"{name}{ext}"
                    if test_path.exists():
                        sound_path = test_path
                        break
                
                if sound_path is None:
                    for ext in ['.ogg', '.mp3', '.wav']:
                        test_path = config.SOUNDS_DIR / f"{name}{ext}"
                        if test_path.exists():
                            sound_path = test_path
                            break
                
                if sound_path is None:
                    logger.error(f"Sound file not found: {name}")
                    return pygame.mixer.Sound(buffer=b'')
                    
                path = sound_path
            
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(volume * config.SFX_VOLUME)
            self.sounds[name] = sound
            logger.info(f"Loaded sound: {name}")
            return sound
            
        except pygame.error as e:
            logger.error(f"Failed to load sound {name}: {e}")
            return pygame.mixer.Sound(buffer=b'')
    
    def load_font(self, name: str, size: int, path: Optional[Path] = None) -> pygame.font.Font:
        """Load and cache a font"""
        font_key = f"{name}_{size}"
        if font_key in self.fonts:
            return self.fonts[font_key]
            
        try:
            if path is None:
                # Try to find in Shrift directory first (backward compatibility)
                font_path = Path("Shrift") / f"{name}.ttf"
                if not font_path.exists():
                    font_path = config.FONTS_DIR / f"{name}.ttf"
                    
                if not font_path.exists():
                    logger.warning(f"Font file not found: {name}, using default font")
                    font = pygame.font.Font(None, size)
                else:
                    font = pygame.font.Font(str(font_path), size)
            else:
                font = pygame.font.Font(str(path), size)
                
            self.fonts[font_key] = font
            logger.info(f"Loaded font: {name} size {size}")
            return font
            
        except pygame.error as e:
            logger.error(f"Failed to load font {name}: {e}")
            return pygame.font.Font(None, size)
    
    def load_music(self, name: str, path: Optional[Path] = None):
        """Load background music"""
        try:
            if path is None:
                # Try to find in Sound directory first (backward compatibility)
                music_path = None
                for ext in ['.ogg', '.mp3', '.wav']:
                    test_path = Path("Sound") / f"{name}{ext}"
                    if test_path.exists():
                        music_path = test_path
                        break
                
                if music_path is None:
                    for ext in ['.ogg', '.mp3', '.wav']:
                        test_path = config.SOUNDS_DIR / f"{name}{ext}"
                        if test_path.exists():
                            music_path = test_path
                            break
                
                if music_path is None:
                    logger.error(f"Music file not found: {name}")
                    return False
                    
                path = music_path
            
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(config.MUSIC_VOLUME)
            self.music_loaded = True
            logger.info(f"Loaded music: {name}")
            return True
            
        except pygame.error as e:
            logger.error(f"Failed to load music {name}: {e}")
            return False
    
    def preload_assets(self):
        """Preload common game assets"""
        logger.info("Preloading game assets...")
        
        # Load player sprites
        for i in range(1, 7):
            self.load_image(f"somm{i if i > 1 else ''}")
        
        # Load enemy sprites
        for i in range(2, 6):
            self.load_image(f"ino{i}")
            self.load_image(f"ino{i}svet")
        
        # Load bullets
        self.load_image("b1")
        self.load_image("b2")
        self.load_image("mybule")
        self.load_image("xarchok1")
        self.load_image("xarchok2")
        
        # Load UI elements
        self.load_image("HP")
        self.load_image("Max_HP", scale=(30, 30))
        self.load_image("Damage", scale=(30, 30))
        self.load_image("AtakSpeade", scale=(30, 30))
        self.load_image("Vampir", scale=(30, 30))
        self.load_image("speade", scale=(30, 30))
        self.load_image("leg2")
        
        # Load background
        self.load_image("BackGround", scale=(config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        
        # Load sounds
        self.load_sound("pew", volume=0.1)
        self.load_sound("expl6", volume=0.1)
        self.load_sound("expl3", volume=0.1)
        self.load_sound("rumble1", volume=0.1)
        self.load_sound("sfx_shieldUp")
        self.load_sound("click_001")
        self.load_sound("sfx_keypress")
        self.load_sound("cartoon-bubble-pop-01-")
        
        # Load font
        self.load_font("Kenney Mini Square", 30)
        
        # Load music
        self.load_music("ost_fighter")
        
        logger.info("Asset preloading complete")
    
    def get_image(self, name: str) -> pygame.Surface:
        """Get a cached image"""
        return self.images.get(name, self.load_image(name))
    
    def get_sound(self, name: str) -> pygame.mixer.Sound:
        """Get a cached sound"""
        return self.sounds.get(name, self.load_sound(name))
    
    def get_font(self, name: str, size: int) -> pygame.font.Font:
        """Get a cached font"""
        font_key = f"{name}_{size}"
        return self.fonts.get(font_key, self.load_font(name, size))


# Global resource manager instance
resource_manager = ResourceManager()