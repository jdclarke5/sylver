"""
Algorithms for brute force autosearching for positions
"""

from .game import Game

import copy
import networkx as nx


def get_children(position):
    """
    Generates the tree of a semigroup to immediate children.
    """
    children = []
    for g in position.gaps:
        _pos = copy.deepcopy(_pos)
        _pos.add(g)
        children.append(_pos)

def generate_descendant_tree(
    seeds, 
    length,
    database=None,
    trimmed=True,
    verbose=False,
):
    """
    Generates the full game graph from seeds and 
    length (i.e. an initial position).

    Args:
        `database`: Retrieve and store results in pymongo database.
        `trimmed`: Only generate to leaves with known status.
    """
    # Start the game to track history
    game = Game(seeds, length, verbose=verbose)
    # Initialise the directed graph
    graph = nx.DiGraph()
    _pos = copy.deepcopy(game.state)
    seed = repr(game.state)
    graph.add_node(seed, position=_pos)
    # Recursively traverse the graph and add nodes/edges
    def _traverse_gaps(parent):
        if verbose:
            print(parent)
        for g in game.state.gaps:
            # Play an available move
            game.play(g)
            # Add this node/edge to graph
            _pos = copy.deepcopy(game.state)
            name = repr(_pos)
            # If already there, add the edge
            if graph.has_node(name):
                graph.add_edge(parent, name)
            # Otherwise add node, edge, and (possibly) continue traverse
            else:
                graph.add_node(name, position=_pos)
                graph.add_edge(parent, name)
                # Add node status if available in database
                if database is not None:
                    _node = database["positions"].find_one({"_repr": name}, {"status": 1})
                    if _node is not None and _node.get("status"):
                        _pos.status = _node["status"]
                # Set irreducibles (except [2,3]) to N, including [1]
                if (_pos.is_irreducible == True and 
                        _pos.generators.tolist() != [2, 3] and
                        _pos.gcd == 1):
                    _pos.status = "N"
                # Stop traversing if trimmed and status
                if not (trimmed and _pos.status):
                    _traverse_gaps(name)
            # We are done with this play
            # Undo and continue
            game.undo()
    # Begin the traverse
    _traverse_gaps(seed)
    return graph

def determine_status(
    graph,
    database=None,
):
    """
    Finds P/N status of nodes from a graph. 
    If database set then stores results.
    """
    # This algorithm traverses the graph multiple, each time
    # filling in what it can, until it is done.
    def _traverse():
        complete = True
        for name, data in graph.nodes.items():
            _pos = data["position"]
            # Stop iF gcd not 1
            if _pos.gcd > 1:
                raise ValueError("Method cannot handle GCD greater than 1")
            # Skip if already known
            if _pos.status:
                continue
            complete = False
            # Set irreducibles (except [2,3]) to N, including [1]
            if (_pos.is_irreducible == True and 
                    _pos.generators.tolist() != [2, 3] and
                    _pos.gcd == 1):
                _pos.status = "N"
                print("N (irreducible) : {}".format(repr(_pos)))
                continue
            # If unknown has one child P, then it's N.
            # If unknown has all children N, then it's P.
            for child in graph.successors(name):
                _child = graph.nodes[child].get("position")
                if _child.status == "P":
                    _pos.status = "N"
                    print("N (child is P)  : {}".format(repr(_pos)))
                    break
                if _child.status != "N":
                    break
            else:
                # No break, so must be P
                _pos.status = "P"
                print("P (child all N) : {}".format(repr(_pos)))
        return complete
    # Loop until we are complete
    iter = 1
    while True:
        print("Traverse iteration: {}".format(iter))
        if _traverse():
            break
        iter = iter + 1
    # Store results
    if database is not None:
        print("Storing results...")
        for _, data in graph.nodes.items():
            data["position"].store(database)
