"""
Player class for Ghost of Space game
"""
import pygame
import math
from typing import List, Tuple
from utils.logger import logger
import config
from resource_manager import resource_manager


class Player(pygame.sprite.Sprite):
    """Player character class with improved structure and documentation"""
    
    def __init__(self, x: int = None, y: int = None):
        """
        Initialize the player
        
        Args:
            x: Initial x position (default: center of screen)
            y: Initial y position (default: bottom of screen)
        """
        super().__init__()
        
        # Load player image
        self.image = resource_manager.get_image("somm")
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 3.5)
        
        # Position
        if x is None:
            x = config.SCREEN_WIDTH // 2
        if y is None:
            y = int(config.SCREEN_HEIGHT / 1.2)
            
        self.rect.center = (x, y)
        
        # Movement
        self.speed_x = 0
        self.speed_y = 0
        self.base_speed = config.PLAYER_SPEED
        
        # Combat stats
        self.hp = config.HP_BASE
        self.max_hp = config.HP_BASE
        self.total_hp = 300  # Maximum possible HP
        self.damage = config.DAMAGE_BASE
        self.life_steal = 0.0
        
        # Shooting
        self.last_shot = 0
        self.shot_delay = 200  # milliseconds
        self.bullet_count = 1
        
        # Movement speed multiplier
        self.speed_multiplier = 1.0
        
        # Input state
        self.keys_pressed = set()
        
        logger.info("Player initialized")
    
    def handle_input(self, keys_pressed: pygame.key.ScancodeWrapper):
        """Handle player input"""
        self.keys_pressed = keys_pressed
        
        # Reset movement
        self.speed_x = 0
        self.speed_y = 0
        
        # Calculate movement
        total_speed = self.base_speed + self.speed_multiplier
        
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            self.speed_x = -total_speed
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            self.speed_x = total_speed
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            self.speed_y = -total_speed
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            self.speed_y = total_speed
    
    def update(self):
        """Update player state"""
        # Apply movement
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Keep player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        
        # Handle shooting
        if self.keys_pressed.get(pygame.K_SPACE, False):
            self.try_shoot()
    
    def try_shoot(self) -> List['Bullet']:
        """
        Try to shoot bullets
        
        Returns:
            List of created bullets
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot < self.shot_delay:
            return []
        
        self.last_shot = current_time
        bullets = []
        
        # Play shoot sound
        sound = resource_manager.get_sound("pew")
        sound.play()
        
        if self.bullet_count == 1:
            bullet = Bullet(self.rect.centerx - 2, self.rect.top + 35)
            bullets.append(bullet)
        elif self.bullet_count == 2:
            bullet1 = Bullet(self.rect.left + 32, self.rect.centery + 2)
            bullet2 = Bullet(self.rect.right - 32, self.rect.centery + 2)
            bullets.extend([bullet1, bullet2])
        else:  # 3 or more bullets
            bullet1 = Bullet(self.rect.left + 21, self.rect.centery + 2)
            bullet2 = Bullet(self.rect.right - 21, self.rect.centery + 2)
            bullet3 = Bullet(self.rect.centerx, self.rect.top + 40)
            bullets.extend([bullet1, bullet2, bullet3])
        
        return bullets
    
    def take_damage(self, damage: int):
        """
        Apply damage to player
        
        Args:
            damage: Amount of damage to take
        """
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        logger.debug(f"Player took {damage} damage. HP: {self.hp}/{self.max_hp}")
    
    def heal(self, amount: int):
        """
        Heal the player
        
        Args:
            amount: Amount to heal
        """
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        actual_heal = self.hp - old_hp
        if actual_heal > 0:
            logger.debug(f"Player healed {actual_heal} HP. HP: {self.hp}/{self.max_hp}")
    
    def apply_life_steal(self, damage_dealt: int):
        """
        Apply life steal healing based on damage dealt
        
        Args:
            damage_dealt: Amount of damage dealt to enemy
        """
        if self.life_steal > 0 and self.hp < self.max_hp:
            heal_amount = int(damage_dealt * self.life_steal)
            self.heal(heal_amount)
    
    def is_alive(self) -> bool:
        """Check if player is alive"""
        return self.hp > 0
    
    def upgrade_max_hp(self, amount: int):
        """
        Increase maximum HP
        
        Args:
            amount: Amount to increase max HP by
        """
        old_max = self.max_hp
        self.max_hp = min(self.max_hp + amount, self.total_hp)
        actual_increase = self.max_hp - old_max
        if actual_increase > 0:
            logger.debug(f"Max HP increased by {actual_increase}. Max HP: {self.max_hp}")
    
    def upgrade_damage(self, amount: int):
        """
        Increase damage
        
        Args:
            amount: Amount to increase damage by
        """
        self.damage += amount
        logger.debug(f"Damage increased by {amount}. Damage: {self.damage}")
    
    def upgrade_life_steal(self, amount: float):
        """
        Increase life steal
        
        Args:
            amount: Amount to increase life steal by (as percentage)
        """
        self.life_steal += amount
        logger.debug(f"Life steal increased by {amount}. Life steal: {self.life_steal}")
    
    def upgrade_attack_speed(self, reduction: int):
        """
        Increase attack speed by reducing shot delay
        
        Args:
            reduction: Amount to reduce shot delay by
        """
        self.shot_delay = max(50, self.shot_delay - reduction)  # Minimum 50ms delay
        logger.debug(f"Attack speed increased. Shot delay: {self.shot_delay}ms")
    
    def upgrade_speed(self, amount: float):
        """
        Increase movement speed
        
        Args:
            amount: Amount to increase speed multiplier by
        """
        self.speed_multiplier += amount
        logger.debug(f"Speed increased by {amount}. Speed multiplier: {self.speed_multiplier}")
    
    def upgrade_bullet_count(self):
        """Increase the number of bullets shot at once"""
        self.bullet_count += 1
        logger.debug(f"Bullet count increased to {self.bullet_count}")


class Bullet(pygame.sprite.Sprite):
    """Player bullet class"""
    
    def __init__(self, x: int, y: int):
        """
        Initialize bullet
        
        Args:
            x: Initial x position
            y: Initial y position
        """
        super().__init__()
        
        self.image = resource_manager.get_image("b2")
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 7)
        
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -config.BULLET_SPEED
        
        logger.debug(f"Bullet created at ({x}, {y})")
    
    def update(self):
        """Update bullet position"""
        self.rect.y += self.speed_y
        
        # Remove bullet if it goes off screen
        if self.rect.bottom < 0:
            self.kill()
            logger.debug("Bullet destroyed (off screen)")