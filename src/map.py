from src.player import Player


class Map :
    def __init__(self, name, player=None):
        self._name = name
        self.player = player
        self.camera = [0, 0]

    def get_name(self):
        return self._name