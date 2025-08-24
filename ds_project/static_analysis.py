import sqlite3
from typing import Dict, List, Union, Tuple, Set

import utils
from regraph import NXGraph
from utils import format_b_string

argument_list_ignore = {"(", ",", ")"}


def extract_imports(graph: NXGraph) -> Dict[str, str]:
    mappings = {}
    for node, attr in graph.nodes(data=True):
        (node_type,) = attr["type"]
        if node_type == "import_from_statement":
            children = utils.get_successor_list(graph, node)
            prefix_id = children[1]
            (prefix,) = graph.get_node(prefix_id)["text"]
            prefix = format_b_string(prefix)
            for child in children[3:]:
                child_attrs = graph.get_node(child)
                (child_type,) = child_attrs["type"]
                if child_type == "dotted_name":
                    (child_text,) = child_attrs["text"]
                    child_text = format_b_string(child_text)
                    mappings[child_text] = prefix + "." + child_text
        if node_type == "aliased_import":
            children = utils.get_successor_list(graph, node)
            (prefix, ) = graph.get_node(children[0])["text"]
            (alias,) = graph.get_node(children[2])["text"]
            alias = format_b_string(alias)
            mappings[alias] = format_b_string(prefix)
    return mappings


def extract_files(graph: NXGraph) -> Set[str]:
    files = []
    for node, attr in graph.nodes(data=True):
        (node_type,) = attr["type"]
        if node_type == "assignment":
            assignment_children = utils.get_successor_list(graph, node)
            assigned_to_attr = graph.get_node(assignment_children[2])
            (assigned_type,) = assigned_to_attr["type"]
            if assigned_type == "call":
                call_children = utils.get_successor_list(graph, assignment_children[2])
                f_name_attr = graph.get_node(call_children[0])
                (f_name_type,) = f_name_attr["type"]
                (f_name,) = f_name_attr["text"]
                if f_name_type == "identifier" and format_b_string(f_name) == "open":
                    file_name_attr = graph.get_node(assignment_children[0])
                    (file_name,) = file_name_attr["text"]
                    files.append(format_b_string(file_name))
    return set(files)

def find_call_in_kb(function_name: str, up_to_arguments: int, con: sqlite3.Connection) -> Union[None, List[str]]:
    cur = con.cursor()
    if up_to_arguments > 0:
        cur.execute(
            """SELECT argument_name
             FROM functions as f, arguments as a 
             WHERE function_title = ? 
             AND f.function_id = a.function_id
             AND argument_position BETWEEN 1 AND ?""",
            (function_name, up_to_arguments))
        result = [arg_name for (arg_name,) in cur.fetchall()]
        return result if len(result) > 0 else None
    else:
        cur.execute("""
        SELECT function_id FROM functions as f WHERE function_title = ?""", (function_name, ))
        return [] if (len(cur.fetchall()) > 0) else None

def find_arguments(graph: NXGraph, call_node: int) -> Tuple[List[int], Dict[str, int]]:
    arguments = utils.get_successor_list(graph, utils.get_successor_list(graph, call_node)[1])
    arguments = [(node, graph.get_node(node)["type"]) for node in arguments]
    arguments = [(node, node_type) for (node, (node_type,)) in arguments if node_type not in argument_list_ignore]
    named_arguments = {}
    positional_arguments = []

    for (node, node_type) in arguments:
        if node_type == "keyword_argument":
            children = utils.get_successor_list(graph, node)
            (name, ) = graph.get_node(children[0])["text"]
            named_arguments[format_b_string(name)] = children[2]
        else:
            positional_arguments.append(node)

    return positional_arguments, named_arguments

def create_parameter_tracker(function_name: str, argument_name: str, run_id: int, expr_id: int) -> Tuple[bytes, bytes]:
    before = "trackers.hyperparam_tracker(\"{}\", \"{}\", ".format(function_name, argument_name)
    after = ", run_id={}, expr_id={})".format(run_id, expr_id)
    return (bytes(before, "utf8"), bytes(after, "utf8"))

def create_stdout_tracker(run_id: int) -> Tuple[bytes, bytes]:
    before = "trackers.stdout_tracker("
    after = ", {})".format(run_id)
    return (bytes(before, "utf8"), bytes(after, "utf8"))

def create_file_tracker(file: str, run_id: int) -> Tuple[bytes, bytes]:
    before = "trackers.file_tracker("
    after = ", {}, {})".format(file, run_id)
    return (bytes(before, "utf8"), bytes(after, "utf8"))

def create_plot_tracker(run_id: int) -> Tuple[bytes, bytes]:
    before = "trackers.plot_tracker("
    after = ", {})".format(run_id)
    return (bytes(before, "utf8"), bytes(after, "utf8"))


def resolve_attribute_or_identifier(graph: NXGraph, node: int, name_mapping: Dict[str, str], files: Set[str]) -> Union[Tuple[str], Tuple[str, str]]:
    attrs = graph.get_node(node)
    (kind, ) = attrs["type"]
    if kind == "identifier":
        (name,) = attrs["text"]
        name = format_b_string(name)
        if name in name_mapping:
            return (name_mapping[name],)
        else:
            return (name,)
    if kind == "attribute":
        children = utils.get_successor_list(graph, node)
        (first_identifier,) = graph.get_node(children[0])["text"]
        first_identifier = format_b_string(first_identifier)
        if first_identifier in files:
            (function_name,) = graph.get_node(children[2])["text"]
            function_name = format_b_string(function_name)
            return (function_name, first_identifier)
        if first_identifier in name_mapping:
            first_identifier = name_mapping[first_identifier]
        name_parts = [first_identifier] + \
                     [format_b_string(graph.get_node(child)["text"])
                      for child in children[1:]]
        return ("".join([part.replace("'", "") for part in name_parts]),)

def insert_trackers(
        graph: NXGraph,
        script: bytes,
        name_mapping: Dict[str, str],
        kb_con: sqlite3.Connection,
        isomorphism: Dict[int, int],
        run_id: int,
        files: Set[str]) -> bytes:
    insertions: List[Tuple[int, bytes]] = []
    def remember_tracker(to_insert: Tuple[bytes, bytes], node: int):
        arg_attr = graph.get_node(node)
        (begin,) = arg_attr["start"]
        (end,) = arg_attr["end"]
        insertions.append((begin, to_insert[0]))
        insertions.append((end, to_insert[1]))

    for node, attr in graph.nodes(data=True):
        (node_type,) = attr["type"]
        if node_type == "call":
            #Extract all necessary information from the node
            children = utils.get_successor_list(graph, node)
            decoded_name = resolve_attribute_or_identifier(graph, children[0], name_mapping, files)
            if len(decoded_name) == 1:
                (function_name,) = decoded_name
                file_name = None
            else:
                (function_name, file_name) = decoded_name
            positional_arguments, named_arguments = find_arguments(graph, node)
            positional_naming = find_call_in_kb(function_name, len(positional_arguments), kb_con)
            if file_name is not None and function_name == "write":
                to_insert = create_file_tracker(file_name, run_id)
                remember_tracker(to_insert, positional_arguments[0])
            if function_name == "print":
                to_insert = create_stdout_tracker(run_id)
                remember_tracker(to_insert, positional_arguments[0])
            elif function_name == "matplotlib.pyplot.savefig":
                to_insert = create_plot_tracker(run_id)
                remember_tracker(to_insert, positional_arguments[0])
            #Check if call is in KB, if so insert hyperparameter tracker
            elif positional_naming is not None:
                #Only continue if function is in knowledge base
                named_arguments.update({function_name: node for (function_name, node) in zip(positional_naming, positional_arguments)})
                for arg_name, arg_node in named_arguments.items():
                    to_insert = create_parameter_tracker(function_name, arg_name, run_id, isomorphism[node])
                    remember_tracker(to_insert, arg_node)

    #Sort insertions by position
    insertions.sort(key=lambda it: it[0])
    #Calculate the offset caused by the previous insertions for each insertion
    running_sum = 0
    offset = []
    for insert in insertions:
        offset.append(running_sum)
        running_sum += len(insert[1])
    #Insert the insertions into the original script
    script = bytearray(script)
    for i, (index, to_write) in enumerate(insertions):
        index += offset[i]
        script[index:index] = to_write

    return bytes(script)

