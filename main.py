import pygame

from CSV_Scores import user, write_rec, giv_rec
from OprepCol import ge_col
from Setting import H, W, FPS
from Presets import background, background_rect, exp_sound, bonus, \
    boomPlaer_sound, dead, puk
import sys
from Mob import Mob
import Player
from Structur import Base
import random
from Bonus import Bonus, LegBonus
from Button import Button
from Particle import Particle
from os import path
from Presets import img_dir

# user32 = ctypes.windll.user32
# screensize = user32.GetSystemMetrics(0)W, user32.GetSystemMetrics(1)H

global runMenu, Pause, mus
runMenu, Pause, mus = True, True, True

all_sprites = pygame.sprite.Group()

mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
bons = pygame.sprite.Group()
leg_bons = pygame.sprite.Group()
particle = pygame.sprite.Group()
bulletMob = pygame.sprite.Group()

screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font('Shrift/Kenney Mini Square.ttf', size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_HP(surf, x, y, Hp, MaxHp, colour):
    BAR_LENGTH = MaxHp
    BAR_HEIGHT = 17
    fill = (Hp / MaxHp) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, colour, fill_rect, 0, 0)  # Hp
    pygame.draw.rect(surf, (255, 255, 255), outline_rect, 2, 0)


def draw_Score(surf, x, y, Score, W, colour):
    BAR_LENGTH = W
    BAR_HEIGHT = 22
    fill = (Score / W) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, colour, fill_rect, 0, 0)  # Hp
    pygame.draw.rect(surf, (146, 143, 99), outline_rect, 3, 0)
    pygame.draw.rect(surf, (199, 186, 150), outline_rect, 2, 0)


def fps(clock):
    font = pygame.font.Font('Shrift/Kenney Mini Square.ttf', 30)
    display_fps = str(int(clock.get_fps()))
    render = font.render(display_fps, True, (0, 255, 0))
    screen.blit(render, (5, 60))


def Exit():
    sys.exit()


def Lose():
    for item in all_sprites:
        item.kill()
    pres = pygame.key.get_pressed()
    screen.fill((0, 0, 0))
    dead.play()
    # screen.blit(background, background_rect)  # фон (2/10)
    draw_text(screen, "You lose, press (r) to restart", 30, W / 2, H / 2 - 50)
    draw_text(screen, "press (esc) to exit", 30, W / 2, H / 2 + 10)
    if pres[pygame.K_r]:
        dead.stop()
        run()
    if pres[pygame.K_ESCAPE]:
        sys.exit()


def pause():
    global Pause

    while Pause:
        pres = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # screen.fill((0, 0, 0))
        # screen.blit(background, background_rect)
        # all_sprites.draw(screen)

        # but = Button(200, 50)
        # Pause = but.draw(screen, W / 2 - 100, H / 2, "back menu", Pause, draw_menu)

        draw_text(screen, "PAUSED, press (enter) to continue", 30, W / 2, H / 2 - 50)

        # draw_text(screen, "Exit to menu (ESC)", 30, W / 2, H / 2)

        if pres[pygame.K_RETURN]:
            Pause = False
        '''if pres[pygame.K_ESCAPE]:
            Pause = False
            draw_menu()'''

        pygame.display.flip()
        clock.tick(FPS)


def music_volume():
    global mus

    def _nusic_vol():
        vol = pygame.mixer.music.get_volume()
        vol = round(vol, 1)
        if vol >= 0.1:
            pygame.mixer.music.set_volume(vol - 0.1)

    def nusic_vol():
        vol = pygame.mixer.music.get_volume()
        vol = round(vol, 1)
        if vol < 1:
            pygame.mixer.music.set_volume(vol + 0.1)

    while mus:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill((0, 0, 0))
        draw_text(screen, "options", 75, W / 2, 150)
        draw_text(screen, ". .", 80, W / 2, 200)
        draw_text(screen, "_", 80, W / 2, 220)

        vol = pygame.mixer.music.get_volume()
        print(vol)
        draw_text(screen, str(round(vol, 1)), 40, W - 170, 450)

        but = Button(200, 50)
        but.draw(screen, W / 2 - 100, H / 2 - 50, "+Vol", None, nusic_vol)

        but = Button(200, 50)
        but.draw(screen, W / 2 - 100, H / 2 + 10, "-Vol", None, _nusic_vol)

        but3 = Button(200, 50)
        but3.draw(screen, W / 2 - 100, H / 2 + 130, "back", None, setting)

        clock.tick(FPS)
        pygame.display.flip()


def setting():
    p = True
    while p:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill((0, 0, 0))

        draw_text(screen, "options", 75, W / 2, 150)
        draw_text(screen, ". .", 80, W / 2, 200)
        draw_text(screen, "_", 80, W / 2, 220)

        but = Button(200, 50)
        but.draw(screen, W / 2 - 100, H / 2 - 50, "Music", None, music_volume)

        but2 = Button(200, 50)
        but2.draw(screen, W / 2 - 100, H / 2 + 10, "textures", None, setting)

        but3 = Button(200, 50)
        but3.draw(screen, W / 2 - 100, H / 2 + 130, "back", None, draw_menu)

        clock.tick(FPS)
        pygame.display.flip()


def draw_name():
    global text
    t = True
    prov = False
    text = ''
    text_name = 'Name'
    tick = 50
    while t:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and prov:
                    run()
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 8:
                        text += event.unicode

        screen.fill((0, 0, 0))
        draw_text(screen, "PLAY", 75, W / 2, 150)
        draw_text(screen, ". .", 80, W / 2, 200)
        draw_text(screen, "_", 80, W / 2, 220)

        pygame.draw.rect(screen, (23, 204, 58), (W / 2 - 100 - 3, H / 2 + 45, 200, 5), 0, 10)

        if len(text) >= 2:
            draw_text(screen, 'enter', 50, W / 2, H / 2 + 80)
            prov = True

        tick -= 1
        if len(text) == 0:
            if tick >= 0:
                draw_text(screen, str(text_name), 30, W / 2, H / 2 + 10)
            if tick == -50:
                tick = 50
            if tick < -50:
                tick = 50
        else:
            draw_text(screen, str(text), 30, W / 2, H / 2 + 10)

        clock.tick(FPS)
        pygame.display.flip()


def scores():
    t = True
    people = giv_rec()
    size = len(people)
    while t:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill((0, 0, 0))

        draw_text(screen, "scores", 75, W / 2, 150)
        draw_text(screen, ". .", 80, W / 2, 200)
        draw_text(screen, "_", 80, W / 2, 220)

        draw_text(screen, str(people[1]), 30, W / 2, H / 2 - 50)
        draw_text(screen, "2", 30, W / 2, H / 2 + 10)
        draw_text(screen, "3", 30, W / 2, H / 2 + 70)
        draw_text(screen, "4", 30, W / 2, H / 2 + 130)
        draw_text(screen, "5", 30, W / 2, H / 2 + 190)

        but3 = Button(200, 50)
        but3.draw(screen, W / 2 - 100, H / 2 + 300, "back", None, draw_menu)

        clock.tick(FPS)
        pygame.display.flip()


def draw_menu():
    global runMenu
    pygame.init()
    pygame.display.set_caption("Ghost of Space")

    while runMenu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill((0, 0, 0))

        draw_text(screen, "Ghost of Space", 75, W / 2, 150)
        draw_text(screen, ". .", 80, W / 2, 200)
        draw_text(screen, "_", 80, W / 2, 220)

        but = Button(200, 50)
        but.draw(screen, W / 2 - 100, H / 2 - 50, "PLAY", None, draw_name)

        but2 = Button(200, 50)
        but2.draw(screen, W / 2 - 100, H / 2 + 10, "scores", None, scores)

        but2 = Button(200, 50)
        but2.draw(screen, W / 2 - 100, H / 2 + 70, "options", None, setting)

        but3 = Button(200, 50)
        but3.draw(screen, W / 2 - 100, H / 2 + 130, "exit", None, Exit)

        clock.tick(FPS)
        pygame.display.flip()


def run():
    # окно игры
    global run1, run2, end_game, kef_lv, Pause, runMenu, cgl
    run1 = True
    run2 = True
    end_game = True
    kef_lv = 1
    stage = 1
    score = 0
    total_scores = 0
    garant = 0
    Lv_up = 100

    pygame.init()
    pygame.display.set_caption("Ghost of Space")
    bg_color = (28, 28, 28)

    # спрайт игрока и БАЗЫ
    player = Player.Player()
    base = Base.Base()
    all_sprites.add(player)
    all_sprites.add(base)

    # появление мобов
    def NewBob():
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    N = 5
    for i in range(N):
        NewBob()

    # draw_menu()

    # главный цикл игры (событий)
    while end_game:
        # music.play(-1)
        while run1:
            clock.tick(FPS)

            pres = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            if pres[pygame.K_ESCAPE]:
                # pygame.time.delay(300)
                Pause = True
                runMenu = True
                pause()

            # Обновлениев
            all_sprites.update()
            # столкновение игрок моб
            hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
            for hit in hits:
                exp_sound.play()  # звук

                '''if hit.type == '1' or hit.type == '3':
                    cgl = 2
                elif hit.type == '2' or hit.type == '4':
                    cgl = 1'''

                png = ge_col(hit.png)
                for i in range(25):
                    p = Particle(hit.rect.centerx, hit.rect.centery, png, hit.setting)
                    particle.add(p)
                    all_sprites.add(p)
                player.HP -= hit.radius
                score += hit.Score - 5
                total_scores += hit.Score - 5
                garant += hit.Score - 5
                NewBob()

            # столкновение пуля моб
            hits = pygame.sprite.groupcollide(mobs, bullets, False, False, pygame.sprite.collide_circle)
            for hit in hits:
                hits = pygame.sprite.spritecollide(hit, bullets, True, pygame.sprite.collide_circle)
                for bb in hits:
                    png = ge_col(bb.png)
                    for i in range(25):
                        p = Particle(bb.rect.centerx, bb.rect.centery, png, 1)
                        particle.add(p)
                        all_sprites.add(p)
                    bb.kill()

                '''if hit.type == '4':
                    hit.image = pygame.image.load(path.join(img_dir, 'ino2svet.png'))
                if hit.type == '1':
                    hit.image = pygame.image.load(path.join(img_dir, 'ino4svet.png'))
                if hit.type == '3':
                    hit.image = pygame.image.load(path.join(img_dir, 'ino5svet.png'))
                if hit.type == '2':
                    hit.image = pygame.image.load(path.join(img_dir, 'ino3svet.png'))'''

                hit.Hp -= player.Damage
                if hit.Hp <= 0:
                    hit.kill()

                    '''if hit.type == '1' or hit.type == '3':
                        cgl = 2
                    elif hit.type == '2' or hit.type == '4':
                        cgl = 1'''

                    png = ge_col(hit.png)
                    for i in range(25):
                        p = Particle(hit.rect.centerx, hit.rect.centery, png, hit.setting)
                        particle.add(p)
                        all_sprites.add(p)

                    score += hit.Score
                    total_scores += hit.Score
                    garant += hit.Score

                    exp_sound.play()  # звук
                    # puk.play()
                    NewBob()
                    if random.randrange(1, 100) > 95 or garant == 100:
                        bon = Bonus.Bonus(hit.rect.center)
                        all_sprites.add(bon)
                        garant = 0
                        bons.add(bon)
                else:
                    # boom_sound.play()# звук
                    puk.play()

                if player.HP < player.MaxHp:
                    player.HP += player.LifeSteal * player.Damage
                if player.HP > player.MaxHp:
                    player.HP = player.MaxHp

            # пуля моба игрок
            hits = pygame.sprite.spritecollide(player, bulletMob, True, pygame.sprite.collide_circle)
            for hit in hits:
                exp_sound.play()  # звук
                # puk.play()
                player.HP -= 5

            # бонус игрок
            hits = pygame.sprite.spritecollide(player, bons, True, pygame.sprite.collide_circle)
            for hit in hits:
                bonus.play()
                if hit.type == 'LifeSteal':
                    player.LifeSteal += 0.02
                if hit.type == 'MaxHp':
                    player.MaxHp += 10
                    if player.MaxHp > player.TotalHp:
                        player.MaxHp = player.TotalHp
                if hit.type == 'HP':
                    player.HP += 20
                    if player.HP > player.MaxHp:
                        player.HP = player.MaxHp
                if hit.type == 'Damage':
                    player.Damage += 2
                if hit.type == 'AtakSpeade':
                    player.shot_delay -= 20
                if hit.type == 'speade':
                    player.SpeedKef += 0.1

            # база моб
            hits = pygame.sprite.spritecollide(base, mobs, True)
            for hit in hits:
                boomPlaer_sound.play()
                base.Hp_base -= 10
                NewBob()

            # Отрисовка
            screen.fill(bg_color)
            screen.blit(background, background_rect)
            fps(clock)

            # particle.draw(screen)
            all_sprites.draw(screen)
            '''pygame.draw.line(screen, (255, 255, 255), (player.rect.x, player.rect.y), (player.rect.x + W * math.cos(player.angle),
                                                     player.rect.y + W * math.sin(player.angle)), 2)'''

            if (score * ((W - 10) / Lv_up)) >= W - 10:
                draw_Score(screen, 5, 5, W - 10, W - 10, (34, 101, 217))
            if (score * ((W - 10) / Lv_up)) < W - 10:
                draw_Score(screen, 5, 5, (score * ((W - 10) / Lv_up)), W - 10, (34, 101, 217))

            draw_HP(screen, 30, 30, player.HP, player.MaxHp, (0, 205, 0))
            draw_HP(screen, 87, 50, base.Hp_base, base.Max_Hp_base, (255, 0, 0))

            draw_text(screen, "LV " + str(stage), 20, W - 50, 3)
            draw_text(screen, "HP", 20, 17, 25)
            draw_text(screen, "HP Base", 20, 45, 45)

            if score >= Lv_up:
                for item in all_sprites:
                    item.kill()

                bon = LegBonus.LegBonus((W / 4, H / 3))
                all_sprites.add(bon)
                player.rect.center = (W / 2, H / 1.2)
                all_sprites.add(player)
                leg_bons.add(bon)
                stage += 1
                run1 = False
                run2 = True

            if player.HP < 0 or base.Hp_base < 0:
                write_rec(user(text, total_scores))
                Lose()

            # end
            pygame.display.flip()

        while run2:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            all_sprites.update()

            hits = pygame.sprite.spritecollide(player, leg_bons, True, pygame.sprite.collide_circle)
            for hit in hits:
                bonus.play()
                if stage == 3 or stage == 6:
                    if hit.type == 'KolBullet':
                        player.KolBullet += 1

                for item in all_sprites:
                    item.kill()

                player.rect.center = (W / 2, H / 1.2)

                all_sprites.add(player)

                run1 = True
                run2 = False
                kef_lv += 1
                Lv_up += 130
                score = 0

                N += 5

                if stage == 2:
                    for i in range(N):
                        NewBob()
                if stage == 3:
                    for i in range(N):
                        NewBob()
                if stage == 4:
                    for i in range(N):
                        NewBob()
                if stage == 5:
                    for i in range(N):
                        NewBob()
                if stage == 6:
                    for i in range(N):
                        NewBob()
                if stage == 7:
                    for i in range(N):
                        NewBob()
                if stage == 8:
                    for i in range(N):
                        NewBob()
                if stage == 9:
                    for i in range(N):
                        NewBob()
                if stage == 10:
                    for i in range(N):
                        NewBob()
                if stage > 10:
                    for i in range(N):
                        NewBob()

            screen.fill(bg_color)
            all_sprites.draw(screen)
            if (score * ((W - 10) / Lv_up)) >= W - 10:
                draw_Score(screen, 5, 5, W - 10, W - 10, (255, 48, 48))
            if (score * ((W - 10) / Lv_up)) < W - 10:
                draw_Score(screen, 5, 5, (score * ((W - 10) / Lv_up)), W - 10, (255, 48, 48))

            draw_HP(screen, 30, 30, player.HP, player.MaxHp, (0, 205, 0))
            # draw_HP(screen, 8, 900, base.Hp_base, base.Max_Hp_base, (255, 0, 0))

            draw_text(screen, "LV " + str(stage - 1), 20, 700, 3)
            draw_text(screen, "HP", 20, 17, 25)

            pygame.display.flip()
