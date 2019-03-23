from abc import ABC
import pprint


class Gui(ABC):
    """ Interfarce for Gui """

    def print_map(self, game_map):
        """ display map to user

        :param GameMap game_map: The actual GameMap instance to display
        """
        raise NotImplementedError


class TerminalGui(Gui):
    """TerminalGui is a Gui """

    def print_map(self, game_map):
        pprint.pprint(game_map.maps)


class GameMap:
    """ GameMap is a matrice """

    def __init__(self, width=12, length=12):
        self.maps = [[0 for _ in range(width)] for _ in range(length)]


class App:
    """ App contain rules and handle GUI """

    def __init__(self, gui, game_map):
        self.gui = gui
        self.game_map = game_map

    @classmethod
    async def create(cls, settings=None):
        """ do the setup to create an app and it's required objects

        :returns: App
        """
        return cls(TerminalGui(), GameMap())

    def start(self):
        """ Start the App

        :FIXME: Takes inputs from Gui
        """
        while True:
            user_input = input("Action? (p, stop, ...) ")
            if user_input == "p":
                self.gui.print_map(self.game_map)
            elif user_input == "stop":
                break
            else:
                print("???")
