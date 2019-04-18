import logging

logger = logging.getLogger(__name__)


def sign(a): return (a > 0) - (a < 0)


class Action:
    """ Manage collisition between items """
    registry = {}

    def __init__(self, game_map):
        self.game_map = game_map

    @classmethod
    def register(cls, action):
        cls.registry[action.__name__] = action
        return action

    @classmethod
    def load(cls, name):
        return cls.registry[name]

    def apply(self, you, item):
        """ actual method defining collision behavior

        :returns: collision make the party win
        """
        # default action : do nothing
        logger.debug("Apply Action")
        return False


Action.register(Action)


@Action.register
class Stop(Action):

    def apply(self, you, item):
        logger.debug(f"Apply {self.__class__} : {you.__class__}({you.rule})→{item.__class__}({item.rule})")
        you.vectx = 0
        you.vecty = 0
        return False


@Action.register
class Push(Action):

    def apply(self, you, item):
        logger.debug(f"Apply {self.__class__} : {you.__class__}({you.rule})→{item.__class__}({item.rule})")
        # push all the line
        if item.posx == you.posx:
            for h in range(self.game_map.height):
                next_item = self.game_map.maps[item.posx][(item.posy+sign(you.vecty)*h)%self.game_map.height]
                if next_item is None:
                    break
                next_item.vecty = you.vecty
        else:
            for w in range(self.game_map.width):
                next_item = self.game_map.maps[(item.posx+sign(you.vectx)*w)%self.game_map.width][item.posy]
                if next_item is None:
                    break
                next_item.vectx = you.vectx
        return False


@Action.register
class Win(Action):

    def apply(self, you, item):
        logger.debug(f"Apply {self.__class__} : {you.__class__}({you.rule})→{item.__class__}({item.rule})")
        return True
