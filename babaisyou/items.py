""" Items used in game """
from actions import Action


class Item:
    """ Item of the game """

    def __init__(self, posx, posy, rule=False):
        self.posx = posx
        self.posy = posy
        self.actions = [Action.load("Block")]
        self.rule = True


class Baba(Item):
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
        self.ref_action = Action


class You(Rule):
    pass


class Is(Rule):
    pass


class Win(Rule):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.ref_action = Action.load("Win")


class Push(Rule):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.ref_action = Action.load("Win")
