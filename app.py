import pygame as pg

from src.map import Map
from src.player import Player


class Main_game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((800, 600))
        pg.display.set_caption("Hello World")
        self.running = True

        self.player = Player()

        self.overworld_map = Map(name="overworld", player=self.player)
        self.maps = {"overworld": self.overworld_map}

        self.current_map = "overworld"

    def update(self):
        for event in pg.event.get():  # permet de recuperer les evenements (genre appuit des touches ect)
            if event.type == pg.QUIT:
                self.running = False

    def draw(self):
        self.screen.fill((0, 0, 0))
        pg.display.flip()

    def run(self):

        while self.running:
            self.update()
            self.draw()

        pg.quit()


if __name__ == "__main__":
    game = Main_game()
    game.run()
