from LRA import *
from core import *

x = Var('x', 'Rat')
y = Var('y', 'Rat')
problem = [
    Clause([ReLU(x, y)]),
    Clause([LinearConstraint('Lt0', RationalCombination({y: 2}))])
]


# def propagate(trail)
#
#
# def solve(problem):
#     vars = problem.vars()
#     trail = Trail()
#     while True:
#         try:
#             propagate()
#         except Conflict c of clause:
#             explanation = analyzeConflict(trail, clause)
#             if not explanation:
#                 return False
#             backtractWith(train, explanation)
#         else:
#             if not vars:
#                 return True
#             var = vars.pop()
#             decideValue(x)
