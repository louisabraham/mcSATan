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
from mcSATan.parsers.DIMACS import parse_cnf

parser = argparse.ArgumentParser()
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                    default=stdin)
parser.add_argument('--debug', nargs='?', type=int, default=30)


if __name__ == '__main__':

    args = parser.parse_args()
    logger.setLevel(args.debug)

    dbt = time()
    solver = parse_cnf(args.infile)
    print('Parsed %.02fs' % (time() - dbt), file=stderr)

    dbt = time()
    solver.solve()
    pprint(solver.stats)
    print('Solved %.02fs' % (time() - dbt), file=stderr)
