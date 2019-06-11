"""
Tracks the history of a game; allows infinite undos.
"""

from . import position

import copy


class Game():
    """
    Manages the game history.
    """
    def __init__(self, seeds, length, verbose=True):
        """
        Initialised in the same way as a position.
        """
        self.history = [position.Position(seeds, length, verbose=verbose)]
        self.numbers_played = []

    @property
    def state(self):
        return self.history[-1]

    def play(self, n):
        """
        Play a given number
        """
        _pos = copy.deepcopy(self.state)
        _pos.add(n)
        self.history.append(_pos)
        self.numbers_played.append(n)

    def undo(self):
        """
        Roll back to the previous state
        """
        if len(self.history) == 1:
            raise ValueError("Reached first move, cannot undo!")
        self.history = self.history[:-1]
        self.numbers_played = self.numbers_played[:-1]

