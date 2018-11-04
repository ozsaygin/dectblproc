import sys
from typing import List

from satispy import CnfFromString
from satispy.solver import Minisat
from tabulate import tabulate


def is_conditions_equal(first_index: int, second_index: int, conditions_list: list) -> bool:
    """
    :return: Returns true if conditions are logically equal, otherwise false
    :param first_index: Index of first condition
    :param second_index: Index of second condition
    :param conditions_list: List containing conditions for each rule
    """
    for char_index in range(len(conditions_list[first_index])):
        if conditions_list[first_index][char_index] == 'T' and conditions_list[second_index][char_index] == 'F':
            return False
        elif conditions_list[second_index][char_index] == 'T' and conditions_list[first_index][char_index] == 'F':
            return False
    return True


def calculate_remaining_rule_count(rules: list, conditions: list) -> int:
    """
    :param rules: indices of rules
    :param conditions: conditions of each rule with/without don't care conditions
    :return: returns list of unique rules by removing redundant rules due to don't cares
    """
    total_valid_rules = 0
    for r in rules:
        total_valid_rules += pow(2, conditions[r - 1].count('-'))

    return total_valid_rules


def increment_pair(lst: list) -> list:
    """
    :param lst: list of tuples to be incremented by one
    :return: returns a list of pairs incremented by one
    """
    updated = list()
    for t in lst:
        updated.append((t[0] + 1, t[1] + 1))
    return updated


def merge_values(val_lst: list) -> list:
    """
    :param val_lst: list of list which contains char versions of actions/conditions
    :return: returns a list of strings by merging chars from input list
    """
    merged_lst = list()
    for value in range(len(val_lst[0])):
        temp = ""
        for char in range(len(val_lst)):
            temp += val_lst[char][value]
        merged_lst.append(temp)
    return merged_lst


def replace_char(condition, char_index, char):
    """

    :param condition:
    :param char_index:
    :param char:
    :return:
    """
    condition = list(condition)
    condition[char_index] = char
    return ''.join(condition)


def expand_all_conditions(conditions: List[str]) -> List[str]:
    """

    :param conditions: list contains a condition with at least one don't care value
    :return: returns list of conditions containing expanded version of original condition by considering don't cares
    """
    expanded_conditions = list()
    for c in conditions:
        char_index = c.find('-')
        if char_index >= 0:
            conditions.append(replace_char(c, char_index, 'T'))
            conditions.append(replace_char(c, char_index, 'F'))

    return [c for c in conditions if c.count('-') == 0]


def generate_test_suite(conditions: list, expressions: list, discarded_conditions: list) -> list:
    """
    :param conditions: list of conditions in string form
    :param expressions: list of boolean expression corresponding to each condition existing
    :param discarded_conditions: list of conditions which will be discarded
    :return: returns list of lists containing row values for test suite table
    """

    expression_problems = list()
    for c in conditions:
        if c.count('-') > 0:  # if there is any don't care condition
            expanded_conditions = expand_all_conditions([c])
            rule_expression = ""
            for exp_c in expanded_conditions:
                for char_index in range(len(exp_c)):
                    if exp_c[char_index] == 'T':  # condition is true
                        rule_expression += "(" + expressions[char_index] + ") & "
                    elif exp_c[char_index] == 'F':  # condition is false
                        rule_expression += "-(" + expressions[char_index] + ") & "
                rule_expression += "(" + rule_expression[:-3] + ") | "
            expression_problems.append(rule_expression[:-3])

        else:  # there is no don't care condition
            rule_expression = ""
            for char_index in range(len(c)):
                if c[char_index] == 'T':  # condition is true
                    rule_expression += "(" + expressions[char_index] + ") & "
                elif c[char_index] == 'F':  # condition is false
                    rule_expression += "-(" + expressions[char_index] + ") & "
            expression_problems.append(rule_expression[:-3])

    solutions = list()
    solver = Minisat()
    exp = None
    symbols = dict()
    table = list()
    for p in range(len(expression_problems)):
        exp, symbols = CnfFromString.create(expression_problems[p])
        solution = solver.solve(exp)
        rule_name = "r" + str(p + 1)
        boolean_values = [rule_name]
        if solution.success:
            for symbol_name in sorted(symbols.keys()):
                boolean_values.append(str(solution[symbols[symbol_name]])[0])
            if p + 1 not in discarded_conditions:
                table.append(boolean_values)

    headers = ["rules"] + sorted(symbols.keys())
    print(tabulate(table, headers, tablefmt="fancy_grid"))


def main(argv):
    # extract file to a buffer
    filename = sys.argv[1]
    buffer = open(filename).readlines()

    # get bool values of conditions
    condition_char_arr = list()
    action_char_arr = list()
    is_expressions_extracted = False
    expressions = list()
    tmp = list()

    for line in buffer:  # get char-by-char
        if line.startswith('##'):
            is_expressions_extracted = True

        if line.startswith('c') and not is_expressions_extracted:  # Is an expression?
            expressions.append(line.split(":")[1][1:-1])

        if line.startswith('a'):  # Is an action?
            action_char_arr.append(list(line.split()[1]))

        if line.startswith('c') and is_expressions_extracted:  # Is an condition?
            condition_char_arr.append(list(line.split()[1]))

    conditions = merge_values(condition_char_arr)
    actions = merge_values(action_char_arr)  # merge them to see actions for each rule

    inconsistent = list()
    redundant = list()

    # compare each condition with all conditions linearly
    for i in range(len(conditions)):
        remaining_conditions = conditions[(i + 1):]
        for j in range(len(remaining_conditions)):
            actual_j = len(conditions) - len(remaining_conditions) + j
            if conditions[i] == remaining_conditions[j]:  # certainly redundant or inconsistent
                if actions[i] == actions[actual_j]:  # redundant
                    redundant.append((i, actual_j))
                else:  # inconsistent
                    inconsistent.append((i, actual_j))
            else:
                if is_conditions_equal(i, actual_j, conditions):
                    if actions[i] == actions[actual_j]:  # redundant
                        redundant.append((i, actual_j))
                    else:  # inconsistent
                        inconsistent.append((i, actual_j))

    # simplify decision table

    total_conditions = pow(2, len(conditions[0]))
    discarded_conditions = []

    # always picks right element in tuple to discard
    for p in increment_pair(redundant):
        if conditions[p[0] - 1].count('-') > conditions[p[1] - 1].count('-'):
            discarded_conditions.append(p[1])
        else:
            discarded_conditions.append(p[0])

    for p in increment_pair(inconsistent):
        if conditions[p[0] - 1].count('-') > conditions[p[1] - 1].count('-'):
            discarded_conditions.append(p[1])
        else:
            discarded_conditions.append(p[0])

    discarded_conditions = set(discarded_conditions)
    rule_indices = list(range(1, len(conditions) + 1))

    for r in discarded_conditions:
        rule_indices.remove(r)

    completeness = calculate_remaining_rule_count(rule_indices, conditions) * 100 / total_conditions

    # print out stats about decision table

    print("Processing file: %s " % sys.argv[1])
    print("Is table complete?  %d%% complete" % completeness)

    if len(redundant) > 0:
        print("Is table redundant? %s" % "Yes")
        output = ""
        for pair in increment_pair(redundant):
            output += "(r" + str(pair[0]) + ", r" + str(pair[1]) + "), "
        print("\t Redundant pairs of rules: %s" % output[:-2])
    else:
        print("Is table redundant? %s" % "No")

    if len(inconsistent) > 0:
        print("Is table inconsistent? %s" % "Yes")
        output = ""
        for pair in increment_pair(inconsistent):
            output += "(r" + str(pair[0]) + ", r" + str(pair[1]) + "), "
        print("\t Inconsistent pairs of rules: %s" % output[:-2])
    else:
        print("Is table inconsistent? %s" % "No")

    # generating a test suite
    # concatenate all expressions by & operator and check if the rule is satisfiable

    print("Testsuite")
    print("=========")

    # discarded conditions in human readable indices
    generate_test_suite(conditions, expressions, discarded_conditions)
    # print(tabulate(header, generate_test_suite(conditions, expressions, discarded_conditions)))
    # print(tabulate)


main(sys.argv)
