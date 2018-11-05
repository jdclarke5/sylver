"""
This module defines the position class.
"""

from functools import reduce
import json
import math
import numpy as np
    

class Position(object):
    """
    Positions are the primary objects in the game of Sylver Coinage.
    They represent a unique state of gameplay. Currently we only
    implement logic for a semigroup (position with gcd=1).
    A numerical semigroup is a subset S of the integers N
    closed under addition and with N\S finite.
    """

    def __init__(self, seeds, length, verbose=True):
        """
        Initialise the position.

        Args:
            seeds: a list of positive integers that are equivalent to
                numbers that have been played.
            length: length of array for brute force calculations.
        """
        self.verbose = verbose
        # Parse the seeds for validity
        seeds = self._parse_seeds(seeds)
        # Initialise some properties
        self.length = length
        self.generators = np.array([], dtype=np.int32)
        self.members_array = np.zeros(self.length, dtype=np.bool)
        self.members_array[0] = True
        # Add the seeds determine members and generators
        for s in seeds:
            self._add(s)
        # Check for and set Frobenius number
        self._check_sufficient_length()
        self._set_frobenius()
        # Check irreducibility
        self._check_irreducible()

        # # Get coordinates, i.e. the m-tuple (with m the 
        # # multiplicity of S) with i'th entry equal to the 
        # # least element e in S such that e mod m = i
        # self.coordinates = self.apery_set(self.multiplicity)
        # # Get the special/lonely gaps
        # # This takes the most compute
        # if find_gaps:
        #     self.special_gaps = self._get_special_gaps()
        #     self.lonely_gaps = self._get_lonely_gaps()
        #     self.ender_gaps = self._get_ender_gaps()
        # else:
        #     self.special_gaps = None
        #     self.lonely_gaps = None
        #     self.ender_gaps = None

        # Print the string representation
        if self.verbose:
            print(self)

    def __repr__(self):
        return "Position({}, {})".format(
            self.generators.tolist(),
            self.length
        )

    def __str__(self):
        return json.dumps(self.asdict(), indent=2)

    @property
    def gaps(self):
        return np.where(self.members_array==0)[0]

    @property
    def embedding_dim(self):
        """Returns the cardinality of the minimal set of generators."""
        return len(self.generators)

    @property
    def genus(self):
        """Returns cardinality of the set of gaps."""
        return self.length-np.count_nonzero(self.members_array)

    @property
    def multiplicity(self):
        """Returns least positive integer belonging to P."""
        return np.min(self.generators)

    def asdict(self):
        """Returns dict of properties"""
        # Convert numpy arrays to lists
        return {
            "generators": self.generators.tolist(),
            "frobenius": self.frobenius,
            "is_irreducible": self.is_irreducible,
            "irreducible_type": self.irreducible_type,
            "multiplicity": int(self.multiplicity),
            "genus": self.genus,
            "gaps": self.gaps.tolist(),
            # "antisymm_fails": self.antisymm_fails.tolist(),
            # "coordinates": self.coordinates.tolist(),
            # "special_gaps": self.special_gaps.tolist() if self.special_gaps is not None else None,
            # "lonely_gaps": self.lonely_gaps.tolist() if self.lonely_gaps is not None else None,
            # "ender_gaps": self.ender_gaps.tolist() if self.ender_gaps is not None else None,
        }

    def add(self, n):
        """
        Add a number to the position.
        """
        self._add(n)
        self._set_frobenius()
        self._check_irreducible()
        if self.verbose:
            print("Added {}".format(n))
            print(repr(self))
            print(self)

    def apery_set(self, n):
        """
        Returns the Apery set of S with respect to n, i.e.
        the n-tuple with i'th entry equal to the least element 
        e in S such that e mod n = i.
        """
        ntuple = np.zeros(n).astype(np.int32)
        for i in range(n):
            # Filter to list all numbers with which are i mod n
            submembers = self.members_array[i::n]
            # Find first True
            for j, status in enumerate(submembers):
                if status:
                    ntuple[i] = n*j+i
                    break
        return ntuple

    def _parse_seeds(self, seeds):
        """
        Determine if the seeds are valid.
        """
        # Return sorted unique integer elements
        seeds = np.unique(seeds).astype(np.int32)
        # Seeds must be a list of positive integers
        if len(seeds) < 1:
            raise ValueError("Seeds must have at least one element.")
        if not (seeds>0).all():
            raise ValueError("Seeds cannot contain non-positive integers")
        # Not a numerical semigroup if the GCD is not 1
        gcd = reduce(math.gcd, seeds)
        if gcd != 1:
            raise ValueError(
                "gcd({})={} is not 1. ".format(seeds, gcd)
            )
        return seeds

    def _add(self, n):
        """
        Add a number n to the members; alter members array and
        generators accordingly. Does not recalculate properties
        (see exposed "add" method for this).
        """
        # Skip if invalid number
        n = int(n)
        if n <= 0:
            raise ValueError("Number must be a positive integer")
        if self.members_array[n]:
            raise ValueError("Number is not in play")
        # Keep track of generators which will stay after addition
        gens_dict = {}
        for g in self.generators:
            if g < n: 
                gens_dict[g] = True
            if g > n: 
                gens_dict[g] = False
        # Loop through members from the beginning
        for i, status in enumerate(self.members_array):
            # Fill out Trues n steps ahead of existing Trues
            if status:
                self.members_array[i::n] = True
                # Flag generators to include as necessary.
                # A smaller number n has eliminated a larger number m as
                # a generator only if all numbers which were eliminated by m 
                # are now eliminated by n.
                for m, b in gens_dict.items():
                    if b:
                        continue
                    if (i-m >= 0 and 
                        self.members_array[i-m] == True and
                        self.members_array[i-n] == False):
                        gens_dict[m] = True
        # Reset the generators
        gens = [g for g, b in gens_dict.items() if b] + [n]
        self.generators = np.unique(gens).astype(np.int32)

    def _check_sufficient_length(self):
        """
        Checks if the length of the members_array is large enough
        for consistent computation by our brute force methods.
        Require max(generators) Trues at the end of the members_array.
        """
        if not self.members_array[-max_gen:].all():
            raise ValueError("Length insufficient; must be Frobenius + max(gens) + 1 long!")

    def _set_frobenius(self):
        """
        Sets the Frobenius number; assumes that the length of 
        members_array is long enough to contain it (i.e. that 
        _check_sufficient_length has been run during init).
        """
        # Travel from the end and return the first 0 found
        for i, status in enumerate(np.flip(self.members_array,0)):
            if status==0:
                self.frobenius = self.length-i-1
                break
            else:
                self.frobenius = 0
        # Set sufficient length for members_array so that
        # future brute force computations are quicker
        self.length = int(self.frobenius + np.max(self.generators) + 1)
        #self.length = self.frobenius + 1
        self.members_array = self.members_array[:self.length]

    def _check_irreducible(self):
        """
        Checks and sets self.is_irreducible and self.irreducible_type
        which indicates whether the semigroup is irreducible.
        Irreducible type is one of: '' (unset), 's' (symmetric),
        or 'p' (pseudosymmetric).
        """
        # Get the array to the Frobenius number
        array_to_frob = np.copy(self.members_array[:self.frobenius+1])
        rvrse_to_frob = np.flip(array_to_frob, 0)
        length = len(array_to_frob)
        # If length is odd then append middle number to failures list
        fails = [self.frobenius/2] if (self.frobenius%2)==0 else []
        return_string = "pseudosymm" if (self.frobenius%2)==0 else "symm"
        # Check for antisymmetry
        # The floor/ceil removes middle val if odd in length
        symm = (
            np.append(array_to_frob[:math.floor(length/2)],array_to_frob[math.ceil(length/2):])
            == np.append(rvrse_to_frob[:math.floor(length/2)],rvrse_to_frob[math.ceil(length/2):])
        )
        fails = np.append(np.where(symm==True)[0], fails).astype(np.int32)

        # TODO: Potentially return the failures
        antisymm_fails = np.intersect1d(fails, self.gaps)
        if symm.any():
            # If any are true then not completely antisymmetric
            self.is_irreducible = False
            self.irreducible_type = ""
        else:
            self.is_irreducible = True
            self.irreducible_type = return_string

    # def _get_special_gaps(self):
    #     """Returns the gaps x such that S union {x} is a
    #     numerical semigroup"""

    #     gaps = self.gaps
    #     not_special = np.array([]).astype(np.int32)

    #     for i, gap in enumerate(gaps):
    #         # Does the lower gap eliminate any higher gaps?
    #         # If it does then it's not special!
    #         for higher_gap in gaps[i+1:]:
    #             # Eliminates if a True is multiple of gaps away
    #             if self.members_array[higher_gap::-gap].any():
    #                 not_special = np.append(not_special, gap)
    #                 break
        
    #     # Return difference of gaps and not_specials
    #     return np.setdiff1d(gaps, not_special)

    # def _get_lonely_gaps(self):
    #     """Returns the gaps x that are eliminated by
    #     all of the smaller gaps"""

    #     gaps = self.gaps
    #     not_lonely = np.array([]).astype(np.int32)

    #     for i, gap in enumerate(gaps):
    #         # Is the higher gap not eliminated by a lower gap?
    #         # If so then it's not lonely!
    #         for lower_gap in gaps[:i]:
    #             # Eliminates if a True is multiple of lower_gaps away
    #             if not self.members_array[gap::-lower_gap].any():
    #                 not_lonely = np.append(not_lonely, gap)
    #                 break
        
    #     # Return difference of gaps and not_lonelys
    #     return np.setdiff1d(gaps, not_lonely)

    # def _get_ender_gaps(self):
    #     """Returns the gaps x which, when added to the generators, 
    #     create an irreducible numerical semigroup (an ender)"""

    #     gaps = self.gaps
    #     ender_gaps = np.array([], dtype=np.int32)

    #     for i, gap in enumerate(gaps):
    #         # Get the members_array with gap added
    #         # and get the Frobenius as a bonus
    #         array = np.copy(self.members_array)
    #         frobenius = 0
    #         for i, status in enumerate(array):
    #             if status:
    #                 array[i::gap] = True
    #             else:
    #                 frobenius = i
    #         # Add if irreducible
    #         if self._check_irreducible(members_array=array, frobenius=frobenius)[0]:
    #             ender_gaps = np.append(ender_gaps, gap)

    #     return ender_gaps
