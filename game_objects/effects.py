"""
Visual effects for Ghost of Space game
"""
import pygame
import random
from typing import List, Tuple
from utils.logger import logger
import config


class Particle(pygame.sprite.Sprite):
    """Improved particle system for explosion and hit effects"""
    
    def __init__(self, x: int, y: int, colors: List[Tuple[int, int, int]], effect_type: int = 1):
        """
        Initialize particle
        
        Args:
            x: Initial x position
            y: Initial y position
            colors: List of colors for the particle
            effect_type: Type of effect (1=small, 2=medium, 3=large)
        """
        super().__init__()
        
        # Set particle size based on effect type
        if effect_type == 1:
            size = (5, 5)
            speed_multiplier = 0.5
        elif effect_type == 2:
            size = (7, 7)
            speed_multiplier = 0.6
        else:
            size = (8, 8)
            speed_multiplier = 0.7
        
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect()
        
        # Set random color from the provided palette
        color = random.choice(colors)
        self.image.fill(color)
        
        # Position
        self.rect.center = (x, y)
        
        # Movement
        self.velocity_x = random.randrange(-10, 11) * speed_multiplier
        self.velocity_y = random.randrange(-10, 11) * speed_multiplier
        
        # Ensure particle has some movement
        if self.velocity_x == 0 and self.velocity_y == 0:
            self.velocity_x = random.choice([-1, 1]) * speed_multiplier
            self.velocity_y = random.choice([-1, 1]) * speed_multiplier
        
        # Lifetime
        self.lifetime = random.randrange(200, 500)  # milliseconds
        self.birth_time = pygame.time.get_ticks()
        
        # Visual effects
        self.alpha = 255
        self.fade_rate = 255 / (self.lifetime / 16.67)  # Fade over lifetime assuming 60 FPS
        
        logger.debug(f"Particle created at ({x}, {y}) with type {effect_type}")
    
    def update(self):
        """Update particle state"""
        # Move
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Apply gravity/friction
        self.velocity_y += 0.1  # Slight gravity
        self.velocity_x *= 0.99  # Air friction
        self.velocity_y *= 0.99
        
        # Fade out over time
        self.alpha = max(0, self.alpha - self.fade_rate)
        if self.alpha > 0:
            self.image.set_alpha(int(self.alpha))
        
        # Check if particle should die
        current_time = pygame.time.get_ticks()
        if (current_time - self.birth_time > self.lifetime or 
            self.alpha <= 0 or
            self.rect.x < -10 or self.rect.x > config.SCREEN_WIDTH + 10 or
            self.rect.y < -10 or self.rect.y > config.SCREEN_HEIGHT + 10):
            self.kill()


class Explosion(pygame.sprite.Sprite):
    """Explosion effect with animated frames"""
    
    def __init__(self, center: Tuple[int, int], size: str = 'medium'):
        """
        Initialize explosion
        
        Args:
            center: Center position of explosion
            size: Size of explosion ('small', 'medium', 'large')
        """
        super().__init__()
        
        # Create explosion frames (simplified since we don't have animation frames)
        sizes = {
            'small': 32,
            'medium': 48,
            'large': 64
        }
        
        explosion_size = sizes.get(size, 48)
        self.frames = self._create_explosion_frames(explosion_size)
        self.current_frame = 0
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        
        self.frame_rate = 80  # milliseconds per frame
        self.last_update = pygame.time.get_ticks()
        
        logger.debug(f"Explosion created at {center} with size {size}")
    
    def _create_explosion_frames(self, size: int) -> List[pygame.Surface]:
        """Create explosion animation frames"""
        frames = []
        colors = [
            (255, 255, 0),  # Yellow
            (255, 128, 0),  # Orange
            (255, 64, 0),   # Red-orange
            (128, 64, 0),   # Dark orange
            (64, 32, 0),    # Very dark
        ]
        
        for i, color in enumerate(colors):
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            # Create expanding circle effect
            radius = size // 2 - (i * 2)
            if radius > 0:
                pygame.draw.circle(frame, color, (size//2, size//2), radius)
                # Add some inner glow
                if radius > 5:
                    inner_color = tuple(min(255, c + 50) for c in color)
                    pygame.draw.circle(frame, inner_color, (size//2, size//2), radius // 2)
            frames.append(frame)
        
        return frames
    
    def update(self):
        """Update explosion animation"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.last_update = current_time
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                self.kill()
            else:
                old_center = self.rect.center
                self.image = self.frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.center = old_center


class EffectsManager:
    """Manages all visual effects in the game"""
    
    def __init__(self):
        """Initialize effects manager"""
        self.particle_group = pygame.sprite.Group()
        self.explosion_group = pygame.sprite.Group()
        
        logger.info("Effects manager initialized")
    
    def create_particle_explosion(self, x: int, y: int, colors: List[Tuple[int, int, int]], 
                                count: int = 25, effect_type: int = 2):
        """
        Create a particle explosion effect
        
        Args:
            x: X position of explosion
            y: Y position of explosion
            colors: List of colors for particles
            count: Number of particles to create
            effect_type: Type of particle effect
        """
        for _ in range(count):
            particle = Particle(x, y, colors, effect_type)
            self.particle_group.add(particle)
        
        logger.debug(f"Created particle explosion with {count} particles at ({x}, {y})")
    
    def create_explosion(self, x: int, y: int, size: str = 'medium'):
        """
        Create an explosion effect
        
        Args:
            x: X position of explosion
            y: Y position of explosion
            size: Size of explosion
        """
        explosion = Explosion((x, y), size)
        self.explosion_group.add(explosion)
        
        logger.debug(f"Created explosion at ({x}, {y}) with size {size}")
    
    def create_enemy_death_effect(self, enemy):
        """
        Create death effect for an enemy
        
        Args:
            enemy: Enemy object that died
        """
        # Get colors from enemy
        colors = enemy.get_color_palette()
        
        # Create particle explosion
        self.create_particle_explosion(
            enemy.rect.centerx, 
            enemy.rect.centery, 
            colors, 
            count=30, 
            effect_type=enemy.particle_setting
        )
        
        # Create explosion
        size = 'large' if enemy.particle_setting == 3 else 'medium'
        self.create_explosion(enemy.rect.centerx, enemy.rect.centery, size)
    
    def create_bullet_hit_effect(self, bullet):
        """
        Create hit effect for a bullet
        
        Args:
            bullet: Bullet object that hit something
        """
        # Simple particle effect for bullet hits
        colors = [(255, 255, 255), (255, 255, 0), (255, 128, 0)]
        self.create_particle_explosion(
            bullet.rect.centerx,
            bullet.rect.centery,
            colors,
            count=10,
            effect_type=1
        )
    
    def update(self):
        """Update all effects"""
        self.particle_group.update()
        self.explosion_group.update()
    
    def draw(self, screen: pygame.Surface):
        """
        Draw all effects
        
        Args:
            screen: Surface to draw on
        """
        self.explosion_group.draw(screen)
        self.particle_group.draw(screen)
    
    def clear_all(self):
        """Clear all effects"""
        self.particle_group.empty()
        self.explosion_group.empty()
        logger.debug("All effects cleared")