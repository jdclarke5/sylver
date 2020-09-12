"""Algorithms for solving."""

from .backend import LocalBackend
from .error import LengthError

from sympy.ntheory.primetest import isprime


def solve(position, backend=None, reverse=False, deep=False, verbose=False):
    """General purpose solver.
    
    # TODO: try odd moves, then short evens, then longs

    Args:
        `backend`: Specify a backend to store/lookup results. By default this 
            method uses an internally instanced LocalBackend.
        `reverse`: Loop over gaps in reverse.
        `deep`: Loop over all gaps (hence finding all replies).
        `verbose`: Print all statuses encountered.
    """
    # Ensure a backend to store results
    backend = backend or LocalBackend()
    replies = set([])
    # Check backend or quick status
    status = quick(position, deep=deep) or backend.get_status(position)
    if status:
        pass
    # gcd = 1
    elif position.gcd == 1:
        position = position.reduce_length()
        for gap in position.gaps(reverse=reverse):
            child = position.add(gap)
            child_status = solve(child, backend=backend,
                reverse=reverse, deep=deep, verbose=verbose)
            if child_status == "P":
                status = "N"
                replies.add(gap)
                if not deep:
                    break
    # gcd > 1 and short
    elif position.irreducible == "s" and isprime(position.gcd):
        for gap in position.gaps(reverse=reverse):
            # No winning move greater than the frobenius (Quiet End Theorem)
            if gap > position.frobenius:
                continue
            child = position.add(gap)
            child_status = solve(child, backend=backend,
                reverse=reverse, deep=deep, verbose=verbose)
            if child_status == "P":
                status = "N"
                replies.add(gap)
                if not deep:
                    break
            elif child_status == "?":
                status = "?"
    # gcd > 1 and long
    else:
        #TODO: gcd==2 periodicity theorem
        print("{}: LONG".format(position))
        for gap in position.gaps(reverse=reverse):
            try:
                child = position.add(gap)
            except LengthError:
                continue
            child_status = solve(child, backend=backend,
                reverse=reverse, deep=deep, verbose=verbose)
            if child_status == "P":
                status = "N"
                replies.add(gap)
                if not deep:
                    break
            elif child_status == "?":
                status = "?"
        else:
            if not replies:
                print("WARNING: Unable to find reply to long position: {}"
                    .format(position))
                status = status or "?"
    # Save and return the results
    status = status or "P"
    backend.save(position, status, replies)
    if verbose:
        print("{} ({}): {}".format(status, replies or {}, position))
    return status

def quick(position, deep=False):
    """Quick tests for whether the position status is known."""
    if position.generators == [1]:
        return "N"
    # Return early if deep
    if deep:
        return
    # Note that [1] is irreducible (p) according to our definitions
    if position.gcd == 1 and position.irreducible \
            and position.generators != [2, 3]:
        return "N"
    if len(position.generators) == 1 and position.generators[0] > 3 \
            and isprime(position.generators[0]):
        return "P"
    # Hard-coded (gcd > 1) P positions
    # TODO: Solve these from first principles
    if position.generators == [8, 10, 22]:
        return "P"
    if position.generators == [8, 10, 12, 16]:
        return "P"
    if len(position.generators) == 4 and position.generators[:2] == [8, 12] \
            and position.generators[2] % 8 == 2 \
            and position.generators[3] == position.generators[2] + 4:
        return "P"
