import sys

from satispy import CnfFromString
from satispy.solver import Minisat


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


def generate_test_suite(conditions: list, expressions: list, discarded_conditions: list):
    """
    :param conditions: list of conditions in string form
    :param expressions: list of boolean expression corresponding to each condition existing
    :param discarded_conditions: list of conditions which will be discarded
    """
    for c in conditions:
        overall_expression = ""
        for i in range(len(expressions)):
            if c[i] == 'T':  # true
                overall_expression += "(" + expressions[i] + ") & "
            elif c[i] == 'F':  # false
                overall_expression += "-(" + expressions[i] + ") & "
        expressions(overall_expression[:-3])

    solver = Minisat()
    solutions = list()
    sym_junkyard = list()

    for e in expressions:
        exp, symbols = CnfFromString.create(e)
        sym_junkyard += list(symbols.keys())
        solutions.append(solver.solve(exp))

    print("\n\n")
    print("Testsuite")
    print("=========")

    out = ""
    for v in sorted(list(set(sym_junkyard)), key=str.lower):
        out += v + " "
    print('   \t    %s' % out)
    print("   \t--------------")

    for s in range(1, len(solutions) + 1):
        solution = solutions[s - 1]
        out = "r" + str(s) + ":\t"
        if s not in discarded_conditions:
            if solution.success:
                exp, symbols = CnfFromString.create()
                sol = solver.solve(expressions[s - 1])
                for var in sym_junkyard:
                    out += str(solution[t[1]])[0] + "  "
                print(out)


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
        discarded_conditions.append(p[1])

    for p in increment_pair(inconsistent):
        discarded_conditions.append(p[1])

    condition_count = len(conditions) - len(set(discarded_conditions))
    rule_indices = list(range(1, len(conditions) + 1))

    for r in set(discarded_conditions):
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

    # generate_test_suite(conditions, expressions, discarded_conditions)


main(sys.argv)
