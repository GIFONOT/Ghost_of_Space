import pygame
import random
import main
from Presets import powerup_img


class Bonus(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['MaxHp', 'LifeSteal', 'HP', 'Damage', 'AtakSpeade', 'speade'])
        self.image = powerup_img[self.type]
        self.rect = self.image.get_rect()

        self.radius = int(self.rect.width / 2.5)
        # draw.circle(self.image, (255, 0, 0), self.rect.center, self.radius)  # хит_боксs

        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > main.H:
            self.kill()
