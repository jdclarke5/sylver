"""
This module defines the position class.
"""

from functools import reduce
import math
import numpy as np

import matplotlib.pyplot as plt


class Position(object):
    """Positions are the primary objects in the game of Sylver Coinage.
    They represent a unique state of gameplay."""

    def __init__(self, l):
        """Instanced with a list of integers."""
        # zero must be in the set
    

class Semigroup(object):
    """A numerical semigroup is a subset S of the integers N
    closed under addition and with N\S finite. At the moment,
    everything below is automatically calculated by brute force
    with an upper limit to the size of the gaps."""

    def __init__(self, l, length, find_gaps=True):
        """Instanced with a list of integers, and a length
        specifying the max length to use for brute force
        calculations of the properties."""
        
        # Return sorted unique integer elements of l
        self.l = np.unique(l).astype(np.int32)

        if len(self.l) < 1:
            raise ValueError("l must have at least one element.")
        if not (self.l>0).all():
            raise ValueError("l cannot contain non-positive integers")

        self.length = length
        if self.length < max(self.l):
            raise ValueError("Length must be greater than all " 
                "sorted unique integer members of l"
            )

        # Not a numerical semigroup if the GCD is not 1
        self.gcd = reduce(math.gcd, l)
        if self.gcd != 1:
            raise ValueError(
                "gcd({})={} is not 1. " 
                "Please try again.".format(self.l, self.gcd)
            )

        # Brute force find the members of the semigroup
        self.members_array, self.generators = \
            self._get_members_and_generators()

        # Check for and return Frobenius number
        self.frobenius = self._get_frobenius()

        # Check if irreducible
        self.is_irreducible, self.irreducible_type = \
            self._check_irreducible()

        # Get coordinates, i.e. the m-tuple (with m the 
        # multiplicity of S) with i'th entry equal to the 
        # least element e in S such that e mod m = i
        self.coordinates = self.apery_set(self.multiplicity)

        # Get the special/lonely gaps
        # This takes the most compute
        if find_gaps:
            self.special_gaps = self._get_special_gaps()
            self.lonely_gaps = self._get_lonely_gaps()
            self.ender_gaps = self._get_ender_gaps()
        else:
            self.special_gaps = None
            self.lonely_gaps = None
            self.ender_gaps = None

        # Print a summary
        self.print_properties()

    def print_properties(self):
        """Prints the auto-calculated properties summary"""
        print(
            " l: {}"
            "\n generators: {}"
            "\n frobenius: {}"
            "\n genus: {}"
            "\n is_irreducible: {}"
            "\n irreducible_type: {}"
            #"\n coordinates: {}"
            "\n special_gaps: {}"
            "\n lonely_gaps: {}"
            "\n ender_gaps: {}"
            .format(
                self.l,
                self.generators,
                self.frobenius,
                self.genus,
                self.is_irreducible,
                self.irreducible_type,
                #self.coordinates,
                self.special_gaps,
                self.lonely_gaps,
                self.ender_gaps)
        )

    def _get_members_and_generators(self):
        """Returns the members of the semigroup as an array
        of True/False, with length given by length. 
        Note that if length is not large enough the Frobenius 
        number may not be included. Also finds the
        generators as it goes."""

        # Instance arrays
        generators = np.array([], dtype=np.int32)
        array = np.zeros(self.length, dtype=np.bool)
        
        # Fill every entry that is 0 mod l[0] with a True
        array[::self.l[0]] = True
        generators = np.append(generators, self.l[0])
        # Loop through the array for every n
        for n in self.l[1:]:
            # Skip if number already in members
            if array[n]:
                continue
            generators = np.append(generators, n)
            # Fill out Trues n steps ahead of existing Trues
            for i, status in enumerate(array):
                if status:
                    array[i::n] = True

        return array, generators

    def _get_frobenius(self):
        """Gets the Frobenius number if the length is long enough.
        Otherwise let the user know to increase the length."""

        # TODO: Special cases:
        #  two generators 
        #  arithmetic sequence
        #  geometric sequence
        #  three generators

        if not self._check_sufficient_length():
            raise ValueError("Length insufficient for Frobenius number")

        # Just travel from the end and return the first 0 found
        for i, status in enumerate(np.flip(self.members_array,0)):
            if status==0:
                return self.length-i-1
    
    def _check_sufficient_length(self):
        """Checks if Frobenius number is in the members_array."""
        
        # If there are max_generator Trues at the end of the
        # members_array then the length is sufficient
        # to contain the Frobenius number
        max_gen = np.max(self.generators)
        if self.members_array[-max_gen:].all():
            return True

        # The Frobenius number might still be in there...
        # To be really sure extend members_array by max_gen
        # and ask the same question again
        array = np.append(self.members_array, np.zeros(max_gen, dtype=np.bool))
        for n in self.generators:
            # Only bother to look forward from previous last n values
            for i, status in enumerate(array[-max_gen-n:]):
                if status:
                    array[-max_gen-n+i::n] = True

        if array[-max_gen:].all():
            return True
        
        return False

    def _check_irreducible(self, members_array=None, frobenius=None):
        """Returns one of three possible tuples indicating
        whether the numerical semigroup is irreducible:
        (False, None), (True, "symm"), (True, "pseudosymm")."""

        members_array = members_array if members_array is not None else self.members_array
        frobenius = frobenius if frobenius is not None else self.frobenius

        # Get the array to the Frobenius number
        array_to_frobenius = np.copy(members_array[:frobenius+1])

        # If frobenius is even remove the middle value
        # Since antisymmetry will fail at middle point
        if frobenius % 2 == 0:
            array_to_frobenius = np.delete(array_to_frobenius, [frobenius/2])
            potential_return_string = "pseudosymm"
        else:
            potential_return_string = "symm"
        
        # Check for antisymmetry
        if (array_to_frobenius == np.invert(np.flip(array_to_frobenius,0))).all():
            return True, potential_return_string
        else:
            return False, None

    def _get_special_gaps(self):
        """Returns the gaps x such that S union {x} is a
        numerical semigroup"""

        gaps = self.gaps
        not_special = np.array([]).astype(np.int32)

        for i, gap in enumerate(gaps):
            # Does the lower gap eliminate any higher gaps?
            # If it does then it's not special!
            for higher_gap in gaps[i+1:]:
                # Eliminates if a True is multiple of gaps away
                if self.members_array[higher_gap::-gap].any():
                    not_special = np.append(not_special, gap)
                    break
        
        # Return difference of gaps and not_specials
        return np.setdiff1d(gaps, not_special)

    def _get_lonely_gaps(self):
        """Returns the gaps x that are eliminated by
        all of the smaller gaps"""

        gaps = self.gaps
        not_lonely = np.array([]).astype(np.int32)

        for i, gap in enumerate(gaps):
            # Is the higher gap not eliminated by a lower gap?
            # If so then it's not lonely!
            for lower_gap in gaps[:i]:
                # Eliminates if a True is multiple of lower_gaps away
                if not self.members_array[gap::-lower_gap].any():
                    not_lonely = np.append(not_lonely, gap)
                    break
        
        # Return difference of gaps and not_lonelys
        return np.setdiff1d(gaps, not_lonely)

    def _get_ender_gaps(self):
        """Returns the gaps x which, when added to the generators, 
        create an irreducible numerical semigroup (an ender)"""

        gaps = self.gaps
        ender_gaps = np.array([], dtype=np.int32)

        for i, gap in enumerate(gaps):
            # Get the members_array with gap added
            # and get the Frobenius as a bonus
            array = np.copy(self.members_array)
            frobenius = 0
            for i, status in enumerate(array):
                if status:
                    array[i::gap] = True
                else:
                    frobenius = i
            # Add if irreducible
            if self._check_irreducible(members_array=array, frobenius=frobenius)[0]:
                ender_gaps = np.append(ender_gaps, gap)

        return ender_gaps

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

    def apery_set(self, n):
        """Returns the Apery set of S with respect to n, i.e.
        the n-tuple with i'th entry equal to the least element 
        e in S such that e mod n = i."""

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

    def plot(self, n=None):
        """Plot the members_array wrapping with height of n"""

        n = n or self.multiplicity

        # Add 1's to end of array so reshape will work
        remainder = n - (self.length % n)
        array = np.pad(self.members_array, 
            (0,remainder), 
            "constant", 
            constant_values=True)
        # Reshape
        reshaped_array = array.reshape([-1,n]).transpose()

        plt.imshow(reshaped_array, cmap='hot', interpolation='nearest')
        plt.show()
        
