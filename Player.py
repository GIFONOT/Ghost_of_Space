import math
import pygame
from Presets import image, skin_img, shoot_sound
from Setting import W, H


class Player(pygame.sprite.Sprite):
    def __init__(self, skin=0):
        super().__init__()
        self.image = skin_img[skin]
        self.rect = self.image.get_rect(center=(W / 2, H - 115))
        self.pos = pygame.Vector2(self.rect.center)
        self.radius = 18
        self.HP = self.MaxHp = 100
        self.TotalHp = 250
        self.LifeSteal = 0
        self.shot_delay = 0.22
        self.Damage = 8
        self.SpeedKef = 330
        self.velocity = pygame.Vector2()
        self.KolBullet = 1
        self.shot_timer = self.invulnerable = self.dash_cooldown = self.dash_time = 0
        self.dash_direction = pygame.Vector2(0, -1)
        self.ram_level = self.afterburner = self.bulwark = 0
        self.pierce_level = self.rail_level = self.overpenetration = 0
        self.ram_cooldowns = {}

    @property
    def dash_delay(self):
        return 3 - 0.65 * self.afterburner

    @property
    def ram_damage(self):
        return 35 + 25 * self.ram_level + self.MaxHp * 0.15 * self.bulwark

    @property
    def ram_guard(self):
        return min(0.55, 0.15 + self.ram_level * 0.05 + self.bulwark * 0.1)

    def update(self, dt, game):
        self.shot_timer = max(0, self.shot_timer - dt)
        self.invulnerable = max(0, self.invulnerable - dt)
        self.dash_cooldown = max(0, self.dash_cooldown - dt)
        self.dash_time = max(0, self.dash_time - dt)
        self.ram_cooldowns = {enemy: time - dt for enemy, time in self.ram_cooldowns.items()
                              if enemy.alive() and time > dt}
        keys = pygame.key.get_pressed()
        movement = game.movement_keys
        direction = pygame.Vector2(
            int(pygame.KSCAN_D in movement or keys[pygame.K_d] or keys[pygame.K_RIGHT])
            - int(pygame.KSCAN_A in movement or keys[pygame.K_a] or keys[pygame.K_LEFT]),
            int(pygame.KSCAN_S in movement or keys[pygame.K_s] or keys[pygame.K_DOWN])
            - int(pygame.KSCAN_W in movement or keys[pygame.K_w] or keys[pygame.K_UP]))
        if direction.length_squared():
            direction = direction.normalize()
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.dash_cooldown == 0:
            self.dash_direction = direction if direction.length_squared() else pygame.Vector2(0, -1)
            self.dash_time = 0.18 + 0.02 * self.ram_level
            self.dash_cooldown = self.dash_delay
            self.invulnerable = max(self.invulnerable, self.dash_time + 0.1)
            self.ram_cooldowns.clear()
        if self.dash_time:
            self.velocity = self.dash_direction * 900
            self.pos += self.velocity * dt
        else:
            if self.velocity.length_squared() > self.SpeedKef ** 2:
                self.velocity.scale_to_length(self.SpeedKef)
            target = direction * self.SpeedKef
            response = 16 if direction.length_squared() else 10
            decay = math.exp(-response * dt)
            # Integrate the easing curve so inertia feels the same at different frame rates.
            self.pos += target * dt + (self.velocity - target) * (1 - decay) / response
            self.velocity = target + (self.velocity - target) * decay
            if not direction.length_squared() and self.velocity.length_squared() < 0.25:
                self.velocity.update(0, 0)
        unclamped = self.pos.copy()
        self.pos.x = max(self.rect.width / 2, min(W - self.rect.width / 2, self.pos.x))
        self.pos.y = max(105 + self.rect.height / 2, min(H - 15 - self.rect.height / 2, self.pos.y))
        if self.pos.x != unclamped.x:
            self.velocity.x = 0
        if self.pos.y != unclamped.y:
            self.velocity.y = 0
        self.rect.center = self.pos
        if (keys[pygame.K_SPACE] or game.settings['autofire']) and self.shot_timer == 0:
            self.shot_timer = self.shot_delay * 1.18 ** self.rail_level
            for i in range(self.KolBullet):
                offset = i - (self.KolBullet - 1) / 2
                damage = self.Damage * 1.4 ** self.rail_level / (1 + 0.65 * (self.KolBullet - 1))
                bullet = Bullet(self.rect.centerx + offset * 19, self.rect.top, offset * 75, damage,
                                pierce=self.pierce_level, rail=self.rail_level, overpenetration=self.overpenetration)
                game.bullets.add(bullet)
            shoot_sound.play()

    def hurt(self, damage):
        if self.invulnerable > 0:
            return False
        self.HP = max(0, self.HP - damage)
        self.invulnerable = 0.65
        return True

    def upgrade(self, kind):
        if kind == 'HP':
            self.HP = min(self.MaxHp, self.HP + 30)
        elif kind == 'MaxHp':
            gain = min(15, self.TotalHp - self.MaxHp)
            self.MaxHp += gain
            self.HP = min(self.MaxHp, self.HP + gain)
        elif kind == 'Damage':
            self.Damage = min(24, self.Damage + 2)
        elif kind == 'AtakSpeade':
            self.shot_delay = max(0.14, self.shot_delay - 0.012)
        elif kind == 'speade':
            self.SpeedKef = min(480, self.SpeedKef + 20)
        elif kind == 'LifeSteal':
            self.LifeSteal = min(0.06, self.LifeSteal + 0.01)
        elif kind == 'KolBullet':
            self.KolBullet = min(3, self.KolBullet + 1)
        elif kind == 'Ram' and self.ram_level < 3:
            self.ram_level += 1
            gain = min(20, self.TotalHp - self.MaxHp)
            self.MaxHp += gain
            self.HP = min(self.MaxHp, self.HP + gain)
        elif kind == 'Afterburner' and self.ram_level:
            self.afterburner = min(2, self.afterburner + 1)
            self.dash_cooldown = min(self.dash_cooldown, self.dash_delay)
        elif kind == 'Bulwark' and self.ram_level:
            self.bulwark = min(2, self.bulwark + 1)
        elif kind == 'Pierce' and self.pierce_level < 3:
            self.pierce_level += 1
            self.Damage = min(24, self.Damage + 2)
        elif kind == 'Rail' and self.pierce_level:
            self.rail_level = min(2, self.rail_level + 1)
        elif kind == 'Overpenetration' and self.pierce_level:
            self.overpenetration = min(2, self.overpenetration + 1)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speedx=0, damage=8, pierce=0, rail=0, overpenetration=0):
        super().__init__()
        self.image = image('b2.png')
        if pierce:
            self.image = pygame.Surface((8 + rail * 2, 22 + rail * 5), pygame.SRCALPHA)
            self.image.fill((65, 185, 245))
            pygame.draw.rect(self.image, (215, 250, 255), (3, 0, 3, self.image.get_height()))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.pos = pygame.Vector2(self.rect.center)
        self.radius = 5
        self.speedx = speedx
        self.speedy = -680 - 150 * rail
        self.damage = damage
        self.piercing = pierce > 0
        self.remaining_hits = 1 + pierce
        self.retention = 0.82 + 0.14 * overpenetration
        self.hit_targets = set()
        self.previous_pos = self.pos.copy()

    def update(self, dt):
        self.previous_pos.update(self.pos)
        self.pos += pygame.Vector2(self.speedx, self.speedy) * dt
        self.rect.center = self.pos
        if self.rect.bottom < 0:
            self.kill()

    def intersects(self, target):
        if target in self.hit_targets:
            return False
        start = self.previous_pos
        delta = self.pos - start
        if delta.length_squared():
            fraction = max(0, min(1, (pygame.Vector2(target.rect.center) - start).dot(delta) / delta.length_squared()))
            closest = start + delta * fraction
        else:
            closest = self.pos
        return closest.distance_to(target.rect.center) <= self.radius + target.radius
