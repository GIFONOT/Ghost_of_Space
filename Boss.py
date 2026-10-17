import math
import pygame
from Difficulty import DIFFICULTIES
from Mob import Mob, Bullet
from Presets import pixel_sprite
from Setting import W, H


class Hazard(pygame.sprite.Sprite):
    def __init__(self, kind, center, target=None, warning=0.9, duration=0.7, width=32, difficulty=None):
        super().__init__()
        self.kind = kind
        self.pos = pygame.Vector2(center)
        self.target = pygame.Vector2(target) if target is not None else self.pos.copy()
        self.difficulty = DIFFICULTIES['hard'] if difficulty is None else difficulty
        self.warning = warning * math.sqrt(self.difficulty['fire_delay'])
        self.duration, self.width = duration, width
        self.age = 0
        self.radius = 14
        self.Hp = 22 * self.difficulty['health']
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (70, 225, 245), (14, 14), 12, 3)
        pygame.draw.circle(self.image, (245, 110, 215), (14, 14), 5)
        self.rect = self.image.get_rect(center=center)
        self.damage = {'beam': 48, 'shock': 38, 'mine': 34, 'well': 24}.get(kind, 0)

    @property
    def active(self):
        return self.age >= self.warning

    @property
    def vulnerable(self):
        return self.kind == 'mine'

    @property
    def ring_radius(self):
        return 25 + max(0, self.age - self.warning) * 260 * self.difficulty['bullet_speed']

    def update(self, dt, game):
        self.age += dt
        if self.kind == 'well' and self.active and not game.player.dash_time:
            delta = self.pos - game.player.pos
            if 30 < delta.length() < 170:
                game.player.pos += delta.normalize() * min(delta.length(), 150 * dt)
                game.player.rect.center = game.player.pos
        if self.age >= self.warning + self.duration:
            if self.kind == 'mine':
                for angle in range(0, 360, 45):
                    game.enemy_bullets.add(Bullet(*self.pos, direction=pygame.Vector2(0, 1).rotate(angle),
                        speed=310 * self.difficulty['bullet_speed'], damage=26))
            self.kill()

    def collides(self, player):
        if not self.active:
            return False
        distance = player.pos.distance_to(self.pos)
        if self.kind == 'shock':
            return abs(distance - self.ring_radius) <= player.radius + 9
        if self.kind in ('mine', 'well'):
            return distance <= player.radius + (14 if self.kind == 'mine' else 27)
        if self.kind == 'beam':
            line = self.target - self.pos
            if not line.length_squared():
                return False
            fraction = max(0, min(1, (player.pos - self.pos).dot(line) / line.length_squared()))
            return player.pos.distance_to(self.pos + line * fraction) <= player.radius + self.width / 2
        return False

    def draw(self, surface):
        if self.kind in ('beam', 'path'):
            color = (255, 85, 125, 220) if self.active else (255, 145, 95, 95)
            width = max(1, round(self.width)) if self.kind == 'beam' else 3
            pygame.draw.line(surface, color, self.pos, self.target, max(1, width))
            if self.active and self.kind == 'beam':
                pygame.draw.line(surface, (255, 240, 210, 240), self.pos, self.target, max(2, width // 4))
            else:
                pygame.draw.line(surface, (255, 185, 100, 220), self.pos, self.target, 2)
                pygame.draw.circle(surface, (255, 180, 90, 220), self.target, 18, 2)
        elif self.kind == 'shock':
            radius = round(self.ring_radius) if self.active else 30
            pygame.draw.circle(surface, (255, 155, 65, 210), self.pos, radius, 12 if self.active else 2)
        elif self.kind == 'mine':
            surface.blit(self.image, self.rect)
            color = (255, 95, 145, 230) if self.active else (95, 230, 245, 180)
            pygame.draw.circle(surface, color, self.pos, 22 + int(self.age * 6) % 4, 2)
        else:
            color = (150, 100, 245, 90 if self.active else 40)
            pygame.draw.circle(surface, color, self.pos, 170, 2)
            pygame.draw.circle(surface, (130, 100, 255, 100), self.pos, 28)
            for radius in (45, 85, 125):
                rect = pygame.Rect(0, 0, radius * 2, radius * 2)
                rect.center = self.pos
                pygame.draw.arc(surface, (110, 215, 255, 170), rect, self.age * 3, self.age * 3 + 4, 4)


class Missile(Bullet):
    def __init__(self, x, y, player, difficulty):
        super().__init__(x, y, direction=player.pos - pygame.Vector2(x, y),
                         speed=350 * difficulty['bullet_speed'], damage=36)
        self.player = player
        self.tracking = 1.25
        self.image = pygame.Surface((12, 22), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (255, 190, 90), ((6, 0), (12, 13), (8, 22), (4, 22), (0, 13)))
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = 6

    def update(self, dt):
        self.tracking -= dt
        delta = self.player.pos - self.pos
        if self.tracking > 0 and delta.length_squared():
            angle = (self.velocity.angle_to(delta) + 180) % 360 - 180
            turn = max(-140 * dt, min(140 * dt, angle))
            self.velocity.rotate_ip(turn)
        super().update(dt)


class Boss(pygame.sprite.Sprite):
    INTERVAL = 5
    NAMES = ('WARDEN', 'TEMPEST', 'OVERLORD')
    PATTERNS = (
        (('railguns', 'barrage', 'execution'), ('charge', 'execution', 'shockwave')),
        (('spiral', 'minefield', 'eruption'), ('vortex', 'crossfire', 'eruption')),
        (('escorts', 'missiles', 'siege'), ('lockdown', 'hunt', 'siege')),
    )

    def __init__(self, stage, difficulty=None):
        super().__init__()
        self.difficulty = DIFFICULTIES['hard'] if difficulty is None else difficulty
        self.stage = stage
        self.variant = (stage // self.INTERVAL - 1) % 3
        self.image = pixel_sprite(('boss-warden.png', 'boss-tempest.png', 'boss-overlord.png')[self.variant], 240, grid=96)
        self.home_y = 325 if self.variant == 1 else 270
        self.rect = self.image.get_rect(center=(W / 2, -140))
        self.pos = pygame.Vector2(self.rect.center)
        self.radius = 68
        self.Hp = self.max_hp = (2600 + (stage // self.INTERVAL - 1) * 1100) * self.difficulty['health']
        self.Score = 700 * (stage // self.INTERVAL)
        self.is_boss = True
        self.name = self.NAMES[self.variant]
        self.damage = 60
        self.hit_flash = self.age = 0
        self.phase = 1
        self.action = 'arrive'
        self.action_timer = 0
        self.shot_timer = 1.0
        self.pressure_timer = 1.2
        self.attack_index = 0
        self.last_attack = ''
        self.stream_time = self.stream_tick = 0
        self.escorts = pygame.sprite.Group()
        self.charge_target = pygame.Vector2()

    @property
    def shielded(self):
        return self.variant == 2 and self.phase == 2 and bool(self.escorts)

    @property
    def vulnerable(self):
        return self.action not in ('arrive', 'transition') and not self.shielded

    @property
    def enraged(self):
        return self.phase == 2

    def take_damage(self, amount, ram=False, penetrating=False):
        if not self.vulnerable:
            return 0
        armor = 1.35 if self.action == 'recover' else 1 if ram or penetrating else 0.7
        floor = self.max_hp / 2 if self.phase == 1 else 0
        dealt = min(self.Hp - floor, amount * armor)
        self.Hp -= max(0, dealt)
        return max(0, dealt)

    def hazard(self, game, kind, pos, target=None, **options):
        hazard = Hazard(kind, pos, target, difficulty=self.difficulty, **options)
        game.hazards.add(hazard)
        return hazard

    def fire(self, game, directions, speed=340):
        for direction in directions:
            game.enemy_bullets.add(Bullet(*self.pos, direction=direction,
                speed=speed * self.difficulty['bullet_speed'], damage=30))

    def summon(self, game, count):
        existing = len(self.escorts)
        for i in range(min(count, 5 - existing)):
            escort = Mob(self.stage, kind=3 if self.phase == 2 else 0, difficulty=self.difficulty)
            escort.pos.update(130 + i * 100, 330)
            escort.rect.center = escort.pos
            escort.entered = True
            escort.Hp *= 0.65
            escort.max_hp = escort.Hp
            escort.Score = 0
            escort.summoned = True
            game.mobs.add(escort)
            self.escorts.add(escort)

    def attack(self, game):
        pattern = self.PATTERNS[self.variant][self.phase - 1]
        attack = pattern[self.attack_index % len(pattern)]
        self.attack_index += 1
        self.last_attack = attack
        p = game.player.pos
        if attack == 'railguns':
            for i, x in enumerate((p.x, max(40, p.x - 110), min(W - 40, p.x + 110))):
                self.hazard(game, 'beam', (x, 170), (x, H), warning=0.8 + i * 0.3, duration=0.85, width=46)
        elif attack == 'barrage':
            self.fire(game, [(p - self.pos).rotate(a) for a in range(-48, 49, 12)], 410)
        elif attack == 'execution':
            for i, dx in enumerate((-180, 0, 180)):
                start = pygame.Vector2(max(25, min(W - 25, p.x + dx)), 170)
                direction = p - start
                if not direction.length_squared():
                    direction.update(0, 1)
                self.hazard(game, 'beam', start, start + direction.normalize() * H * 2,
                            warning=0.8 + i * 0.22, duration=0.7, width=38)
        elif attack == 'charge':
            self.charge_target.update(max(110, min(W - 110, p.x)), max(480, min(H - 125, p.y)))
            marker = self.hazard(game, 'path', self.pos, self.charge_target, warning=0.85, duration=0.01)
            self.action = 'windup'
            self.action_timer = marker.warning
        elif attack == 'shockwave':
            self.hazard(game, 'shock', self.pos, warning=0.7, duration=3.5)
            self.fire(game, [(p - self.pos).rotate(a) for a in (-45, -22, 0, 22, 45)], 380)
        elif attack == 'spiral':
            self.stream_time = 2.4
            self.stream_tick = 0
        elif attack == 'minefield':
            for i, x in enumerate((100, 250, 400, 550)):
                self.hazard(game, 'mine', (x, 440 + (i % 2) * 120), warning=1, duration=2.2)
        elif attack == 'eruption':
            for dx in (-100, 0, 100):
                self.hazard(game, 'mine', (max(30, min(W - 30, p.x + dx)), p.y),
                            warning=0.85, duration=1.4)
            self.hazard(game, 'shock', self.pos, warning=0.7, duration=3.5)
        elif attack == 'vortex':
            self.hazard(game, 'well', (W / 2, 580), warning=0.9, duration=4.5)
            self.stream_time, self.stream_tick = 3.4, 0
        elif attack == 'crossfire':
            self.hazard(game, 'beam', (p.x, 170), (p.x, H), warning=1.0, duration=0.7, width=32)
            y = max(440, min(H - 100, p.y))
            self.hazard(game, 'beam', (0, y), (W, y), warning=1.0, duration=0.7, width=32)
        elif attack == 'escorts':
            self.summon(game, 3)
        elif attack in ('missiles', 'hunt'):
            for dx in (-65, 0, 65):
                game.enemy_bullets.add(Missile(self.pos.x + dx, self.rect.bottom, game.player, self.difficulty))
            if attack == 'hunt':
                self.fire(game, [pygame.Vector2(0, 1).rotate(a) for a in range(-65, 66, 26)], 260)
        elif attack == 'lockdown':
            self.summon(game, 3)
            left = max(40, min(W - 210, p.x - 85))
            right = left + 170
            for x, width in ((left / 2, left), ((right + W) / 2, W - right)):
                self.hazard(game, 'beam', (x, 170), (x, H), warning=1.2, duration=1.1, width=width)
        elif attack == 'siege':
            self.hazard(game, 'beam', (p.x, 170), (p.x, H), warning=0.9, duration=1.2, width=60)
            for dx in (-100, 100):
                game.enemy_bullets.add(Missile(self.pos.x + dx, self.rect.bottom, game.player, self.difficulty))

    def update(self, dt, game):
        self.age += dt * self.difficulty['speed']
        self.hit_flash = max(0, self.hit_flash - dt)
        if self.phase == 1 and self.Hp <= self.max_hp / 2:
            self.phase = 2
            game.burst(self.pos, self.image, 45, fragments=True)
            self.action, self.action_timer = 'transition', 1.4
            self.attack_index = 0
            self.stream_time = 0
            game.enemy_bullets.empty()
            game.hazards.empty()
        if self.action == 'arrive':
            self.pos.y = min(self.home_y, self.pos.y + 280 * dt)
            if self.pos.y >= self.home_y:
                self.action = 'idle'
        elif self.action in ('transition', 'recover', 'windup'):
            self.action_timer -= dt
            if self.action == 'transition':
                self.pos += (pygame.Vector2(W / 2, self.home_y) - self.pos) * min(1, dt * 5)
            if self.action_timer <= 0:
                self.action = 'charge' if self.action == 'windup' else 'idle'
                self.shot_timer = 0.5 if self.phase == 2 else 1
        elif self.action == 'charge':
            delta = self.charge_target - self.pos
            step = 880 * self.difficulty['speed'] * dt
            if delta.length() <= step:
                self.pos.update(self.charge_target)
                self.action, self.action_timer = 'recover', 0.65
                self.hazard(game, 'shock', self.pos, warning=0.45, duration=2.4)
            elif delta.length_squared():
                self.pos += delta.normalize() * step
        else:
            home = pygame.Vector2(W / 2 + math.sin(self.age * (1.5 if self.phase == 1 else 1.9)) * 195,
                                  self.home_y + math.sin(self.age * 2.1) * 45)
            if self.variant == 1:
                home.y += math.sin(self.age * 1.3) * 20
            delta = home - self.pos
            if delta.length_squared():
                self.pos += delta.normalize() * min(delta.length(), 390 * dt * self.difficulty['speed'])
            self.shot_timer -= dt / self.difficulty['fire_delay']
            if self.shot_timer <= 0:
                self.attack(game)
                self.shot_timer = (1.9 if self.phase == 1 else 1.45) + (0.4 if self.variant == 2 else 0)
        self.rect.center = self.pos
        if self.action == 'idle':
            self.pressure_timer -= dt / self.difficulty['fire_delay']
            if self.pressure_timer <= 0:
                aim = game.player.pos + game.player.velocity * 0.25 - self.pos
                self.fire(game, [aim.rotate(a) for a in (-12, 0, 12)], 430)
                self.pressure_timer = 1.15 if self.phase == 1 else 0.85
        if self.stream_time > 0 and self.action != 'transition':
            self.stream_time -= dt
            self.stream_tick -= dt / self.difficulty['fire_delay']
            if self.stream_tick <= 0:
                self.stream_tick = 0.12
                base = pygame.Vector2(0, 1).rotate(self.age * 135)
                self.fire(game, [base, -base] if self.phase == 1 else [base.rotate(a) for a in (0, 90, 180, 270)], 300)
