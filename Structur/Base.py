import pygame
from Setting import W, H


class Base(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((W, 5))
        self.image.fill((85, 205, 190))
        self.rect = self.image.get_rect(midbottom=(W / 2, H))
        self.Hp_base = self.Max_Hp_base = 100

    def repair(self, amount):
        self.Hp_base = min(self.Max_Hp_base, self.Hp_base + amount)
