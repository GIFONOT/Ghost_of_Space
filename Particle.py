from collections import Counter
from functools import lru_cache
import random
import pygame


@lru_cache(maxsize=128)
def debris(source):
    colors = Counter()
    fragments = []
    width, height = source.get_size()
    for x in range(width):
        for y in range(height):
            color = source.get_at((x, y))
            if color.a > 128:
                colors[tuple(color[:3])] += 1
                if x % 5 == 0 and y % 5 == 0:
                    rect = pygame.Rect(x, y, min(5, width - x), min(5, height - y))
                    fragments.append(source.subsurface(rect).copy())
    total = sum(colors.values())
    average = tuple(sum(color[c] * count for color, count in colors.items()) // total for c in range(3)) if total else (255, 255, 255)
    return (average, *(color for color, _ in colors.most_common(4))), fragments


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, source, fragment=False):
        super().__init__()
        colors, fragments = debris(source)
        if fragment and fragments:
            self.image = pygame.transform.scale(random.choice(fragments), (7, 7))
            self.image = pygame.transform.rotate(self.image, random.randrange(360))
        else:
            size = random.randint(2, 5)
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            self.image.fill(random.choice(colors))
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-210, 210), random.uniform(-210, 210))
        self.duration = self.life = random.uniform(0.25, 0.65)

    def update(self, dt):
        self.pos += self.velocity * dt
        self.velocity *= max(0, 1 - 1.8 * dt)
        self.rect.center = self.pos
        self.life -= dt
        if self.life <= 0:
            self.kill()
        else:
            self.image.set_alpha(round(255 * self.life / self.duration))
