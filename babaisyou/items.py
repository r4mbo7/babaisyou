""" Items used in game """
from babaisyou.actions import Action
import logging


class Item:
    """ Item of the game """

    def __init__(self, posx, posy, rule=False, you=False):
        self.posx = posx  # position on map
        self.posy = posy
        self.vectx = 0  # next move vector
        self.vecty = 0
        # actions on collision
        self.actions = []
        self.rule = rule  # item is a rule
        if self.rule:
            self.actions = [Action.load("Push")]
        self.you = you  # item is you
        self.players = set([])  # players ids owning the object
        self.win = False  # party is win
        self.dead = False  # item is dead

    def set_rules(self, rules, game_map):
        """ Rules with self involved
            'Self is Item' with Item.rule True
        """
        # reset actions
        logging.debug(f"set rules on {self.__class__.__name__}")
        self.actions = set([])
        self.you = False
        self.players = set([])
        for rule in rules:
            logging.debug(f"{rule.__class__.__name__}")
            apply_actions = getattr(rule, "apply_actions", lambda rule: None)
            apply_actions(self)
            # rule is rule
            self.you |= any([isinstance(you, rule.__class__)
                             for you in game_map.get_items(Item)
                             if you.you])
            for item in game_map.get_items(Item):
                if isinstance(item, rule.__class__):
                    self.players = self.players.union(item.players)
        logging.debug(f"Rules for {self.__class__.__name__}(you={self.you}, players={self.players})\nActions={self.actions}")


class Baba(Item):
    pass


class Cucu(Item):
    pass


class Flag(Item):
    pass


class Wall(Item):
    pass


class Rule(Item):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.actions = [Action.load("Push")]
        self.rule = True

    def apply_actions(self, item):
        pass


class Is(Rule):
    pass


class You(Rule):

    def apply_actions(self, item):
        logging.debug(f"{item.__class__.__name__} is you")
        if not item.rule:
            item.you = True


class Player(Rule):

    def set_player_id(self, player_id):
        self.player_id = player_id
        # self.is_client = lambda : self.you = client_id == self.player_id
        self.is_you = lambda item: False
        logging.debug(f"Load Player{player_id}")

    def apply_actions(self, item):
        logging.debug(f"{item.__class__.__name__} is p{self.player_id}")
        if not item.rule:
            item.players.add(self.player_id)
        logging.debug(f"Is you is {self.is_you(self)}")
        self.you = self.is_you(self)


class Win(Rule):

    def apply_actions(self, item):
        item.actions.add(Action.load("Win"))


class Push(Rule):

    def apply_actions(self, item):
        if Action.load("Stop") in item.actions:
            item.actions.remove(Action.load("Stop"))
        else:
            item.actions.add(Action.load("Push"))


class Stop(Rule):

    def apply_actions(self, item):
        if Action.load("Push") in item.actions:
            item.actions.remove(Action.load("Push"))
        else:
            item.actions.add(Action.load("Stop"))


class Dead(Rule):

    def apply_actions(self, item):
        item.actions.add(Action.load("Dead"))
