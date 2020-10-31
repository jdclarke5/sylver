"""
Server for sylver web application.
"""

from sylver import error, position, solve
from sylver.backend.redis import RedisBackend

from flask import (
    Flask,
    jsonify,
    request,
)

from multiprocessing import Pool, Process, Queue

# Initialise the backend
backend = RedisBackend(host="localhost", port=6379)

class Pool():
    """Worker pool for solving unknown positions in the background 
    in separate processes."""
    
    def __init__(self, num_workers):
        self.num_workers = num_workers
        self.processes = []
        self.positions = []
    
    def solve(self, pos):
        solve.solve(pos, verbose=False, backend=backend, 
            deep=False, reverse=False)
    
    def submit(self, pos):
        if pos.name in self.positions:
            print(f"Already submitted position for solving: {pos}")
            return
        print(f"Submitted position for solving: {pos}")
        # Trim processes to `num_workers`
        self.processes = [p for p in self.processes if p.is_alive()]
        if len(self.processes) == self.num_workers:
            print("Terminating a solver process")
            self.processes[0].terminate()
            self.processes = self.processes[1:]
            self.positions = self.positions[1:]
        # Start a solve process
        p = Process(target=self.solve, args=(pos,), daemon=True)
        p.start()
        self.processes.append(p)
        self.positions.append(pos.name)

solver_pool = Pool(4)

app = Flask(__name__)

@app.route("/api/get", methods=["GET"])
def get():
    """
    Request parameters:
        input ([int]): Array of integers for seeds of position.
        length (int): Length of bitarray to use.
        children (bool): Whether to fetch children.
    """
    params = request.args.to_dict()
    print(f"Request received: {params}")
    try:
        # Create position
        seeds = [int(i) for i in params["input"].split(",")]
        length = int(params["length"]) if params.get("length") else None
        pos = position.Position(seeds, length=length)
        # Fetch status from backend
        status = solve.quick(pos) or backend.get_status(pos) or "?"
        # If unknown status submit to the solver pool
        if status == "?":
            solver_pool.submit(pos)
        # Construct response
        response = {
            **pos.to_dict(),
            "status": status,
            "bitarray": pos.bitarray.tolist(),
        }
        # Get the status of children
        if params.get("children"):
            children = {}
            for gap in pos.gaps():
                try:
                    child = pos.add(gap)
                except error.LengthError:
                    break
                status = solve.quick(child) or backend.get_status(child) or "?"
                children[str(gap)] = {
                    **child.to_dict(), 
                    "status": status,
                }
            response["children"] = children
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(response)
