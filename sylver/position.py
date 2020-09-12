
from .error import LengthError

from bitarray import bitarray
from copy import deepcopy
from functools import reduce
import math
import warnings

class Position(object):
    """Positions are the primary objects in the game of Sylver Coinage. They 
    represent a unique state of gameplay. When the gcd of the given seeds is
    1, tthis corresponds to semigroup. A numerical semigroup is a subset 
    S of the integers N closed under addition and with N\S finite. When
    the gcd is greater than 1, all given values are with respect to the slice
    array[::gcd], which we call the reduced semigroup. This generalises the 
    concept of the semigroup.
    """

    def __init__(self, seeds, length=None):
        """
        Initialise the position.

        Args:
            seeds ([int]): a list of positive integers that are equivalent to 
                numbers that have been played.
            length (int, optional): length of array for brute force 
                calculations.
        """

        # Sorted unique integers
        seeds = sorted(set([int(s) for s in seeds]))
        # Seeds must be a list of positive integers
        if len(seeds) < 1:
            raise ValueError("Seeds must have at least one element.")
        if any([s < 1 for s in seeds]):
            raise ValueError("Seeds cannot contain non-positive integers")
        self._seeds = seeds 

        # Determine gcd
        self._set_gcd()

        # Set length of the bitarray.
        # If length not set take a length that is the minimum given generator
        # longer than the maximum possible Frobenius.
        if not length:
            if len(self._seeds) > 1:
                max_gcd1_frobenius = (self._seeds[-1] / self.gcd - 1) \
                    * (self._seeds[-2] / self.gcd - 1) - 1
            else:
                max_gcd1_frobenius = 0
            self.length = self.gcd * int(max_gcd1_frobenius) \
                + min(self._seeds) + self.gcd
        else:
            self.length = length

        # Initialise and fill the bitarray
        self.generators = []
        self.bitarray = bitarray(self.length)
        self.bitarray.setall(0)
        self.bitarray[0] = 1
        for s in self._seeds:
            self._add(s)

        # Set the frobenius number and throw error if insufficient length
        self._set_frobenius()

        # Set the irreducible type
        self._set_irreducible()

    def __repr__(self):
        return "Position({})".format(self.generators)

    def __str__(self):
        generators = "{}".format(self.generators)
        return "{{{}}}".format(generators[1:-1])

    @property
    def name(self):
        return str(self)
    
    @property
    def embedding_dim(self):
        """Returns the cardinality of the minimal set of generators."""
        return len(self.generators)

    @property
    def genus(self):
        """Returns cardinality of the set of gaps."""
        return (~self.bitarray[::self.gcd]).count()

    @property
    def multiplicity(self):
        """Returns least positive integer belonging to P."""
        return min(self.generators)
    
    def gaps(self, reverse=False):
        """Returns an iterator over the gaps."""
        if not reverse:
            for i, b in enumerate(self.bitarray):
                if not b: 
                    yield i 
        else:
            for i, b in enumerate(self.bitarray[::-1]):
                if not b: 
                    yield self.length - 1 - i

    def to_dict(self):
        """Returns dict of properties."""
        return {
            "generators": self.generators,
            "gcd": self.gcd,
            "multiplicity": self.multiplicity,
            "genus": self.genus,
            "frobenius": self.frobenius,
            "irreducible": self.irreducible,
        }

    def copy(self):
        """Return a copy of this object."""
        return deepcopy(self)

    def add(self, n, inplace=False):
        """Add a number to the position, i.e. make a move. This will return a
        new object and leave this object alone, unless inplace is set.

        Args:
            n (int): The number to add.
            inplace (bool): Whether to modify the Position in place.
        
        Returns:
            pos (Position): Resulting Position object.
        """
        n = int(n)
        if n < 1:
            raise ValueError("Cannot add a non-positive integer")
        if inplace:
            pos = self
        else:
            pos = deepcopy(self)
        pos._add(n)
        pos._seeds = pos.generators
        pos._set_gcd()
        pos._set_frobenius()
        pos._set_irreducible()
        return pos

    def apery_set(self, n):
        """Returns the Apery set of S with respect to n, i.e. the n-tuple 
        with i'th entry equal to the least element e in S such that 
        (e mod n) = i.
        """
        ntuple = [0] * n
        for i in range(n):
            subarray = self.bitarray[::self.gcd][i::n]
            ntuple[i] = (n * subarray.index(1) + i) * self.gcd
        return ntuple
    
    def reduce_length(self, mod=1):
        """Remove extraneous 1s from end of bitarray. This can improve speed
        for future computations.
        
        Args:
            mod (int): Mandates that length must be an integer multiple of mod. 
        """
        self.length = self.frobenius + min(self.generators) + self.gcd
        self.length = (self.length // mod + 1) * mod
        self.bitarray = self.bitarray[:self.length]
        return self

    def _set_gcd(self):
        """Set the GCD and throw a warning if not 1.
        """
        self.gcd = int(reduce(math.gcd, self._seeds))
        if self.gcd != 1:
            print("WARNING: gcd({})={} is not 1.".format(self._seeds, self.gcd))
    
    def _add(self, n):
        # Skip if already a member
        if self.bitarray[n]:
            return
        # Fill members n steps ahead of existing
        for i, bit in enumerate(self.bitarray):
            if not bit:
                continue
            self.bitarray[i::n] = 1
        # Keep generators which are smaller than n, and those that eliminate
        # members which n does not.
        self.generators = sorted([g for g in self.generators if g < n or
            (self.bitarray[:-g] & ~self.bitarray[g-n:-n]).any()] + [n])
    
    def _set_frobenius(self):
        # Check sufficient length
        min_gen = int(min(self.generators)/self.gcd)
        if not self.bitarray[::self.gcd][-min_gen:].all():
            suggestion = (self.generators[-1] / self.gcd - 1) \
                * (self.generators[-2] / self.gcd - 1) - 1
            raise LengthError("{}: Length insufficient! Must be at least "
                "(frobenius + min(generators) + gcd) long! A length of {:.0f} "
                "(but potentially smaller) will do.".format(self, suggestion))
        # Frobenius is first 0 from the end
        try:
            reduced_array = self.bitarray[::self.gcd]
            self.frobenius = ( len(reduced_array) \
                - reduced_array[::-1].index(0) - 1 ) * self.gcd
        except ValueError as e:
            if str(e) == "0 is not in bitarray":
                self.frobenius = 0
            else:
                raise e
    
    def _set_irreducible(self):
        """Checks and sets `self.irreducible` which indicates whether the 
        semigroup is irreducible. Irreducible is one of: None, 's' (symmetric),
        or 'p' (pseudosymmetric).
        """
        reduced_frob = int(self.frobenius / self.gcd)
        half_frob = (reduced_frob + 1) // 2
        # Check for antisymmetry around half frobenius
        left = self.bitarray[::self.gcd][:half_frob]
        right = self.bitarray[::self.gcd][:reduced_frob + 1][::-1][:half_frob]
        if left != ~right:
            self.irreducible = None
        else:
            self.irreducible = "s" if (reduced_frob % 2) else "p"