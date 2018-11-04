import unittest

from dectblproc.dectblproc import *


class TestDectblproc(unittest.TestCase):
    def test_is_conditions_equal(self):
        self.assertEqual(is_conditions_equal(0, 1, ["TTT", "TT-"]), True)

    def test_calculate_remaining_rule_count(self):
        self.assertEqual(calculate_remaining_rule_count(["TTT, TF-, FFF"], list(range(1, 9))), True)
