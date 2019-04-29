from abc import ABC

class Gui(ABC):
    """ Interfarce for Gui """

    def update(self):
        """ display map to user """
        raise NotImplementedError

    def party_end(self, win):
        """ party is over """
        raise NotImplementedError