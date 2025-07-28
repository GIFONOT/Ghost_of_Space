"""
Enemy classes for Ghost of Space game
"""
import pygame
import random
from typing import Optional, Tuple
from utils.logger import logger
import config
from resource_manager import resource_manager


class Enemy(pygame.sprite.Sprite):
    """Improved enemy class with better structure and documentation"""
    
    ENEMY_TYPES = {
        '1': {'image': 'ino4', 'hp': 20, 'score': 5, 'size': 'large'},
        '2': {'image': 'ino3', 'hp': 15, 'score': 4, 'size': 'small'},
        '3': {'image': 'ino5', 'hp': 25, 'score': 6, 'size': 'large'},
        '4': {'image': 'ino2', 'hp': 12, 'score': 3, 'size': 'small'}
    }
    
    def __init__(self, enemy_type: str = None, x: int = None, y: int = None):
        """
        Initialize enemy
        
        Args:
            enemy_type: Type of enemy ('1', '2', '3', '4') or None for random
            x: Initial x position (None for random)
            y: Initial y position (None for random off-screen)
        """
        super().__init__()
        
        # Select enemy type
        if enemy_type is None:
            self.enemy_type = random.choice(list(self.ENEMY_TYPES.keys()))
        else:
            self.enemy_type = enemy_type
            
        enemy_data = self.ENEMY_TYPES[self.enemy_type]
        
        # Load image
        self.image = resource_manager.get_image(enemy_data['image'])
        self.rect = self.image.get_rect()
        
        # Set collision radius based on size
        if enemy_data['size'] == 'small':
            self.radius = int(self.rect.width / 7)
            self.particle_setting = 2
        else:
            self.radius = int(self.rect.width / 3)
            self.particle_setting = 3
        
        # Position
        if x is None:
            x = random.randrange(0, config.SCREEN_WIDTH - self.rect.width)
        if y is None:
            y = random.randrange(-200, -40)
            
        self.rect.x = x
        self.rect.y = y
        
        # Movement
        self.speed_y = random.randrange(*config.MOB_SPEED_RANGE)
        self.speed_x = random.randrange(-4, 5)
        
        # Combat stats
        self.max_hp = enemy_data['hp']
        self.hp = self.max_hp
        self.score_value = enemy_data['score']
        
        # Shooting (for aggressive enemies)
        self.can_shoot = random.choice([True, False])
        self.last_shot = 0
        self.shot_delay = random.randrange(1500, 3000)
        
        logger.debug(f"Enemy type {self.enemy_type} created at ({x}, {y})")
    
    def update(self):
        """Update enemy state"""
        # Move
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # Bounce off screen edges
        if self.rect.right >= config.SCREEN_WIDTH:
            self.speed_x = -abs(self.speed_x)
        elif self.rect.left <= 0:
            self.speed_x = abs(self.speed_x)
        
        # Handle shooting
        if self.can_shoot:
            self.try_shoot()
        
        # Remove if too far off screen
        if (self.rect.top > config.SCREEN_HEIGHT + 50 or 
            self.rect.right < -50 or 
            self.rect.left > config.SCREEN_WIDTH + 50):
            self.respawn()
    
    def try_shoot(self) -> Optional['EnemyBullet']:
        """
        Try to shoot a bullet
        
        Returns:
            EnemyBullet if shot, None otherwise
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot < self.shot_delay:
            return None
            
        self.last_shot = current_time
        
        # Create bullet based on enemy size
        bullet_type = 1 if self.particle_setting == 2 else 2
        bullet = EnemyBullet(self.rect.centerx, self.rect.centery - 25, bullet_type)
        
        logger.debug(f"Enemy {self.enemy_type} shot bullet")
        return bullet
    
    def take_damage(self, damage: int) -> bool:
        """
        Apply damage to enemy
        
        Args:
            damage: Amount of damage to take
            
        Returns:
            True if enemy died, False otherwise
        """
        self.hp -= damage
        
        if self.hp <= 0:
            logger.debug(f"Enemy {self.enemy_type} destroyed")
            return True
        else:
            # Flash effect when hit
            self.show_hit_effect()
            logger.debug(f"Enemy {self.enemy_type} took {damage} damage. HP: {self.hp}/{self.max_hp}")
            return False
    
    def show_hit_effect(self):
        """Show visual effect when enemy is hit"""
        # Load the "svet" (light) version of the sprite
        hit_image_name = f"{self.ENEMY_TYPES[self.enemy_type]['image']}svet"
        try:
            self.image = resource_manager.get_image(hit_image_name)
        except:
            # If hit effect image doesn't exist, briefly change color
            self.image.fill(config.WHITE, special_flags=pygame.BLEND_ADD)
    
    def respawn(self):
        """Respawn enemy at a new position"""
        self.rect.x = random.randrange(0, config.SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -40)
        self.speed_y = random.randrange(*config.MOB_SPEED_RANGE)
        self.speed_x = random.randrange(-4, 5)
        self.hp = self.max_hp
        
        # Reset image to normal
        enemy_data = self.ENEMY_TYPES[self.enemy_type]
        self.image = resource_manager.get_image(enemy_data['image'])
        
        logger.debug(f"Enemy {self.enemy_type} respawned")
    
    def get_color_palette(self) -> list:
        """Get color palette for particle effects"""
        # This would ideally use the ColorThief functionality
        # For now, return some default colors based on enemy type
        color_palettes = {
            '1': [(255, 153, 0), (255, 193, 7)],
            '2': [(0, 77, 86), (0, 105, 93)],
            '3': [(255, 153, 0), (255, 235, 59)],
            '4': [(0, 77, 86), (255, 39, 39)]
        }
        return color_palettes.get(self.enemy_type, [(255, 255, 255), (128, 128, 128)])


class EnemyBullet(pygame.sprite.Sprite):
    """Enemy bullet class"""
    
    def __init__(self, x: int, y: int, bullet_type: int = 1):
        """
        Initialize enemy bullet
        
        Args:
            x: Initial x position
            y: Initial y position
            bullet_type: Type of bullet (1 or 2)
        """
        super().__init__()
        
        # Load appropriate bullet image
        if bullet_type == 1:
            self.image = resource_manager.get_image("xarchok1")
        else:
            self.image = resource_manager.get_image("xarchok2")
            
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 12)
        
        self.rect.centerx = x
        self.rect.top = y
        
        # Movement
        self.speed_y = random.randrange(5, 8)
        self.speed_x = random.randrange(-2, 3)
        
        self.damage = 5  # Damage dealt to player
        
        logger.debug(f"Enemy bullet type {bullet_type} created at ({x}, {y})")
    
    def update(self):
        """Update bullet position"""
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # Remove bullet if it goes off screen
        if self.rect.top > config.SCREEN_HEIGHT:
            self.kill()
            logger.debug("Enemy bullet destroyed (off screen)")


class EnemyManager:
    """Manages enemy spawning and behavior"""
    
    def __init__(self, initial_count: int = 3):
        """
        Initialize enemy manager
        
        Args:
            initial_count: Initial number of enemies to spawn
        """
        self.enemy_count = initial_count
        self.max_enemies = config.MAX_MOBS
        self.spawn_delay = 1000  # milliseconds
        self.last_spawn = 0
        
        logger.info(f"Enemy manager initialized with {initial_count} enemies")
    
    def spawn_enemy(self) -> Enemy:
        """Spawn a new enemy"""
        return Enemy()
    
    def should_spawn_enemy(self, current_enemy_count: int) -> bool:
        """
        Check if a new enemy should be spawned
        
        Args:
            current_enemy_count: Current number of enemies alive
            
        Returns:
            True if should spawn, False otherwise
        """
        current_time = pygame.time.get_ticks()
        
        return (current_enemy_count < self.max_enemies and 
                current_time - self.last_spawn > self.spawn_delay)
    
    def update_difficulty(self, level: int):
        """
        Update difficulty based on level
        
        Args:
            level: Current game level
        """
        self.enemy_count = min(3 + level, self.max_enemies)
        self.spawn_delay = max(500, 1000 - (level * 50))  # Faster spawning at higher levels
        
        logger.info(f"Difficulty updated for level {level}: {self.enemy_count} enemies, {self.spawn_delay}ms spawn delay")