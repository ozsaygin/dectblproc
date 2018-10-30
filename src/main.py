from collections import Counter
import numpy as np
import sys
import operator

def is_conditions_equal(i: int, j: int, conditions: list) -> bool:
    """
    :return:
    :rtype: bool
    :return:
    :param i:
    :param j:
    :type conditions: list
    """
    for char_index in range(len(conditions[i])):
        if conditions[i][char_index] == 'T' and conditions[j][char_index] == 'F':
            return False
        elif conditions[j][char_index] == 'T' and conditions[i][char_index] == 'F':
            return False
    return True


def calculate_remaining_rule_count(rules: list, conditions: list) -> int:
    total_valid_rules = 0
    for r in rules:
        total_valid_rules += pow(2, conditions[r - 1].count('-'))

    return total_valid_rules


def fix_index(lst):
    updated = []
    for t in lst:
        updated.append((t[0] + 1, t[1] + 1))
    return updated


# extract file to a buffer
filename = sys.argv[1]
f = open(filename).readlines()

# put results of conditions into a list for each rule

# get bool values of conditions
cond_arr = []
flag = False
for line in f:
    if line.startswith('##'):
        flag = True

    if line.startswith('c') and flag:
        cond_arr.append(list(line.split()[1]))

# print(cond_arr)  # debug

# and convert merge them to find conditions of each rule
merged_cond = []
for j in range(len(cond_arr[0])):
    s = ''
    for k in range(len(cond_arr)):
        s += cond_arr[k][j]
    merged_cond.append(s)

# print(merged_cond)  # debug

# get action as we get conditions above

# get char-by-char
act_arr = []
for line in f:
    if line.startswith('a'):
        act_arr.append(list(line.split()[1]))

# print(act_arr) # debug

# merge them to see actions for each rule
merged_act = []
for j in range(len(act_arr[0])):
    s = ''
    for k in range(len(act_arr)):
        s += act_arr[k][j]
    merged_act.append(s)

# print(merged_act)  # debug


# find redundants and inconsistencies WIP
# algorithm: pick a condition in order and compare it with conditions in its right
inconsistents = list()
redundants = list()

conditions = merged_cond.copy()
actions = merged_act.copy()

for i in range(len(conditions)):
    remaining_conditions = conditions[(i + 1):]
    for j in range(len(remaining_conditions)):
        actual_j = len(conditions) - len(remaining_conditions) + j
        if conditions[i] == remaining_conditions[j]:
            # certainly redundant or inconsistent
            if actions[i] == actions[actual_j]:
                # redundant
                redundants.append((i, actual_j))
            else:
                # inconsistent
                inconsistents.append((i, actual_j))
        else:
            if is_conditions_equal(i, actual_j, conditions):
                if actions[i] == actions[actual_j]:
                    # redundant
                    redundants.append((i, actual_j))
                else:
                    # inconsistent
                    inconsistents.append((i, actual_j))

is_redundant = False
is_inconsistent = False

if len(redundants) > 0:
    is_redundant = True

if len(inconsistents) > 0:
    is_inconsistent = True

# print('redundants: ', fix_index(redundants))
# print('inconsistents: ', fix_index(inconsistents))

# simplify decision table

total_conditions = pow(2, len(conditions[0]))
deleted_conditions = []

for p in fix_index(redundants):
    deleted_conditions.append(p[1])
for p in fix_index(inconsistents):
    deleted_conditions.append(p[1])

condition_count = len(conditions) - len(set(deleted_conditions))

# print(deleted_conditions) # debug

rules = list(range(1, len(conditions) + 1))
# print(rules) # debug

for r in set(deleted_conditions):
    rules.remove(r)

completeness = calculate_remaining_rule_count(rules, conditions) * 100 / total_conditions

print("Processing file: %s " % sys.argv[1])
print("Is table complete?  %d%% complete" % completeness)

if is_redundant:
    print("Is table redundant? %s" % "Yes")
    output = ""
    for pair in fix_index(redundants):
        output += "(r" + str(pair[0]) + ", r" + str(pair[1])  + "), "
    print("\t Redundant pairs of rules: %s" % output[:-2])
else:
    print("Is table redundant? %s" % "No")

if is_inconsistent:
    print("Is table inconsistent? %s" % "Yes")
    output = ""
    for pair in fix_index(inconsistents):
        output += "(r" + str(pair[0]) + ", r" + str(pair[1]) + "), "
    print("\t Inconsistent pairs of rules: %s" % output[:-2])
else:
    print("Is table inconsistent? %s" % "No")





### testing

from satispy import Variable, Cnf
from satispy.solver import Minisat



# algo: concatenate all expressions by & and check if the rule is satifiable

bool_exps = []
exps = []
symbols = []
for line in f:
    if line.startswith('##'):
        break

    if line.startswith('c'):
        bool_exps.append(line.split(":")[1][1:-1])

print(bool_exps)


from satispy import Variable, Cnf
from satispy.solver import Minisat
from satispy import CnfFromString
from satispy.solver import Minisat

expressions = []
for c in conditions:
    overall_expression = ""
    for i in range(len(bool_exps)):
        if c[i] == 'T': # true
            overall_expression += "(" + bool_exps[i] + ") & "
        elif c[i] == 'F': # false
            overall_expression += "-(" + bool_exps[i] + ") & "
    expressions.append(overall_expression[:-3])

print(expressions)


solver = Minisat()

solutions = []
symbols = None
for e in expressions:
    exp, symbols = CnfFromString.create(e)
    solutions.append(solver.solve(exp))
#
print("\n\n")
print("Testsuite")
print("=========")
#
#
#
out = ""
for v in sorted(list(symbols.keys()), key=str.lower):
    out += v + " "
print('    %s' % out)
print("    --------------")


for s in range(1, len(solutions)+1):
    solution = solutions[s-1]
    out = "r" + str(s) + ":\t"
    if s not in deleted_conditions:
        if solution.success:
            sorted_symbols = sorted(symbols.items(), key=operator.itemgetter(1))
            for t in sorted_symbols:
                out += str(solution[t[1]])[0] + "  "
            print(out)
        else:
            print(out + "unsatisfiable rule")

