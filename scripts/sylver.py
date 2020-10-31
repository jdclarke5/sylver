"""
Python translation of the `sylver.pl` script written by Col. George Sicherman.
The original is at https://userpages.monmouth.com/~colonel/sylver/index.html.
This was done as an exercise in order to understand the approach taken by
Sicherman. Where possible, the original varable names, comments, order and logic 
have been kept. This means we sometimes choose to use globals against better
practices for python. Some comments are added for clarity. Stream mode is not 
implemented.
"""

import argparse
from bitarray import bitarray
from functools import reduce
import math
from sympy.ntheory.primetest import isprime
import warnings

def mainsolve(arg, mflag=False, v=False, allflag=False, u=None):

    # Check validity of inputs
    for number in arg:
        if number < 2:
            raise ValueError("Numbers must be greater than 1")

    # Eliminate duplicates (and sort)
    arg = sorted(set(arg))

    # Determine the GCD and check against -m flag
    global g
    g = int(reduce(math.gcd, arg))
    if g > 1 and not mflag:
        raise ValueError("You must specify -m if g > 1")
    if g == 1 and mflag:
        warnings.warn("g = 1, ignoring -m")

    # Print position
    print("# {}".format(" ".join([str(a) for a in arg])))

    # Determine the position and t
    global precision
    global t
    if g == 1:
        t = syltop(arg)
        # If t is 1 we are at the end-game
        if t == 1:
            print("P")
            exit()
        precision = 1 + t // 32
    else:
        precision = mflag
        t = precision * 32 - 1

    # NOTE: The init() func is run here to ensure empty is set
    global empty
    global safe
    global canned1
    empty, safe, canned1 = init()

    string = empty.copy()
    for move in arg:
        string = make(move, string)

    # Print g (and t, and if quiet ender)
    tag = "# g={}".format(g)
    if g == 1:
        tag += ", t={}".format(t)
        if quiet(string):
            tag += " quiet ender"
    print(tag)

    # If it's a known long P-position, and -v isn't specified,
    # just print "P" and exit.
    if (not v and safe.get(string.to01()) and arg[0] != 12):
        print("P")
        exit()

    global ufile
    ufile = u
    global vflag
    vflag = v
    solve(1, allflag, string) or print("P")

def init():
    # NOTE: Not sure why factor of 4 is here?
    global empty
    global safe
    empty = bitarray(4 * precision * 32)
    empty.setall(0)
    safe = {}
    canned1 = {2: [3], 3: [2], 4: [6], 6: [4,9],
		8: [12], 10: [5,14,26]}
    if g == 2:
        addsafe([4, 6], [8, 10, 22], [8, 10, 12, 14],
			[8,12,18,22], [8,12,26,30], [8,12,34,38],
			[8,12,42,46], [8,12,50,54])
    if g == 3:
        addsafe([6, 9], [12, 15, 18], [12, 18, 21])
    if g == 4:
        addsafe([8,12])
    return empty, safe, canned1

def addsafe(*safes):
    for s in safes:
        spos = empty.copy()
        for m in s:
            spos = make(m, spos)
        # NOTE: Sicherman doesn't store safe positions which have a 0 where
        # the string already has a 1, i.e. 1 in (~spos & string). This is an 
        # optimisation not implemented here.
        safe[spos.to01()] = 1

def solve(printflag, allflag, pos):
    retval = 0
    pair = empty.copy()

    # Is this position a single value?
    for b in range(1, t + 1):
        if pos[b]:
            break
    if pos == make(b, empty):
        return solve1(printflag, allflag, b)

    # Is it {2, 3}?
    if pos[:4].to01() == "0011":
        return 0
    
    # To save time, check for an instant winner
    for x in range(2, t + 1):
        if pos[x]:
            continue
        if safe.get(make(x, pos).to01()):
            return x
    
    fuse = 0
    bomb = -1
    for x in range(2, t + 1):
        if pos[x]:  # Not a legal move
            # NOTE: The fuse gets set to the smallest taken number. If we ever
            # get more than this many illegal moves in a row then we are done,
            # since everything after must be a 1.
            fuse = fuse or x    # Measure the fuse
            bomb -= 1
            if bomb == 0:
                break
            continue
        bomb = fuse # Light the fuse
        if pair[x]: # Eliminated by pairing
            continue
        newpos = make(x, pos)
        issafe = safe.get(newpos.to01())
        if (not issafe):
            response = solve(0, 0, newpos)
        if (not issafe and response):
            if response > x:
                pair[response] = 1
            if printflag and vflag:
                # Print it as a clique if appropriate.
                if response > x:
                    clique = 1
                else:
                    rpos = make(response, pos)
                    # NOTE: Clique if x is not clobbered by response
                    clique = not rpos[x]
                print(("({}, {})" if clique else "{}? {}!").format(x, response))
        else:
            # NOTE: This means it is safe but may not be in the list
            if not issafe:
                safe[newpos.to01()] = 1
                if ufile:
                    with open(ufile, "a+") as f:
                        f.write(zdisp(newpos))
            printflag and print("{}!".format(x))
            if not allflag:
                return x
            retval = retval or x
    return retval

def syltop(arg):
    """arg: Position as a sorted set of numbers."""
    # NOTE: Largest possible t based on largest two generators
    top = (arg[-1] - 1) * (arg[-2] - 1) - 1
    # NOTE: Original script has `my $vec = chr(0) x $tprecision`, which just
    # means to create a bit array from stringing together 32-bit "longwords".
    tprecision = 1 + top // 32
    vec = bitarray(tprecision * 32)
    vec.setall(0)
    global t
    t = top
    for move in arg:
        vec = make(move, vec)
    # NOTE: Decrement top until a 0 is found
    while top > 1 and vec[top]:
        top -= 1
    return top

def solve1(printflag, allflag, b):
    sols = canned1.get(b)
    if sols:
        if printflag:
            for sol in sols:
                print("{}!".format(sol))
                if not allflag:
                    break
        return sols[0]
    if isprime(b):
        return 0
    raise ValueError("Cannot solve {{{}}}".format(b))

def make(move, pos):
    """Make a move in a position. NOTE: Doesn't touch original bitarray."""
    pos = pos.copy()
    pos[move] = 1
    # NOTE: Loop over whole pos length (not just t) to ensure pos ends in 1s
    for i in range(2, len(pos) - move):
        if pos[i] == 0:
            continue
        pos[move + i] = 1
    return pos

def quiet(string):
    """Is a position a quiet ender? This algorithm uses the characterization 
    that no two legal moves sum to t."""
    # Find highest legal move
    post = t
    while post > 0 and string[post]:
        post -= 1
    t2 = t // 2
    for i in range(1, t2 + 1):
        if not string[i] and not string[post-i]:
            print(i)
            return 0
    return 1

def zdisp(pos):
    """Returns the string list of generators (including 0)."""
    r = ""
    goal = empty.copy()
    for b in range(0, t + 1):
        if not (pos[b] and not goal[b]):
            continue
        r += "{} ".format(b)
        goal = make(b, goal)
    return r + "0\n"

if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="sylver - compute winning "
        "moves in Sylver Coinage.\nIf g.c.d. > 1, you can get erroneous "
        "results from setting the precision too low.")
    parser.add_argument("-a", action="store_true", 
        help="Show all winning moves")
    parser.add_argument("-m", type=int, help="Set precision to N longwords")
    parser.add_argument("-u", type=str, help="Write P-positions to file")
    parser.add_argument("-v", action="store_true", 
        help="Show losing moves and replies")
    parser.add_argument("arg", nargs="+", type=int, help="Numbers")
    args = parser.parse_args()

    mainsolve(args.arg, mflag=args.m, v=args.v, allflag=args.a, u=args.u)