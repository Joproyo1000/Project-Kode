import pygame


class Player:
    def __init__(self):
        self.pos = [0, 0]
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], 32, 32)

    @property
    def x(self):
        return self.pos[0]
    @property
    def y(self, x):
        self.pos[1] = x

    def tp(self, x, y):
        self.pos = [x, y]
