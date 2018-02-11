mcSATan: A diabolic implementation of mcSAT
===========================================

mcSAT is a paradigm for SMT ([Satisfiability modulo
theories](https://en.wikipedia.org/wiki/Satisfiability_modulo_theories))
solving.

You can read the [Implementation
Notes](https://github.com/louisabraham/mcSATan/blob/master/Implementation%20Notes.md).

Usage
=====

You can use it to solve SAT problems with DIMACS-formatted `.cnf` files.

    python3 -m mcSATan.cnf file.cnf

You can also directly plug the output of
[cnfgen](https://massimolauria.github.io/cnfgen/):

    cnfgen php 6 8 | python3 -m mcSATan.cnf

TODO
====

-   convert Watches to integers
-   2WL watched literals
-   config file
-   ACIDS branching heuristic
-   SBR strategy for clause forget
-   Luby's restart
-   Plugin for LRA
-   Unit Tests
-   C implementation of 2WL
-   C implementation of dyadics for LRA
-   SMT-LIB parser
