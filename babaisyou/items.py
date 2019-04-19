""" Items used in game """
from actions import Action
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
        self.win = False  # party is win
        self.dead = False  # item is dead

    def set_rules(self, rules, game_map):
        # reset actions
        # logging.debug(f"set rule : {[rule.__class__.__name__ for rule in rules]} on {self.__class__.__name__}")
        self.actions = set([])
        self.you = False
        for item in rules:
            if isinstance(item, You):
                self.you = True
            elif item.__class__.__name__ in Action.registry:
                # item is rule with action
                self.actions = item.set_actions(self.actions)
            else:
                # item is item
                self.you = any([isinstance(you, item.__class__)
                                for you in game_map.get_items(Item)
                                if you.you])
        # logging.debug(f"rules for {self} : {self.actions}")
        return self


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


class You(Item):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.rule = True
        self.actions = [Action.load("Push")]


class Rule(Item):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.actions = [Action.load("Push")]
        self.rule = True

    def set_actions(self, actions):
        return actions.add()


class Win(Rule):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)

    def set_actions(self, actions):
        actions.add(Action.load("Win"))
        return actions


class Push(Rule):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)

    def set_actions(self, actions):
        if Action.load("Stop") in actions:
            actions.remove(Action.load("Stop"))
        else:
            actions.add(Action.load("Push"))
        return actions


class Stop(Rule):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)

    def set_actions(self, actions):
        if Action.load("Push") in actions:
            actions.remove(Action.load("Push"))
        else:
            actions.add(Action.load("Stop"))
        return actions


class Dead(Rule):
    def __init__(self, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)

    def set_actions(self, actions):
        actions.add(Action.load("Dead"))
        return actions
