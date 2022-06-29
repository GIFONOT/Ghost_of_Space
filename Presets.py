from os import path
import pygame


pygame.mixer.init()


# загрузка файлов
img_dir = path.join(path.dirname(__file__), 'Png')
sound_dir = path.join(path.dirname(__file__), 'Sound')

# текстуры
background = pygame.image.load(path.join(img_dir, 'BackGround.png'))
background = pygame.transform.scale(background, (750, 950))
background_rect = background.get_rect()

powerup_img = {}
powerup_img['HP'] = pygame.image.load(path.join(img_dir, 'HP.png'))
#powerup_img['HP'] = pygame.transform.scale(powerup_img['HP'], (70, 70))

powerup_img['LifeSteal'] = pygame.image.load(path.join(img_dir, 'Vampir.png'))
powerup_img['LifeSteal'] = pygame.transform.scale(powerup_img['LifeSteal'], (30, 30))

powerup_img['MaxHp'] = pygame.image.load(path.join(img_dir, 'Max_HP.png'))
powerup_img['MaxHp'] = pygame.transform.scale(powerup_img['MaxHp'], (30, 30))

powerup_img['Damage'] = pygame.image.load(path.join(img_dir, 'Damage.png'))
powerup_img['Damage'] = pygame.transform.scale(powerup_img['Damage'], (30, 30))

powerup_img['AtakSpeade'] = pygame.image.load(path.join(img_dir, 'AtakSpeade.png'))
powerup_img['AtakSpeade'] = pygame.transform.scale(powerup_img['AtakSpeade'], (30, 30))

powerup_img['speade'] = pygame.image.load(path.join(img_dir, 'speade.png'))
powerup_img['speade'] = pygame.transform.scale(powerup_img['speade'], (30, 30))

leg_powerup_img = {}
leg_powerup_img['KolBullet'] = pygame.image.load(path.join(img_dir, 'leg2.png'))




exp_img = {}
exp_img['Mob_Boom'] = []
exp_img['G'] = []
i = 0
g = 0

skin_img = []
skin_img.append(pygame.image.load(path.join(img_dir, 'somm.png')))
skin_img.append(pygame.image.load(path.join(img_dir, 'somm2.png')))
skin_img.append(pygame.image.load(path.join(img_dir, 'somm3.png')))
skin_img.append(pygame.image.load(path.join(img_dir, 'somm4.png')))
skin_img.append(pygame.image.load(path.join(img_dir, 'somm5.png')))
skin_img.append(pygame.image.load(path.join(img_dir, 'somm6.png')))




# звуки
shoot_sound = pygame.mixer.Sound(path.join(sound_dir, 'pew.mp3'))
pygame.mixer.Sound.set_volume(shoot_sound, 0.1)

boom_sound = pygame.mixer.Sound(path.join(sound_dir, 'expl6.wav'))
pygame.mixer.Sound.set_volume(boom_sound, 0.1)

boomPlaer_sound = pygame.mixer.Sound(path.join(sound_dir, 'expl3.wav'))
pygame.mixer.Sound.set_volume(boomPlaer_sound, 0.1)

dead = pygame.mixer.Sound(path.join(sound_dir, 'Dark souls - You Died_(EEMUSIC.ru).mp3'))
pygame.mixer.Sound.set_volume(dead, 0.09)

bonus = pygame.mixer.Sound(path.join(sound_dir, 'sfx_shieldUp.ogg'))
pygame.mixer.Sound.set_volume(bonus, 1)

exp_sound = pygame.mixer.Sound(path.join(sound_dir, 'rumble1.ogg'))
pygame.mixer.Sound.set_volume(exp_sound, 0.1)

pygame.mixer.music.load(path.join(sound_dir, 'ost_fighter.ogg'))
#pygame.mixer.Sound.set_volume(music, 0.01)



Click = pygame.mixer.Sound(path.join(sound_dir, 'click_001.ogg'))
#pygame.mixer.Sound.set_volume(music, 0.06)

puk = pygame.mixer.Sound(path.join(sound_dir, 'cartoon-bubble-pop-01-.mp3'))

menu_svap = pygame.mixer.Sound(path.join(sound_dir, 'sfx_keypress.wav'))