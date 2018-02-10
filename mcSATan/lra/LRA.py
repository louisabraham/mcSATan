from collections import namedtuple
from abc import ABC
from operator import lt, le
from Types import Atom

# TODO: use tuples for RationalCombination?


class RationalCombination(dict):

    def __getitem__(self, k):
        if k in self:
            return super().__getitem__(k)
        else:
            return 0

    def __add__(a, b):
        ans = RationalCombination()
        ans += a
        ans += b
        return ans

    def __iadd__(self, a):
        for i, v in a.items():
            self[i] += v
        return self

    def __sub__(a, b):
        ans = RationalCombination()
        ans += a
        ans -= b
        return ans

    def __isub__(self, a):
        self += -a
        return self

    def __mul__(self, c):
        ans = self.copy()
        ans *= c
        return ans

    def __imul__(self, c):
        for i in self:
            self[i] *= c
        return self

    def __neg__(self):
        return RationalCombination((i, -v) for i, v in self.items())

    def copy(self):
        return deepcopy(self)

    def vars(self):
        for i in self:
            if i != '__constant__':
                yield i

    def watches(self):
        return tuple(sorted(self.vars()))

    # def eval(self, trail):
    #     """
    #     evals the linexpr
    #     assumes all variables are in values
    #     """
    #     if not trail.has_value(self):
    #         def get_val(var):
    #             if var == '__constant__':
    #                 return 1
    #             else:
    #                 return values[var]
    #         trail.evals_to(
    #             key=self,
    #             val=sum(i * get_val(i) for i in self),
    #             lvl=max(trail.lvl[var] for var in self.vars())
    #         )

    def __repr__(self):
        ans = ''
        if self['__constant__'] > 0:
            ans += ' + %s' % self['__constant__']
        elif self['__constant__'] < 0:
            ans += ' - %s' % (-self['__constant__'])
        for i, v in sorted(self.items()):
            if not v:
                pass
            elif i == '__constant__':
                pass
            elif v == 1:
                ans += ' + ' + i
            elif v == -1:
                ans += ' - ' + i
            elif v > 0:
                ans += ' + %s * %s' % (v, i)
            else:
                ans += ' - %s * %s' % (-v, i)
        return ans[3:] if ans[:3] == ' + ' else ans

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class LinearConstraint(namedtuple('LinearConstraint', 'op expr'), Atom):
    def vars(self):
        yield from expr.vars()

    def neg(self):
        op = {'Leq0': 'Lt0', 'Lt0': 'Leq0'}[self.op]
        return LinearConstraint(op, -self.expr)

    # def eval(self, trail):
    #     if not trail.has_value(self):
    #         try:
    #             res = self.expr.eval(values)
    #         except KeyError:
    #             pass
    #         else:
    #             op = {'Leq0': le, 'Lt0': lt}
    #             trail.evals_to(
    #                 key=self,
    #                 val=op(res, 0),
    #                 lvl=trail.lvl[self.expr]
    #             )


class ReLU(namedtuple('ReLU', 'x y'), Atom):
    def vars(self):
        return [self.x, self.y]

    def eval(self):
        raise NotImplementedError

    def neg(self):
        raise NotImplementedError
