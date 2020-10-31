"""
Sylver coinage command line utility.
"""

import argparse

from sylver import position, solve, backend, error

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Sylver coinage CLI.")
    parser.add_argument("seeds", type=int, nargs="+",
        help="Positive integer position seeds.")
    parser.add_argument("-l", "--length", type=int, default=None,
        help="Length to use for underlying bit array.")
    parser.add_argument("-b", "--backend", type=str, default=None,
        choices=["redis", "postgres"], 
        help="Persistent backend to use for storing/retrieving results.")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="Solve verbosely.")
    parser.add_argument("-d", "--deep", action="store_true",
        help="Solve deeply, i.e. don't stop traverse when P position found.")
    parser.add_argument("-r", "--reverse", action="store_true",
        help="Traverse gaps in reverse (i.e. descending) order.")
    args = parser.parse_args()

    if args.backend == "redis":
        from sylver.backend.redis import RedisBackend
        backend = RedisBackend(host="localhost", port=6379)
    elif args.backend == "postgres":
        from sylver.backend.postgres import PostgresBackend
        backend = PostgresBackend("postgres://sylver:sylver@localhost:5432/sylver")
    else:
        backend = None

    pos = position.Position(args.seeds, length=args.length)
    print(f"Solving position: {pos.to_dict()}")

    sol = solve.solve(pos, verbose=args.verbose, backend=backend, 
        deep=args.deep, reverse=args.reverse)
    print(f"Solution: {sol}")
