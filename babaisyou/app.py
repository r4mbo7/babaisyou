import asyncio
from gui.curses import Curses
import logging


logger = logging.getLogger(__name__)


class GameMap:
    """ GameMap is a matrice """

    def __init__(self, width=24, height=24):
        self.maps = [[None for _ in range(width)] for _ in range(height)]

    @property
    def height(self):
        return len(self.maps)

    @property
    def width(self):
        return len(self.maps[0])

    @property
    def babas(self):
        return [(el, x, y)
                for x, col in enumerate(self.maps)
                for y, el in enumerate(col)
                if isinstance(el, Baba)]

    def debug(self):
        import pprint
        maps = pprint.pformat(self.maps, width=160)
        logger.debug(maps)


class Baba(object):
    """ A Baba"""

    def __init__(self):
        pass


class App:
    """ App contain rules and handle GUI """

    def __init__(self, gui, game_map):
        self.gui = gui
        self.game_map = game_map
        self._close = None

    @classmethod
    async def create(cls, settings=None):
        """ do the setup to create an app and it's required objects

        :returns: App
        """
        game_map = GameMap()
        baba = Baba()
        game_map.maps[1][1] = baba
        gui = Curses(game_map)
        app = cls(gui, game_map)
        gui.register_actions(app.quit,
                             app.move_up,
                             app.move_down,
                             app.move_left,
                             app.move_right)
        return app

    def quit(self):
        """ User hit the 'quit' """
        logger.debug("quit")
        self.close()

    def move_up(self):
        """ The user want to move """
        logger.debug("move_up")
        for baba, x, y in self.game_map.babas:
            self.game_map.maps[x][(y-1) % self.game_map.height] = baba
            self.game_map.maps[x][y] = None
        self.game_map.debug()

    def move_down(self):
        """ The user want to move """
        logger.debug("move_down")
        for baba, x, y in self.game_map.babas:
            self.game_map.maps[x][(y+1) % self.game_map.height] = baba
            self.game_map.maps[x][y] = None
        self.game_map.debug()

    def move_left(self):
        """ The user want to move """
        logger.debug("move_left")
        for baba, x, y in self.game_map.babas:
            self.game_map.maps[(x-1) % self.game_map.width][y] = baba
            self.game_map.maps[x][y] = None
        self.game_map.debug()

    def move_right(self):
        """ The user want to move """
        logger.debug("move_right")
        for baba, x, y in self.game_map.babas:
            self.game_map.maps[(x+1) % self.game_map.width][y] = baba
            self.game_map.maps[x][y] = None
        self.game_map.debug()

    def start(self):
        """ Start the App """
        self._close = asyncio.Future()
        self.gui.start()

    def close(self):
        """ Clean app """
        self.gui.close()
        if self._close:
            self._close.set_result(None)

    async def wait_closed(self):
        await self._close
