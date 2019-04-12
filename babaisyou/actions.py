
class Action:
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
        # default action : do nothing
        return False


@Action.register
class Block(Action):

    def apply(self, item_src, item_dst):
        return False


@Action.register
class Push(Action):

    def apply(self, item_src, item_dst):
        diffx = item_dst.posx - item_src.posx
        diffy = item_dst.posy - item_src.posy
        item_src.posx = (item_src.posx+diffx) % self.game_map.width
        item_src.posy = (item_src.posy+diffy) % self.game_map.height
        item_dst.posx = (item_dst.posx+diffx) % self.game_map.width
        item_dst.posy = (item_dst.posy+diffy) % self.game_map.height
        return False


@Action.register
class Win(Action):

    def apply(self, item_src, item_dst):
        return True
