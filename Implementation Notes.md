This is an implementation of [The Design and Implementation of the Model
Constructing Satisfiability
Calculus](http://csl.sri.com/users/dejan/papers/jovanovic-fmcad2013.pdf)
by D. Jovanovic et al.

Some liberties were taken.

Definitions:
============

**Atom** is an abstract class for the primary entities that have a
boolean meaning. Boolean variables (**BoolVar**) are considered atoms,
and linear inequalities are atoms too.

**Literal** represents an **Atom** or the negation of an **Atom**.

A **Var** has a name and a value. It represents a variable.

**ClauseDB** is a compact representation of the clauses and handles the
boolean propagation.

**VarDB** contains variables and handles the variable order and the
semantic propagation.

The **Trail** contains the levels of the assigned variables and their
reasons.


Repartition of the code
=======================

-   core.py
    -   exception Conflict
    -   class Trail
    -   class Solver
-   Types
    -   class Var
    -   class BoolVar(Var)
    -   class Atom: used in plugins
    -   class Literal: atom or negation of an atom
    -   class Clause: disjunction (list) of literals
    -   class ClauseDB: the database of clauses, in charge of the
        clausal propagation
    -   class VarDB: the variables database that handles the priority
        and semantic propagation
-   priority\_queue.py
-   watches.py
