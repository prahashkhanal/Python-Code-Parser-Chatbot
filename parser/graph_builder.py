import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser.ast_parser import analyze_directory


def build_call_graph(directory):

    data = analyze_directory(directory)
    G = nx.DiGraph()

    for file in data:

        for func in file["functions"]:
            for call in func["calls"]:
                G.add_edge(func["function_name"], call)

        for cls in file["classes"]:
            for method in cls["methods"]:
                method_name = f"{cls['class_name']}.{method['function_name']}"
                for call in method["calls"]:
                    G.add_edge(method_name, call)

    # keep only important nodes
    degree = dict(G.degree())
    important = sorted(degree, key=degree.get, reverse=True)[:10]
    G = G.subgraph(important)

    plt.figure(figsize=(10, 7))

    pos = nx.spring_layout(G, k=2, iterations=50)

    labels = {node: node.split(".")[-1] for node in G.nodes}

    nx.draw(G, pos, labels=labels, with_labels=True,
            node_color="skyblue", node_size=2000, font_size=10)

    plt.title("Simplified Function Flow")
    plt.axis("off")

    os.makedirs("static", exist_ok=True)
    plt.savefig("static/call_graph.png")
    plt.close()

    print("Call graph generated.")