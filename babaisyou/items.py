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
        self.p1 = False  # item is p1
        self.p2 = False  # item is p2
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
        for item in rules:
            logging.debug(f"{item.__class__.__name__}")
            apply_actions = getattr(item, "apply_actions", lambda item: None)
            apply_actions(self)
            # item is item
            self.you |= any([isinstance(you, item.__class__)
                             for you in game_map.get_items(Item)
                             if you.you])
            self.p1 |= any([isinstance(p1, item.__class__)
                             for p1 in game_map.get_items(Item)
                             if p1.p1])
            self.p2 |= any([isinstance(p2, item.__class__)
                             for p2 in game_map.get_items(Item)
                             if p2.p2])
        logging.debug(f"rules for {self.__class__.__name__}(you={self.you}) : {self.actions}")


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


class P1(Rule):

    def apply_actions(self, item):
        logging.debug(f"{item.__class__.__name__} is p1")
        if not item.rule:
            item.p1 = True


class P2(Rule):

    def apply_actions(self, item):
        logging.debug(f"{item.__class__.__name__} is p2")
        if not item.rule:
            item.p2 = True


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
