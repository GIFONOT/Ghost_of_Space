import pygame


class Button:
    def __init__(self, w, h):
        self.w, self.h = w, h

    def draw(self, screen, x, y, text, font, selected=False):
        rect = pygame.Rect(x, y, self.w, self.h)
        hover = rect.collidepoint(pygame.mouse.get_pos()) or selected
        pygame.draw.rect(screen, (28, 68, 83) if hover else (15, 30, 45), rect, border_radius=10)
        pygame.draw.rect(screen, (100, 235, 210) if hover else (50, 85, 105), rect, 2, border_radius=10)
        label = font.render(text, True, (230, 245, 250))
        if label.get_width() > self.w - 24:
            ratio = (self.w - 24) / label.get_width()
            label = pygame.transform.smoothscale(label, (self.w - 24, round(label.get_height() * ratio)))
        screen.blit(label, label.get_rect(center=rect.center))
        return rect
