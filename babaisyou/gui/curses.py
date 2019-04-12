from . import Gui
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import asyncio
from items import *
import logging

logger = logging.getLogger(__name__)

colors = {
    "white": (0, curses.COLOR_WHITE, curses.COLOR_BLACK),
    "white2": (1, curses.COLOR_BLACK, curses.COLOR_WHITE),
    "red": (2, curses.COLOR_RED, curses.COLOR_BLACK),
    "red2": (3, curses.COLOR_RED, curses.COLOR_WHITE),
    "blue": (4, curses.COLOR_BLUE, curses.COLOR_BLACK),
    "blue2": (5, curses.COLOR_BLUE, curses.COLOR_WHITE),
    "green": (6, curses.COLOR_GREEN, curses.COLOR_BLACK),
    "green2": (7, curses.COLOR_GREEN, curses.COLOR_WHITE),
    "yellow": (8, curses.COLOR_YELLOW, curses.COLOR_BLACK),
    "yellow2": (9, curses.COLOR_YELLOW, curses.COLOR_WHITE),
    "pink": (10, curses.COLOR_RED, curses.COLOR_BLACK),
    "pink2": (11, curses.COLOR_RED, curses.COLOR_WHITE),
}

items_repr = {
    You: {
        "letter": "Y",
        "color": "white"
    },
    Is: {
        "letter": "I",
        "color": "red"
    },
    Push: {
        "letter": "P",
        "color": "blue"
    },
    Win: {
        "letter": "W",
        "color": "yellow"
    },
    Baba: {
        "letter": "B",
        "color": "pink"
    },
    Flag: {
        "letter": "F",
        "color": "yellow"
    },
    Wall: {
        "letter": "W",
        "color": "blue"
    }
}


class Curses(Gui):
    """TerminalGui is a Gui """

    def __init__(self, game_map):
        """ 
        :param GameMap game_map: The actual GameMap instance to display
        """
        self.game_map = game_map
        self.color = {}
        self.actions = {}
        self.gui_loop = None
        self.loop = asyncio.get_event_loop()
        self.over = False

    def _curses_init(self):
        """ initialise curese stuff """
        curses.initscr()
        curses.noecho()
        curses.curs_set(0)
        # Initialise colors
        curses.start_color()
        curses.use_default_colors()
        for name, color in colors.items():
            curses.init_pair(*color)
            self.color[name] = curses.color_pair(color[0])
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
        self.winrules.addstr(0, 0, "Good luck :)")
        line = 1
        for item, rep in items_repr.items():
            line += 1
            self.winrules.addstr(line % 10, 1,
                                 f"{rep['letter']} : {item.__name__}",
                                 self.color[rep["color"]+"2"])
        self.winrules.refresh()

        self.win = curses.newwin(1+self.game_map.height+1,
                                 1+self.game_map.width+1,
                                 0, 0)
        self.win.keypad(1)
        self.win.border(0)
        self.win.nodelay(1)
        self.update()
        while not self.over:
            self.win.border(0)
            self.win.addstr(0, 2, 'BABAISYOU!', self.color["white"])
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
                try:
                    el_repr = items_repr[el.__class__]
                except KeyError:
                    self.win.addch(x+1, y+1, ' ')
                else:
                    color = el_repr["color"]
                    if el.rule:
                        color += "2"
                    self.win.addstr(x+1, y+1,
                                    el_repr["letter"],
                                    self.color[color])

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
