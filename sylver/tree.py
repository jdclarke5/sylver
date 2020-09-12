"""Game tree (graph) representation."""

import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout


def tree(position):
    """Generates full game graph/tree from initial (gcd=1) position. This is an
    acyclic directed graph.
    """
    if position.gcd > 1:
        raise ValueError("Position gcd must be equal to 1")
    # Initialise the directed graph
    graph = nx.DiGraph()
    node = graph.add_node(position.name, position=position)
    # Recursively add child nodes
    def add_child_nodes(position):
        for gap in position.gaps():
            child = position.add(gap)
            if not graph.has_node(child.name):
                graph.add_node(child.name, position=child)
                add_child_nodes(child)
            graph.add_edge(position.name, child.name, name=gap)
    add_child_nodes(position)
    return graph

def plot(tree, include_1=False):
    """Plot the game tree."""
    if not include_1:
        tree = tree.copy()
        tree.remove_node("{1}")
    pos = graphviz_layout(tree, prog="dot")
    plt.gcf().clear()
    colors = [{"P": "green", "N": "red", None: "gray"}.get(n.get("status"))
        for _, n in tree.nodes.items()]
    edge_labels = {edge: data["name"] for edge, data in tree.edges.items()}
    nx.draw(tree, pos, arrows=True, with_labels=True, font_size=8,
        node_color=colors)
    nx.draw_networkx_edge_labels(tree, pos, edge_labels=edge_labels, 
        label_pos=0.8, font_size=6, alpha=0.7)
    return plt

def solve(tree):
    """Find P/N for all nodes on game tree."""
    # Set {1} as N
    tree.nodes["{1}"]["status"] = "N"
    # Iteratively traverse, filling in P/N
    def traverse():
        complete = True
        for name, data in tree.nodes.items():
            status = data.get("status")
            # Skip if already known
            if status:
                continue
            complete = False
            # If has one child P, then it's N
            # If has all children N, then it's P
            for child in tree.successors(name):
                child_status = tree.nodes[child].get("status")
                if not child_status:
                    break
                if child_status == "P":
                    print("{}: N".format(name))
                    data["status"] = "N"
                    break
            else:
                print("{}: P".format(name))
                data["status"] = "P"
        return complete
    # Loop until we are complete
    iteration = 0
    while not traverse():
        iteration = iteration + 1
        print("Traverse iteration: {}".format(iteration))
    print("Done!")
