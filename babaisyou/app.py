import asyncio
import logging
from babaisyou.gui.curses import Curses
from babaisyou.items import *
from babaisyou.maps import GameMap

logger = logging.getLogger(__name__)


class App:
    """ App contain rules and handle GUI """

    def __init__(self, map_name, game_map, items, gui):
        self.map_name = map_name
        self.game_map = game_map
        self.items = items
        self.gui = gui
        self.read_rules()
        self._close_future = asyncio.Future()
        self.party_win = None

    @classmethod
    async def create(cls, map_name="maps/default.txt"):
        game_map = GameMap.create(map_name)
        items = game_map.get_items()
        gui = Curses()
        app = cls(map_name, game_map, items, gui)
        gui.set_app(app)
        return app

    @staticmethod
    def are_rules(item1, item2):
        if item1 is None or item2 is None:
            return False
        return item1.rule and item2.rule

    def read_rules(self):
        """ parse map and set active rules to items """
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
        logger.debug(
            f"rules {[(r1.__class__.__name__, 'is', r2.__class__.__name__) for r1, r2 in rules]}")
        # update items with set rules
        for item in self.items:
            if item.rule:
                pass
            else:
                item_rules = []
                for r1, r2 in rules:
                    if isinstance(item, r2.__class__):
                        item_rules.append(r1)
                    if isinstance(item, r1.__class__):
                        item_rules.append(r2)
                item.set_rules(item_rules, self.game_map)

        self.game_map.set_items(self.items)

    async def do_move(self):
        """ apply move and rules """
        # compute move
        for moving in [item for item in self.items if item.vectx != 0 or item.vecty != 0]:
            d_x = (moving.posx+moving.vectx) % self.game_map.width
            d_y = (moving.posy+moving.vecty) % self.game_map.height
            item = self.game_map.maps[d_x][d_y]
            if item is not None:
                for action in item.actions:
                    action(self.game_map).apply(moving, item)

        # apply move
        def move_item(item):
            if item.dead:
                return None
            item.posx = (item.posx+item.vectx) % self.game_map.width
            item.posy = (item.posy+item.vecty) % self.game_map.height
            item.vectx = 0
            item.vecty = 0
            return item
        self.items = list(filter(None, map(move_item, self.items)))
        self.game_map.set_items(self.items)
        if any([item.win for item in self.items]):
            logger.info("You win !")
            self.party_win = True
        elif all([not item.you for item in self.items]):
            logger.info("You loose !")
            self.party_win = False
        else:
            # re-set rules
            self.read_rules()
        self.update_gui()

    def update_gui(self):
        if self.party_win is None:
            self.gui.update()
        else:
            logger.info("You loose !")
            self.gui.party_end(win=self.party_win)

    async def quit(self, info="quit"):
        """ Quit the game """
        logger.info("quit")
        self.close()

    async def retry(self):
        """ The user want to retry """
        logger.info("retry")
        self.game_map = GameMap.create(self.map_name)
        self.read_rules()
        self.party_win = None

    async def move_up(self, fn=lambda x: x.you):
        """ The user want to move """
        logger.debug("move_up")
        for item in filter(fn, self.items):
            item.vecty = -1
        await self.do_move()

    async def move_down(self, fn=lambda x: x.you):
        """ The user want to move """
        logger.debug("move_down")
        for item in filter(fn, self.items):
            item.vecty = +1
        await self.do_move()

    async def move_left(self, fn=lambda x: x.you):
        """ The user want to move """
        logger.debug("move_left")
        for item in filter(fn, self.items):
            item.vectx = -1
        await self.do_move()

    async def move_right(self, fn=lambda x: x.you):
        """ The user want to move """
        logger.debug("move_right")
        for item in filter(fn, self.items):
            item.vectx = 1
        await self.do_move()

    async def start(self):
        """ Start the App """
        await self.gui.start()

    def close(self):
        """ Clean app """
        self.gui.close()
        if not self._close_future.done():
            self._close_future.set_result(None)

    async def wait_closed(self):
        await self._close_future
        await self.gui.wait_closed()
