import pygame


class Player:
    def __init__(self):
        self.pos = [50, 50]
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], 32, 32)
        self.speed = 5
    @property #Ca sert à quoi ?
    def x(self):
        return self.pos[0]
    @property #Ca aussi ?
    def y(self, x):
        self.pos[1] = x

    def tp(self, x, y):
        self.pos = [x, y]

    def move(self, dx, dy):
        self.pos[0]+= dx*self.speed
        self.pos[1]+= dy*self.speed
        self.rect.x, self.rect.y = self.pos[0], self.pos[1]
    def Draw(self,surface):
        pygame.draw.rect(surface,(255,0,0),self.rect)
