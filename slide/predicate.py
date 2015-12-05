# Michal Cyprian
#
# SL predicate expansion and mapping
#
# distributed under GNU GPL license

def replace_var(args_doubles, var):
    '''
    Returns name of argument to replace var in predicate expansion,
    adds _ prefix to avoid variable name collisions
    '''
    try:
        return args_doubles[var]
    except KeyError:
        if var not in args_doubles.values():
            return var
        else:
            return '_' + var


class Rule(object):
    '''
    Class representing  one rule of the predicate
    '''
    def __init__(self, alloc, pointsto, calles, equal, not_equal):
        self.alloc = alloc
        self.pointsto = pointsto
        self.calles = calles
        self.equal = equal
        self.not_equal = not_equal

    @property
    def quadruple(self):
        return (self.alloc, self.pointsto, self.calles, self.equal)


class Predicate(object):
    '''
    Class representing one predicate including list of the rules
    '''
    def __init__(self, name, args, rules):
        self.name = name
        self.args = args
        self.rules = rules

    @property
    def tuple_form(self):
        return (self.args, [rule.quadruple for rule in self.rules])

    def expand(self, top_call):
        args_doubles = dict(zip(self.args, top_call[0][1]))
        args_doubles['nil'] = 'nil'

        expanded_rules = []
        for rule in self.rules:
            expanded_alloc = args_doubles[rule.alloc]
            
            expanded_pointsto = [replace_var(args_doubles, var) for var in rule.pointsto]
                       
            expanded_calles = []
            for call in rule.calles:
                call_args = [replace_var(args_doubles, var) for var in call[1]]
                expanded_calles.append((call[0], call_args))

            expanded_equal = [replace_var(args_doubles, var) for var in rule.equal]
            expanded_not_equal = [replace_var(args_doubles, var) for var in rule.not_equal]

            expanded_rules.append(Rule(expanded_alloc, expanded_pointsto,
                                       expanded_calles, expanded_equal, 
                                       expanded_not_equal))

        return Predicate('expanded', top_call[0][1], expanded_rules)

