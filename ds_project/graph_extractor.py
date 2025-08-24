from rule_executioner import transform_graph
from tree_sitter import Language, Parser
import test_scripts
import time
from regraph import NXGraph


class GraphExtractor:

    def __init__(self):
        Language.build_library(
            # Store the library in the `build` directory
            'build/my-languages.so',
            # Include one or more languages
            [
                'parsers/tree-sitter-python',
                'parsers/tree-sitter-r',
                'parsers/tree-sitter-snakemake-pure'
            ]
        )

    def extract_pipeline(self, code, language):
        assert language != '', 'language is not set'
        language = Language('build/my-languages.so', language)
        parser = Parser()
        parser.set_language(language)
        b = bytes(code, "utf8")
        tree = parser.parse(b)
        nxgraph = self.bfs_tree_traverser(tree)
        G = transform_graph(nxgraph)
        return G


    def bfs_tree_traverser(self, tree):
        """
        Traverses a tree-sitter with Breadth-first search algorithm and
        converts it into an NXGraph
        :param tree: tree-sitter to be traversed
        :return: NXGraph after traversal of a tree-sitter tree
        """
        root_node = tree.root_node
        G = NXGraph()
        node_id, parent_id = 0, 0
        # lists to queue the nodes in order and identify already visited nodes
        visited, queue = [], []
        visited.append(root_node)
        queue.append(root_node)

        # add root_node to the graph
        G.add_node(0, attrs={"type": root_node.type, "text": root_node.text})

        # loop to visit each node
        while queue:
            node = queue.pop(0)
            for i, child_node in enumerate(node.children):
                if child_node not in visited:
                    node_id += 1
                    # add child node to graph
                    G.add_node(node_id, attrs={"type": child_node.type, "text": child_node.text, "pos": i, "start": child_node.start_byte, "end": child_node.end_byte})
                    # add edge between parent_node and child_node
                    G.add_edge(parent_id, node_id)
                    visited.append(child_node)
                    queue.append(child_node)
            # set parent_id to the id of the next node in queue
            parent_id = parent_id + 1

        return G


if __name__ == "__main__":
    start_time = time.time()
    language = 'python'
    code = test_scripts.Python.code_0
    start = time.time()
    extractor = GraphExtractor()
    extractor.extract_pipeline(code, language)
    print("--- %s seconds ---" % (time.time() - start_time))

