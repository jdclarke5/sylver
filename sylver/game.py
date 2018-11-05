"""
Tracks the history of a game; allows infinite undos.
"""

import position

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

    def undo(self):
        """
        Roll back to the previous state
        """
        if len(self.history) == 1:
            raise ValueError("Reached first move, cannot undo!")
        self.history = self.history[:-1]

