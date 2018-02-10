from lra import *
from core import Solver

# # var = s.variables.pop()
# # s.trail.decide(var, var.decide())
# # w = s.clauses.watches
# c = s.solve()
# # s.clausal_propagate()
# # s.semantic_propagate()
#
# x = Var('x', 'Rat')
# y = Var('y', 'Rat')
# problem = [
#     Clause([ReLU(x, y)]),
#     Clause([LinearConstraint('Lt0', RationalCombination({y: 2}))])
# ]
#

s = Solver()
x = s.BoolVar('x')
y = s.BoolVar('y')

lit1 = s.Literal(x, False)
lit2 = s.Literal(y, True)
clause = s.Clause(lit1, lit2)

lit1 = s.Literal(x, False)
lit2 = s.Literal(y, False)
clause = s.Clause(lit1, lit2)

print(s.solve())