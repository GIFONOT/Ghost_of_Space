import random
import pygame
from Presets import powerup_img
from Setting import H


class Bonus(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.type = random.choices(('HP', 'Repair'), weights=(3, 1))[0]
        self.image = powerup_img['MaxHp' if self.type == 'Repair' else self.type]
        self.rect = self.image.get_rect(center=center)
        self.pos = pygame.Vector2(center)
        self.radius = 15

    def update(self, dt, player):
        delta = player.pos - self.pos
        if 0 < delta.length_squared() < 120 ** 2:
            self.pos += delta.normalize() * 260 * dt
        else:
            self.pos.y += 95 * dt
        self.rect.center = self.pos
        if self.rect.top > H:
            self.kill()
