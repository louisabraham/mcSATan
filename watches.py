from collections import defaultdict  # , namedtuple
from operator import add, sub
import logger


# def Watches(fields, default=None):
#     """
#     fields is a string with space-separated
#     names of boolean / integer fields
#     """
#
#     State = namedtuple('State', fields)
#     State.__add__ = lambda a, b: State(*map(operator.add, a, b))
#     State.__sub__ = lambda a, b: State(*map(operator.sub, a, b))
#     if default is None:
#         default = State([1] * len(State._fields))

class Watches():
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
        elem.watches() must be defined and hashable
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
        returns all the watched elements
        with the only variable in they watchlist
        with the value 1
        """
        for wl in self.lists[1]:
            var = next(v for v in wl if self.values[v])
            for elem in self.elems[wl]:
                yield elem, var

    def __repr__(self):
        ans = 'Watches\n'
        for wl, elems in self.elems.items():
            ans += '\twatch:\n'
            ans += '\t\telems: %s\n' % (elems,)
            ans += '\t\twl: %s\n' % (wl,)
            ans += '\t\ttotal: %s\n' % self.total
            ans += '\t\tvalues: %s\n' % [self.values[w] for w in wl]
        return ans + '\n'
