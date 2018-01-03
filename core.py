import Types
import logger

# TODO: clean assign / assign_atom


class Conflict(Exception):

    def __init__(self, clause):
        self.clause = clause

    def __repr__(self):
        return 'Conflict(%s)' % self.clause


class Trail():
    """
    Stores the values of atoms with levels
    """

    def __init__(self, variables, clauses):
        self.variables = variables
        self.clauses = clauses
        self.values = {}
        self.reason = {}
        self.lvl = {}
        self.level = 0

    def has_value(self, key):
        return key in self.values and self.values[key] is not None

    def decide(self, key, val):
        logger.debug(
            'decide\n'
            '\tkey: %s\n'
            '\tvalue: %s\n', key, val)
        if key in self.values:
            raise Error
            # if self.values[key] == val:
            #     logger.warning('Already set %s = %s', key, val)
            #     return
            # else:
            #     raise Conflict(reason)
        self.level += 1
        # no need to remove the variable
        # we assume it has been popped
        self.variables.assign(key)
        self.clauses.assign_atom(key, val)
        self.values[key] = val
        self.reason[key] = 'decide'
        self.lvl[key] = self.level

    # def evals_to(self, key, val):
    #     self.set_element(key, val, self.level, reason='semantic evaluation')

    def clausal_propagate(self, clause, lit):
        logger.info(
            "clausal_propagate\n"
            "\tclause: %s\n"
            "\tlit: %s\n", clause, lit)
        assert isinstance(clause, Types.Clause)
        # if isinstance(lit, Var):
        #     key = lit
        assert isinstance(lit, Types.Literal)
        key, val = lit.atom, lit.bool
        # if isinstance(key, BooleanAtom):
        #     key = key.var
        reason = ('clausal propagation', clause)
        if key in self.values:
            if self.values[key] == val:
                logger.warning('Already set %s = %s', key, val)
                return
            else:
                raise Conflict(clause)
        self.clauses.assign_atom(key, val)
        self.variables.assign(key)
        self.values[key] = val
        self.reason[key] = reason
        self.lvl[key] = self.level

    def lit_lvl(self, lit):
        assert isinstance(lit, Types.Literal)
        # logger.debug('lit_lvl\n\tlit: %s \n', lit)
        return self.lvl[lit.atom]

    def lit_reason(self, lit):
        # logger.debug('lit_reason\n\tlit: %s', lit)
        return self.reason[lit.atom]

    def topLiterals(self, clause):
        assert isinstance(clause, Types.Clause)
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
        top = self.topLiterals(clause)
        # logger.debug(top, self.lit_lvl(top[0]), [self.reason[lit.atom] == 'semantic evaluation' for lit in top])
        return len(top) == 1 and self.lit_lvl(top[0]) > 0 or all(self.lit_reason(lit) == 'semantic evaluation' for lit in top)

    def backtrack_lvl_type(self, clause):
        assert all(isinstance(lit, Types.Literal) for lit in clause)
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
        self.level = lvl
        for key in list(self.values):
            if self.lvl[key] > self.level:
                del self.values[key]
                del self.reason[key]
                del self.lvl[key]
                self.variables.desassign(key)
                self.clauses.desassign_atom(key)
        if type == 'UIP':
            for lit in clause:
                if not self.has_value(lit.atom):
                    self.clausal_propagate(clause, lit)
        elif type == 'semantic split':
            for lit in clause:
                if not self.has_value(lit.atom):
                    self.variables.assign(lit.atom)
                    self.decide(lit.atom, lit.value)
                    break
        else:
            assert False

    def analyse_conflict(self, clause):
        assert isinstance(clause, Types.Clause)
        while clause and not self.can_backtrack_with(clause):
            for lit in clause:
                reason = self.lit_reason(lit)
                if reason[0] == 'clausal propagation':
                    clause = Types.Clause.resolveB(clause, reason[1], lit)
                    break
        return clause


class Solver():

    def __init__(self):
        self.variables = Types.VarDB()
        self.clauses = Types.ClauseDB()
        self.trail = Trail(self.variables, self.clauses)

    def BoolVar(self, *args, **kwargs):
        priority = kwargs.get('priority')
        try:
            del kwargs['priority']
        except KeyError:
            pass
        var = Types.BoolVar(*args, **kwargs)
        self.variables.add(var, priority)
        return var

    def Literal(self, *args, **kwargs):
        # a bit unuseful because we don't
        # register the literals
        lit = Types.Literal(*args, **kwargs)
        return lit

    def Clause(self, *args, **kwargs):
        clause = Types.Clause(*args, **kwargs)
        self.clauses.add(clause)
        return clause

    def clausal_propagate(self):
        try:
            raise Conflict(next(self.clauses.unsat_clauses()))
        except StopIteration:
            pass
        unit_clauses = list(self.clauses.unit_clauses())
        for clause, lit in unit_clauses:
            assert isinstance(clause, Types.Clause) and isinstance(
                lit, Types.Literal)
            self.trail.clausal_propagate(clause, lit)
        return unit_clauses

    def semantic_propagate(self):
        units = list(self.variables.watches.units())
        for elem, var in units:
            elem.propagate(self.trail, var)
            # self.watches.switch_false(var)
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
                logger.info('TRAIL:\n%s\n',
                            logger.pformat({var: (self.trail.values[var], self.trail.lvl[var]) for var in self.trail.values}))
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
            else:
                logger.info('TRAIL: %s\n',
                            logger.pformat(self.trail.values))
                if not self.variables.can_decide():
                    print('SAT')
                    return self.trail.values
                else:
                    var = self.variables.pop()
                    logger.info('DECiDE %s\n', var)
                    self.trail.decide(var, var.decide())
