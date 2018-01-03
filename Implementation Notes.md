This is an implementation of [The Design and Implementation of the Model
Constructing Satisfiability Calculus](http://csl.sri.com/users/dejan/papers/jovanovic-fmcad2013.pdf) by D. Jovanovic et al.

Some liberties were taken.

The trail contains the assignments of variables or atoms (boolean variables are considered atoms).
This way, we cannot have both a literal and its opposite on the trail.


Here is the repartition of the code in the different files:

- core.py
    - exception Conflict
    - class Trail
    - class Solver
- Types
    - class Var
    - class BoolVar(Var)
    - class Atom: used in plugins
    - class Literal: atom or negation of an atom
    - class Clause: disjunction (list) of literals
    - class ClauseDB: the database of clauses, in charge of the clausal propagation
    - class VarDB: the variables database that handles the priority and semantic propagation

- priority_queue.py
- watches.py
    