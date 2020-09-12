"""Tests for package."""

from sylver.position import Position
from sylver.solve import solve

import pytest

verbose = True

def test_solve_1():
    position = Position([1])
    assert solve(position, verbose=verbose) == "N"
    position = Position([1], length=100)
    assert solve(position, verbose=verbose) == "N"

def test_solve_2():
    position = Position([2])
    assert solve(position, verbose=verbose) == "N"
    position = Position([2], length=100)
    assert solve(position, verbose=verbose) == "N"

def test_solve_2_3():
    position = Position([2, 3])
    assert solve(position, verbose=verbose) == "P"
    position = Position([2, 3], length=100)
    assert solve(position, verbose=verbose) == "P"

def test_solve_4():
    position = Position([4])
    assert solve(position, verbose=verbose) == "N"
    position = Position([4], length=100)
    assert solve(position, verbose=verbose) == "N"

def test_solve_5():
    position = Position([5])
    assert solve(position, verbose=verbose) == "P"
    position = Position([5], length=100)
    assert solve(position, verbose=verbose) == "P"

def test_solve_6():
    position = Position([6])
    assert solve(position, verbose=verbose) == "N"
    position = Position([6], length=100)
    assert solve(position, verbose=verbose) == "N"

def test_solve_7():
    position = Position([7])
    assert solve(position, verbose=verbose) == "P"
    position = Position([7], length=100)
    assert solve(position, verbose=verbose) == "P"

# def test_solve_8():
#     position = Position([8])
#     assert solve(position, verbose=verbose) == "?"
#     position = Position([8], length=100)
#     assert solve(position, verbose=verbose) == "N"

def test_solve_9():
    position = Position([9])
    assert solve(position, verbose=verbose) == "N"
    position = Position([9], length=100)
    assert solve(position, verbose=verbose) == "N"

def test_solve_10():
    position = Position([10])
    assert solve(position, verbose=verbose) == "N"
    position = Position([10], length=100)
    assert solve(position, verbose=verbose) == "N"

def test_8_12_18_22_41():
    """This position exposed a irreducible bug in a previous version."""
    position = Position([8, 12, 18, 22, 41])
    assert solve(position, verbose=verbose) == "N"
    position = Position([8, 12, 18, 22, 41], length=100)
    assert solve(position, verbose=verbose) == "N"

def test_solve_6_9():
    position = Position([6, 9])
    assert solve(position, verbose=verbose) == "P"
    position = Position([6, 9], length=100)
    assert solve(position, verbose=verbose) == "P"

# def test_solve_8_12():
#     position = Position([8, 12])
#     assert solve(position, verbose=verbose) == "?"
#     position = Position([8, 12], length=1000)
#     assert solve(position, verbose=verbose) == "P"

# def test_solve_8_12_18():
#     """Test that short position is N."""
#     position = Position([8, 12, 18])
#     assert solve(position, verbose=verbose) == "N"
#     position = Position([8, 12, 18], length=1000)
#     assert solve(position, verbose=verbose) == "N"