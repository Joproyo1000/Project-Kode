import pygame as pg

class Main_game :
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((800, 600))
        pg.display.set_caption("Hello World")
        self.running = True

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
            self.screen.fill((0, 0, 0))
            pg.display.flip()
        pg.quit()



if __name__ == "__main__":
    game = Main_game()
    game.run()