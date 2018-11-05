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

def generate_descendant_tree(seeds, length):
    """
    Generates the full ancestor tree.
    """
    # Start the game to track history
    game = Game(seeds, length)
    # Initialise the directed graph
    graph = nx.DiGraph()
    _pos = copy.deepcopy(game.state)
    seed = repr(game.state)
    graph.add_node(seed, object=_pos)
    # Recursively traverse the graph and add nodes/edges
    def _traverse_gaps(parent):
        for g in game.state.gaps:
            print("TRAVERSE: Adding {} to {}".format(g, parent))
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
                graph.add_node(name, object=_pos)
                graph.add_edge(parent, name)
                _traverse_gaps(name)
            # We are done with this play
            # Undo and continue
            game.undo()
    _traverse_gaps(seed)
    return graph

    

