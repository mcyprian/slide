"""Michal Cyprian

SL predicate expansion

distributed under GNU GPL license
"""

from copy import deepcopy

class CallsContainer(list):
    """Container to store TopCall objects, subclass of built-in list,
    overiding iter method to iterate over single rules of TopCalls
    """

    def __init__(self, initial_value=None, disjunction_check=False):
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
        self.disjunction_check = disjunction_check

    def append(self, element):
        if not isinstance(element, TopCall):
            raise TypeError("Only TopCall objects can be stored to XHSContainer")
        super(CallsContainer, self).append(element)

#    def __iter__(self):
#        self.call_index = 0
#        self.rule_index = -1
#        self.deleted = False
#        return self

    @property
    def rules_iter(self):
        """Iterates over single rules of calls"""

        self.call_index = 0
        self.rule_index = -1
        self.deleted = False

        while self:
            new_index = self.rule_index if self.deleted else self.rule_index + 1

            if new_index == len(self[self.call_index].expanded_rules):
                # end of current expanded_rules list
                self.rule_index = 0
                self.call_index += 1
                if self.call_index == self.__len__():
                    break
            else:
                self.rule_index = new_index

            self.deleted = False
            if self.disjunction_check and len(self[self.call_index].expanded_rules) > 1:
                raise NotImplementedError("Disjunction on LHS not implemented")

            yield self[self.call_index].expanded_rules[self.rule_index]
 
    @property
    def current_call(self):
        return self[self.call_index]

    @property
    def branch_calls(self):
        """Creates copies of self, with current call replaced with one part
        of disjunction."""
        calles = []
        for index, rule in enumerate(self.current_call.expanded_rules):
            call = deepcopy(self)
            call[self.call_index].expanded_rules = [self.current_call.expanded_rules[index]]
            calles.append(call)
        return calles

    def expand_current_call(self, preds, extension_rule=None):
        rule = self[self.call_index].expanded_rules[self.rule_index]
        self[self.call_index].expand(preds[rule.calles[0][0]],
                                     rule.calles[0][1],
                                     extension_rule)
        del self[self.call_index].expanded_rules[self.rule_index].calles[0]
        self.del_current_rule(if_empty=True)

    def del_current_rule(self, if_empty=False, remove_disjunctive=False):
        """Delete rule on current indexes, if if_empty is set current
        rule is removed only if it is empty.
        """
        if if_empty and not self.empty_rule(self[self.call_index].expanded_rules[self.rule_index]):
            return

        if remove_disjunctive:
            # Remove all other disjunctive parts of call
            self[
                self.call_index].expanded_rules = [
                self[
                    self.call_index].expanded_rules[
                    self.rule_index]]
            self.empty_first_rule()
        else:
            del self[self.call_index].expanded_rules[self.rule_index]
            self.del_current_call(if_empty=True)
        self.deleted = True

    def empty_first_rule(self):
        self[self.call_index].expanded_rules[0].alloc = ''
        self[self.call_index].expanded_rules[0].pointsto = []
        if self.empty_rule(self[self.call_index].expanded_rules[0]):
            del self[self.call_index].expanded_rules[0]
            self.del_current_call(if_empty=True)
            self.deleted = True

    def empty_first_call(self):
        self[self.call_index].expanded_rules[0].calles = []
        if self.empty_rule(self[self.call_index].expanded_rules[0]):
            del self[self.call_index].expanded_rules[0]
            self.del_current_call(if_empty=True)
            self.deleted = True

    def del_current_call(self, if_empty=False):
        if if_empty and self[self.call_index].expanded_rules:
            return
        del self[self.call_index]

    @property
    def calls_tuple_form(self):
        """Returns calls in form compatible with original structure
        represention of calles.
        """
        return [call.expanded_rules_tuple_form for call in self]

    @property
    def is_empty(self):
        """Indicates if object is completely empty (everithing was mapped) or
        not.
        """
        return not [rule for rule in self.rules_iter]

    @property
    def has_nodes(self):
        """Indicates if object contains any pointsto or predicate calls."""
        nodes = False
        for rule in self.rules_iter:
            if rule.alloc or rule.calles:
                nodes = True
        return nodes

    @property
    def remove_nodes_from_disjunction(self):
        """Removes parts of disjunction containing allocated nodes."""

        if not len(self[self.call_index].expanded_rules) > 1:
            return

        for rule in self.rules_iter:
            if rule.alloc:
                self.del_current_rule()

    @staticmethod
    def empty_rule(rule):
        if not isinstance(rule, Rule):
            raise TypeError("Argument rule must be instance of class Rule")
        return (not rule.alloc and not rule.pointsto and not rule.calles
                and not rule.equal and not rule.not_equal)


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
        self.expanded_rules = [Rule('', [], [(pred_name, call)], [], [])
                               ] if pred_name or call else []
        if self.call:
            TopCall.top_level_vars |= {var for var in self.call if var != 'nil'}

    @property
    def global_equal(self):
        return [{rule.alloc: rule.equal} for rule in self.expanded_rules]

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
        if self.expanded_rules is None:
            self.call = []
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
                args_doubles.update({var: uniq_id})
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
