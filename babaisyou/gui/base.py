from abc import ABC

class Gui(ABC):
    """ Interfarce for Gui """

    def update(self):
        """ display map to user """
        raise NotImplementedError
