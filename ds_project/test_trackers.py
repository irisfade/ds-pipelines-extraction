import parser

import static_analysis
from graph_extractor import GraphExtractor
import test_scripts
from db_tracker import setup_db
import time
from tree_sitter import Language, Parser
import utils
from static_analysis import extract_imports
import db_driver

from bfs_struc import strip_graph, load_graph, save_graph, gen_model_id, find_isomorphism

def test_isomorphism():
    setup_db()
    start_time = time.time()
    language = 'python'
    code = test_scripts.Python.code_8
    code_a = test_scripts.Python.code_8_a
    code_b = test_scripts.Python.code_8_b
    codes = [code, code_a, code_b]

    language = Language('build/my-languages.so', language)
    parser = Parser()
    parser.set_language(language)
    byteEncodings = [bytes(it, "utf8") for it in codes]
    trees = [parser.parse(byte) for byte in byteEncodings]
    extractor = GraphExtractor()
    Gs = [extractor.bfs_tree_traverser(tree) for tree in trees]
    mappings = [extract_imports(G) for G in Gs]
    Gs = [(i, strip_graph(G, 0)) for i, G in enumerate(Gs)]
    found = find_isomorphism(Gs[0][1], Gs[3:0:-1])
    #utils.print_graph(G)
    print("--- %s seconds ---" % (time.time() - start_time))
    #save_graph(G, 0, 0)
    #G = load_graph(0)
    #utils.print_graph(G)
    print("done")


def test_insertion():
    setup_db()
    kb_con = db_driver.setup_db()
    start_time = time.time()
    file = open("testScripts/simpleKMeans.py")
    code = test_scripts.Python.code_8
    code = "\n".join(file.readlines())
    byte_encoding = bytes(code, "utf8")
    language = Language('build/my-languages.so', "python")
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(byte_encoding)
    extractor = GraphExtractor()
    G = extractor.bfs_tree_traverser(tree)
    isomorphism = dict(zip(G.nodes(), G.nodes()))
    mappings = static_analysis.extract_imports(G)
    files = static_analysis.extract_files(G)
    modified = static_analysis.insert_trackers(G, byte_encoding, mappings, kb_con, isomorphism, 0, files)
    modified = utils.format_b_string(modified)
    modified = modified.replace("\\n", "\n").replace("\\'", "'")
    modified = utils.format_script(modified)
    modified = "import trackers\n" + modified.strip()
    print(modified)
    exec(modified)


if __name__ == "__main__":
    test_insertion()
