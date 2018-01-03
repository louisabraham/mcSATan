from collections import namedtuple
from copy import deepcopy
from itertools import chain

from priority_queue import MaxPriorityQ
from watches import Watches
import logger


class Var(namedtuple('Var', 'name')):
    def vars(self):
        return [self]


class BoolVar(Var):
    type = 'Bool'

    def decide(self):
        return True


class Atom():
    """
    Abstract class
    """
    pass


def isAtom(x):
    return isinstance(x, Atom) or isinstance(x, BoolVar)


class Literal(namedtuple('Literal', 'atom bool')):
    """
    atom or negation of an atom
    """

    @property
    def neg(self):
        if not hasattr(self, '_neg'):
            self._neg = Literal(self.atom, not self.bool)
        return self._neg

    def eval(self, trail):
        """
        try to evaluate itself with the values dict
        return True / False / None
        """
        return self.bool == self.atom.eval(trail)

    def vars(self):
        return self.atom.vars()

    # def watches(self):
    #     return [self] + self.vars()


class Clause(tuple):
    """
    Disjunction of literals
    """

    def __new__(cls, *args):
        return super().__new__(cls, sorted(set(args)))

    # def vars(self):
    #     return set.union(x.vars() for x in self)

    def watches(self):
        return self

    @staticmethod
    def resolveB(clause1, clause2, lit):
        
        # unuseful optimization (by merging)
        # clause = []
        # i = j = 0
        # while i < len(clause1) or j < len(clause2):
        #     if i == len(clause1):
        #         llit = clause2[j]
        #         if llit != lit and llit != lit.neg:
        #             clause.append(llit)
        #         j += 1
        #     elif j == len(clause2):
        #         llit = clause1[i]
        #         if llit != lit and llit != lit.neg:
        #             clause.append(llit)
        #         i += 1
        #     else:
        #         lit1, lit2 = clause1[i], clause2[j]
        #         if lit1 < lit2:
        #             if lit1 != lit and lit1 != lit.neg:
        #                 clause.append(lit1)
        #             i += 1
        #         elif lit2 < lit1:
        #             if lit2 != lit and lit2 != lit.neg:
        #                 clause.append(lit2)
        #             j += 1
        #         else:
        #             if lit1 != lit and lit1 != lit.neg:
        #                 clause.append(lit1)
        #             i += 1
        #             j += 1
        # ans = Clause(*clause)
        
        clause = list(clause1 + clause2)
        clause.remove(lit)
        clause.remove(lit.neg)
        ans = Clause(*clause)
        
        
        logger.debug('resolveB:\n'
                     '\tclause1: %s\n'
                     '\tclause2: %s\n'
                     '\tans: %s',
                     clause1, clause2, ans)
        return ans

    def __repr__(self):
        return 'Clause%s' % super().__repr__()


class ClauseDB():
    """
    a compact representation of all the clauses in the system
    """

    def __init__(self):
        # this instances of Watches is unique for the
        # clausal propagations
        # Literal assigned to False -> 0
        # Literal not assigned -> 1
        # Literal assigned to True -> 2
        # This way, a clause is unit iff its total is 1
        self.watches = Watches()

    def add(self, clause):
        """
        Add the clause to the database,
        and watches all its literals
        """
        self.watches.add_watch(clause)

    def unit_clauses(self):
        """
        return the unit clauses along with
        the literal that makes them unit
        """
        yield from self.watches.units()

    def unsat_clauses(self):
        yield from self.watches.zeros()

    def assign_atom(self, atom, val):
        self.watches.set(Literal(atom, val), 2)
        self.watches.set(Literal(atom, not val), 0)

    def desassign_atom(self, atom):
        self.watches.set(Literal(atom, True), 1)
        self.watches.set(Literal(atom, False), 1)

    def __repr__(self):
        return 'ClauseDB(%s)' % self.watches


class VarDB():
    """
    Variables with priority of assignment
    """

    priority_from_type = {'Bool': 1, 'Rat': 2}

    def __init__(self):
        # Unused now, list of all variables
        self.vars = []
        # Semantic propagation
        self.watches = Watches()
        # Variable choice policy
        self.pq = MaxPriorityQ()

    def add(self, var, priority=None):
        self.vars.append(var)
        if priority is None:
            priority = self.priority_from_type[var.type]
        self.pq.push(var, priority)

    def assign(self, var):
        self.pq.remove(var)
        self.watches.set(var, 0)

    def desassign(self, var):
        priority = self.priority_from_type[var.type]
        self.pq.push(var, priority)
        self.watches.set(var, 1)

    def pop(self):
        return self.pq.pop()

    def can_decide(self):
        return bool(self.pq)
