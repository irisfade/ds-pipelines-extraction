import json
import sqlite3
from regraph import NXGraph, Rule


class RuleEntry:
    name = ""
    description = ""
    type = ""
    by_user = bool
    rule_dict = {}

    def add_rule_to_db(self, rule_dict):
        connection = sqlite3.connect("knowledge_base.db")
        cursor = connection.cursor()

        pattern = create_pattern(rule_dict)
        rule = create_rule(pattern, rule_dict)

        self.name = rule_dict.pop("name")
        self.description = rule_dict.pop("description")
        self.type = rule_dict.pop("type")
        self.by_user = rule_dict.pop("by_user")
        self.rule_dict = rule_dict

        # get id
        cursor.execute("SELECT COUNT(*) FROM rules")
        rule_id = cursor.fetchall()[0][0] + 1

        cursor.execute(
            "INSERT INTO rules(rule_id, rule_name, rule_description, rule, rule_type, added_by_user) VALUES(?, ?, ?, ?, ?, ?)",
            [rule_id, self.name, self.description, str(self.rule_dict), self.type, self.by_user])

        rule["name"] = self.name
        rule["description"] = self.description
        rule["type"] = self.type
        rule["by_user"] = self.by_user

        if rule_exists(rule):
            raise ValueError('This rule already exists!')

        out_file = open("knowledge_base/rule_base.txt", "a")
        out_file.write(str(rule) + "\n")
        out_file.close()

        connection.commit()

        print(rule)
        print("Rule created successfully!")
        pass


def get_rules_from_db(cursor):
    cursor.execute("SELECT rule FROM rules ORDER BY rule_id")
    rules = cursor.fetchall()
    return rules


def create_rule_from_file(path):
    # create rule
    rule_dict = get_dict_from_json(path)

    rule_entry = RuleEntry()
    rule_entry.add_rule_to_db(rule_dict)


def rule_exists(rule):
    with open("knowledge_base/rule_base.txt") as file:
        for line in file:
            if str(rule) == line.strip():
                return True


def get_dict_from_json(path):
    # read json file
    f = open(path, "r")
    rule_dict = json.loads(f.read())
    return rule_dict


def create_pattern(rule_dict):
    # create pattern
    pattern = NXGraph()

    # get nodes
    if "nodes" in rule_dict["pattern"]:
        node_list = rule_dict["pattern"]["nodes"]
        # parse input
        for node in node_list:
            node_id = node.pop("node_id")
            if node:
                # print(node)
                pattern.add_node(node_id, node)
            else:
                pattern.add_node(node_id)

    # get edges
    if "edges" in rule_dict["pattern"]:
        edge_list = rule_dict["pattern"]["edges"]
        # parse input
        for edge in edge_list:
            # extract nodes ids
            parent_node_id = edge.pop("parent_node_id")
            child_node_id = edge.pop("child_node_id")
            # if other attributes left, extract them too
            if edge:
                edge_attrs = edge
                pattern.add_edge(parent_node_id, child_node_id, edge_attrs)
            else:
                pattern.add_edge(parent_node_id, child_node_id)

    return pattern


def create_rule(pattern, rule_dict):
    # create rule
    rule = Rule.from_transform(pattern)
    # transformations
    # get nodes to remove
    if "remove_nodes" in rule_dict["transformations"]:
        nodes_to_remove = rule_dict["transformations"]["remove_nodes"]
        # parse input
        for node in nodes_to_remove:
            node_id = node.pop("node_id")
            rule.inject_remove_node(node_id)

    # get attributes to remove
    if "remove_node_attrs" in rule_dict["transformations"]:
        atts_to_remove = rule_dict["transformations"]["remove_node_attrs"]
        # parse input
        for node in atts_to_remove:
            node_id = node.pop("node_id")
            node_attrs_to_remove = node
            rule.inject_remove_node_attrs(node_id, node_attrs_to_remove)

    # get attributes to update
    if "update_node_attributes" in rule_dict["transformations"]:
        attrs_to_update = rule_dict["transformations"]["update_node_attributes"]
        # parse input
        for node in attrs_to_update:
            node_id = node.pop("node_id")
            node_attrs_to_update = node
            rule.inject_update_node_attrs(node_id, node_attrs_to_update)

    # get nodes to add
    if "add_nodes_with_attributes" in rule_dict["transformations"]:
        nodes_to_add = rule_dict["transformations"]["add_nodes_with_attributes"]
        # parse input
        for node in nodes_to_add:
            node_id = node.pop("node_id")
            node_attrs = node
            rule.inject_add_node(node_id, node_attrs)

    # get attributes to add
    if "add_node_attributes" in rule_dict["transformations"]:
        attributes_to_add = rule_dict["transformations"]["add_node_attributes"]
        # parse input
        print("yes")
        for node in attributes_to_add:
            node_id = node.pop("node_id")
            node_attrs = node
            rule.inject_add_node_attrs(node_id, node_attrs)

    # get nodes to clone
    if "clone_nodes" in rule_dict["transformations"]:
        nodes_to_clone = rule_dict["transformations"]["clone_nodes"]
        for node in nodes_to_clone:
            node_id = node.pop("node_id")
            rule.inject_clone_node(node_id)
        # TODO cloned node id not working

    # get nodes to merge
    if "merge_nodes" in rule_dict["transformations"]:
        nodes_to_merge = rule_dict["transformations"]["merge_nodes"]
        node_ids_to_merge = []
        for node in nodes_to_merge:
            node_id = node.pop("node_id")
            node_ids_to_merge.append(node_id)
        rule.inject_merge_nodes(node_ids_to_merge)
        # TODO add new node id

    # get edges to add
    if "add_edges" in rule_dict["transformations"]:
        edges_to_add = rule_dict["transformations"]["add_edges"]
        for edge in edges_to_add:
            parent_node_id = edge.pop("parent_node_id")
            child_node_id = edge.pop("child_node_id")
            attributes = edge
            rule.inject_add_edge(parent_node_id, child_node_id, attributes)

    # get edge attributes to add
    if "add_attributes_to_edges" in rule_dict["transformations"]:
        edge_attrs_to_add = rule_dict["transformations"]["add_attributes_to_edges"]
        for edge in edge_attrs_to_add:
            parent_node_id = edge.pop("parent_node_id")
            child_node_id = edge.pop("child_node_id")
            attributes = edge
            rule.inject_add_edge_attrs(parent_node_id, child_node_id, attributes)

    # get edges to remove
    if "remove_edges" in rule_dict["transformations"]:
        edges_to_remove = rule_dict["transformations"]["remove_edges"]
        for edge in edges_to_remove:
            parent_node_id = edge.pop("parent_node_id")
            child_node_id = edge.pop("child_node_id")
            rule.inject_remove_edge(parent_node_id, child_node_id)

    # get edge attributes to remove
    if "remove_edge_attrs" in rule_dict["transformations"]:
        edge_attrs_to_remove = rule_dict["transformations"]["remove_edge_attrs"]
        for edge in edge_attrs_to_remove:
            parent_node_id = edge.pop("parent_node_id")
            child_node_id = edge.pop("child_node_id")
            attributes = edge
            rule.inject_remove_edge_attrs(parent_node_id, child_node_id, attributes)

    # get edge attributes to update
    if "update_edge_attrs" in rule_dict["transformations"]:
        edge_attrs_to_update = rule_dict["transformations"]["update_edge_attrs"]
        for edge in edge_attrs_to_update:
            parent_node_id = edge.pop("parent_node_id")
            child_node_id = edge.pop("child_node_id")
            attributes = edge
            rule.inject_update_edge_attrs(parent_node_id, child_node_id, attributes)
    rule = rule.to_json()
    return rule


if __name__ == "__main__":
    create_rule_from_file("knowledge_base/rule_creation.json")
