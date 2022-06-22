import pygame
import random
from Presets import leg_powerup_img


class LegBonus(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['KolBullet'])
        self.image = leg_powerup_img[self.type]
        self.rect = self.image.get_rect()

        self.radius = int(self.rect.width / 2.5)
        # draw.circle(self.image, (255, 0, 0), self.rect.center, self.radius)  # хит_боксs

        self.rect.center = center
