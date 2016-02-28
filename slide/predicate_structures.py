# Michal Cyprian
#
# SL predicate expansion
#
# distributed under GNU GPL license


class Rule(object):
    """Class representing  one rule of the predicate"""
    def __init__(self, alloc, pointsto, calles, equal, not_equal):
        self.alloc = alloc
        self.pointsto = pointsto
        self.calles = calles
        self.equal = equal
        self.not_equal = not_equal

    @property
    def quadruple(self):
        return (self.alloc, self.pointsto, self.calles, self.equal)

    @property
    def quintuple(self):
        return (self.alloc, self.pointsto, self.calles, self.equal, self.not_equal)


class TopCall(object):
    """Class representing top call"""
    top_level_vars = set()

    def __init__(self, pred_name, call):
        self.pred_name = pred_name
        self.call = call
        self.expanded_rules = [Rule('', [], [(pred_name, call)], [], [])]
        TopCall.top_level_vars |= {var for var in self.call if var != 'nil'}


    @property
    def global_equal(self):
        return  [{rule.alloc: rule.equal} for rule in self.expanded_rules]

    @property
    def tuple_form(self):
        if self.call:
            return (self.pred_name, self.call)
        else:
            return tuple()
    
    @property
    def expanded_rules_tuple_form(self):
        return [rule.quintuple for rule in self.expanded_rules]

    def expand(self, pred, call_args):
        if self.expanded_rules == None:
            self.call = None
            self.expanded_rules = []
        self.expanded_rules += pred(call_args)


class Predicate(object):
    """Class representing one predicate including list of the rules"""
    uniq_id_counter = 0

    def __init__(self, name, args, rules):
        if not isinstance(rules, list):
            rules = [rules]
        self.name = name
        self.args = args        
        self.rules = rules

    @property
    def tuple_form(self):
        return (self.args, [rule.quintuple for rule in self.rules])

    @property
    def short_tuple_form(self):
        return (self.args, [rule.quadruple for rule in self.rules])


    def replace_var(self, args_doubles, var):
        """Returns name of argument to replace var in predicate expansion,
        adds _ prefix to avoid variable name collisions
        """
        try:
            return args_doubles[var]
        except KeyError:
            if var not in args_doubles.values():
                return var
            else:
                uniq_id = '{0}_{1}'.format(var, Predicate.uniq_id_counter)
                Predicate.uniq_id_counter += 1
                args_doubles.update({var : uniq_id})
                return uniq_id

    def __call__(self, arguments):
        """Replace variables with arguments of call and returns new rules"""
        args_doubles = dict(zip(self.args, arguments))
        args_doubles['nil'] = 'nil'

        expanded_rules = []
        for rule in self.rules:
            expanded_alloc = self.replace_var(args_doubles, rule.alloc)
            
            expanded_pointsto = [self.replace_var(args_doubles, var) for var in rule.pointsto]
                       
            expanded_calles = []
            for call in rule.calles:
                call_args = [self.replace_var(args_doubles, var) for var in call[1]]
                expanded_calles.append((call[0], call_args))

            if len(rule.equal) > 0 and isinstance(rule.equal[0], list):
                expanded_equal = []
                for eq in rule.equal:
                    expanded_equal.append([self.replace_var(args_doubles, eq[0]), 
                                           self.replace_var(args_doubles, eq[1])])
            else:
                expanded_equal = [self.replace_var(args_doubles, var) for var in rule.equal]
            expanded_not_equal = []
            for s in rule.not_equal:
                expanded_not_equal.append((self.replace_var(args_doubles, s[0]),
                                           self.replace_var(args_doubles, s[1])))

            expanded_rules.append(Rule(expanded_alloc, expanded_pointsto,
                                       expanded_calles, expanded_equal, 
                                       expanded_not_equal))

        return expanded_rules

