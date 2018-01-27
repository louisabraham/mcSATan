#!/usr/bin/env python3


"""
A DIMACS SAT-Solver based on mcSAT
"""


import fileinput
from time import time
from sys import stderr
from pprint import pprint

dbt = time()

from core import Solver
buf = []
nClauses = float('inf')
for line in fileinput.input():
    if not nClauses:
        break
    line = line.split()
    if line[0] == 'c':
        continue
    if line[0] == 'p':
        assert line[1] == 'cnf'
        solver = Solver(CDCL=True)
        nVar = int(line[2])
        nClauses = int(line[3])
        variables = {i: solver.BoolVar('var%s' % i)
                     for i in range(1, nVar + 1)}
        continue
    *line, = map(int, line)
    line = buf + line
    buf = []
    if line[-1] != 0:
        buf = line
        continue
    nClauses -= 1
    solver.Clause(*[solver.Literal(variables[abs(i)], i > 0)
                    for i in line[:-1]])

print('Parsed %.02fs' % (time() - dbt), file=stderr)
dbt = time()
solver.solve()
pprint(solver.stats)
print('Solved %.02fs' % (time() - dbt), file=stderr)
