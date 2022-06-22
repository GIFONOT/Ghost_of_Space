import random
import pygame
from Setting import H, W


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, png, setting):
        pygame.sprite.Sprite.__init__(self)
        kef = 1

        '''kef = 1
        if int == 1:
            col1 = {}
            col1['col_green_1'] = (27, 94, 31)
            col1['col_green_2'] = (48, 125, 50)
            col1['col_green_3'] = (55, 142, 61)
            kef = 0.6
            self.image = pygame.Surface((7, 7))
            cols1 = random.choice(['col_green_1', 'col_green_2', 'col_green_3'])
            self.cols = col1[cols1]
        elif int == 2:
            col2 = {}
            col2['col_green_1'] = (0, 77, 86)
            col2['col_green_2'] = (0, 105, 93)
            col2['col_green_3'] = (255, 39, 39)
            kef = 0.7
            self.image = pygame.Surface((8, 8))
            cols2 = random.choice(['col_green_1', 'col_green_2', 'col_green_3'])
            self.cols = col2[cols2]
        elif int == 3:
            col3 = {}
            col3['col_green_1'] = (255, 153, 0)
            col3['col_green_2'] = (255, 193, 7)
            col3['col_green_3'] = (255, 235, 59)
            kef = 0.5
            self.image = pygame.Surface((5, 5))
            cols3 = random.choice(['col_green_1', 'col_green_2', 'col_green_3'])
            self.cols = col3[cols3]'''

        if setting == 1:
            kef = 0.5
            self.image = pygame.Surface((5, 5))
        elif setting == 2:
            kef = 0.6
            self.image = pygame.Surface((7, 7))
        elif setting == 3:
            kef = 0.7
            self.image = pygame.Surface((8, 8))

        # self.cols = ge_col(png)

        self.rect = self.image.get_rect()

        pygame.draw.rect(self.image, png[random.randrange(0, 2)], self.rect)

        self.tin = pygame.time.get_ticks()

        self.rect.x = x
        self.rect.y = y

        self.last_shot = pygame.time.get_ticks()
        self.shot_delay = random.randrange(200, 500)

        self.sy = random.randrange(-10, 10) * kef  # * random.uniform(1.1, 1.5)
        self.sx = random.randrange(-10, 10) * kef  # * random.uniform(1.1, 1.5)
        while self.sy == 0 or self.sx == 0:
            self.sy = random.randrange(-10, 10) * kef
            self.sx = random.randrange(-10, 10) * kef

    def update(self):
        self.rect.y += self.sy
        self.rect.x += self.sx

        if self.sx == 0 or self.sy == 0:
            self.kill()

        if self.rect.x > W or self.rect.y > H or self.rect.x < 0 or self.rect.y < 0:
            self.kill()

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shot_delay:
            self.last_shot = now
            self.kill()
