""" Items used in game """


class Item:
    """ Item of the game """
    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy


class Baba(Item):
    pass


class Flag(Item):
    pass


class Wall(Item):
    pass
