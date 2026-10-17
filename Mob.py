import math
from functools import lru_cache
import random
import pygame
from Presets import pixel_sprite
from Setting import H, W
from Difficulty import DIFFICULTIES


@lru_cache(maxsize=6)
def enemy_image(kind):
    return pixel_sprite(('enemy-raider.png', 'enemy-flanker.png', 'enemy-armored.png',
                         'enemy-hunter.png', 'enemy-mantis.png', 'enemy-oracle.png')[kind],
                        (63, 56, 72, 44, 72, 72)[kind])


class Mob(pygame.sprite.Sprite):
    def __init__(self, stage=1, kind=None, lane=None, difficulty=None):
        super().__init__()
        self.difficulty = DIFFICULTIES['hard'] if difficulty is None else difficulty
        self.type = random.randrange(min(6, 2 + stage // 2)) if kind is None else kind
        self.image = enemy_image(self.type)
        x = lane if lane is not None else random.randint(65, W - 65)
        self.rect = self.image.get_rect(center=(x, 55))
        self.pos = pygame.Vector2(self.rect.center)
        self.radius = min(27, self.rect.width * 0.34)
        self.Hp = (24, 22, 65, 38, 32, 44)[self.type] + (stage - 1) * (5 if self.type == 2 else 3.5)
        self.Hp *= self.difficulty['health']
        self.max_hp = self.Hp
        self.Score = (10, 14, 22, 18, 20, 24)[self.type]
        self.speed = (110, 160, 90, 120, 155, 110)[self.type] + min(stage * 3, 65)
        self.drift = random.choice((-1, 1)) * random.uniform(65, 105)
        if self.type == 1:
            self.pos.update(random.choice((-40, W + 40)), random.randint(180, 300))
            self.drift = 160 if self.pos.x < 0 else -160
            self.rect.center = self.pos
        self.shot_timer = random.uniform(0.3, 0.65)
        self.age = 0
        self.is_boss = False
        self.damage = 16 if self.type != 2 else 25
        self.dive_timer = random.uniform(1.3, 2.1)
        self.dive_direction = pygame.Vector2(0, 1)
        self.diving = False
        self.aim = pygame.Vector2(0, 1)
        self.hit_flash = 0
        self.entered = False

    @property
    def vulnerable(self):
        return self.entered

    def update(self, dt, game):
        self.age += dt * self.difficulty['speed']
        motion_dt = dt * self.difficulty['speed']
        self.hit_flash = max(0, self.hit_flash - dt)
        if not self.entered:
            if self.type == 1:
                self.pos.x += (360 if self.drift > 0 else -360) * motion_dt
                self.entered = 65 <= self.pos.x <= W - 65
            else:
                self.pos.y += 320 * motion_dt
                self.entered = self.pos.y >= 170
            self.rect.center = self.pos
            return
        self.shot_timer -= dt / self.difficulty['fire_delay']
        # Lock aim during the visible wind-up so a deliberate dodge can evade it.
        if self.shot_timer > 0.28:
            lead = 0.45 if self.type in (3, 5) else 0
            self.aim = game.player.pos + game.player.velocity * lead - self.pos
        if self.type == 4:
            self.dive_timer -= dt
            if self.dive_timer > 0.4:
                self.dive_direction = game.player.pos - self.pos
                if self.dive_direction.length_squared():
                    self.dive_direction = self.dive_direction.normalize()
            if self.dive_timer <= 0:
                self.diving = True
                self.pos += self.dive_direction * 460 * motion_dt
                if self.pos.y < 160 or self.pos.x < 30 or self.pos.x > W - 30:
                    self.dive_direction = pygame.Vector2(0, 1)
            else:
                self.pos.y += 35 * motion_dt
        else:
            self.pos.x += (math.sin(self.age * 4) * 200 if self.type == 1 else self.drift) * motion_dt
            self.pos.y += (30 if self.type in (2, 5) and self.age < 4.5 else self.speed) * motion_dt
        if self.pos.x < 35 or self.pos.x > W - 35:
            self.pos.x = max(35, min(W - 35, self.pos.x))
            self.drift *= -1
        self.rect.center = self.pos
        if self.shot_timer <= 0 and self.rect.centery < H - 130:
            self.shot_timer = max(0.85, 1.9 - game.stage * 0.035) + (0.5 if self.type == 2 else 0)
            angles = (-24, 0, 24) if self.type == 2 else (-12, 12) if self.type == 1 else (0,)
            for angle in angles:
                direction = self.aim.rotate(angle)
                game.enemy_bullets.add(Bullet(*self.pos, direction=direction,
                    speed=((360 if self.type == 5 else 260) + min(game.stage * 4, 80)) * self.difficulty['bullet_speed'], damage=10))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, type=1, direction=None, speed=220, damage=8):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 110, 125), (6, 6), 6)
        pygame.draw.circle(self.image, (255, 235, 205), (6, 6), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        direction = pygame.Vector2(direction) if direction is not None else pygame.Vector2(0, 1)
        self.velocity = direction.normalize() * speed if direction.length_squared() else pygame.Vector2(0, speed)
        self.radius, self.damage = 5, damage

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        if not pygame.Rect(-40, -40, W + 80, H + 80).colliderect(self.rect):
            self.kill()
