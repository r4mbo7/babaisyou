import asyncio
import logging
from gui.curses import Curses
from items import *

logger = logging.getLogger(__name__)


dipacth = {
    "y": lambda x, y: You(x, y),
    "i": lambda x, y: Is(x, y, rule=True),
    "x": lambda x, y: Win(x, y),
    "p": lambda x, y: Push(x, y),
    "b": lambda x, y: Baba(x, y, rule=True),
    "B": lambda x, y: Baba(x, y, you=True),
    "w": lambda x, y: Wall(x, y, rule=True),
    "W": lambda x, y: Wall(x, y),
    "f": lambda x, y: Flag(x, y, rule=True),
    "F": lambda x, y: Flag(x, y),
}


class GameMap:
    """ GameMap is a matrice """

    def __init__(self, width=24, height=24):
        self.width = width
        self.height = height
        self.maps = self.empty_map

    @classmethod
    def create(cls, path):
        width = 0
        height = 0
        items = []
        with open(path, 'r') as file:
            wid = 1
            while True:
                char = file.read(1)
                if not char:  # end of file
                    break
                elif char == "\n":  # end of line
                    width = max(width, wid)
                    wid = 0
                    height += 1
                elif char == " ":
                    pass
                else:
                    items.append(dipacth[char](wid, height))
                wid += 1
        game_map = cls(width, height)
        game_map.set_items(items)
        return game_map

    @property
    def empty_map(self):
        return [[None for _ in range(self.height)] for _ in range(self.width)]

    def set_items(self, items):
        """ Update map with given items """
        self.maps = self.empty_map
        for item in items:
            self.maps[item.posx][item.posy] = item

    def get_items(self, cls=None):
        """ List of items on map """
        cls = cls or Item
        return [item
                for col in self.maps
                for item in col
                if isinstance(item, cls)]
