from . import Gui
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
import logging


logger = logging.getLogger(__name__)


class Curses(Gui):
    """TerminalGui is a Gui """

    BABA = "Y"

    def __init__(self, game_map):
        """ 
        :param GameMap game_map: The actual GameMap instance to display
        """
        self.game_map = game_map
        self.actions = {}
        self._worker = None

    def start(self):
        """ Start GUI and event loop """
        curses.initscr()
        curses.noecho()
        curses.curs_set(0)
        curses.wrapper(self._event_loop)

    def _event_loop(self, stdscr):
        """ Gui event loop """
        self.win = curses.newwin(1+self.game_map.width+1, 1+self.game_map.height+1, 0, 0)
        self.win.keypad(1)
        self.win.border(0)
        self.win.nodelay(1)
        self.update()
        while True:
            self.win.border(0)
            self.win.addstr(0, 2, 'BABAISYOU')
            self.win.timeout(1)

            event = self.win.getch()
            if event == -1:
                continue
            key = event

            try:
                action = self.actions[key]
            except KeyError:
                print(f"no action for key : {key}")
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
                else:
                    self.win.addch(x+1, y+1, self.BABA)

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
        curses.echo()
        curses.nocbreak()
        curses.endwin()