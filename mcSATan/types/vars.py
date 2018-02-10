from .atomic import Atom
from ..utils.priority_queue import MaxPriorityQ
from ..watches import Watches


class Var():
    __slots__ = ('name', 'value',)

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    # def vars(self):
    #     return [self]

    def decide(self):
        raise NotImplementedError

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.name, self.value)


class BoolVar(Var, Atom):
    type = 'Bool'

    def decide(self):
        return False


class VarDB():
    """
    Variables database
    
    Handles:
        - priority of assignment
        - mapping name -> Var (??? unicity of name)
        - semantic propagation
    """

    # this should be defined here and not in
    # the type because it is only used here
    # strings are used for speed
    priority_from_type = {'Bool': 1, 'Rat': 2}

    def __init__(self, stats):
        self.stats = stats
        # mapping of all variables
        self.vars = {}
        # Semantic propagation
        self.watches = Watches()
        # Variable choice policy
        self.pq = MaxPriorityQ()

    def add(self, var):  # , priority=None):
        assert var.name not in self.vars
        self.vars[var.name] = var
        # if priority is None:
        priority = self.priority_from_type[var.type]
        self.pq.push(var, priority)

    def assign(self, var, value):
        var.value = value
        self.pq.remove(var)
        self.watches.set(var, 0)

    def desassign(self, var):
        var.value = None
        priority = self.priority_from_type[var.type]
        self.pq.push(var, priority)
        self.watches.set(var, 1)

    def pop(self):
        return self.pq.pop()

    def can_decide(self):
        return bool(self.pq)
