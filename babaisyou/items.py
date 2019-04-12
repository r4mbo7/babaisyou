""" Items used in game """
from actions import Action
import logging

class Item:
    """ Item of the game """

    def __init__(self, posx, posy, rule=False, you=False):
        self.posx = posx  # position on map
        self.posy = posy
        self.actions = [Action.load("Block")]  # actions on collision
        self.rule = rule  # item is a rule
        if self.rule:
            self.actions = [Action.load("Push")]
        self.you = you  # item is you

    def set_rules(self, rules):
        # reset actions
        logging.debug(f"set rule : {[rule.__class__.__name__ for rule in rules]} on {self.__class__.__name__}")
        self.actions = []
        self.you = False
        for rule in rules:
            if isinstance(rule, You):
                self.you = True
            else:
                self.actions.append(rule.ref_action)


class Baba(Item):
    pass


class Flag(Item):
    pass


class Wall(Item):
    pass


class Is(Item):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.actions = [Action.load("Push")]


class Rule(Item):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.actions = [Action.load("Push")]
        self.rule = True
        self.ref_action = Action


class You(Rule):
    pass


class Win(Rule):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.ref_action = Action.load("Win")


class Push(Rule):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.ref_action = Action.load("Push")
