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

    def apply(self, item_src, item_dst):
        """ actual method defining collision behavior

        :returns: collision make the party win
        """
        # default action : do nothing
        logger.debug("Apply Action")
        diffx = item_dst.posx - item_src.posx
        diffy = item_dst.posy - item_src.posy
        item_src.posx += sign(diffx)
        item_src.posy += sign(diffy)
        return False


Action.register(Action)


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
class PushSameAsYou(Action):

    def apply(self, item_src, item_dst):
        logger.debug(f"Apply {self.__class__} : {item_src.__class__}({item_src.rule})→{item_dst.__class__}({item_dst.rule})")
        diffx = item_dst.posx - item_src.posx
        diffy = item_dst.posy - item_src.posy
        if item_src.you and item_dst.you:
            item_src.posx += sign(diffx)
            item_src.posy += sign(diffy)
        else:
            # collision
            # item are sorted by y, x
            # send the item_src at the back
            # move →
            if diffx > 0:
                # put after the last you at left
                for w in range(self.game_map.width):
                    nex = (item_src.posx-w) % self.game_map.width
                    item = self.game_map.maps[nex][item_src.posy]
                    if item is None or not item.you:
                        break
                if w > 1:
                    item_src.posx = nex
            # move ←
            elif diffx < 0:
                # put at the last you on right
                for w in range(self.game_map.width):
                    nex = (item_src.posx+w) % self.game_map.width
                    item = self.game_map.maps[nex][item_src.posy]
                    if item is None or not item.you:
                        break
                if w > 1:
                    item_src.posx = nex-1
            # move ↓
            elif diffy > 0:
                # put before the last you on top
                for h in range(self.game_map.height):
                    nex = (item_src.posy-h) % self.game_map.height
                    item = self.game_map.maps[item_src.posx][nex]
                    if item is None or not item.you:
                        break
                if h > 1:
                    item_src.posy = nex-1
            # move ↑
            elif diffy < 0:
                # put at the last you on bottom
                for h in range(self.game_map.height):
                    nex = (item_src.posy+h) % self.game_map.height
                    item = self.game_map.maps[item_src.posx][nex]
                    if item is None or not item.you:
                        break
                if h > 1:
                    item_src.posy = nex
        return False


@Action.register
class Win(Action):

    def apply(self, item_src, item_dst):
        logger.debug(f"Apply {self.__class__} : {item_src.__class__}({item_src.rule})→{item_dst.__class__}({item_dst.rule})")
        return True
