# Michal Cyprian
#
# SL predicate expansion
#
# distributed under GNU GPL license

class CallsContainer(list):
    """Container to store TopCall objects, subclass of built-in list,
    overiding iter method to iterate over single rules of TopCalls
    """

    def __init__(self, initial_value=None):
        if initial_value is None:
            initial_value = []
        try:
            for elem in initial_value:
                if not isinstance(elem, TopCall):
                    raise TypeError("Only TopCall objects can be stored to CallsContainer")
        except TypeError:
            if not isinstance(initial_value, TopCall):
                raise TypeError("Only TopCall objects can be stored to CallsContainer")

        super(CallsContainer, self).__init__(initial_value)
        self.call_index = 0
        self.rule_index = -1
        self.deleted = False

    def append(self, element):
        if not isinstance(element, TopCall):
            raise TypeError("Only TopCall objects can be stored to XHSContainer")
        super(CallsContainer, self).append(element)

    def __iter__(self):
        self.call_index = 0
        self.rule_index = -1
        self.deleted = False
        return self

    def next(self):
        """Iterates over single rules of calls"""
        new_index = self.rule_index if self.deleted else self.rule_index + 1

        if new_index == len(self[self.call_index].expanded_rules):
            # end of current expanded_rules list
            self.rule_index = 0
            self.call_index += 1
            if self.call_index == self.__len__():
                # end of self list
                raise StopIteration
        else:
            self.rule_index = new_index
        print("\n\nCall index {} rule index {}".format(self.call_index,
                self.rule_index))

        self.deleted = False
        return self[self.call_index].expanded_rules[self.rule_index]

    def del_current_rule(self):
        del self[self.call_index].expanded_rules[rule_index]
        self.deleted = True

    @property
    def calls_tuple_form(self):
        """Returns calls in form compatible with original structure
        represention of calles.
        """
        index = 0
        calls_list = []
        while index < self.__len__():
            calls_list.append(self[index])
            index += 1

        return [call.tuple_form for call in calls_list]


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

    def __init__(self, pred_name='', call=None):
        self.pred_name = pred_name
        self.call = call
        self.expanded_rules = [Rule('', [], [(pred_name, call)], [], [])] if pred_name or call else []
        if self.call:
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

    def expand(self, pred, call_args, extension_rule=None):
        if self.expanded_rules == None:
            self.call = None
            self.expanded_rules = []
        self.expanded_rules += pred(call_args, extension_rule)


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

    def __call__(self, arguments, extension_rule):
        """Replace variables with arguments of call and returns new rules"""
        args_doubles = dict(zip(self.args, arguments))
        args_doubles['nil'] = 'nil'
        if extension_rule and not isinstance(extension_rule, Rule):
            raise TypeError("extension rule must be Rule object.")

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
            if extension_rule:
                expanded_equal += extension_rule.equal
                expanded_not_equal += extension_rule.not_equal

            expanded_rules.append(Rule(expanded_alloc, expanded_pointsto,
                                       expanded_calles, expanded_equal, 
                                       expanded_not_equal))

        return expanded_rules

