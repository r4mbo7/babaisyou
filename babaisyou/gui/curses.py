import asyncio
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import logging

from babaisyou.items import *
from . import Gui

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
    "cyan": (10, curses.COLOR_CYAN, curses.COLOR_BLACK),
    "cyan2": (11, curses.COLOR_CYAN, curses.COLOR_WHITE),
    "maganta": (12, curses.COLOR_MAGENTA, curses.COLOR_BLACK),
    "maganta2": (13, curses.COLOR_MAGENTA, curses.COLOR_WHITE),
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
    Dead: {
        "letter": "D",
        "color": "red"
    },
    Push: {
        "letter": "P",
        "color": "blue"
    },
    Stop: {
        "letter": "S",
        "color": "blue"
    },
    Win: {
        "letter": "W",
        "color": "yellow"
    },
    Baba: {
        "letter": "B",
        "color": "white"
    },
    Cucu: {
        "letter": "C",
        "color": "maganta"
    },
    Flag: {
        "letter": "F",
        "color": "yellow"
    },
    Wall: {
        "letter": "W",
        "color": "blue"
    },
    Player: {
        "color": "cyan",
        "letter": "0"
    },
}


class Curses(Gui):
    """TerminalGui is a Gui """

    def __init__(self):
        self._app = None
        self.color = {}
        self.actions = {}
        self.gui_loop = None
        self.loop = asyncio.get_event_loop()
        self.over = False

    def set_app(self, app):
        """ Default app use """
        self._app = app
        self.register_actions(self._app.quit,
                              self._app.move_up,
                              self._app.move_down,
                              self._app.move_left,
                              self._app.move_right,
                              self._app.retry)

    @property
    def game_map(self):
        return self._app.game_map

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
        self.gui_loop = asyncio.ensure_future(self.worker())

    async def worker(self):
        """ Gui event loop """
        self.header = curses.newwin(10, 30, 0, 0)
        self.update_header()
        self.header.refresh()

        self.side = curses.newwin(20, 30, 0, 1+self.game_map.width+1)
        self.update_rules()
        self.side.refresh()

        self.body = curses.newwin(1+self.game_map.height+1,
                                  1+self.game_map.width+1,
                                  1, 0)
        self.body.keypad(1)
        self.body.border(0)
        self.body.nodelay(1)
        self.update()
        while not self.over:
            await asyncio.sleep(0)
            self.body.border(0)
            self.body.timeout(1)

            event = self.body.getch()
            if event == -1:
                continue
            key = event

            try:
                action = self.actions[key]
            except KeyError:
                logger.info(f"no action for key : {key}")
                continue

            await action()
            self.update()

    def update_header(self):
        self.header.addstr(0, 1, " ← ↑ ↓ → r esc ")

    def update_rules(self):
        player_id = None
        for player in self.game_map.get_items(Player):
            if player.is_you(player.player_id):
                player_id = player.player_id
        if player_id:
            self.side.addstr(0, 0, f"You are player {player_id}",
                             self.color["cyan"])
        self.side.addstr(1, 0, "Rules")
        line = 1
        for item, rep in items_repr.items():
            line += 1
            self.side.addstr(line % 20, 1,
                             f"{rep['letter']} : {item.__name__}",
                             self.color[rep["color"]+"2"])

    def update(self):
        """ Refresh screen """
        for y, col in enumerate(self.game_map.maps):
            for x, el in enumerate(col):
                try:
                    el_repr = items_repr[el.__class__]
                except KeyError:
                    self.body.addch(x+1, y+1, ' ')
                else:
                    color = el_repr["color"]
                    letter = el_repr["letter"]
                    if el.rule:
                        color += "2"
                    if isinstance(el, Player):
                        letter = str(el.player_id)
                    self.body.addstr(x+1, y+1,
                                     letter,
                                     self.color[color])
        self.update_header()
        self.update_rules()

    def party_end(self, win):
        """ Party over

        :param bool win: user win or not
        """
        if win:
            print("You win !")
        else:
            print("You loose :(")
        self.body.refresh()

    def register_actions(self, quit, up, down, left, right, retry):
        """ Callback when user did an action """
        self.actions = {
            27: quit,
            KEY_UP: up,
            KEY_DOWN: down,
            KEY_LEFT: left,
            KEY_RIGHT: right,
            114: retry,
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
            if self.gui_loop is not None:
                await self.gui_loop
        except asyncio.CancelledError:
            pass
