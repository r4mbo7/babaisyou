import asyncio
import logging
from gui.curses import Curses
from items import *

logger = logging.getLogger(__name__)


class GameMap:
    """ GameMap is a matrice """

    def __init__(self, width=24, height=24):
        self.width = width
        self.height = height
        self.maps = self.empty_map

    @property
    def empty_map(self):
        return [[None for _ in range(self.width)] for _ in range(self.height)]

    def set_items(self, items):
        """ Update map with given items """
        self.maps = self.empty_map
        for item in items:
            self.maps[item.posx][item.posy] = item

    def get_items(self, cls):
        """ List of items on map """
        return [item
                for x, col in enumerate(self.maps)
                for y, item in enumerate(col)
                if isinstance(item, cls)]

    def debug(self):
        import pprint
        maps = pprint.pformat(self.maps, width=160)
        logger.debug(maps)


class App:
    """ App contain rules and handle GUI """

    def __init__(self, gui, items, game_map):
        self.gui = gui
        self.items = items
        self.game_map = game_map
        self._close_future = asyncio.Future()

    @classmethod
    async def create(cls, settings=None):
        """ do the setup to create an app and it's required objects

        :returns: App
        """
        game_map = GameMap()
        items = [
            Baba(1, 1),
            Wall(1, 2),
            Flag(3, 3),
            # rules
            Baba(0, 0, rule=True),
            Is(1, 0, rule=True),
            You(2, 0, rule=True),
            Wall(5, 0, rule=True),
            Is(6, 0, rule=True),
            Push(7, 0, rule=True),
            Flag(9, 10, rule=True),
            Is(10, 10, rule=True),
            Win(11, 10, rule=True),
        ]
        game_map.set_items(items)
        gui = Curses(game_map)
        app = cls(gui, items, game_map)
        gui.register_actions(app.quit,
                             app.move_up,
                             app.move_down,
                             app.move_left,
                             app.move_right)
        return app

    @staticmethod
    def are_rules(item1, item2):
        if item1 is None or item2 is None:
            return False
        return item1.rule and item2.rule

    def read_rules(self):
        rules = []
        for rule in self.game_map.get_items(Is):
            adjacent = [((rule.posx-1) % self.game_map.width, rule.posy,
                         (rule.posx+1) % self.game_map.width, rule.posy),
                        ((rule.posx, (rule.posy-1) % self.game_map.height,
                          rule.posx, (rule.posy+1) % self.game_map.height))]
            for i1x, i1y, i2x, i2y in adjacent:
                item1 = self.game_map.maps[i1x][i1y]
                item2 = self.game_map.maps[i2x][i2y]
                if self.are_rules(item1, item2):
                    rules.append((item1, item2))
        # set rules
        for item in self.items:
            # reset actions
            item.actions = []
            # set action accoring to the rules
            for i1r, i2r in rules:
                if isinstance(item, i1r.__class__) or isinstance(item, i2r.__class__):
                    item.actions.extend([i1r.ref_action, i2r.ref_action])

    def do_move(self, move):
        """ apply move and rules """
        is_win = False
        for you, d_x, d_y in move:
            item = self.game_map.maps[d_x][d_y]
            if item is None:
                # simple move
                you.posx = d_x
                you.posy = d_y
            else:
                is_win |= any([action(self.game_map).apply(you, item)
                               for action in item.actions])
        self.game_map.set_items(self.items)
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
        self.do_move([(baba, baba.posx, (baba.posy-1) % self.game_map.height)
                      for baba in self.game_map.get_items(Baba)])

    def move_down(self):
        """ The user want to move """
        logger.debug("move_down")
        self.do_move([(baba, baba.posx, (baba.posy+1) % self.game_map.height)
                      for baba in self.game_map.get_items(Baba)])

    def move_left(self):
        """ The user want to move """
        logger.debug("move_left")
        self.do_move([(baba, (baba.posx-1) % self.game_map.width, baba.posy)
                      for baba in self.game_map.get_items(Baba)])

    def move_right(self):
        """ The user want to move """
        logger.debug("move_right")
        self.do_move([(baba, (baba.posx+1) % self.game_map.width, baba.posy)
                      for baba in self.game_map.get_items(Baba)])

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
