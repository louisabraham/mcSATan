#!/usr/bin/env bash

python3 -OO -m cProfile -o $1.prof ./cnf.py $1
gprof2dot -f pstats $1.prof | dot -Tpdf -o $1.prof.pdf
open $1.prof.pdf
snakeviz $1.prof

# also
# python3 -m vprof -c h "./cnf.py $1"