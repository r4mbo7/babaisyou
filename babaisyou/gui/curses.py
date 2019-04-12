from . import Gui
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import asyncio
from app import Baba, Flag
import logging

logger = logging.getLogger(__name__)


class Curses(Gui):
    """TerminalGui is a Gui """

    YOU = "Y"
    YOU_COLOR = 0
    FLAG = "F"
    FLAG_COLOR = 4

    def __init__(self, game_map):
        """ 
        :param GameMap game_map: The actual GameMap instance to display
        """
        self.game_map = game_map
        self.actions = {}
        self.gui_loop = None
        self.loop = asyncio.get_event_loop()
        self.over = False

    def _curses_init(self):
        """ initialise curese stuff """
        curses.initscr()
        curses.noecho()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(0, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_WHITE)
        if curses.can_change_color():
            logger.debug("terminal can change color")
        else:
            logger.debug("terminal can not change color")

    async def start(self):
        """ Start GUI and event loop """
        self._curses_init()
        self.gui_loop = asyncio.ensure_future(
            self.loop.run_in_executor(None,
                                      lambda: curses.wrapper(self._event_loop))
        )

    def _event_loop(self, stdscr):
        """ Gui event loop """
        self.winrules = curses.newwin(10, 30, 0, 1+self.game_map.width+1)
        self.winrules.bkgd(' ', curses.color_pair(0))
        self.winrules.addstr(0, 0, "RULES")
        self.winrules.addstr(2, 1, "Y : You", curses.color_pair(0))
        self.winrules.addstr(3, 1, "F : Flag", curses.color_pair(4))
        self.winrules.refresh()

        self.win = curses.newwin(1+self.game_map.width+1,
                                 1+self.game_map.height+1,
                                 0, 0)
        self.win.keypad(1)
        self.win.border(0)
        self.win.nodelay(1)
        self.update()
        while not self.over:
            self.win.border(0)
            self.win.addstr(0, 2, 'BABAISYOU!', curses.color_pair(2))
            self.win.timeout(1)

            event = self.win.getch()
            if event == -1:
                continue
            key = event

            try:
                action = self.actions[key]
            except KeyError:
                logger.info(f"no action for key : {key}")
                continue

            action()
            self.update()

    def update(self):
        """ Refresh screen """
        for y, col in enumerate(self.game_map.maps):
            for x, el in enumerate(col):
                if el is None:
                    self.win.addch(x+1, y+1, ' ')
                elif isinstance(el, Baba):
                    self.win.addch(x+1, y+1, self.YOU, curses.color_pair(self.YOU_COLOR))
                elif isinstance(el, Flag):
                    self.win.addch(x+1, y+1, self.FLAG, curses.color_pair(self.FLAG_COLOR))

    def register_actions(self, quit, up, down, left, right):
        """ Callback when user did an action """
        self.actions = {
            27: quit,
            KEY_UP: up,
            KEY_DOWN: down,
            KEY_LEFT: left,
            KEY_RIGHT: right,
        }

    def close(self):
        """ Clean """
        self.over = True
        if self.gui_loop is not None and not self.gui_loop.cancelled():
            self.gui_loop.cancel()
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        logger.debug("Gui closed")

    async def wait_closed(self):
        """ Wait until gui loop is over """
        try:
            await self.gui_loop
        except asyncio.CancelledError:
            pass
