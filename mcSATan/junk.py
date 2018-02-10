import numpy as np


class WatchesNP():
    """
    Allow to set watchlists, aka lists of variables with memoized total.
    Modify values of variables and the totals will be updated.
    You can retrieve all the unit watchlists with their only unit term.

    For convenience, you retrieve directly the element and not its watchlist


    The watchlists are hashed, that allows *slightly* better performances
    if multiple elements have the same watchlists.
    """

    def __init__(self):
        # lines are var, columns are wl
        self.matrix = np.zeros(shape=(0, 0))
        # values of the variables
        self.values = np.zeros(shape=(0,))
        # sum of values of a wl
        self.total = np.zeros(shape=(0,))
        self.var_to_id = dict()
        self.id_to_var = dict()
        self.wl_to_id = dict()
        # self.id_to_wl = dict()

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

        if wl not in self.wl_to_id:
            # add the ids
            self.wl_to_id[wl] = wl_id = len(self.wl_to_id)
            newVar = 0
            for var in wl:
                if not var in self.var_to_id:
                    self.var_to_id[var] = var_id = len(self.var_to_id)
                    self.id_to_var[var_id] = var
                    newVar += 1

            # add lines
            nl, nc = self.matrix.shape
            newvars = np.zeros(shape=(newVar, nc))
            self.matrix = np.append(self.matrix, newvars, axis=0)
            # add variables
            if newVar:
                self.values = np.append(self.values, np.ones(shape=(newVar,)))

            # add column
            newCol = np.zeros(shape=(nl + newVar, 1))
            for var in wl:
                newCol[self.var_to_id[var]] = 1
            self.matrix = np.append(self.matrix, newCol, axis=1)

            # add total
            self.total = np.append(
                self.total, [sum(self.matrix[:, -1] * self.values)])

        self.elems[wl_id].add(elem)

    def set(self, var, val):
        """
        change the value of var to val
        and update the concerned totals
        """
        var = self.var_to_id[var]
        if self.values[var] == val:
            return
        self.total += (val - self.values[var]) * self.matrix[var]
        self.values[var] = val
        logger.debug('set\n'
                     '\tmatrix: %s\n'
                     '\tvar: %s\n'
                     '\tval: %s\n',
                     self, var, val)

    def units(self):
        """
        returns the watched elements and the only
        unit variable in their watchlist
        """
        for wl_id in np.where(self.total == 1)[0]:
            var_id = np.argmax(self.matrix[:, wl_id] * self.values)
            for elem in self.elems[wl_id]:
                yield elem, self.id_to_var[var_id]

    def zeros(self):
        """
        returns the watched elements
        """
        for wl_id in np.where(self.total == 0)[0]:
            yield from self.elems[wl_id]

    def __repr__(self):
        ans = 'Watches\n'
        for wl, elems in self.elems.items():
            ans += '\twatch:\n'
            ans += '\t\telems: %s\n' % (elems,)
            ans += '\t\twl: %s\n' % (wl,)
            ans += '\t\ttotal: %s\n' % self.total
            ans += '\t\tvalues: %s\n' % [self.values[w] for w in wl]
        return ans + '\n'

class Clause(tuple):

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