import asyncio
import logging
from gui.curses import Curses
from items import *
from maps import GameMap

logger = logging.getLogger(__name__)


class App:
    """ App contain rules and handle GUI """

    MAP = "maps/default.txt"

    def __init__(self):
        self.game_map = GameMap.create(self.MAP)
        self.read_rules()
        self.gui = Curses(self)
        self.gui.register_actions(self.quit,
                             self.move_up,
                             self.move_down,
                             self.move_left,
                             self.move_right,
                             self.retry)
        self._close_future = asyncio.Future()

    @property
    def items(self):
        return self.game_map.get_items()

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
        logger.debug(f"rules {[(r1.__class__.__name__, 'is', r2.__class__.__name__) for r1, r2 in rules]}")
        # set rules
        for item in self.items:
            if not item.rule:
                item_rules = []
                for r1, r2 in rules:
                    if isinstance(item, r2.__class__):
                        item_rules.append(r1)
                    if isinstance(item, r1.__class__):
                        item_rules.append(r2)
                item.set_rules(item_rules)

    def do_move(self, move):
        """ apply move and rules """
        is_win = False
        for you, d_x, d_y in move:
            item = self.game_map.maps[d_x][d_y]
            if item is None:
                # simple move
                logger.debug("move")
                you.posx = d_x
                you.posy = d_y
            else:
                logger.debug(f"collisition with {item.__class__}")
                is_win |= any([action(self.game_map).apply(you, item)
                               for action in item.actions])
        self.game_map.set_items(self.items)
        if is_win:
            logger.info("You win !")
            self.quit()
        else:
            # re-set rules
            self.read_rules()

    def quit(self):
        """ Quit the game """
        logger.info("quit")
        self.close()

    def retry(self):
        """ The user want to retry """
        logger.info("retry")
        self.game_map = GameMap.create(self.MAP)
        self.read_rules()

    def move_up(self):
        """ The user want to move """
        self.do_move([(item, item.posx, (item.posy-1) % self.game_map.height)
                      for item in self.game_map.get_items(Item)
                      if item.you])

    def move_down(self):
        """ The user want to move """
        self.do_move([(item, item.posx, (item.posy+1) % self.game_map.height)
                      for item in self.game_map.get_items(Item)
                      if item.you])

    def move_left(self):
        """ The user want to move """
        self.do_move([(item, (item.posx-1) % self.game_map.width, item.posy)
                      for item in self.game_map.get_items(Item)
                      if item.you])

    def move_right(self):
        """ The user want to move """
        self.do_move([(item, (item.posx+1) % self.game_map.width, item.posy)
                      for item in self.game_map.get_items(Item)
                      if item.you])

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
