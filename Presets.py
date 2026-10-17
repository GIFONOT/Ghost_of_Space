from functools import lru_cache
import pygame
from Setting import W, H
from Paths import ROOT

img_dir = str(ROOT / 'Png')
pygame.font.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass


@lru_cache(maxsize=None)
def image(name):
    loaded = pygame.image.load(str(ROOT / 'Png' / name))
    return loaded if name == 'background-nebula.png' else loaded.subsurface(loaded.get_bounding_rect()).copy()


@lru_cache(maxsize=8)
def pixel_sprite(name, width, grid=32):
    source = image(name)
    source = source.subsurface(source.get_bounding_rect(min_alpha=128))
    height = max(1, round(source.get_height() * grid / source.get_width()))
    pixels = pygame.transform.scale(source, (grid, height))
    return pygame.transform.scale(pixels, (width, max(1, round(width * height / grid))))


class Sound:
    def __init__(self, name, volume=0.2):
        self.volume = volume
        self.sound = pygame.mixer.Sound(str(ROOT / 'Sound' / name)) if pygame.mixer.get_init() else None

    def play(self):
        if self.sound:
            self.sound.play()

    def stop(self):
        if self.sound:
            self.sound.stop()

    def set_volume(self, volume):
        if self.sound:
            self.sound.set_volume(volume * self.volume)


background = pygame.transform.scale(image('background-nebula.png'), (W, H))
background_rect = background.get_rect()
skin_img = [image(name) for name in ('somm.png', 'somm2.png', 'somm3.png', 'somm4.png', 'somm5.png', 'somm6.png')]
skin_img += [pixel_sprite(name, 96) for name in ('ship-kestrel.png', 'ship-bastion.png')]
powerup_img = {key: pygame.transform.scale(image(filename), (30, 30)) for key, filename in {
    'HP': 'HP.png', 'MaxHp': 'Max_HP.png', 'LifeSteal': 'Vampir.png',
    'Damage': 'Damage.png', 'AtakSpeade': 'AtakSpeade.png', 'speade': 'speade.png',
}.items()}
leg_powerup_img = {'KolBullet': image('leg2.png')}
exp_img = {'Mob_Boom': [], 'G': []}
shoot_sound = Sound('pew.mp3', 0.12)
boom_sound = Sound('expl6.wav')
boomPlaer_sound = Sound('expl3.wav')
dead = Sound('Dark souls - You Died_(EEMUSIC.ru).mp3', 0.12)
bonus = Sound('sfx_shieldUp.ogg', 0.4)
exp_sound = Sound('rumble1.ogg')
Click = Sound('click_001.ogg')
puk = Sound('cartoon-bubble-pop-01-.mp3', 0.1)
menu_svap = Sound('sfx_keypress.wav')
sounds = [shoot_sound, boom_sound, boomPlaer_sound, dead, bonus, exp_sound, Click, puk, menu_svap]
if pygame.mixer.get_init():
    pygame.mixer.music.load(str(ROOT / 'Sound' / 'ost_fighter.ogg'))


def set_audio(music, effects):
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(music)
    for sound in sounds:
        sound.set_volume(effects)
