import textwrap
from typing import List

from regraph.backends.networkx.graphs import NXGraph
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
import matplotlib.pyplot as plt
import numpy as np
import ast


def get_successor_list(G: NXGraph, node_id: int) -> List[int]:
    positions = {}
    for child in G.successors(node_id):
        (pos,) = G.get_node(child)["pos"]
        positions[child] = pos

    children = list(G.successors(node_id))
    children.sort(key=lambda x: positions[x])
    return children


def get_root_node_id(G: NXGraph):
    # TODO: rewrite to search for a real root node
    root_node = 0
    return root_node


def create_graph_from_pattern(pattern):
    # check if pattern is a connected graph
    nodes = pattern.nodes()
    edges = pattern.edges()
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph


def pattern_connected(pattern: NXGraph):
    return nx.is_connected(create_graph_from_pattern(pattern))


def remove_nodes(G, ids):
    for id in ids:
        G.remove_node(id)
    return


# creates a pattern to filter a graph based on "node type"
# attr_name -> name given to the variable used to identify this node type
# node_type -> the type of node that wants to be filtered
def create_pattern(id, attr_name, node_type):
    pattern = NXGraph()
    pattern.add_node(id, {attr_name: node_type})
    return pattern


# TODO restrict subgraph deepness
def get_ancestors_nodes(G: NXGraph, node_id):
    subg_nodes = list(G.ancestors(node_id))
    subg_nodes.append(node_id)
    return subg_nodes


def create_subgraph(G, node_id):
    subg_nodes = list(G.descendants(node_id))
    subg_nodes.append(node_id)
    subgraph = G.generate_subgraph(G, subg_nodes)
    return subgraph


def print_graph(G):
    # print clear view of all nodes and their edges
    print("List of nodes: ")
    for n, attrs in G.nodes(data=True):
        print("\t", n, attrs)
    print()
    print("List of edges: ")
    for s, t, attrs in G.edges(data=True):
        print("\t{}->{}".format(s, t), attrs)
    print()


def print_nodes(graph, node_ids):
    for id in node_ids:
        print(graph.get_node(id))


def convert_nxgraph_to_graph(NXGraph):
    """
    Extracts and nx.Graph from the NXGraph
    :param NXGraph
    :return: nx.Graph
    """
    nxGraph = nx.Graph(NXGraph._graph)
    return nxGraph


def read_rule_from_line(line):
    string = line.rstrip()
    rule = ast.literal_eval(string)
    return rule

def nxraph_to_digraph(nxgraph: NXGraph):
    digraph = nx.DiGraph()
    for node_id, node_attrs in nxgraph.nodes(data=True):
        digraph.add_nodes_from([(node_id, {name: attr}) for (name, attr) in node_attrs.items()])
    for s, t, attrs in nxgraph.edges(data=True):
        if len(attrs.items()) != 0:
            digraph.add_edges_from([(s, t, {name: attr}) for (name, attr) in attrs.items()])
        else:
            digraph.add_edge(s, t)
    # print_graph(digraph)
    return digraph


def draw_graph(G, attribute="text", id=False, fig_num=1):
    fig = plt.figure(fig_num)
    if type(G) is NXGraph:
        G = nxraph_to_digraph(G)
    # set graph structure to tree
    pos = graphviz_layout(G, prog="dot")
    if not id:
        ids = G.nodes()
        labels = nx.get_node_attributes(G, attribute)
        # transform labels from finite set to strings
        for id, k in zip(ids, labels):
            for value in labels[k]:
                if isinstance(value, str):
                    labels[k] = id, value.replace("'", "")
                else:
                    labels[k] = id, value.decode("utf-8").replace("'", "")
        nx.draw(G, pos=pos,
                with_labels=True,
                node_color="lightgrey",
                edge_color="lightgrey",
                labels=labels,
                alpha=0.9,
                width=2,
                node_size=2200,
                arrowsize=20)
    else:
        nx.draw(G, pos=pos,
                with_labels=True,
                node_color="lightgrey",
                edge_color="lightgrey",
                alpha=0.9,
                width=2,
                node_size=2200,
                arrowsize=20)
    plt.figure(figsize=(20, 20))
    plt.show()
    return fig


def draw_diffgraph(Gdiff, attribute="text"):
    # transform labels from finite set to strings
    if type(Gdiff) is NXGraph:
        Gdiff = nxraph_to_digraph(Gdiff)
    ids = Gdiff.nodes()
    labels = nx.get_node_attributes(Gdiff, attribute)
    # transform labels from finite set to strings
    for id, k in zip(ids, labels):
        for value in labels[k]:
            labels[k] = id, value.replace("'", "")
    pos = graphviz_layout(Gdiff, prog="dot")
    # color different nodes depending on the labels
    val_map = {"both": "lightgrey",
               "G1": "red",
               "G2": "green",
               "updated": "lightblue"
               }
    node_colors = []
    for node, attrs in Gdiff.nodes(data=True):
        if len(attrs["origin"]) == 2:
            node_colors.append(val_map["both"])
        elif len(attrs["origin"]) == 1:
            for elem in attrs["origin"]:
                if elem == "G1":
                    node_colors.append(val_map["G1"])
                elif elem == "G2":
                    node_colors.append(val_map["G2"])
                elif elem == "updated":
                    node_colors.append(val_map["updated"])
    edge_colors = []
    for s, t, attrs in Gdiff.edges(data=True):
        if len(attrs["origin"]) == 2:
            edge_colors.append(val_map["both"])
        elif len(attrs["origin"]) == 1:
            for elem in attrs["origin"]:
                if elem == "G1":
                    edge_colors.append(val_map["G1"])
                elif elem == "G2":
                    edge_colors.append(val_map["G2"])
    # add labels=labels, for different labeling
    # add node_color='lightblue' for one colored nodes
    nx.draw(Gdiff, pos=pos,
            with_labels=True,
            cmap=plt.get_cmap('inferno'),
            node_color=node_colors,
            edge_color=edge_colors,
            labels=labels,
            alpha=0.9,
            width=2,
            node_size=2200,
            arrowsize=20)
    #plt.show()


def format_b_string(toFormat: bytes) -> str:
    string = str(toFormat)
    return string[2:-1]


def format_script(script: str) -> str:
    return textwrap.dedent(script)
    lines = script.splitlines()
    for i, line in enumerate(lines):
        if line.isspace():
            del lines[i]
        else:
            break


