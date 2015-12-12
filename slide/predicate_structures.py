# Michal Cyprian
#
# SL predicate expansion
#
# distributed under GNU GPL license

import collections

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


class TopCall(object):
    '''
    Class representing top call
    '''
    def __init__(self, pred_name, call, expanded_rules = None):
        self.pred_name = pred_name
        self.call = call
        self.expanded_rules = expanded_rules

    @property
    def global_equal(self):
        return  [{rule.alloc: rule.equal} for rule in self.expanded_rules]

    @property
    def tuple_form(self):
        return (self.pred_name, self.call)
    
    @property
    def expanded_rules_tuple_form(self):
        return [rule.quadruple for rule in self.expanded_rules]

    def expand(self, pred):
        self.expanded_rules = pred(self.call)


class Predicate(object):
    '''
    Class representing one predicate including list of the rules
    '''
    def __init__(self, name, args, rules):
        if not isinstance(rules, list):
            rules = [rules]
        self.name = name
        self.args = args        
        self.rules = rules

    @property
    def tuple_form(self):
        return (self.args, [rule.quadruple for rule in self.rules])

    def __call__(self, arguments):
        '''
        Replace variables with arguments of call and return new rules
        '''
        args_doubles = dict(zip(self.args, arguments))
        args_doubles['nil'] = 'nil'

        expanded_rules = []
        for rule in self.rules:
            expanded_alloc = replace_var(args_doubles, rule.alloc)
            
            expanded_pointsto = [replace_var(args_doubles, var) for var in rule.pointsto]
                       
            expanded_calles = []
            for call in rule.calles:
                call_args = [replace_var(args_doubles, var) for var in call[1]]
                expanded_calles.append((call[0], call_args))

            if isinstance(rule.equal, list):
                expanded_equal = []
                for eq in rule.equal:
                    expanded_equal.append([replace_var(args_doubles, eq[0]), 
                                           replace_var(args_doubles, eq[1])])
            else:
                expanded_equal = [replace_var(args_doubles, var) for var in rule.equal]
            expanded_not_equal = []
            for s in rule.not_equal:
                expanded_not_equal.append((replace_var(args_doubles, s[0]),
                                           replace_var(args_doubles, s[1])))

            expanded_rules.append(Rule(expanded_alloc, expanded_pointsto,
                                       expanded_calles, expanded_equal, 
                                       expanded_not_equal))

        return expanded_rules

