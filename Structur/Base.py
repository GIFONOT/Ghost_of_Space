import pygame
import main
from Setting import W


class Base(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((W, 5))
        self.rect = self.image.get_rect()
        self.image.fill((255, 0, 0))
        self.rect.center = (main.W/2, main.H+20)

        self.Hp_base = 100
        self.Max_Hp_base = 100
