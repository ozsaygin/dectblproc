from collections import Counter
import numpy as np
import sys


def is_conditions_equal(i, j, conditions):
    for char_index in range(len(conditions[i])):
        if conditions[i][char_index] == 'T' and conditions[j][char_index] == 'F':
            return False
        elif conditions[j][char_index] == 'T' and conditions[i][char_index] == 'F':
            return False
    return True


def calculate_remaining_rule_count(rules, conditions):
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
    print("\t Redundant pairs of rules: %s" % str(fix_index(redundants))[1:-1])
else:
    print("Is table redundant? %s" % "No")

if is_inconsistent:
    print("Is table inconsistent? %s" % "Yes")
    print("\t Inconsistent pairs of rules: %s" % str(fix_index(inconsistents))[1:-1])
else:
    print("Is table inconsistent? %s" % "No")

### testing

# from satispy import CnfFromString
# from satispy.solver import Minisat
#
# bool_exps = []
# exps = []
# symbols = []
# for line in f:
#     if line.startswith('##'):
#         break
#
#     if line.startswith('c'):
#         bool_exps.append(line.split()[1])
#
# for e in bool_exps:
#     exp, symbol = CnfFromString.create(e)
#     exps.append(exp)
#     symbols.append(symbol)
#
#
# solver = Minisat()
#
# solution = solver.solve(exp)
#
# if solution.success:
#     for symbol_name in symbols.keys():
#         print("%s is %s" % (symbol_name, solution[symbols[symbol_name]]))
# else:
#     print("The expression cannot be satisfied")
#
#
# print("Testsuite")
# print("=========")
# print("\t ")