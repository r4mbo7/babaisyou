import logging

logger = logging.getLogger(__name__)


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

    def apply(self, item_src, item_dst):
        """ actual method defining collision behavior

        :returns: collision make the party win
        """
        # default action : do nothing
        return False


@Action.register
class Block(Action):

    def apply(self, item_src, item_dst):
        logger.debug(f"Apply {self.__class__} : {item_src.__class__}({item_src.rule})→{item_dst.__class__}({item_dst.rule})")
        return False


@Action.register
class Push(Action):

    def apply(self, item_src, item_dst):
        logger.debug(f"Apply {self.__class__} : {item_src.__class__}({item_src.rule})→{item_dst.__class__}({item_dst.rule})")
        diffx = item_dst.posx - item_src.posx
        diffy = item_dst.posy - item_src.posy

        to_push = []
        if diffx != 0:
            for w in range(self.game_map.width):
                nex = (item_src.posx+w*diffx) % self.game_map.width
                item = self.game_map.maps[nex][item_src.posy]
                if item is None:
                    break
                to_push.append(item)
            for item in to_push:
                item.posx = (item.posx+diffx) % self.game_map.width
        else:
            for h in range(self.game_map.height):
                nex = (item_src.posy+h*diffy) % self.game_map.height
                item = self.game_map.maps[item_src.posx][nex]
                if item is None:
                    break
                to_push.append(item)
            for item in to_push:
                item.posy = (item.posy+diffy) % self.game_map.height
        return False


@Action.register
class Win(Action):

    def apply(self, item_src, item_dst):
        logger.debug(f"Apply {self.__class__} : {item_src.__class__}({item_src.rule})→{item_dst.__class__}({item_dst.rule})")
        return True
