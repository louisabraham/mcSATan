from collections import namedtuple

from ..watches import Watches
from .. import logger


class Literal(namedtuple('Literal', 'atom bool')):
    """
    atom or negation of an atom
    """

    @property
    def neg(self):
        return Literal(self.atom, not self.bool)

    # not useful because it will be hashed
    # for the BCP
    # if not hasattr(self, '_neg'):
    #     self._neg = Literal(self.atom, not self.bool)
    # return self._neg

    def eval(self):
        return self.bool == self.atom.value

    # not useful because it is not
    # used in the semantic propagation
    # def vars(self):
    #     return self.atom.vars()
    # def watches(self):
    #     return [self] + self.vars()


class Clause(tuple):
    """
    Disjunction of literals
    """
    # TODO: make unsafe clauses for analyse_conflict
    # TODO: ensure clause does not contain a literal and its negation
    def __new__(cls, *args):
        seen = set()
        ls = []
        for e in args:
            if not e in seen:
                ls.append(e)
                seen.add(e)
        ls.sort()
        return super().__new__(cls, ls)

    # def vars(self):
    #     return set.union(x.vars() for x in self)

    def watches(self):
        return self

    @staticmethod
    def resolveB(clause1, clause2, lit):
        # merging doesn't improve the
        # performances
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
    Clauses database

    Handles:
        - BCP
    """
    # TODO: clause forget

    def __init__(self, stats):
        self.stats = stats
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
        for clause, lit in self.watches.units():
            assert isinstance(clause, Clause)
            assert isinstance(lit, Literal)
            yield clause, lit

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
