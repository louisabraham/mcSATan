from collections import defaultdict  # , namedtuple
from operator import add, sub

from . import logger


class Watches():
    """
    Allow to set watchlists, aka lists of variables with memoized total.
    Modify values of variables and the totals will be updated.
    You can retrieve all the unit watchlists with their only unit term.

    For convenience, you retrieve directly the element and not its watchlist


    The watchlists are hashed, that allows *slightly* better performances
    if multiple elements have the same watchlists.

    TODO: handle tuples values (subclass)
    """

    def __init__(self):
        # dict of watchlists to total of their values
        self.total = dict()
        # self.lists[val] = set of watchlists with total val
        # inverse of self.lists
        self.lists = defaultdict(set)
        # values of the variables
        self.values = defaultdict(lambda: 1)
        # in_watch[x] = list of watchlists containing x
        self.in_watch = defaultdict(set)
        # elements associated with a wl
        self.elems = defaultdict(set)

    def add_watch(self, elem, wl=None):
        """
        new values default to True
        calls elem.watches() if wl is None
        """
        if wl is None:
            wl = elem.watches()
        wl = tuple(sorted(set(wl), key=str))
        logger.debug('add_watch:\n'
                     '\telem: %s\n'
                     '\twl: %s\n',
                     elem, wl)
        self.elems[wl].add(elem)
        if not wl in self.lists:
            for i in wl:
                self.in_watch[i].add(wl)
            tot = sum(map(self.values.__getitem__, wl))
            self.total[wl] = tot
            self.lists[tot].add(wl)

    def set(self, var, val):
        """
        change the value of var to val
        and update the concerned totals
        """
        if self.values[var] == val:
            return
        for wl in self.in_watch[var]:
            tot = self.total[wl]
            self.lists[tot].remove(wl)
            tot += val - self.values[var]
            self.total[wl] = tot
            self.lists[tot].add(wl)
        self.values[var] = val
        logger.debug('set\n'
                     '\twatches: %s\n'
                     '\tvar: %s\n'
                     '\tval: %s\n',
                     self, var, val)

    def units(self):
        """
        returns the watched elements and the only
        unit variable in their watchlist
        """
        for wl in self.lists[1]:
            var = next(v for v in wl if self.values[v])
            for elem in self.elems[wl]:
                yield elem, var

    def zeros(self):
        """
        returns the watched elements
        """
        for wl in self.lists[0]:
            yield from self.elems[wl]

    def __repr__(self):
        ans = 'Watches\n'
        for wl, elems in self.elems.items():
            ans += '\twatch:\n'
            ans += '\t\telems: %s\n' % (elems,)
            ans += '\t\twl: %s\n' % (wl,)
            ans += '\t\ttotal: %s\n' % self.total
            ans += '\t\tvalues: %s\n' % [self.values[w] for w in wl]
        return ans + '\n'


from random import shuffle


class Watches2WL():
    """

    Implementation of the watched literals from
    http://matryoshka.gforge.inria.fr/pubs/sat_2wl_paper.pdf

    Allow to set watchlists, aka lists of variables with memoized total.
    Modify values of variables and the totals will be updated.
    You can retrieve all the unit watchlists with their only unit term.

    For convenience, you retrieve directly the element and not its watchlist


    The watchlists are hashed, that allows *slightly* better performances
    if multiple elements have the same watchlists.

    TODO: handle single clauses, handle tuples in a nice way
    """

    def __init__(self):

        # values of the variables
        self.values = defaultdict(lambda: 1)
        # in_watch[x] = list of watchlists containing x
        self.in_watch = defaultdict(set)

        # array of the watchlist
        # watchlists are hashed
        # but associated with an array
        self.array = {}

        # elements associated with a wl
        self.elems = defaultdict(set)

        self.unitswl = []
        self.zeroswl = []

    @staticmethod
    def get_value(var):
        x = self.values[var]
        if isinstance(x, int):
            return x
        return x[0]

    def swap2(self, l):
        n = len(l)
        i0 = max(range(n), key=self.values.__getitem__)
        l[0], l[i0] = l[i0], l[0]
        i1 = max(range(1, n), key=self.values.__getitem__)
        l[1], l[i1] = l[i1], l[1]

    def add_watch(self, elem, wl=None):
        """
        new values default to True
        calls elem.watches() if wl is None
        """
        if wl is None:
            wl = elem.watches()
        wl = tuple(sorted(set(wl), key=str))
        logger.debug('add_watch:\n'
                     '\telem: %s\n'
                     '\twl: %s\n',
                     elem, wl)
        self.elems[wl].add(elem)
        if not wl in self.array:
            arr = self.array[wl] = list(wl)
            self.swap2(arr)
            self.handle(wl)
            self.in_watch[arr[0]].add(wl)
            self.in_watch[arr[1]].add(wl)

    def handle(self, wl):
        arr = self.array[wl]
        val = self.get_value(arr[0]) + self.get_value(arr[1])
        if val == 0:
            self.zeroswl.append(wl)
        if val == 1:
            self.unitswl.append(wl)

    def set(self, var, val):
        """
        change the value of var to val
        and update the concerned totals
        """
        if self.values[var] == val:
            return
        for wl in self.in_watch[var]:
            arr = self.array[wl]
            self.swap2(arr)
            self.handle(wl)
        logger.debug('set\n'
                     '\twatches: %s\n'
                     '\tvar: %s\n'
                     '\tval: %s\n',
                     self, var, val)

    def units(self):
        """
        returns the watched elements and the only
        unit variable in their watchlist
        """
        for wl in self.unitswl:
            var = self.array[wl][0]
            for elem in self.elems[wl]:
                yield elem, var

    def zeros(self):
        """
        returns the watched elements
        """
        for wl in self.zeroswl:
            yield from self.elems[wl]

    def __repr__(self):
        ans = 'Watches\n'
        for wl, elems in self.elems.items():
            ans += '\twatch:\n'
            ans += '\t\telems: %s\n' % (elems,)
            ans += '\t\twl: %s\n' % (wl,)
            ans += '\t\ttotal: %s\n' % self.total
            ans += '\t\tvalues: %s\n' % [self.values[w] for w in wl]
        return ans + '\n'


if __name__ == '__main__':
    w = Watches()
    w.add_watch('z', 'xy')
    w.add_watch('a', 'x')
