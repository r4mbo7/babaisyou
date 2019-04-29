import asyncio
import logging
from babaisyou.gui.curses import Curses
from babaisyou.items import *

logger = logging.getLogger(__name__)


dipacth = {
    "y": lambda x, y: You(x, y, rule=True),
    "i": lambda x, y: Is(x, y, rule=True),
    "x": lambda x, y: Win(x, y, rule=True),
    "p": lambda x, y: Push(x, y, rule=True),
    "s": lambda x, y: Stop(x, y, rule=True),
    "d": lambda x, y: Dead(x, y, rule=True),
    "w": lambda x, y: Wall(x, y, rule=True),
    "b": lambda x, y: Baba(x, y, rule=True),
    "c": lambda x, y: Cucu(x, y, rule=True),
    "f": lambda x, y: Flag(x, y, rule=True),
    "B": lambda x, y: Baba(x, y),
    "C": lambda x, y: Cucu(x, y),
    "W": lambda x, y: Wall(x, y),
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
                    item = dipacth.get(char)
                    if item is not None:
                        items.append(item(wid, height))
                    else:# item is player
                        item = Player(wid, height, rule=True)
                        item.set_player_id(int(char))
                        items.append(item)
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
