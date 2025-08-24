import networkx as nx
from regraph import NXGraph, Rule
from utils import print_graph, nxraph_to_digraph, draw_diffgraph, draw_graph
from rule_creator import create_rule, create_pattern, RuleEntry


class RuleExtractor:

    def extract_rule(self, G1, G2, by_text=True):
        Gdiff, nodes_to_add, nodes_to_update, nodes_to_delete, edges_to_add, edges_to_delete = self.calculate_diff_graph(
            G1, G2)

        # trim not relevant attributes
        G1 = self.trim_attributes(G1, by_text)
        G2 = self.trim_attributes(G2, by_text)

        # transform NXGraph into an nx DiGraph
        draw_graph(G1)
        draw_graph(G2)
        draw_diffgraph(Gdiff)

        pattern = self.find_subgraph_from_node_list(Gdiff, nodes_to_add, nodes_to_update, nodes_to_delete, edges_to_add,
                                                    edges_to_delete)
        pattern, transformations = self.translate_changes_into_rule(pattern, nodes_to_add, nodes_to_update,
                                                                    nodes_to_delete,
                                                                    edges_to_add,
                                                                    edges_to_delete)
        pattern_nxgraph = create_pattern(pattern)
        rule = create_rule(pattern_nxgraph, transformations)

        result = self.get_transformation_result(pattern_nxgraph, rule)
        print_graph(G1)
        return pattern_nxgraph, result

    def adapt_rule(self, pattern, result, rule_name, rule_description, by_text=True):
        Gdiff, nodes_to_add, nodes_to_update, nodes_to_delete, edges_to_add, edges_to_delete = self.calculate_diff_graph(
            pattern, result)

        # trim not relevant attributes
        pattern = self.trim_attributes(pattern, by_text)
        result = self.trim_attributes(result, by_text)

        pattern, transformations = self.translate_changes_into_rule(pattern, nodes_to_add, nodes_to_update,
                                                                    nodes_to_delete,
                                                                    edges_to_add,
                                                                    edges_to_delete)
        pattern_nxgraph = create_pattern(pattern)
        rule_dict = create_rule(pattern_nxgraph, transformations)

        # add db entry attributes
        rule_dict["name"] = rule_name
        rule_dict["description"] = rule_description
        if by_text:
            rule_dict["type"] = "semantic"
        else:
            rule_dict["type"] = "syntactic"
        rule_dict["by_user"] = True

        result = self.get_transformation_result(pattern_nxgraph, rule_dict)

        # add rule into db
        rule_entry = RuleEntry()
        rule_entry.add_rule_to_db(rule_dict)

        return rule_dict

    def trim_attributes(self, G: NXGraph, by_text):
        """
        Trim all attributes except type, text and identifier.

        "call" type nodes keep type and text;
        "keyword_argument" nodes keep type and identifier;
        Rest only keep type.

        :param G: NXGraph to trim
        :param by_text: by type only or by text as well
        :return: both graphs with trimmed attributes
        """
        trimmed_G = NXGraph()
        for node_id, attrs in G.nodes(data=True):
            # if node type is in whitelist
            for elem in attrs["type"]:
                # keep type and text
                if elem == "call" and by_text is True:
                    trimmed_attrs = {"type": attrs["type"], "text": attrs["text"]}
                    break
                # keep type and identifier
                elif elem == "keyword_argument" and by_text:
                    trimmed_attrs = {"type": attrs["type"], "identifier": attrs["identifier"]}
                    break
                # only keep type
                else:
                    trimmed_attrs = {"type": attrs["type"]}
            trimmed_G.add_node(node_id, trimmed_attrs)
        for s, t in G.edges():
            trimmed_G.add_edge(s, t)
        return trimmed_G

    # TODO type and text or just type comparison
    def calculate_diff_graph(self, G1: NXGraph, G2: NXGraph):
        # add G1 nodes to Gdiff, label them as of G1 origin, add nodes to hash table
        Gdiff = NXGraph()
        hash_table_nodes, nodes_to_add, nodes_to_delete, nodes_to_update = {}, {}, {}, {}
        hash_table_edges, edges_to_add, edges_to_delete = [], [], []
        for g1_node, g1_attr in G1.nodes(data=True):
            hash_table_nodes[g1_node] = g1_attr.copy()
            g1_attr["origin"] = "G1"
            Gdiff.add_node(g1_node, g1_attr)
            nodes_to_delete[g1_node] = g1_attr

        # traverse G2 and check if a node is in the Gdiff graph yet
        for g2_node, g2_attr in G2.nodes(data=True):
            # same node present in both graphs
            if g2_node in hash_table_nodes and hash_table_nodes[g2_node] == g2_attr:
                Gdiff.add_node_attrs(g2_node, {"origin": "G2"})
                nodes_to_delete.pop(g2_node)
            # same node, new attrs
            elif g2_node in hash_table_nodes:
                hash_table_nodes[g2_node] = g2_attr.copy()
                nodes_to_update[g2_node] = {}
                nodes_to_update[g2_node]["old"] = G1.get_node(g2_node)
                nodes_to_update[g2_node]["new"] = g2_attr.copy()
                g2_attr["origin"] = "updated"
                # save old attrs
                for old_attr, new_attr in zip(G1.get_node(g2_node), hash_table_nodes[g2_node]):
                    if G1.get_node(g2_node)[old_attr] != hash_table_nodes[g2_node][new_attr]:
                        old_attr_name = "old_" + old_attr
                        g2_attr[old_attr_name] = G1.get_node(g2_node)[old_attr]
                Gdiff.update_node_attrs(g2_node, g2_attr)
                nodes_to_delete.pop(g2_node)

            # new node
            else:
                hash_table_nodes[g2_node] = g2_attr.copy()
                nodes_to_add[g2_node] = g2_attr.copy()
                g2_attr["origin"] = "G2"
                Gdiff.add_node(g2_node, g2_attr)
        # add all E1 edges to diff graph and to hash table, label them as of G1 origin
        for s, t in G1.edges():
            hash_table_edges.append((s, t))
            edge_attr = {"origin": "G1"}
            Gdiff.add_edge(s, t, edge_attr)
            # only add edge to list of edges to delete if
            # it's not going to be deleted automatically
            if s not in list(nodes_to_delete.keys()) and t not in list(nodes_to_delete.keys()):
                edges_to_delete.append((s, t))

        # traverse E2 and check if current edge is in the Gdiff graph yet
        for s, t in G2.edges():
            # same edge present in both graphs
            if (s, t) in hash_table_edges:
                Gdiff.add_edge_attrs(s, t, {"origin": "G2"})
                edges_to_delete.remove((s, t))
            # new edge
            else:
                Gdiff.add_edge(s, t, {"origin": "G2"})
                edges_to_add.append((s, t))

        # print_graph(Gdiff)
        return Gdiff, nodes_to_add, nodes_to_update, nodes_to_delete, edges_to_add, edges_to_delete

    # TODO add case if there is no path between nodes
    def find_subgraph_from_node_list(self, G, nodes_to_add, nodes_to_update, nodes_to_delete, edges_to_add,
                                     edges_to_delete):
        changed_nodes, new_nodes = [], []
        changed_nodes.extend(list(nodes_to_delete.keys()))
        changed_nodes.extend(list(nodes_to_update.keys()))
        new_nodes.extend(list(nodes_to_add.keys()))

        # add all nodes involved in edge changes
        for edge in edges_to_delete:
            if edge[0] not in changed_nodes:
                changed_nodes.append(edge[0])
            if edge[1] not in changed_nodes:
                changed_nodes.append(edge[1])

        for edge in edges_to_add:
            if edge[0] not in changed_nodes and edge[0] not in new_nodes:
                changed_nodes.append(edge[0])
            if edge[1] not in changed_nodes and edge[1] not in new_nodes:
                changed_nodes.append(edge[1])

        # remove G2 only edges from G
        g2_edges = {}
        for s, t, attrs in G.edges(data=True):
            if len(attrs["origin"]) == 1:
                for elem in attrs["origin"]:
                    if elem == "G2":
                        g2_edges[(s, t)] = attrs
        for edge in g2_edges:
            G.remove_edge(edge[0], edge[1])

        # create all combinations
        if type(G) is NXGraph:
            G = nxraph_to_digraph(G)
        H = nx.to_undirected(G)
        paths = []
        for i in range(len(changed_nodes) - 1):
            if len(changed_nodes) == 1:
                paths.append(i)
            paths.append((changed_nodes[0], changed_nodes[i + 1]))

        # create paths between node combinations
        subgraph_nodes = nx.Graph()
        nodes_in_subgraph = []
        longest_induced_path = []
        for path in paths:
            if path[0] in nodes_in_subgraph and path[1] in nodes_in_subgraph:
                continue
            longest_induced_path.extend(nx.shortest_path(H, *path))
            nodes_in_subgraph.extend(longest_induced_path)

        # find nodes that are not to be deleted
        nodes_to_stay = list(set(nodes_in_subgraph) - set(changed_nodes))

        # bring back the deleted edges
        for edge in g2_edges:
            G.add_edge(edge[0], edge[1], origin={"G2"})

        # find path to newly added nodes
        if new_nodes:
            for node in new_nodes:
                longest_induced_path.extend(nx.shortest_path(H, node, nodes_to_stay[0]))
                nodes_in_subgraph.extend(longest_induced_path)
        subgraph_nodes.add_nodes_from(longest_induced_path)

        # create subgraph
        subgraph = nx.subgraph(G, subgraph_nodes)

        # change updated nodes labels
        for id, attrs in subgraph.nodes(data=True):
            for attr in attrs:
                if attr == "old_text":
                    attrs["text"] = attrs["old_text"]
                if attr == "old_type":
                    attrs["type"] = attrs["old_type"]

        # trim G2 nodes and edges
        nodes_to_remove = []
        edges_to_remove = []
        for s, t, attrs in subgraph.edges(data=True):
            if len(attrs["origin"]) == 1:
                for elem in attrs["origin"]:
                    if elem == "G2":
                        edges_to_remove.append((s, t))
        for id, attrs in subgraph.nodes(data=True):
            if len(attrs["origin"]) == 1:
                for elem in attrs["origin"]:
                    if elem == "G2":
                        nodes_to_remove.append(id)

        pattern = nx.DiGraph(subgraph)
        pattern.remove_edges_from(edges_to_remove)
        pattern.remove_nodes_from(nodes_to_remove)
        return pattern

    def translate_changes_into_rule(self, raw_pattern, nodes_to_add: dict, nodes_to_update: dict, nodes_to_delete: dict,
                                    edges_to_add: list,
                                    edges_to_delete: list):
        # adjust pattern: remove extra attributes
        pattern, transformations = {}, {}
        pattern["nodes"] = []
        for id, attrs in raw_pattern.nodes(data=True):
            for type, text in zip(attrs["type"], attrs["text"]):
                pattern["nodes"].append({"node_id": id, "type": type, "text": text})
        pattern["edges"] = []
        for s, t in raw_pattern.edges():
            pattern["edges"].append({"parent_node_id": s, "child_node_id": t})

        # add nodes
        if nodes_to_add:
            transformations["add_nodes_with_attributes"] = []
            for key in nodes_to_add:
                for type, text in zip(nodes_to_add[key]["type"], nodes_to_add[key]["text"]):
                    transformations["add_nodes_with_attributes"].append(
                        {"node_id": key, "type": type, "text": text})

        # add edges
        if edges_to_add:
            transformations["add_edges"] = []
            for (s, t) in edges_to_add:
                transformations["add_edges"].append({"parent_node_id": s, "child_node_id": t})

        # update nodes
        if nodes_to_update:
            transformations["update_node_attributes"] = []
            for key in nodes_to_update:
                for type, text in zip(nodes_to_update[key]["old"]["type"], nodes_to_update[key]["old"]["text"]):
                    transformations["update_node_attributes"].append(
                        {"node_id": key, "type": type,
                         "text": text})

        # remove edges
        if edges_to_delete:
            transformations["remove_edges"] = []
            for (s, t) in edges_to_delete:
                transformations["remove_edges"].append({"parent_node_id": s, "child_node_id": t})

        # remove nodes
        if nodes_to_delete:
            transformations["remove_nodes"] = []
            for node in nodes_to_delete:
                transformations["remove_nodes"].append({"node_id": node})

        # print("pattern:")
        # print(pattern)
        # print("transformations:")
        # print(transformations)

        pattern_dict = {"pattern": pattern}
        transformation_dict = {"transformations": transformations}
        print(transformation_dict)
        return pattern_dict, transformation_dict

    # pattern | result
    def get_transformation_result(self, pattern: NXGraph, rule: dict):
        # print_graph(pattern)
        rule = Rule.from_json(rule)
        result = NXGraph()
        result.add_nodes_from(pattern.nodes(data=True))
        result.add_edges_from(pattern.edges(data=True))
        instances = result.find_matching(pattern)
        for instance in instances:
            result.rewrite(rule, instance)
        print("pattern:")
        print_graph(pattern)
        print("result:")
        print_graph(result)
        return result


if __name__ == "__main__":
    G1, G2 = NXGraph(), NXGraph()
    G1.add_nodes_from([(0, {"type": "call", "text": "A"}),
                       (1, {"type": "call", "text": "B"}),
                       (2, {"type": "keyword_argument", "text": "D", "identifier": "d"}),
                       (3, {"type": "function", "text": "E"}),
                       (4, {"type": "function", "text": "F"}),
                       (6, {"type": "function", "text": "H"}),
                       (7, {"type": "function", "text": "I"}),
                       (8, {"type": "function", "text": "J"}),
                       (9, {"type": "function", "text": "K"}),
                       (10, {"type": "function", "text": "L"})])
    G1.add_edges_from([(0, 1), (1, 2), (0, 3), (2, 4), (4, 6), (7, 0), (8, 0), (9, 2), (2, 10)])

    G2.add_nodes_from([(0, {"type": "call", "text": "A"}),
                       (1, {"type": "call", "text": "C"}),
                       (2, {"type": "call", "text": "D"}),
                       (3, {"type": "call", "text": "E"}),
                       (4, {"type": "function", "text": "F"}),
                       (5, {"type": "function", "text": "G"}),
                       (7, {"type": "function", "text": "I"}),
                       (8, {"type": "function", "text": "J"}),
                       (9, {"type": "function", "text": "K"}),
                       (10, {"type": "function", "text": "L"})])
    G2.add_edges_from([(0, 1), (1, 2), (0, 3), (3, 4), (4, 5), (7, 0), (8, 0), (9, 2), (2, 10)])

    rule_extractor = RuleExtractor()
    rule_extractor.extract_rule(G1, G2)
