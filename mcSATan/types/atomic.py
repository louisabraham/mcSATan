class Atom():
    """
    Abstract class for the primary entities
    that have a boolean meaning
    """

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def isAtom(cls, x):
        return isinstance(x, cls)
