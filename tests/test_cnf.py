from pathlib import Path

import pytest

from mcSATan.parsers.DIMACS import parse_cnf



folder = Path(__file__).parent / 'cnf'
tests = [
    ('php10.cnf', False),
    ('php32.cnf', False),
    ('php33.cnf', True),
    ('php54.cnf', False),
    ('php77.cnf', True),
    ('php88.cnf', True),
    ('php1414.cnf', True),
    ('simple_v3_c2.cnf', True),
]

@pytest.mark.parametrize("name,ans", tests)
def test_cnf(name, ans):
    f = folder / name
    solver = parse_cnf(f.open())
    assert (solver.solve() is not False) == ans
    