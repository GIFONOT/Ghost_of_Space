import pygame
import random
import main
from os import path
from Presets import img_dir
from Setting import H, W
from colorthief import ColorThief


class Mob(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.Surface((30, 40))
        # self.image.fill((0, 0, 0))

        global img, png
        img = {}
        png = {}

        png['4'] = ColorThief('Png/ino2.png')
        png['2'] = ColorThief('Png/ino3.png')
        png['1'] = ColorThief('Png/ino4.png')
        png['3'] = ColorThief('Png/ino5.png')

        img['1'] = pygame.image.load(path.join(img_dir, 'ino4.png'))
        img['2'] = pygame.image.load(path.join(img_dir, 'ino3.png'))
        img['3'] = pygame.image.load(path.join(img_dir, 'ino5.png'))
        img['4'] = pygame.image.load(path.join(img_dir, 'ino2.png'))

        self.type = random.choice(['1', '2', '3', '4'])
        self.image = img[self.type]

        self.png = png[self.type]

        self.rect = self.image.get_rect()  # хит_бокс

        if self.type == '4' or self.type == '2':
            self.radius = int(self.rect.width / 7)
            self.setting = 2
        else:
            self.radius = int(self.rect.width / 3)
            self.setting = 3

        # pygame.draw.circle(self.image, (255, 0, 0), self.rect.center, self.radius)# хит_боксs
        # pygame.draw.rect(self.image, (255, 0, 0), self.rect)

        self.rect.x = random.randrange(main.W - self.rect.width)
        self.rect.y = random.randrange(-200, -40)
        self.speedy = random.randrange(1, 2)
        self.speedx = random.randrange(-4, 4)

        # Статы дефолт крипа
        self.Hp = 20
        self.Score = random.randrange(2, 7)

        self.last_shot = pygame.time.get_ticks()
        self.shot_delay = random.randrange(1500, 3000)
        self.shans = random.randrange(1, 100)

        self.svet = 0
        self.pasiv = random.randrange(2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        self.image = img[self.type]

        # Puk puk
        if self.pasiv == 1:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shot_delay:
                self.last_shot = now
                if self.type == '4' or self.type == '2':
                    bullet = Bullet(self.rect.centerx, self.rect.centery - 25, 1)
                else:
                    bullet = Bullet(self.rect.centerx, self.rect.centery - 25, 2)

                main.bulletMob.add(bullet)
                main.all_sprites.add(bullet)

        if self.rect.right > W:
            self.speedx = 0
            self.speedx -= random.randrange(2, 4)
        elif self.rect.left < 0:
            self.speedx = 0
            self.speedx += random.randrange(2, 4)

        if self.rect.top > H + 10 or self.rect.right < -25 or self.rect.left > W + 20:
            self.rect.x = random.randrange(main.W - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 2)
            self.speedx += random.randrange(-4, 4)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)

        if type == 1:
            self.image = pygame.image.load(path.join(img_dir, 'xarchok1.png'))
        else:
            self.image = pygame.image.load(path.join(img_dir, 'xarchok2.png'))

        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 12)
        # pygame.draw.circle(self.image, (255, 0, 0), self.rect.center, self.radius)  # хит_бокс

        self.rect.top = y
        self.rect.centerx = x
        self.speedy = random.randrange(5, 7)
        self.speedx = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.top > H:
            self.kill()
