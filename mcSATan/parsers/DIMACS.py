#!/usr/bin/env python3

from mcSATan.core import Solver


def parse_cnf(infile):
    solver = Solver(CDCL=True)
    buf = []
    nClauses = float('inf')
    for line in infile:
        if not nClauses:
            break
        line = line.split()
        if line[0] == 'c':
            continue
        if line[0] == 'p':
            assert line[1] == 'cnf'
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
    return solver
