#!/usr/bin/env python3


"""
A DIMACS SAT-Solver based on mcSAT
"""

import argparse
from time import time
from sys import stderr, stdin, path
from pprint import pprint

from mcSATan.core import Solver
from mcSATan.logger import logger


def parse(infile):
    solver = Solver(CDCL=True)
    buf = []
    nClauses = float('inf')
    for line in args.infile:
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


parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                    default=stdin)
parser.add_argument('--debug', nargs='?', type=int, default=30)


if __name__ == '__main__':

    args = parser.parse_args()
    logger.setLevel(args.debug)

    dbt = time()
    solver = parse(args.infile)
    print('Parsed %.02fs' % (time() - dbt), file=stderr)

    dbt = time()
    solver.solve()
    pprint(solver.stats)
    print('Solved %.02fs' % (time() - dbt), file=stderr)
