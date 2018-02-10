from collections import defaultdict

from . import types
from . import logger

"""
TODO: put values as a field in variable class without name
retrieve the variable from VarDB
"""


class Conflict(Exception):

    def __init__(self, clause):
        self.clause = clause

    def __repr__(self):
        return 'Conflict(%s)' % self.clause


class Trail():
    """
    Stores the values of atoms with levels
    """

    def __init__(self, variables, clauses, stats):
        self.stats = stats
        self.variables = variables
        self.clauses = clauses

        self.reason = {}
        self.lvl = {}
        self.level = 0
        self.at_lvl = defaultdict(list)

    def set_value(self, var, val, reason, lvl):
        self.variables.assign(var, val)
        self.reason[var] = reason
        self.lvl[var] = lvl
        self.at_lvl[lvl].append(var)
        if var.type == 'Bool':
            self.clauses.assign_atom(var, val)

    def del_values_at_lvl(self, lvl):
        if lvl not in self.at_lvl:
            return
        for var in self.at_lvl[lvl]:
            del self.reason[var]
            del self.lvl[var]
            self.variables.desassign(var)
            if var.type == 'Bool':
                self.clauses.desassign_atom(var)
        del self.at_lvl[lvl]

    def has_value(self, var):
        return var.value is not None

    def decide(self, var, val):
        logger.debug(
            'decide\n'
            '\tvar: %s\n'
            '\tvalue: %s\n', var, val)
        assert var.value is None
        self.level += 1
        # no need to remove the variable
        # we assume it has already been popped
        # from the VarDB
        self.set_value(var, val, 'decide', self.level)

    # def evals_to(self, key, val):
    #     self.set_element(key, val, self.level, reason='semantic evaluation')

    def clausal_propagate(self, clause, lit):
        logger.info(
            "clausal_propagate\n"
            "\tclause: %s\n"
            "\tlit: %s\n", clause, lit)
        # maybe one wants to count differently
        self.stats.nb_clausal_propagations += 1
        assert isinstance(clause, types.Clause)
        assert isinstance(lit, types.Literal)
        var, val = lit.atom, lit.bool
        assert var.type == 'Bool'
        reason = ('clausal propagation', clause)
        if var.value is not None:
            if var.value == val:
                return
            else:
                raise Conflict(clause)
        self.set_value(var, val, reason, self.level)

    def lit_lvl(self, lit):
        assert isinstance(lit, types.Literal)
        # logger.debug('lit_lvl\n\tlit: %s \n', lit)
        return self.lvl[lit.atom]

    def lit_reason(self, lit):
        assert isinstance(lit, types.Literal)
        # logger.debug('lit_reason\n\tlit: %s', lit)
        return self.reason[lit.atom]

    def topLiterals(self, clause):
        assert isinstance(clause, types.Clause)
        logger.debug(
            'topLiterals:\n'
            '\tclause: %s\n', clause)
        lvls = [self.lit_lvl(lit) for lit in clause]
        m = max(lvls)
        return [lit for lit in clause if self.lit_lvl(lit) == m]

    def can_backtrack_with(self, clause):
        logger.debug(
            'can_backtrack_with:\n'
            '\tclause: %s\n', clause
        )
        # equivalent but less efficient:
        # top = self.topLiterals(clause)
        # return len(top) == 1 and self.lit_lvl(top[0]) > 0 or all(self.lit_reason(lit) == 'semantic evaluation' for lit in top)

        maxlvl = -1
        uip = True
        semeval = True
        for lit in clause:
            lvl = self.lit_lvl(lit)
            if lvl > maxlvl:
                maxlvl = lvl
                uip = True
            elif lvl == maxlvl:
                uip = False
            if semeval:
                semeval = self.lit_reason(lit) == 'semantic evaluation'
        return uip and maxlvl > 0 or semeval

    def backtrack_lvl_type(self, clause):
        assert all(isinstance(lit, types.Literal) for lit in clause)
        top = self.topLiterals(clause)
        if len(top) == 1:
            # The clause is an UIP
            # (unique implication point)
            return max((self.lit_lvl(i) for i in clause
                        if not i in top),
                       default=0), 'UIP'
        else:
            # it must be a semantic split clause
            assert all(self.reason[lit.atom] == 'semantic evaluation')
            return self.lit_lvl(top[0]) - 1, 'semantic split'

    def backtrack_with(self, clause):
        lvl, type = self.backtrack_lvl_type(clause)
        logger.info('backtrack_with: \n'
                    '\tclause %s\n'
                    '\tlvl %s \n'
                    '\ttype %s\n',
                    clause, lvl, type)
        for l in range(self.level, lvl, -1):
            self.del_values_at_lvl(l)
        self.level = lvl
        if type == 'UIP':
            count = 0
            for lit in clause:
                if not self.has_value(lit.atom):
                    self.clausal_propagate(clause, lit)
                    count += 1
            assert count == 1
        elif type == 'semantic split':
            # UNDO-DECIDE
            for lit in clause:
                if not self.has_value(lit.atom):
                    self.variables.assign(lit.atom)
                    self.decide(lit.atom, lit.value)
                    break
        else:
            assert False

    def analyse_conflict(self, clause):
        # TODO: optimize this part
        assert isinstance(clause, types.Clause)
        while clause and not self.can_backtrack_with(clause):
            for lit in clause:
                reason = self.lit_reason(lit)
                if reason[0] == 'clausal propagation':
                    clause = types.Clause.resolveB(clause, reason[1], lit)
                    break
        return clause


class SolverStats(dict):
    def __getitem__(self, key):
        if not key in self:
            self[key] = 0
        return super().__getitem__(key)

    def __getattr__(self, key):
        try:
            return super().__getattr__(key)
        except AttributeError:
            return self[key]

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class Solver():

    def __init__(self, CDCL=True):
        self.stats = SolverStats()
        self.variables = types.VarDB(self.stats)
        self.clauses = types.ClauseDB(self.stats)
        self.trail = Trail(self.variables, self.clauses, self.stats)

        self.CDCL = CDCL

    def BoolVar(self, name):
        self.stats.nb_vars += 1
        # priority = kwargs.get('priority')
        var = types.BoolVar(name)
        self.variables.add(var)
        return var

    def Literal(self, *args, **kwargs):
        # a bit unuseful because we don't
        # register the literals
        lit = types.Literal(*args, **kwargs)
        return lit

    def Clause(self, *args, **kwargs):
        self.stats.nb_clauses += 1
        clause = types.Clause(*args, **kwargs)
        self.clauses.add(clause)
        return clause

    def clausal_propagate(self):
        try:
            raise Conflict(next(self.clauses.unsat_clauses()))
        except StopIteration:
            pass
        unit_clauses = list(self.clauses.unit_clauses())
        for clause, lit in unit_clauses:
            self.trail.clausal_propagate(clause, lit)
        return unit_clauses

    def semantic_propagate(self):
        units = list(self.variables.watches.units())
        for elem, var in units:
            # elem.propagate is defined in plugins
            elem.propagate(self.trail, var)
        return units

    def propagate(self):
        while self.clausal_propagate() or self.semantic_propagate():
            pass

    def solve(self):
        while True:
            try:
                self.propagate()
            except Conflict as conflict:
                # return conflict
                # if logger.isEnabledFor(logger.INFO):
                #     logger.info('TRAIL:\n%s\n',
                #                 logger.pformat({var: (self.trail.values[var], self.trail.lvl[var]) for var in self.trail.values}))
                logger.info('CONFLICT\n'
                            '\tconflict: %s\n',
                            conflict)

                analyzed_conflict = self.trail.analyse_conflict(
                    conflict.clause)
                logger.info('CONFLICT\n'
                            '\tconflict: %s\n'
                            '\tanalyzed conflict: %s\n',
                            conflict, analyzed_conflict)
                if not analyzed_conflict:
                    print('UNSAT')
                    return False
                else:
                    self.trail.backtrack_with(analyzed_conflict)
                    # CDCL is happening here
                    if self.CDCL:
                        self.clauses.add(analyzed_conflict)
                        self.stats.nb_learned_clauses += 1
            else:
                # if logger.isEnabledFor(logger.INFO):
                #     logger.info('TRAIL:\n%s\n',
                #                 logger.pformat({var: (self.trail.values[var], self.trail.lvl[var]) for var in self.trail.values}))
                if not self.variables.can_decide():
                    print('SAT')
                    return list(self.variables.vars.values())
                else:
                    var = self.variables.pop()
                    logger.info('DECiDE %s\n', var)
                    self.trail.decide(var, var.decide())
