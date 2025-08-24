import sqlite3
from regraph import NXGraph, Rule, FiniteSet, plot_graph
import json
import time
import utils
from utils import draw_graph, print_graph, read_rule_from_line
from models.Function import Function
from rule_extractor import RuleExtractor
from rule_creator import get_rules_from_db
import matplotlib.pyplot as plt


def flip_tree(G: NXGraph):
    """
    Turns the initial tree upside down, allows for better rules definition
    and application.

    :param G: an NXGraph object
    """
    root_node = utils.get_root_node_id(G)
    flip_node(G, root_node)


def flip_node(G: NXGraph, node_to_flip, id_to_ignore=-1):
    if not G.successors(node_to_flip):
        return
    children = list()
    for child in G.successors(node_to_flip):
        children.append(child)
    while children:
        child = children.pop(0)
        if child == id_to_ignore:
            continue
        G.add_edge(child, node_to_flip)
        G.remove_edge(node_to_flip, child)
        flip_node(G, child, node_to_flip)


def append_identifier_to_call(G: NXGraph):
    """
    Adds identifier attribute to call node, remove identifier node.

    :param G: an NXGraph object
    """
    pattern = NXGraph()
    pattern.add_node(1, {'type': 'identifier'})
    pattern.add_node(2, {'type': 'call'})
    pattern.add_edge(1, 2)

    instances = []
    instances.extend(G.find_matching(pattern))

    for instance in instances:
        identifier_id = instance[1]
        call_id = instance[2]
        identifier_attrs = G.get_node(identifier_id)
        identifier_text = identifier_attrs["text"]
        G.update_node_attrs(call_id, {"type": "call", "text": identifier_text})
        G.remove_node(identifier_id)
    return


def adjust_attributes(G: NXGraph):
    pattern = NXGraph()
    pattern.add_node(1, {'type': 'attribute'})
    pattern.add_node(2, {'type': 'call'})
    pattern.add_edge(1, 2)
    instances = G.find_matching(pattern)
    for instance in instances:
        attr_id = instance[1]
        call_id = instance[2]
        attr_attrs = G.get_node(attr_id)
        attr_text = attr_attrs["text"]
        G.update_node_attrs(call_id, {"type": "call", "text": attr_text})
        parents = G.predecessors(attr_id)
        children = G.successors(attr_id)
        for child in children:
            for parent in parents:
                G.add_edge(parent, child)
        G.remove_node(attr_id)
    return


def adjust_arguments(G: NXGraph):
    # connect parents and children of argument list, remove argument list node
    pattern = NXGraph()
    pattern.add_node(1, {'type': 'argument_list'})
    instances = G.find_matching(pattern)
    for instance in instances:
        argument_id = instance[1]
        parents = G.predecessors(argument_id)
        children = G.successors(argument_id)
        for child in children:
            for parent in parents:
                G.add_edge(parent, child)
                parent_node = G.get_node(parent)
                # if it is an identifier, rename to input variable
                for elem in parent_node["type"]:
                    if elem == "identifier":
                        G.update_node_attrs(parent, {"text": parent_node["text"], "type": "input_variable"})
        G.remove_node(argument_id)
    return


def adjust_assignment(G: NXGraph):
    pattern = NXGraph()
    pattern.add_node(1, {'type': 'identifier'})
    pattern.add_node(2, {'type': 'assignment'})
    pattern.add_node(3, {'type': 'identifier'})
    pattern.add_edge(1, 2)
    pattern.add_edge(3, 2)
    instances = G.find_matching(pattern)
    if instances:
        for instance in instances:
            if instance[1] < instance[3]:
                G.remove_edge(instance[1], instance[2])
                G.add_edge(instance[2], instance[1])
                attrs_output_variable = G.get_node(instance[1])
                attrs_output_variable["type"] = "output_variable"
                attrs_assignment = G.get_node(instance[2])
                attrs_assignment["type"] = "variable_assignment"
                attrs_input_variable = G.get_node(instance[3])
                attrs_input_variable["type"] = "input_variable"
                G.update_node_attrs(instance[1], attrs_output_variable)
                G.update_node_attrs(instance[2], attrs_assignment)
                G.update_node_attrs(instance[3], attrs_input_variable)
    return


def save_identifier_into_keyword_argument(G: NXGraph):
    """
    Saves "identifier" text into "keyword_argument" node as "identifier"
    attribute.

    :param G: an NXGraph object
    """
    pattern = NXGraph()
    pattern.add_node(1, {'type': 'identifier'})
    pattern.add_node(2, {'type': 'keyword_argument'})
    pattern.add_edge(1, 2)
    instances = G.find_matching(pattern)
    if instances:
        for instance in instances:
            attrs = G.get_node_attrs(instance[1])
            G.add_node_attrs(instance[2], {"identifier": attrs["text"]})
            print_graph(G)

    return


def save_import_aliases(G: NXGraph):
    """
    Handles 'import numpy as np'.

    :param G: A NXGraph object
    """
    # create pattern for aliases
    pattern = NXGraph()
    pattern.add_node(1, {'type': 'aliased_import'})
    pattern.add_node(2, {'type': 'dotted_name'})
    pattern.add_node(3, {'type': 'identifier'})
    pattern.add_edge(2, 1)
    pattern.add_edge(3, 1)

    instances = []

    if utils.pattern_connected(pattern):
        # get subgraphs
        subgraphs = get_ascendant_subgraphs_by_pattern(G, pattern)
        for subgraph in subgraphs:
            instances.extend(G.find_matching(pattern, subgraph))
    else:
        instances = G.find_matching(pattern)

    aliases_dict = {}

    # save all aliases
    for instance in instances:
        aliased_import_id = instance[1]
        dotted_name_id = instance[2]
        identifier_id = instance[3]

        dotted_name = G.get_node(dotted_name_id)
        identifier = G.get_node(identifier_id)
        for key, value in zip(identifier["text"], dotted_name["text"]):
            aliases_dict[key] = value
    return aliases_dict


def save_imported_functions(G: NXGraph):
    """
    Handles "from numpy import function".

    :param G:
    :return:
    """
    pattern = NXGraph()
    pattern.add_node(1, {'type': 'dotted_name'})
    pattern.add_node(2, {'type': 'import_from_statement'})
    pattern.add_node(3, {'type': 'dotted_name'})
    pattern.add_edge(1, 2)
    pattern.add_edge(3, 2)

    instances = []

    if utils.pattern_connected(pattern):
        # get subgraphs
        subgraphs = get_ascendant_subgraphs_by_pattern(G, pattern)
        for subgraph in subgraphs:
            instances.extend(G.find_matching(pattern, subgraph))
    else:
        instances = G.find_matching(pattern)

    functions_dict = {}
    if instances:
        for instance in instances:
            if instance[1] < instance[3]:
                module_name = G.get_node(instance[1])["text"]
                function_name = G.get_node(instance[3])["text"]
                for mod_name, func_name in zip(module_name, function_name):
                    functions_dict[func_name] = mod_name.decode("utf-8") + "." + func_name.decode("utf-8")
                    # print(functions_dict)
    return functions_dict


def save_imported_modules(G: NXGraph):
    """
    Handles "import module".

    Finds instances of imported modules "dotted_name" -> "import_statement"
    and returns them as a list of strings.

    :param G: A NXGraph object
    :return: A list of strings representing the imported modules
    """

    pattern = NXGraph()
    pattern.add_node(1, {'type': 'dotted_name'})
    pattern.add_node(2, {'type': 'import_statement'})
    pattern.add_edge(1, 2)
    instances = []

    if utils.pattern_connected(pattern):
        # get subgraphs
        subgraphs = get_ascendant_subgraphs_by_pattern(G, pattern)
        for subgraph in subgraphs:
            instances.extend(G.find_matching(pattern, subgraph))
    else:
        instances = G.find_matching(pattern)

    imported_modules = []
    if instances:
        for instance in instances:
            imported_modules.append(G.get_node(instance[1])["text"])

    return imported_modules


def remove_import_statements(G: NXGraph):
    """
    Removes import statements from a given NXGraph object.
    It searches for both 'import_statement' and 'import_from_statement' nodes
    and removes them along with their ancestors nodes.

    Parameters:
    G (NXGraph): The NXGraph object containing the import statements to remove.

    Returns:
    None
    """
    instances = []
    pattern = NXGraph()
    pattern.add_node(1, {'type': 'import_statement'})
    instances.extend(G.find_matching(pattern))

    pattern = NXGraph()
    pattern.add_node(1, {'type': 'import_from_statement'})
    instances.extend(G.find_matching(pattern))
    if instances:
        for instance in instances:
            nodes = utils.get_ancestors_nodes(G, instance[1])
            for node in nodes:
                G.remove_node(node)
    return


def initial_cleanup(G: NXGraph):
    """
    Removes nodes that are not carrying any information and are not required
    in future transformations.

    :param G: an NXGraph object
    """
    redundancy_list = [
        "comment",
        ".",
        ",",
        ")",
        "(",
        "[",
        "]",
        ":",
        ";",
        "}",
        "{",
        "\"",
        "\'"
    ]
    clean_from_list(G, redundancy_list)


def clean_from_list(G: NXGraph, redundancy_list: list):
    """
    Remove nodes from a NetworkX graph based on a list of redundancy values

    :param G: A NetworkX graph object
    :param redundancy_list: A list of values to be used as criteria for removing nodes.
    :return:
    """
    for redundancy in redundancy_list:
        redundancy_pattern = utils.create_pattern("node_id", "type", redundancy)
        instances = G.find_matching(redundancy_pattern)
        for instance in instances:
            utils.remove_nodes(G, [instance["node_id"]])


def post_cleanup(G: NXGraph):
    """
    Remove nodes that no longer carry any information after the transformations
    were done.

    :param G: an NXGraph objec
    """
    redundancy_list = [
        "expression_statement",
        "assignment",
        "pattern_list",
        "module",
        "slice",
        "=",
        "+",
        "*",
        "%",
        "-",
        "<",
        ">",
        "expression_list"
    ]
    clean_from_list(G, redundancy_list)

    # keyword argument children
    # eventually save them into the node instead
    keyword_parents = [
        "string",
        "integer",
        "float",
        "true",
        "false"
    ]
    for parent in keyword_parents:
        keyword_pattern = NXGraph()
        keyword_pattern.add_node(1, {'type': parent})
        keyword_pattern.add_node(2, {'type': 'keyword_argument'})
        keyword_pattern.add_edge(1, 2)
        keyword_instances = G.find_matching(keyword_pattern)
        for keyword_instance in keyword_instances:
            G.remove_node(keyword_instance[1])


def compare_outputs_inputs(G: NXGraph, output_instances, input_instances, nodes_to_remove):
    """
    Compares the output instances and the input instances, and if they have the same
    name, it adds the input node to the nodes_to_remove list, updates the attribute
    of the output node, setting its "type" to "passable_data" and its
    "text" to the text of the input node and then adds an
    edge between the output node and the input node's caller function

    :param G: a NXGraph object
    :param output_instances: a list of output instances
    :param input_instances: a list of input instances
    :param nodes_to_remove: a list of nodes to be removed from the graph
    :return: an updated NXGraph object, the output instances, the input instances and the nodes_to_remove list
    """
    # check if same names, remove input node, update output attriute
    for output_instance in output_instances:
        output_identifier = output_instance[2]
        output_caller_function = output_instance[1]
        output_node = G.get_node(output_identifier)
        for input_instance in input_instances:
            input_identifier = input_instance[1]
            input_caller_function = input_instance[2]
            input_node = G.get_node(input_identifier)
            # if same, remove nodes and add edge
            if output_node['text'] == input_node['text']:
                # if output_identifier not in nodes_to_remove:
                # nodes_to_remove.append(output_identifier)
                if input_identifier not in nodes_to_remove:
                    nodes_to_remove.append(input_identifier)
                G.update_node_attrs(output_identifier, {"type": "passable_data", "text": output_node['text']})
                # add edge between caller functions
                # if exists, add further attribute
                G.add_edge(output_identifier, input_caller_function)

                continue

    return G, output_instances, input_instances, nodes_to_remove


def establish_dependencies(G: NXGraph):
    """
    1. Find output and input instances in the graph
    2. Compare the output instances and input instances with compare_outputs_inputs()
    and if they have the same name, it updates the attribute of the output node,
    adding an edge between the output node and the input node's caller function.
    3. Go leftover input instances and save them into their belonging functions as
    an attribute.
    4. Checks for potential inputs by searching for identifier nodes that are children
    to other nodes and calls the compare_outputs_inputs() function again.
    5. Go through the leftover output instances and saves them into their belonging
    functions as an attribute.
    6. Remove identified nodes that are no longer needed in the graph.

    :param G: a NXGraph object
    """
    # TODO eventually optimization needed, since node 1 has no attrs
    # if an identifier node is a child of a call, it is an
    # output value of a function
    output_pattern = NXGraph()
    output_pattern.add_node(1)
    output_pattern.add_node(2, {'type': 'output_variable'})
    output_pattern.add_edge(1, 2)
    output_instances = G.find_matching(output_pattern)

    # if an identifier node is a parent to any node, it is an input value
    # into that function
    input_pattern = NXGraph()
    input_pattern.add_node(1, {'type': 'input_variable'})
    input_pattern.add_node(2)
    input_pattern.add_edge(1, 2)
    input_instances = G.find_matching(input_pattern)

    nodes_to_remove = []

    G, output_instances, input_instances, nodes_to_remove = compare_outputs_inputs(G, output_instances,
                                                                                   input_instances, nodes_to_remove)
    # go though leftover inputs, save them into their
    # belonging functions as attribute
    for input_instance in input_instances:

        input_id = input_instance[1]
        children = G.successors(input_id)
        input_node = G.successors(input_id)
        # save attr in child
        input_node = G.get_node(input_id)
        child_id = list(children)[0]
        child_node = G.get_node(child_id)
        if "input_variable" in child_node:
            for elem in input_node["text"]:
                child_node["input_variable"].add(elem)
        else:
            child_node["input_variable"] = input_node["text"]
        G.update_node_attrs(child_id, child_node)
        # uncomment this to make input variables that werent defined anywhere before invisible
        # if input_id not in nodes_to_remove:
        # nodes_to_remove.append(input_id)

    # check identifiers for potential inputs
    input_pattern = NXGraph()
    input_pattern.add_node(1, {'type': 'identifier'})
    input_pattern.add_node(2)
    input_pattern.add_edge(1, 2)

    input_instances = G.find_matching(input_pattern)
    G, output_instances, input_instances, nodes_to_remove = compare_outputs_inputs(G, output_instances,
                                                                                   input_instances, nodes_to_remove)
    for input_instance in input_instances:
        input_id = input_instance[1]
        children = G.successors(input_id)
        # save attr in child
        input_node = G.get_node(input_id)
        child_id = list(children)[0]
        child_node = G.get_node(child_id)
        # if we met this node before, it is an object or a variable
        if input_id in nodes_to_remove:
            child_node["variable"] = input_node["text"]
        else:
            if "identifier" in child_node:
                for elem in input_node["text"]:
                    child_node["identifier"].add(elem)
            else:
                child_node["identifier"] = input_node["text"]
        G.update_node_attrs(child_id, child_node)
        if input_id not in nodes_to_remove:
            nodes_to_remove.append(input_id)

    # go through leftover outputs, save them into their
    # belonging functions as attribute
    for output_instance in output_instances:
        output_id = output_instance[2]
        # if output_id in nodes_to_remove:
        # continue
        parents = G.predecessors(output_id)
        # save attribute in parent
        output_node = G.get_node(output_id)
        parent_id = list(parents)[0]
        parent_node = G.get_node(parent_id)
        if "output_variable" in parent_node:
            for elem in output_node["text"]:
                parent_node["output_variable"].add(elem)
        else:
            parent_node["output_variable"] = output_node["text"]
        G.update_node_attrs(parent_id, parent_node)
        # if output_id not in nodes_to_remove:
        # nodes_to_remove.append(output_id)
    for id in nodes_to_remove:
        G.remove_node(id)


def connect_parents_children_drop_node(G: NXGraph, attr: str):
    """
    Find instances of the node we want to remove, connect its parents and children,
    remove node.

    :param G: a NXGraph object
    :param attr: attribute of the node that we want to remove
    """
    # connect parents and children of slice, remove node by type
    pattern = NXGraph()
    pattern.add_node(1, {'type': attr})
    instances = G.find_matching(pattern)
    for instance in instances:
        node_id = instance[1]
        parents = G.predecessors(node_id)
        children = G.successors(node_id)
        for child in children:
            for parent in parents:
                G.add_edge(parent, child)
        G.remove_node(node_id)


def add_attributes_from_import_aliases(G: NXGraph, alieses_dict: dict, cursor):
    """
    Looks for instances of nodes with the attribute "identifier" that match a key
    in the aliases_dict. If such nodes are found, the function removes the "identifier"
    attribute and adds the "module" attribute with the value of the corresponding value
    in the aliases_dict. The function also adds the "full_function_call" attribute
    by concatenating the value of the aliases_dict with the text attribute of the node,
    if the key appears in the text attribute. The function also attempts to retrieve a
    knowledge base entry for the function and adds the description of that entry as an
    attribute to the node, if it is found.

    :param G: a NXGraph object
    :param alieses_dict: A dictionary of import aliases, where keys are the short identifiers
     and values are the full function names.
    :param cursor: A cursor object to access a database, which is used to retrieve a
    knowledge base entry for the functions
    """
    for key in alieses_dict:
        pattern = NXGraph()
        pattern.add_node(1, {'identifier': key})
        instances = (G.find_matching(pattern))
        if instances:
            for instance in instances:
                # remove short identifier from identifiers list
                node_id = instance[1]
                node_attrs = G.get_node(node_id)
                G.remove_node_attrs(node_id, {'identifier': key})
                # add "module" attribute and put full function name there
                module_name = alieses_dict[key].decode("utf-8")
                G.add_node_attrs(node_id, {"module": module_name})
                # add full function call to the node
                for value in node_attrs["text"]:
                    node_text = value.decode("utf-8")
                    short_name = key.decode("utf-8")
                    long_name = alieses_dict[key].decode("utf-8")
                    if short_name in node_text:
                        full_name = long_name + node_text[len(short_name):]
                        G.add_node_attrs(node_id, {"full_function_call": full_name})
                # get knowledge base entry
                kb_function = Function.parse_from_db(cursor, module_name, full_name)
                if kb_function != -1:
                    G.add_node_attrs(node_id, {"description": kb_function.description})


def add_attributes_from_functions_dict(G: NXGraph, functions_dict: dict, cursor):
    for key in functions_dict:
        pattern = NXGraph()
        pattern.add_node(1, {'text': key})
        instances = (G.find_matching(pattern))
        for instance in instances:
            # add "module" attribute and put full function name there
            node_id = instance[1]
            index = functions_dict[key].find(".")
            module_name = functions_dict[key][:index]
            G.add_node_attrs(node_id, {"module": module_name})
            # add full function call to the node
            full_name = functions_dict[key]
            G.add_node_attrs(node_id, {"full_function_call": full_name})
            # get knowledge base entry
            kb_function = Function.parse_from_db(cursor, module_name, full_name)
            if kb_function != -1:
                G.add_node_attrs(node_id, {"description": kb_function.description})


def add_attributes_from_module_list(G: NXGraph, imported_modules: list, cursor):
    for module in imported_modules:
        for module_name in module:
            pattern = NXGraph()
            pattern.add_node(1, {'identifier': module_name})
            instances = (G.find_matching(pattern))
            for instance in instances:
                # add "module" attribute and put full function name there
                node_id = instance[1]
                function_call = G.get_node(node_id)["text"]
                for function_name in function_call:
                    G.add_node_attrs(node_id, {"module": module_name.decode("utf-8")})
                    # add full function call
                    G.add_node_attrs(node_id, {"full_function_call": function_name.decode("utf-8")})
                    kb_function = Function.parse_from_db(cursor, module_name.decode("utf-8"),
                                                         function_name.decode("utf-8"))
                    if kb_function != -1:
                        G.add_node_attrs(node_id, {"description": kb_function.description})


def add_labels(G: NXGraph):
    """
    Adds labels that will be displayed in the front-end.

    :param G: an NXGraph object
    """
    nodes = G.nodes()
    for node_id in nodes:
        node = G.get_node(node_id)
        node_text = node["text"]
        G.add_node_attrs(node_id, {"label": node_text})


def get_ascendant_subgraphs_by_pattern(G: NXGraph, pattern: NXGraph):
    """
    Finds a complete subgraph of ascendants for a given pattern.

    :param G: an NXGraph object
    :param pattern: pattern to find ascendants of
    :return: found subgraphs
    """
    anti_root_id = [node for node in pattern.nodes() if len(pattern.descendants(node)) == 0][0]
    anti_root_attrs = pattern.get_node(anti_root_id)
    # find all instances of root in graph
    root_pattern = NXGraph()
    root_pattern.add_node(anti_root_id, anti_root_attrs)
    instances = G.find_matching(root_pattern)
    subgraphs = []
    if instances:
        for instance in instances:
            subgraphs.append(utils.get_ancestors_nodes(G, list(instance.values())[0]))
    return subgraphs


def apply_rule(G, json_rule):
    """
    Applies given rule on a graph.

    :param G: an NXGraph object
    :param json_rule: rule instance
    """
    rule = Rule.from_json(json_rule)
    pattern = rule.lhs
    instances = []
    if utils.pattern_connected(pattern):
        # get subgraphs for faster instance finding
        subgraphs = get_ascendant_subgraphs_by_pattern(G, pattern)
        for subgraph in subgraphs:
            instances.extend(G.find_matching(pattern, subgraph))
    else:
        instances = G.find_matching(pattern)

    if instances:
        for instance in instances:
            G.rewrite(rule, instance)

    return G


def jsonify_finite_set(param):
    if len(param.to_json()["data"]) > 1:
        result_list = list()
        for element in param.to_json()["data"]:
            if isinstance(element, (bytes, bytearray)):
                result_list.append(element.decode("utf-8"))
            else:
                result_list.append(element)
        return result_list
    data = param.to_json()["data"][0]
    if isinstance(data, (bytes, bytearray)):
        data = data.decode("utf-8")
    return data


def convert_graph_to_json(G):
    graph_dict = {"nodes": [], "edges": []}
    for n, attrs in G.nodes(data=True):
        if str(attrs["type"]) == "{'input'}":
            metadata = {"id": str(n), "type": "input", "targetPosition": "top", "position": {"x": 0, "y": 0},
                        "data": {}}
        else:
            metadata = {"id": str(n), "type": "default", "targetPosition": "top", "position": {"x": 0, "y": 0},
                        "data": {}}
        # node_attrs = {}
        node_raw_attrs = G.get_node(n)
        for key in node_raw_attrs:
            metadata["data"].update({key: jsonify_finite_set(node_raw_attrs[key])})

        # node_attrs.update(G.get_node(n))
        graph_data = {}
        graph_dict["nodes"].append(metadata)
        # graph_dict["nodes"].append(graph_data)
    i = 1
    for s, t, attrs in G.edges(data=True):
        edge_id = "edge-" + str(i)
        edge_attrs = {"id": edge_id, "source": str(s), "target": str(t), 'type': 'smoothstep'}
        graph_dict["edges"].append(edge_attrs)
        i += 1
    with open('graph.json', 'w') as fp:
        json.dump(graph_dict, fp, indent=4)
    # print(graph_dict)
    return graph_dict


def draw_rule():
    with open("knowledge_base/rule_base.txt") as file:
        for counter, line in enumerate(file, 1):
            rule_dict = read_rule_from_line(line)
            if counter == 14:
                rule = Rule.from_json(rule_dict)
                pattern = rule.lhs
                extractor = RuleExtractor()
                result = extractor.get_transformation_result(pattern, rule_dict)
                pattern_fig = draw_graph(pattern, fig_num=2)
                result_fig = draw_graph(result, fig_num=3)
                plt.show()


def transform_graph(G: NXGraph):
    """
    Applies rules from the rule base and further transformations to the given graph.

    :param G: an NXGraph object
    :return: graph in a json format
    """

    start_iner = time.time()

    # connect to db
    connection = sqlite3.connect("knowledge_base.db")
    cursor = connection.cursor()

    # initial graph transformation
    flip_tree(G)
    initial_cleanup(G)

    # transform and save import statements, remove them from tree
    aliases_dict = save_import_aliases(G)
    functions_dict = save_imported_functions(G)
    imported_modules = save_imported_modules(G)
    remove_import_statements(G)

    # pre rule base transformations that cannot be fit into the rule definition
    save_identifier_into_keyword_argument(G)
    adjust_assignment(G)
    append_identifier_to_call(G)
    adjust_attributes(G)
    adjust_arguments(G)

    end_iner = time.time()
    print(f'pre transformations done in {end_iner - start_iner}')
    start_outer = time.time()

    # apply rules from rule base one by one
    rules = get_rules_from_db(cursor)
    for counter, rule in enumerate(rules, 1):
        start_iner = time.time()
        json_rule = read_rule_from_line(rule[0])
        # print(f'Applying rule #{counter}')
        G = apply_rule(G, json_rule)
        end_iner = time.time()
        # print(f'line {counter} done in {end_iner - start_iner}')
    end_outer = time.time()
    # print(f'apply rule  done in {end_outer - start_outer}')
    start_iner = time.time()

    # apply transformations that are required after application from rules from rule base
    connect_parents_children_drop_node(G, "subscript")
    connect_parents_children_drop_node(G, "slice")
    connect_parents_children_drop_node(G, "binary_operator")
    connect_parents_children_drop_node(G, "expression_list")
    post_cleanup(G)

    # find and connect related nodes
    establish_dependencies(G)

    # add knowledge base enrichment to functions that are present there
    add_attributes_from_import_aliases(G, aliases_dict, cursor)
    add_attributes_from_functions_dict(G, functions_dict, cursor)
    add_attributes_from_module_list(G, imported_modules, cursor)
    add_labels(G)

    end_iner = time.time()
    print(f'post transformations done in {end_iner - start_iner}')
    print_graph(G)
    graph_dict = convert_graph_to_json(G)
    return graph_dict
