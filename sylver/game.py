"""
Tracks the history of a game.
"""

class Game():
    """
    Manages the game history.
    """

    def __init__(self, position):
        """Initialised with a `position.Position` object.
        """
        self.history = [position]
        self.numbers_played = []

    @property
    def state(self):
        return self.history[-1]

    def play(self, n):
        """Play a given number.
        """
        position = self.state.add(n)
        self.history.append(position)
        self.numbers_played.append(n)

    def undo(self):
        """Roll back to the previous state. Inifinite undos are allowed (the
        initial position is never removed).
        """
        if len(self.history) == 1:
            return
        self.history = self.history[:-1]
        self.numbers_played = self.numbers_played[:-1]
