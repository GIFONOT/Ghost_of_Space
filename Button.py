import pygame
import main
from Presets import Click, menu_svap


class Button:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        # self.col1 = col1
        # self.col1 = col2

    def draw(self, screen, x, y, text, activ=True, ex=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < x + self.w and y < mouse[1] < y + self.h:

            pygame.draw.rect(screen, (23, 204, 58), (x, y, self.w, self.h), 0, 10)
            main.draw_text(screen, text, 30, x + 100, y + 6)

            #menu_svap.play()

            #pygame.time.delay(300)

            if click[0] == 1:
                #Click.play()
                menu_svap.play()
                pygame.time.delay(300)

                if ex is not None:
                    ex()
                if activ:
                    activ = False
                    return activ
        else:
            pygame.draw.rect(screen, (23, 204, 58), (x, y, self.w, self.h), 5, 10)
            main.draw_text(screen, text, 30, x + 100, y + 6)

        #main.draw_text(screen, text, 30, x + 100, y + 6)
        activ = True
        return activ
