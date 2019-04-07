import asyncio
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

    def get_entities(self, cls):
        """ List of entities with their position """
        return [(el, x, y)
                for x, col in enumerate(self.maps)
                for y, el in enumerate(col)
                if isinstance(el, cls)]

    def debug(self):
        import pprint
        maps = pprint.pformat(self.maps, width=160)
        logger.debug(maps)


class Baba:
    pass


class Flag:
    pass


class App:
    """ App contain rules and handle GUI """

    def __init__(self, gui, game_map):
        self.gui = gui
        self.game_map = game_map
        self._close_future = asyncio.Future()

    @classmethod
    async def create(cls, settings=None):
        """ do the setup to create an app and it's required objects

        :returns: App
        """
        from gui.curses import Curses
        game_map = GameMap()
        baba = Baba()
        flag = Flag()
        game_map.maps[1][1] = baba
        game_map.maps[3][3] = flag
        gui = Curses(game_map)
        app = cls(gui, game_map)
        gui.register_actions(app.quit,
                             app.move_up,
                             app.move_down,
                             app.move_left,
                             app.move_right)
        return app

    def do_move(self, move):
        """ apply move and rules """
        is_win = False
        flags = self.game_map.get_entities(Flag)
        for you, src, dst in move:
            s_x, s_y = src
            d_x, d_y = dst
            if any([d_x == x and d_y == y for _, x, y in flags]):
                is_win = True
                continue
            self.game_map.maps[s_x][s_y] = None
            self.game_map.maps[d_x][d_y] = you
        if is_win:
            logger.info("You win !")
            self.quit()

    def quit(self):
        """ Quit the game """
        logger.debug("quit")
        self.close()

    def move_up(self):
        """ The user want to move """
        logger.debug("move_up")
        self.do_move([(baba, (x, y), (x, (y-1) % self.game_map.height))
                      for baba, x, y in self.game_map.get_entities(Baba)])

    def move_down(self):
        """ The user want to move """
        logger.debug("move_down")
        self.do_move([(baba, (x, y), (x, (y+1) % self.game_map.height))
                      for baba, x, y in self.game_map.get_entities(Baba)])

    def move_left(self):
        """ The user want to move """
        logger.debug("move_left")
        self.do_move([(baba, (x, y), ((x-1) % self.game_map.width, y))
                      for baba, x, y in self.game_map.get_entities(Baba)])

    def move_right(self):
        """ The user want to move """
        logger.debug("move_right")
        self.do_move([(baba, (x, y), ((x+1) % self.game_map.width, y))
                      for baba, x, y in self.game_map.get_entities(Baba)])

    async def start(self):
        """ Start the App """
        await self.gui.start()

    def close(self):
        """ Clean app """
        self.gui.close()
        self._close_future.set_result(None)

    async def wait_closed(self):
        await self.gui.wait_closed()
        await self._close_future
