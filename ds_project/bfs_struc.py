import sqlite3
from typing import TextIO, Tuple, List, Set, Dict, Union
from typing import TextIO, Dict

from networkx import Graph
from networkx.algorithms.isomorphism import tree_isomorphism
from regraph import NXGraph
import time
import utils
from db_tracker import setup_db
import itertools

from tree_sitter import Language, Parser

import test_scripts
from graph_extractor import GraphExtractor

#We always follow up to the children of the following types
nesting_types = {'module', 'expression_statement', 'assignment', 'call', 'argument_list', 'attribute', 'subscript', 'keyword_argument', 'from', 'dotted_name', 'block', 'for_statement'}

#We always save these types as part of the structure
identifier_types = {'identifier'}

structure_types = nesting_types | identifier_types | {'import'}

max_candidates = 10


def structure_tracker(graph: NXGraph) -> Tuple[int, Dict[int, int]]:
    next_model_id = gen_model_id()
    down_to = max(next_model_id - max_candidates, 0)
    past_models = [(i, load_graph(i)) for i in range(down_to, next_model_id)]
    stripped = strip_graph(graph, 0)
    iso = find_isomorphism(stripped, past_models)
    if iso is None:
        save_graph(graph, 0, next_model_id)
        return next_model_id, dict(zip(stripped.nodes(), stripped.nodes()))
    else:
        return iso[0], iso[2]


def gen_model_id() -> int:
    con = sqlite3.connect("trackers.db")
    cur = con.cursor()
    cur.execute(" SELECT MAX (model_id)+1 FROM expressions")
    return cur.fetchone()[0]

def load_graph(model_id: int) -> NXGraph:
    G = NXGraph()
    con = sqlite3.connect("trackers.db")
    cur = con.cursor()
    queue: List[int] = [0]
    visited: List[int] = []
    cur.execute("""SELECT operator, name FROM Expressions 
                    WHERE Expressions.model_id = ? 
                    AND expr_id = 0""",
                (model_id, ))
    (root_op, root_name) = cur.fetchone()
    G.add_node(0, attrs={"type": root_op, "text": root_name})


    while queue:
        current_id = queue.pop(0)
        cur.execute("""SELECT expr_id, operator, name FROM Edges, Expressions 
                        WHERE Expressions.model_id = ? AND Edges.model_id = ? AND from_edge = ?
                        AND expr_id = to_edge""",
                    (model_id, model_id, current_id))
        result = cur.fetchall()
        for (expr_id, operator, name) in result:
            if expr_id not in visited:
                visited.append(expr_id)
                G.add_node(expr_id, attrs={"type": operator, "text": name})
                G.add_edge(current_id, expr_id)
                if operator in nesting_types:
                    queue.append(expr_id)

    return G


def find_isomorphism(graph: NXGraph, comparison: List[Tuple[int, NXGraph]]) -> Union[Tuple[int, NXGraph, Dict[int, int]], None]:
    for (other_id, other) in comparison:
        #Tree isomorphism only works on undirected graphs
        isomorphism: List[Tuple[int, int]] = tree_isomorphism(Graph(graph._graph), Graph(other._graph))
        if isomorphism:
            return other_id, other, {f: t for (f, t) in isomorphism}

    return None


def strip_graph(graph: NXGraph, root_id) -> NXGraph:
    visited, queue = [], []
    G = NXGraph()
    queue.append(root_id)
    edge_candidates: Dict[int, List[int]] = {}

    while queue:
        current_id = queue.pop(0)
        attributes = graph.get_node(current_id)
        (node_type,) = attributes["type"]
        if node_type in structure_types and current_id not in visited:
            visited.append(current_id)
            #Delete text attribute for everything that is not an identifier because it might contain constants
            if node_type not in identifier_types:
                attributes["text"] = None
            G.add_node(current_id, attributes)
            if node_type in nesting_types:
                queue += graph.successors(current_id)
                edge_candidates[current_id] = graph.successors(current_id)

    #Assembling edges afterwards makes sure we ignore edges from/to nodes we have removed
    edges = [
        (f, t)
        for f in visited
        for t in edge_candidates.get(f, [])
        if t in visited
    ]
    G.add_edges_from(edges)
    return G


def save_graph(graph: NXGraph, root_id, model_id):
    visited, queue = [],[]
    queue.append(root_id)
    visited.append(root_id)
    con = sqlite3.connect("trackers.db")
    cur = con.cursor()

    while queue:
        current_id = queue.pop(0)
        node_attributes = graph.get_node(current_id)
        #For some reason all values in the attributes are one-element sets, so we have to unpack them...
        (node_type,) = node_attributes["type"]

        #We only want to track a limited amount of types of nodes
        #Not every node has children worthwhile to track
        (node_text,) = node_attributes["text"]
        cur.execute("INSERT INTO Expressions VALUES (?, ?, ?, ?)", (node_type, node_text, current_id, model_id))

        for successor in graph.successors(current_id):
            queue.append(successor)
            visited.append(successor)
            cur.execute("INSERT INTO Edges VALUES (?, ?, ?, ?)", (current_id, successor, model_id, None))

        cur.execute("INSERT INTO Models VALUES (?)", (model_id,))
        con.commit()

    con.close()

if __name__ == "__main__":
    setup_db()
    start_time = time.time()
    language = 'python'
    code = test_scripts.Python.code_8
    language = Language('build/my-languages.so', language)
    parser = Parser()
    parser.set_language(language)
    b = bytes(code, "utf8")
    tree = parser.parse(b)
    extractor = GraphExtractor()
    G = extractor.bfs_tree_traverser(tree)
    utils.print_graph(G)
    G = strip_graph(G, 0)
    utils.print_graph(G)
    print("--- %s seconds ---" % (time.time() - start_time))
    #save_graph(G, 0, 0)
    G = load_graph(0)
    utils.print_graph(G)
    print("done")
