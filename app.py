import pygame as pg

from src.map import Map
from src.player import Player



class Main_game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((800, 600))
        pg.display.set_caption("Hello World")
        self.clock = pg.time.Clock()
        self.running = True

        self.player = Player()

        self.overworld_map = Map(name="overworld", player=self.player)
        self.maps = {"overworld": self.overworld_map}

        self.current_map = "overworld"

    def update(self):
        for event in pg.event.get():  # permet de recuperer les evenements (genre appuit des touches ect)
            if event.type == pg.QUIT:
                self.running = False
        keys = pg.key.get_pressed()
        # Adjust player position based on key presses
        if keys[pg.K_LEFT]:
            self.player.move(-1, 0)
        if keys[pg.K_RIGHT]:
            self.player.move(1, 0)
        if keys[pg.K_UP]:
            self.player.move(0, -1)
        if keys[pg.K_DOWN]:
            self.player.move(0, 1)
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.player.Draw(self.screen)
        pg.display.flip()

    def run(self):

        while self.running:
            self.update()
            self.draw()
            self.clock.tick(60)

        pg.quit()


if __name__ == "__main__":
    game = Main_game()
    game.run()
