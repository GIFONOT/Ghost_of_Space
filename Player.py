import pygame.sprite
from colorthief import ColorThief

import main
import math
from os import path
from Presets import img_dir, shoot_sound
from Setting import W, H


class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        #self.image = pygame.Surface((50, 50))
        #self.image.fill((255, 0, 0))
        im = pygame.image.load(path.join(img_dir, 'pixil-frame-0 (31).png'))# Hors_LV1(1).png
        #im = pygame.transform.scale(im, (100, 100))
        self.image = im
        self.rect = self.image.get_rect()  # хит бокс перса
        self.radius = int(self.rect.width / 2.2)

        # pygame.draw.circle(self.image, (255, 0, 0), self.rect.center, self.radius)# хит_бокс

        self.rect.center = (W / 2, H / 1.2)
        self.speedx = 0
        self.speedy = 0

        self.angle = 0

        self.last_shot = pygame.time.get_ticks()

        # Статы игрока
        self.HP = 100
        self.MaxHp = 100
        self.TotalHp = 300

        self.LifeSteal = 0
        self.shot_delay = 200
        self.Damage = 5
        self.SpeedKef = 2

        # гел статы
        self.KolBullet = 1

    # движение
    def update(self):
        #self.image = pygame.image.load(path.join(img_dir, 'my2.png'))
        self.speedx = 0
        self.speedy = 0
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        x = False
        y = False

        '''keystate = pygame.key.get_pressed()
        if keystate[pygame.K_w]:
            self.rect.x += self.SpeedKef * cos_a
            self.rect.y += self.SpeedKef * sin_a
        if keystate[pygame.K_s]:
            self.rect.x += -self.SpeedKef * cos_a
            self.rect.y += -self.SpeedKef * sin_a
        if keystate[pygame.K_a]:
            self.rect.x += self.SpeedKef * sin_a
            self.rect.y += -self.SpeedKef * cos_a
        if keystate[pygame.K_d]:
            self.rect.x += -self.SpeedKef * sin_a
            self.rect.y += self.SpeedKef * cos_a
        if keystate[pygame.K_LEFT]:
            self.angle -= 0.02
        if keystate[pygame.K_RIGHT]:
            self.angle += 0.02'''

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_a]:
            #self.image = pygame.image.load(path.join(img_dir, 'myA.png'))
            self.speedx = -6 - self.SpeedKef
            x = True
        if keystate[pygame.K_d]:
            #self.image = pygame.image.load(path.join(img_dir, 'myD.png'))
            self.speedx = 6 + self.SpeedKef
            x = True
        if keystate[pygame.K_w]:
            #self.image = pygame.image.load(path.join(img_dir, 'my4.png'))
            self.speedy = -4 - self.SpeedKef
            y = True
        if keystate[pygame.K_s]:
            #self.image = pygame.image.load(path.join(img_dir, 'my3.png'))
            self.speedy = 4 + self.SpeedKef
            y = True

        if x:
            self.rect.x += self.speedx
        if y:
            self.rect.y += self.speedy

        if keystate[pygame.K_SPACE]:
            # Выстрел
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shot_delay:
                self.last_shot = now
                if self.KolBullet <= 1:
                    bullet = Bullet(self.rect.centerx+2, self.rect.top + 35)  # +30
                    main.all_sprites.add(bullet)
                    main.bullets.add(bullet)
                    shoot_sound.play()
                if self.KolBullet == 2:
                    bullet1 = Bullet(self.rect.left + 32, self.rect.centery + 2)
                    bullet2 = Bullet(self.rect.right - 32, self.rect.centery + 2)
                    main.all_sprites.add(bullet1)
                    main.all_sprites.add(bullet2)
                    main.bullets.add(bullet1)
                    main.bullets.add(bullet2)
                    shoot_sound.play()
                if self.KolBullet > 2:
                    bullet1 = Bullet(self.rect.left + 21, self.rect.centery + 2)
                    bullet2 = Bullet(self.rect.right - 21, self.rect.centery + 2)
                    bullet3 = Bullet(self.rect.centerx, self.rect.top + 40)
                    main.all_sprites.add(bullet1)
                    main.all_sprites.add(bullet2)
                    main.all_sprites.add(bullet3)
                    main.bullets.add(bullet1)
                    main.bullets.add(bullet2)
                    main.bullets.add(bullet3)
                    shoot_sound.play()

        if self.rect.right > main.W:
            self.rect.right = main.W
        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.bottom > main.H:
            self.rect.bottom = main.H
        if self.rect.top < 0:
            self.rect.top = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        # self.image = pygame.Surface((10, 20))
        # self.image.fill((0, 0, 255))

        self.image = pygame.image.load(path.join(img_dir, 'b2.png')) #b1.png mybule.png
        self.rect = self.image.get_rect()
        self.png = ColorThief('Png/b2.png')
        self.radius = int(self.rect.width / 7)
        #pygame.draw.circle(self.image, (255, 0, 0), self.rect.center, self.radius)  # хит_бокс

        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
            self.kill()
