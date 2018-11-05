"""
Algorithms for brute force autosearching for positions
"""

from game import Game

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

def generate_descendant_tree(seeds, length, verbose=False):
    """
    Generates the full game graph from a seed.
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
        for g in game.state.gaps:
            # Play an available move
            game.play(g)
            # Add this node/edge to graph
            _pos = copy.deepcopy(game.state)
            name = repr(_pos)
            # If already there, add the edge
            if graph.has_node(name):
                graph.add_edge(parent, name)
            # Otherwise add node, edge, and continue traverse
            else:
                graph.add_node(name, position=_pos)
                graph.add_edge(parent, name)
                _traverse_gaps(name)
            # We are done with this play
            # Undo and continue
            game.undo()
    _traverse_gaps(seed)
    return graph

def determine_winners(graph):
    """
    Finds P/N status of nodes from a full game graph.
    """
    # This algorithm traverses the graph multiple, each time
    # filling in what it can, until it is done.
    def _traverse():
        complete = True
        for name, data in graph.nodes.items():
            # Skip if already known
            if data.get("winner"):
                continue
            complete = False
            # Set irreducibles (except [2,3]) to N, including [1]
            _pos = data["position"]
            if (_pos.is_irreducible == True and _pos.generators.tolist() != [2, 3]):
                data["winner"] = "N"
                print("N (irreducible) : {}".format(repr(_pos)))
                continue
            # If unknown has one child P, then it's N.
            # If unknown has all children N, then it's P.
            for child in graph.successors(name):
                if graph.nodes[child].get("winner") == "P":
                    data["winner"] = "N"
                    print("N (child is P)  : {}".format(repr(_pos)))
                    break
                if graph.nodes[child].get("winner") != "N":
                    break
            else:
                # No break, so must be P
                data["winner"] = "P"
                print("P (child all N) : {}".format(repr(_pos)))
        return complete
    # Loop until we are complete
    iter = 1
    while True:
        print("Traverse iteration: {}".format(iter))
        if _traverse():
            break
        iter = iter + 1
         
