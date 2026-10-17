from functools import lru_cache
import random
import pygame
from Setting import H, W, FPS
from Presets import background, skin_img, set_audio, exp_sound, bonus, dead, menu_svap
from Paths import SETTINGS_PATH
from CSV_Scores import user, write_rec, giv_rec, read, write
from Player import Player
from Mob import Mob
from Boss import Boss
from Bonus.Bonus import Bonus
from Structur.Base import Base
from Particle import Particle
from Button import Button
from Localization import RU
from Difficulty import DIFFICULTIES, LABELS

DEFAULT_SETTINGS = {'music': 0.3, 'effects': 0.6, 'skin': 0, 'autofire': False, 'language': 'ru', 'difficulty': 'normal'}
UPGRADES = {
    'Ram': ('RAM HULL', 'Contact damage + armor; +20 maximum hull'),
    'Afterburner': ('AFTERBURNER', 'Ram branch: dash cooldown -0.65 seconds'),
    'Bulwark': ('LIVING FORTRESS', 'Ram scales with hull; ram kills repair you'),
    'Pierce': ('PIERCING ROUNDS', '+1 pierced enemy; +2 damage; bypass boss armor'),
    'Rail': ('RAIL ACCELERATOR', 'Heavier, faster shots with a slower fire rate'),
    'Overpenetration': ('CHAIN ACCELERATION', 'Each pierced target preserves more damage'),
    'Damage': ('DAMAGE +2', 'Stronger shots'),
    'AtakSpeade': ('RAPID FIRE', 'Shorter shot cooldown'),
    'MaxHp': ('HULL +15', 'More maximum health'),
    'LifeSteal': ('LIFE STEAL', 'Recover health when dealing damage'),
    'speade': ('ENGINES +20', 'Faster movement'),
    'KolBullet': ('EXTRA SHOT', 'Wider volley / Shared projectile damage'),
    'Repair': ('REPAIR', 'Restore 30 hull and 25 base health'),
}


@lru_cache(maxsize=32)
def font(size):
    return pygame.font.Font(pygame.font.get_default_font(), size)


def draw_text(surf, text, size, x, y, color=(230, 240, 250)):
    text = str(text)
    width = font(size).size(text)[0]
    if width > W - 40:
        size = max(12, int(size * (W - 40) / width))
    rendered = font(size).render(text, True, color)
    surf.blit(rendered, rendered.get_rect(midtop=(x, y)))


def bar(surf, x, y, width, value, maximum, color, height=12):
    pygame.draw.rect(surf, (25, 38, 55), (x, y, width, height), border_radius=4)
    fill = max(0, min(1, value / maximum)) if maximum else 0
    if fill:
        pygame.draw.rect(surf, color, (x, y, round(width * fill), height), border_radius=4)


class Game:
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption('Ghost of Space')
        self.clock = pygame.time.Clock()
        self.settings = DEFAULT_SETTINGS.copy()
        self.notice = ''
        try:
            saved = read(SETTINGS_PATH)
            if not isinstance(saved, dict):
                raise ValueError('Invalid settings')
            for key in ('music', 'effects'):
                value = saved.get(key)
                if isinstance(value, (float, int)) and 0 <= value <= 1:
                    self.settings[key] = value
            if type(saved.get('skin')) is int and 0 <= saved['skin'] < len(skin_img):
                self.settings['skin'] = saved['skin']
            if saved.get('difficulty') in tuple(DIFFICULTIES):
                self.settings['difficulty'] = saved['difficulty']
            if saved.get('language') in ('ru', 'en'):
                self.settings['language'] = saved['language']
            if type(saved.get('autofire')) is bool:
                self.settings['autofire'] = saved['autofire']
        except (OSError, ValueError):
            self.notice = 'Settings could not be loaded; using defaults'
        set_audio(self.settings['music'], self.settings['effects'])
        if pygame.mixer.get_init():
            pygame.mixer.music.play(-1)
        self.state = 'menu'
        self.running = True
        self.name = ''
        self.focus = 0
        self.buttons = []
        self.movement_keys = set()
        self.records = []
        self.stage = 1
        self.score = 0
        self.mode = 'normal'
        self.boss_build = 'Pierce'
        self.stars = [(random.randrange(W), random.randrange(H), random.choice((25, 55, 100))) for _ in range(80)]
        self.visual_time = 0
        self.hazard_surface = pygame.Surface((W, H), pygame.SRCALPHA)
        self.reset_groups()

    def tr(self, text):
        return RU.get(text, text) if self.settings['language'] == 'ru' else text

    def reset_groups(self):
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()

    def change_state(self, state):
        if self.state == 'lost':
            dead.stop()
        self.state = state
        if state != 'play':
            self.movement_keys.clear()
        self.focus = 0
        self.buttons = []
        if state == 'scores':
            try:
                self.records = sorted(((int(score), name) for score, names in giv_rec().items()
                                       for name in names), reverse=True)[:8]
            except (OSError, ValueError, TypeError):
                self.records = []
                self.notice = 'Scores could not be read; original file kept'

    def save_settings(self):
        set_audio(self.settings['music'], self.settings['effects'])
        try:
            write(self.settings, SETTINGS_PATH)
            self.notice = ''
        except OSError:
            self.notice = 'Could not save settings; active for this session'

    def adjust(self, key, amount):
        if key == 'skin':
            self.settings[key] = (self.settings[key] + amount) % len(skin_img)
        elif key == 'difficulty':
            levels = tuple(DIFFICULTIES)
            self.settings[key] = levels[(levels.index(self.settings[key]) + 1) % len(levels)]
        elif key == 'language':
            self.settings[key] = 'en' if self.settings[key] == 'ru' else 'ru'
        elif key == 'autofire':
            self.settings[key] = not self.settings[key]
        else:
            self.settings[key] = round(max(0, min(1, self.settings[key] + amount)), 1)
        self.save_settings()

    def start(self, mode=None, build=None):
        if mode is not None:
            self.mode = mode
        if build is not None:
            self.boss_build = build
        if not self.name.strip():
            self.name = self.tr('Pilot')
        self.difficulty_name = self.settings['difficulty']
        self.difficulty = DIFFICULTIES[self.difficulty_name]
        self.player = Player(self.settings['skin'])
        self.base = Base()
        self.score, self.stage, self.dry_kills = 0, 1, 0
        if self.mode == 'boss_run':
            self.stage = Boss.INTERVAL
            upgrades = {'Damage': 4, 'AtakSpeade': 4, 'MaxHp': 3, 'speade': 2,
                        'LifeSteal': 2, 'KolBullet': 1}
            upgrades.update({
                'Ram': {'Ram': 3, 'Afterburner': 2, 'Bulwark': 2},
                'Pierce': {'Pierce': 3, 'Rail': 2, 'Overpenetration': 2},
                'Hybrid': {'Ram': 2, 'Afterburner': 1, 'Bulwark': 1,
                           'Pierce': 2, 'Rail': 1, 'Overpenetration': 1},
            }[self.boss_build])
            for kind, count in upgrades.items():
                for _ in range(count):
                    self.player.upgrade(kind)
        self.begin_stage()

    def begin_stage(self):
        self.reset_groups()
        self.player.rect.center = (W / 2, H - 115)
        self.player.pos.update(self.player.rect.center)
        self.player.velocity.update(0, 0)
        self.player.dash_time = 0
        self.player.invulnerable = 1.5
        self.player.shot_timer = 0
        self.player.ram_cooldowns.clear()
        self.spawn_timer = 0.6
        self.clear_timer = 0
        self.stage_time = 0
        self.resolved = self.spawned = 0
        self.wave_size = 1 if self.stage % Boss.INTERVAL == 0 else round(min(24, 8 + self.stage) * self.difficulty['count'])
        self.boss = Boss(self.stage, difficulty=self.difficulty) if self.stage % Boss.INTERVAL == 0 else None
        if self.boss:
            self.mobs.add(self.boss)
            self.spawned = 1
        self.change_state('play')

    def available_upgrades(self):
        p = self.player
        kinetic = ['Ram'] if p.ram_level < 3 else []
        if p.ram_level:
            kinetic += [key for key, available in (('Afterburner', p.afterburner < 2), ('Bulwark', p.bulwark < 2)) if available]
        ballistic = ['Pierce'] if p.pierce_level < 3 else []
        if p.pierce_level:
            ballistic += [key for key, available in (('Rail', p.rail_level < 2), ('Overpenetration', p.overpenetration < 2)) if available]
        support = [key for key, available in (
            ('Damage', p.Damage < 24), ('AtakSpeade', p.shot_delay > 0.14001),
            ('MaxHp', p.MaxHp < p.TotalHp), ('LifeSteal', p.LifeSteal < 0.05999),
            ('speade', p.SpeedKef < 480)) if available]
        if (self.stage % 3 == 0 or self.boss) and p.KolBullet < 3:
            support = ['KolBullet']
        return [random.choice(pool) for pool in (kinetic, ballistic, support) if pool] + ['Repair']

    def upgrade_rank(self, kind):
        fields = {'Ram': ('ram_level', 3), 'Afterburner': ('afterburner', 2), 'Bulwark': ('bulwark', 2),
                  'Pierce': ('pierce_level', 3), 'Rail': ('rail_level', 2), 'Overpenetration': ('overpenetration', 2)}
        if kind in fields:
            field, maximum = fields[kind]
            return ' [%d/%d]' % (getattr(self.player, field) + 1, maximum)
        return ''

    def finish_stage(self):
        if self.mode == 'boss_run':
            self.change_state('won' if self.stage == 3 * Boss.INTERVAL else 'boss_clear')
            return
        self.player.HP = min(self.player.MaxHp, self.player.HP + 5)
        self.base.repair(3)
        if self.boss:
            self.player.HP = min(self.player.MaxHp, self.player.HP + 30)
            self.base.repair(20)
        self.choices = self.available_upgrades()
        self.change_state('upgrade')

    def next_boss(self):
        self.player.HP = self.player.MaxHp
        self.base.repair(self.base.Max_Hp_base)
        self.player.dash_cooldown = self.player.dash_time = 0
        self.stage += Boss.INTERVAL
        self.begin_stage()

    def choose_upgrade(self, kind):
        if kind == 'Repair':
            self.player.HP = min(self.player.MaxHp, self.player.HP + 30)
            self.base.repair(25)
        else:
            self.player.upgrade(kind)
        bonus.play()
        self.stage += 1
        self.begin_stage()

    def lose(self):
        self.change_state('lost')
        dead.play()
        if self.mode == 'boss_run':
            return
        try:
            write_rec(user(self.name.strip(), self.score))
        except (OSError, ValueError, TypeError):
            self.notice = 'Score not saved; existing records kept'

    def burst(self, center, source, count=12, fragments=False):
        for _ in range(count):
            self.particles.add(Particle(*center, source, fragment=fragments))

    def collect(self, pickup):
        if pickup.type == 'Repair':
            self.base.repair(12)
        else:
            self.player.upgrade(pickup.type)
        pickup.kill()

    def damage_enemy(self, enemy, damage, source, ram=False, penetrating=False):
        if not enemy.vulnerable:
            return 0
        if enemy in self.hazards:
            dealt = min(enemy.Hp, damage)
            enemy.Hp -= damage
            if enemy.Hp <= 0:
                self.burst(enemy.rect.center, enemy.image, 12, fragments=True)
                enemy.kill()
            return dealt
        dealt = enemy.take_damage(damage, ram=ram, penetrating=penetrating) if enemy.is_boss else min(enemy.Hp, damage)
        if not enemy.is_boss:
            enemy.Hp -= dealt
        if dealt <= 0:
            return 0
        enemy.hit_flash = 0.1
        self.burst(enemy.rect.center if ram else source, enemy.image, 6, fragments=True)
        self.player.HP = min(self.player.MaxHp, self.player.HP + dealt * self.player.LifeSteal)
        if enemy.Hp <= 0:
            enemy.kill()
            self.resolved += 1
            self.score += enemy.Score
            self.burst(enemy.rect.center, enemy.image, 30, fragments=True)
            exp_sound.play()
            if ram and self.player.bulwark:
                self.player.HP = min(self.player.MaxHp, self.player.HP + 3 * self.player.bulwark)
            if enemy.is_boss:
                self.hazards.empty()
                self.enemy_bullets.empty()
                for escort in list(self.mobs):
                    if getattr(escort, 'summoned', False):
                        self.burst(escort.rect.center, escort.image, 12, fragments=True)
                        escort.kill()
            elif not getattr(enemy, 'summoned', False):
                self.dry_kills += 1
                if random.random() < 0.16 or self.dry_kills >= 7:
                    self.bonuses.add(Bonus(enemy.rect.center))
                    self.dry_kills = 0
        return dealt

    def update(self, dt):
        self.stage_time += dt
        self.player.update(dt, self)
        self.bullets.update(dt)
        self.enemy_bullets.update(dt)
        self.bonuses.update(dt, self.player)
        self.particles.update(dt)
        self.mobs.update(dt, self)
        self.hazards.update(dt, self)
        self.spawn_timer -= dt
        if not self.boss and self.spawned < self.wave_size and self.spawn_timer <= 0:
            slots = max(2, round(min(14, 4 + self.stage // 2) * self.difficulty['count'])) - len(self.mobs)
            count = min(2 + self.stage // 4, slots, self.wave_size - self.spawned)
            lanes = random.sample(range(60, W - 30, 80), min(count, 7))
            for lane in lanes:
                self.mobs.add(Mob(self.stage, lane=lane, difficulty=self.difficulty))
                self.spawned += 1
            self.spawn_timer = max(0.6, 1.15 - self.stage * 0.025)
        for bullet in list(self.bullets):
            targets = list(self.mobs) + [hazard for hazard in self.hazards if hazard.kind == 'mine']
            hits = sorted((target for target in targets if bullet.intersects(target)),
                          key=lambda target: bullet.previous_pos.distance_squared_to(target.rect.center))
            for enemy in hits:
                if not enemy.alive():
                    continue
                self.burst(bullet.pos, bullet.image, 7)
                dealt = self.damage_enemy(enemy, bullet.damage, bullet.pos, penetrating=bullet.piercing)
                bullet.hit_targets.add(enemy)
                bullet.remaining_hits -= 1
                if bullet.remaining_hits <= 0:
                    bullet.kill()
                    break
                if dealt:
                    bullet.damage *= bullet.retention
        for enemy in list(self.mobs):
            if not enemy.alive():
                continue
            if pygame.sprite.collide_circle(self.player, enemy):
                if self.player.ram_level:
                    if enemy not in self.player.ram_cooldowns:
                        self.player.ram_cooldowns[enemy] = 0.65
                        damage = self.player.ram_damage * (2.2 if self.player.dash_time else 1)
                        self.damage_enemy(enemy, damage, enemy.rect.center, ram=True)
                    if enemy.alive():
                        self.player.hurt(enemy.damage * self.difficulty['damage'] * (1 - self.player.ram_guard))
                else:
                    self.player.hurt(enemy.damage * self.difficulty['damage'])
                    if not enemy.is_boss:
                        enemy.kill()
                        self.resolved += 1
                        self.burst(enemy.rect.center, enemy.image, 30, fragments=True)
            elif not enemy.is_boss and enemy.rect.bottom >= self.base.rect.top:
                self.base.Hp_base = max(0, self.base.Hp_base - (12 if enemy.type == 2 else 8) * self.difficulty['damage'])
                enemy.kill()
                self.resolved += 1
                self.burst(enemy.rect.center, enemy.image, 30, fragments=True)
        for bullet in pygame.sprite.spritecollide(self.player, self.enemy_bullets, True, pygame.sprite.collide_circle):
            self.player.hurt(bullet.damage * self.difficulty['damage'])
        for hazard in self.hazards:
            if hazard.collides(self.player):
                self.player.hurt(hazard.damage * self.difficulty['damage'])
        for pickup in pygame.sprite.spritecollide(self.player, self.bonuses, True, pygame.sprite.collide_circle):
            self.collect(pickup)
            bonus.play()
        if self.player.HP <= 0 or self.base.Hp_base <= 0:
            self.lose()
        elif self.spawned == self.wave_size and not self.mobs:
            self.clear_timer += dt
            if self.clear_timer >= 0.75:
                for pickup in list(self.bonuses):
                    self.collect(pickup)
                self.enemy_bullets.empty()
                self.hazards.empty()
                self.finish_stage()

    def add_button(self, text, y, action, x=125, width=400, height=50):
        index = len(self.buttons)
        rect = Button(width, height).draw(self.screen, x, y, text, font(25), index == self.focus)
        self.buttons.append((rect, action))

    def title(self, title, subtitle=''):
        draw_text(self.screen, title, 48, W / 2, 130)
        if subtitle:
            draw_text(self.screen, subtitle, 21, W / 2, 195, (130, 175, 195))

    def draw_play(self):
        self.screen.blit(self.base.image, self.base.rect)
        self.hazard_surface.fill((0, 0, 0, 0))
        for hazard in self.hazards:
            hazard.draw(self.hazard_surface)
        self.screen.blit(self.hazard_surface, (0, 0))
        self.bonuses.draw(self.screen)
        self.bullets.draw(self.screen)
        self.mobs.draw(self.screen)
        for enemy in self.mobs:
            if enemy.hit_flash:
                flash = enemy.image.copy()
                flash.fill((110, 110, 110, 0), special_flags=pygame.BLEND_RGBA_ADD)
                self.screen.blit(flash, enemy.rect)
            if not enemy.vulnerable:
                pygame.draw.ellipse(self.screen, (90, 170, 245), enemy.rect.inflate(12, 12), 2)
            elif not enemy.is_boss:
                if 0 < enemy.shot_timer < 0.28:
                    pygame.draw.circle(self.screen, (255, 170, 85), enemy.rect.midbottom, 10, 2)
                    if enemy.type == 5 and enemy.aim.length_squared():
                        end = enemy.pos + enemy.aim.normalize() * 260
                        pygame.draw.line(self.screen, (155, 65, 95), enemy.pos, end, 2)
                if enemy.type == 4 and 0 < enemy.dive_timer < 0.4:
                    end = enemy.pos + enemy.dive_direction * 160
                    pygame.draw.line(self.screen, (255, 100, 160), enemy.pos, end, 2)
            if not enemy.is_boss and enemy.Hp < enemy.max_hp:
                bar(self.screen, enemy.rect.centerx - 22, enemy.rect.top - 8, 44,
                    enemy.Hp, enemy.max_hp, (240, 150, 100), 4)
        if self.boss and self.boss.alive() and self.boss.action == 'idle' and self.boss.shot_timer < 0.3:
            pygame.draw.circle(self.screen, (255, 180, 100), self.boss.rect.midbottom, 18, 3)
        if self.boss and self.boss.alive() and self.boss.enraged:
            pygame.draw.circle(self.screen, (255, 210, 130), self.boss.pos,
                               12 + int(self.boss.age * 8) % 6, 3)
        if self.boss and self.boss.alive() and self.boss.shielded:
            pygame.draw.ellipse(self.screen, (185, 135, 255), self.boss.rect.inflate(24, 24), 4)
            for escort in self.mobs:
                if getattr(escort, 'summoned', False):
                    pygame.draw.line(self.screen, (135, 90, 190), escort.pos, self.boss.pos, 2)
        self.enemy_bullets.draw(self.screen)
        self.particles.draw(self.screen)
        tail = self.player.rect.midbottom
        flame = 16 + int(self.visual_time * 40) % 12
        pygame.draw.polygon(self.screen, (45, 120, 185), [(tail[0] - 9, tail[1] - 10),
                            (tail[0] + 9, tail[1] - 10), (tail[0], tail[1] + flame)])
        pygame.draw.polygon(self.screen, (130, 240, 255), [(tail[0] - 4, tail[1] - 10),
                            (tail[0] + 4, tail[1] - 10), (tail[0], tail[1] + flame // 2)])
        if not self.player.invulnerable or int(self.player.invulnerable * 12) % 2 == 0:
            self.screen.blit(self.player.image, self.player.rect)
        if self.player.ram_level:
            pygame.draw.circle(self.screen, (255, 185, 90), self.player.pos, 27 + self.player.ram_level * 3, 2)
            if self.player.dash_time:
                direction = self.player.dash_direction
                side = direction.rotate(90) * 22
                pygame.draw.polygon(self.screen, (255, 215, 120), [self.player.pos + direction * 55,
                    self.player.pos + side + direction * 18, self.player.pos - side + direction * 18], 3)
        if self.player.invulnerable:
            pygame.draw.circle(self.screen, (110, 235, 230), self.player.rect.center, 33, 2)
        pygame.draw.rect(self.screen, (10, 18, 32), (0, 0, W, 100))
        draw_text(self.screen, self.tr('HULL %d/%d') % (self.player.HP, self.player.MaxHp), 19, 110, 9)
        draw_text(self.screen, self.tr('BASE %d') % self.base.Hp_base, 19, 310, 9)
        draw_text(self.screen, self.tr('LV %d  |  %d') % (self.stage, self.score), 22, 525, 9)
        bar(self.screen, 20, 38, 180, self.player.HP, self.player.MaxHp, (80, 220, 165))
        bar(self.screen, 230, 38, 160, self.base.Hp_base, 100, (95, 170, 245))
        bar(self.screen, 430, 38, 195, self.player.dash_delay - self.player.dash_cooldown, self.player.dash_delay, (180, 150, 255))
        draw_text(self.screen, self.tr('SHIFT: DASH') if self.player.dash_cooldown == 0 else self.tr('DASH RECHARGING'), 17, 525, 57)
        draw_text(self.screen, self.tr('RAM %d/3 / PIERCE %d/3') % (self.player.ram_level, self.player.pierce_level), 14, 210, 80, (170, 200, 210))
        draw_text(self.screen, self.tr(LABELS[self.difficulty_name]), 14, 525, 80, (145, 175, 195))
        if self.boss:
            if self.mode == 'boss_run':
                draw_text(self.screen, 'BOSS RUN %d/3' % (self.stage // Boss.INTERVAL), 18, 120, 60)
            draw_text(self.screen, self.tr('%s / PHASE %d') % (self.tr(self.boss.name), self.boss.phase), 22, W / 2, 105, (255, 135, 140))
            bar(self.screen, 95, 137, W - 190, self.boss.Hp, self.boss.max_hp, (240, 85, 115))
            pygame.draw.line(self.screen, (255, 220, 220), (W // 2, 137), (W // 2, 149), 2)
            status = 'PHASE SHIFT' if self.boss.action == 'transition' else 'DESTROY THE ESCORTS' if self.boss.shielded else 'CORE EXPOSED' if self.boss.action == 'recover' else self.boss.last_attack.upper()
            draw_text(self.screen, self.tr(status), 17, W / 2, 154, (255, 205, 130))
        else:
            draw_text(self.screen, self.tr('WAVE %d / %d') % (self.resolved, self.wave_size), 18, 120, 60)
            bar(self.screen, 230, 65, 160, self.resolved, self.wave_size, (240, 195, 100), 6)
        if self.stage_time < 1.0:
            draw_text(self.screen, self.tr('BOSS INCOMING') if self.boss else self.tr('WAVE %d') % self.stage, 42, W / 2, 350)
        elif not self.mobs and self.spawned == self.wave_size and self.bonuses:
            draw_text(self.screen, self.tr('WAVE CLEAR'), 25, W / 2, 350)

    def draw(self):
        self.buttons = []
        self.screen.blit(background, (0, 0))
        for x, y, speed in self.stars:
            sy = int((y + self.visual_time * speed) % H)
            color = (65 + speed, 90 + speed, 140 + speed)
            pygame.draw.line(self.screen, color, (x, sy), (x, sy + max(1, speed // 22)))
        if self.state in ('play', 'pause', 'lost', 'upgrade', 'boss_clear', 'won'):
            self.draw_play()
        if self.state != 'play':
            shade = pygame.Surface((W, H), pygame.SRCALPHA)
            shade.fill((4, 12, 25, 220))
            self.screen.blit(shade, (0, 0))
        if self.state == 'menu':
            self.title(self.tr('GHOST OF SPACE'), self.tr('DEFEND THE LAST OUTPOST'))
            for i, (label, state) in enumerate(((self.tr('PLAY'), 'name'), ('BOSS RUN', 'boss_setup'), (self.tr('SCORES'), 'scores'), (self.tr('OPTIONS'), 'options'), (self.tr('HOW TO PLAY'), 'help'))):
                self.add_button(label, 330 + i * 65, lambda state=state: self.change_state(state))
            self.add_button(self.tr('EXIT'), 665, self.quit)
            draw_text(self.screen, self.tr('A boss awaits every 5 levels'), 22, W / 2, 750)
        elif self.state == 'name':
            self.title(self.tr('PILOT NAME'), self.tr('Up to 12 characters / Enter to launch'))
            draw_text(self.screen, self.name or self.tr('Pilot'), 40, W / 2, 335)
            self.add_button(self.tr('DIFFICULTY: ') + self.tr(LABELS[self.settings['difficulty']]), 440, lambda: self.adjust('difficulty', 0))
            self.add_button(self.tr('LAUNCH'), 510, lambda: self.start('normal'))
            self.add_button(self.tr('BACK'), 640, lambda: self.change_state('menu'))
        elif self.state == 'boss_setup':
            self.title('BOSS RUN', self.tr('Three bosses in a row / Choose a ready build'))
            for i, (kind, label) in enumerate((('Ram', 'RAM BUILD'), ('Pierce', 'PIERCING BUILD'), ('Hybrid', 'HYBRID BUILD'))):
                self.add_button(self.tr(label), 330 + i * 70, lambda kind=kind: self.start('boss_run', kind))
            self.add_button(self.tr('DIFFICULTY: ') + self.tr(LABELS[self.settings['difficulty']]), 570, lambda: self.adjust('difficulty', 0))
            draw_text(self.screen, self.tr('Full repair between bosses / No high scores'), 21, W / 2, 650)
            self.add_button(self.tr('BACK'), 730, lambda: self.change_state('menu'))
        elif self.state == 'options':
            self.title(self.tr('OPTIONS'), self.tr('Changes are saved automatically'))
            self.add_button(self.tr('MUSIC -'), 300, lambda: self.adjust('music', -0.1), 70, 230)
            self.add_button(self.tr('MUSIC +'), 300, lambda: self.adjust('music', 0.1), 350, 230)
            draw_text(self.screen, '%d%%' % round(self.settings['music'] * 100), 24, W / 2, 360)
            self.add_button(self.tr('SFX -'), 415, lambda: self.adjust('effects', -0.1), 70, 230)
            self.add_button(self.tr('SFX +'), 415, lambda: self.adjust('effects', 0.1), 350, 230)
            draw_text(self.screen, '%d%%' % round(self.settings['effects'] * 100), 24, W / 2, 475)
            self.add_button(self.tr('AUTOFIRE: ') + (self.tr('ON') if self.settings['autofire'] else self.tr('OFF')), 535, lambda: self.adjust('autofire', 0))
            self.add_button(self.tr('SHIP TEXTURES'), 600, lambda: self.change_state('textures'))
            self.add_button(self.tr('LANGUAGE: ENGLISH'), 665, lambda: self.adjust('language', 0))
            self.add_button(self.tr('DIFFICULTY: ') + self.tr(LABELS[self.settings['difficulty']]), 730, lambda: self.adjust('difficulty', 0))
            self.add_button(self.tr('BACK'), 810, lambda: self.change_state('menu'))
        elif self.state == 'textures':
            self.title(self.tr('SHIP TEXTURES'), self.tr('Cosmetic only / Same stats for every ship'))
            skin = skin_img[self.settings['skin']]
            preview = pygame.transform.scale(skin, (180, round(180 * skin.get_height() / skin.get_width())))
            self.screen.blit(preview, preview.get_rect(center=(W / 2, 390)))
            draw_text(self.screen, self.tr('SHIP %d / %d') % (self.settings['skin'] + 1, len(skin_img)), 28, W / 2, 510)
            if self.settings['skin'] >= 6:
                draw_text(self.screen, self.tr(('KESTREL', 'BASTION')[self.settings['skin'] - 6]), 22, W / 2, 550)
            self.add_button(self.tr('< PREVIOUS'), 585, lambda: self.adjust('skin', -1), 65, 245)
            self.add_button(self.tr('NEXT >'), 585, lambda: self.adjust('skin', 1), 340, 245)
            self.add_button(self.tr('BACK'), 730, lambda: self.change_state('options'))
        elif self.state == 'scores':
            self.title(self.tr('HIGH SCORES'), self.tr('Your original records are preserved'))
            for i, (score, name) in enumerate(self.records):
                draw_text(self.screen, '%d. %s    %d' % (i + 1, name[:12], score), 28, W / 2, 285 + i * 48)
            if not self.records:
                draw_text(self.screen, self.tr('No scores yet'), 30, W / 2, 390)
            self.add_button(self.tr('BACK'), 760, lambda: self.change_state('menu'))
        elif self.state == 'help':
            self.title(self.tr('HOW TO PLAY'))
            lines = [self.tr('WASD / ARROWS - move'), self.tr('SPACE - fire / SHIFT - dash'), self.tr('ESC / P - pause'),
                     self.tr('Protect your ship AND the base'), self.tr('Escaped enemies damage the base'),
                     self.tr('Ram hull + Shift: armored impact'), self.tr('Piercing rounds hit several ships'),
                     self.tr('Shoot mines; dash through shockwaves'), self.tr('Bosses change attacks at half health'),
                     self.tr('Menus: arrows / Enter / mouse')]
            for i, line in enumerate(lines):
                draw_text(self.screen, line, 23, W / 2, 260 + i * 43)
            self.add_button(self.tr('BACK'), 760, lambda: self.change_state('menu'))
        elif self.state == 'pause':
            self.title(self.tr('PAUSED'), self.tr('The battle waits for you'))
            self.add_button(self.tr('CONTINUE'), 360, lambda: self.change_state('play'))
            self.add_button(self.tr('RESTART'), 430, self.start)
            self.add_button(self.tr('MAIN MENU'), 500, lambda: self.change_state('menu'))
            draw_text(self.screen, self.tr('RAM %d/3 / PIERCE %d/3') % (self.player.ram_level, self.player.pierce_level), 25, W / 2, 620)
            draw_text(self.screen, self.tr('DASH RAM: 2.2X CONTACT DAMAGE'), 20, W / 2, 670)
        elif self.state == 'lost':
            self.title(self.tr('MISSION FAILED'), self.tr('Base destroyed') if self.base.Hp_base <= 0 else self.tr('Ship destroyed'))
            draw_text(self.screen, self.tr('LEVEL %d  /  SCORE %d') % (self.stage, self.score), 32, W / 2, 300)
            self.add_button(self.tr('RETRY [R]'), 400, self.start)
            self.add_button(self.tr('MAIN MENU'), 470, lambda: self.change_state('menu'))
        elif self.state in ('boss_clear', 'won'):
            self.title(self.tr('BOSS RUN COMPLETE') if self.state == 'won' else self.tr('BOSS DEFEATED'),
                       self.tr('All three bosses defeated') if self.state == 'won' else self.tr('Full repair before the next fight'))
            draw_text(self.screen, '%d / 3' % (self.stage // Boss.INTERVAL), 42, W / 2, 300)
            if self.state == 'boss_clear':
                self.add_button(self.tr('NEXT BOSS'), 400, self.next_boss)
            else:
                self.add_button(self.tr('RETRY [R]'), 400, self.start)
            self.add_button(self.tr('MAIN MENU'), 470, lambda: self.change_state('menu'))
        elif self.state == 'upgrade':
            self.title(self.tr('LEVEL %d CLEAR') % self.stage, self.tr('Choose one upgrade for the next wave'))
            for i, kind in enumerate(self.choices):
                title, description = UPGRADES[kind]
                self.add_button('%d. %s%s' % (i + 1, self.tr(title), self.upgrade_rank(kind)), 285 + i * 125, lambda kind=kind: self.choose_upgrade(kind))
                draw_text(self.screen, self.tr(description), 21, W / 2, 345 + i * 125)
            draw_text(self.screen, self.tr('HULL %d/%d  /  BASE %d') % (self.player.HP, self.player.MaxHp, self.base.Hp_base), 24, W / 2, 815)
        if self.notice:
            draw_text(self.screen, self.tr(self.notice), 18, W / 2, H - 55, (255, 180, 135))
        if self.state not in ('play', 'name'):
            draw_text(self.screen, self.tr('ARROWS + ENTER  /  ESC TO BACK'), 17, W / 2, H - 30, (120, 155, 175))

    def quit(self):
        self.running = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.state == 'play':
            self.movement_keys.add(getattr(event, 'scancode', 0))
        elif event.type == pygame.KEYUP:
            self.movement_keys.discard(getattr(event, 'scancode', 0))
        if event.type == pygame.QUIT:
            self.quit()
        elif event.type == pygame.WINDOWFOCUSLOST and self.state == 'play':
            self.change_state('pause')
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.state != 'play':
            for rect, action in self.buttons:
                if rect.collidepoint(event.pos):
                    menu_svap.play()
                    action()
                    break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                back = {'play': 'pause', 'pause': 'play', 'textures': 'options', 'upgrade': 'upgrade'}
                self.change_state(back.get(self.state, 'menu'))
            elif self.state == 'play' and event.key == pygame.K_p:
                self.change_state('pause')
            elif self.state == 'name':
                if event.key == pygame.K_RETURN:
                    self.start('normal')
                elif event.key == pygame.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif event.unicode.isprintable() and event.unicode and len(self.name) < 12:
                    self.name += event.unicode
            elif self.state in ('lost', 'won') and event.key == pygame.K_r:
                self.start()
            elif self.state == 'upgrade' and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                index = event.key - pygame.K_1
                if index < len(self.choices):
                    self.choose_upgrade(self.choices[index])
            elif self.state != 'play' and self.buttons:
                if event.key in (pygame.K_DOWN, pygame.K_RIGHT, pygame.K_TAB):
                    self.focus = (self.focus + 1) % len(self.buttons)
                elif event.key in (pygame.K_UP, pygame.K_LEFT):
                    self.focus = (self.focus - 1) % len(self.buttons)
                elif event.key == pygame.K_RETURN:
                    self.buttons[self.focus][1]()

    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000, 0.05)
            if self.state != 'pause':
                self.visual_time += dt
            self.draw()
            previous = self.state
            for event in pygame.event.get():
                self.handle_event(event)
            if self.state == 'play' and previous == 'play':
                self.update(dt)
            pygame.display.flip()
        pygame.quit()


def draw_menu():
    Game().run()


if __name__ == '__main__':
    draw_menu()
