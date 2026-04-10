import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from parser.ast_parser import analyze_directory

# ─────────────────────────────
# CONFIG (BALANCED, NOT TOO STRICT)
# ─────────────────────────────
MAX_NODES = 80          # keep more nodes (you have zoom)
MIN_CONNECTIONS = 1     # allow most nodes
MAX_LABEL_LEN = 14      # shorter labels

BUILTINS = {
    "len","print","range","str","int","list","dict","set","tuple","open",
    "map","filter","sorted","append","get","items","keys","values"
}

def shorten(name):
    name = name.split(".")[-1]
    return name if len(name) <= MAX_LABEL_LEN else name[:MAX_LABEL_LEN] + "…"

def build_call_graph(directory):
    data = analyze_directory(directory)
    G = nx.DiGraph()

    all_functions = set()

    # Collect functions
    for file in data:
        if file.get("error"):
            continue
        for f in file["functions"]:
            all_functions.add(f["function_name"])
        for cls in file["classes"]:
            for m in cls["methods"]:
                all_functions.add(f"{cls['class_name']}.{m['function_name']}")

    # Build edges
    for file in data:
        if file.get("error"):
            continue
        for f in file["functions"]:
            for call in f["calls"]:
                if call in all_functions and call not in BUILTINS:
                    G.add_edge(f["function_name"], call)

        for cls in file["classes"]:
            for m in cls["methods"]:
                name = f"{cls['class_name']}.{m['function_name']}"
                for call in m["calls"]:
                    if call in all_functions and call not in BUILTINS:
                        G.add_edge(name, call)

    if len(G.nodes) == 0:
        print("No graph to display")
        return

    # ─────────────────────────────
    # 🔥 KEEP IMPORTANT NODES FIRST
    # ─────────────────────────────
    degrees = dict(G.degree())
    if len(G.nodes) > MAX_NODES:
        top_nodes = sorted(degrees, key=lambda x: degrees[x], reverse=True)[:MAX_NODES]
        G = G.subgraph(top_nodes).copy()

    # ─────────────────────────────
    # 🔥 SUPER IMPORTANT: SPACING FIX
    # ─────────────────────────────
    pos = nx.spring_layout(
        G,
        k=3.5,          # 🔥 BIG spacing (main fix)
        iterations=300, # smoother layout
        seed=42
    )

    # ─────────────────────────────
    # COLORS + SIZE
    # ─────────────────────────────
    node_colors = []
    node_sizes = []

    for node in G.nodes:
        deg = G.degree(node)

        if deg >= 6:
            node_colors.append("#f59e0b")
            node_sizes.append(2400)
        elif deg >= 3:
            node_colors.append("#0ea5e9")
            node_sizes.append(1800)
        else:
            node_colors.append("#10b981")
            node_sizes.append(1300)

    labels = {n: shorten(n) for n in G.nodes}

    # ─────────────────────────────
    # DRAW
    # ─────────────────────────────
    plt.figure(figsize=(24, 20))   # 🔥 BIG CANVAS (IMPORTANT)
    plt.gca().set_facecolor("#0f172a")
    plt.gcf().patch.set_facecolor("#0f172a")

    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        edgecolors="#1e3a5f",
        linewidths=1
    )

    nx.draw_networkx_edges(
        G, pos,
        edge_color="#475569",
        arrows=True,
        arrowsize=14,
        width=1.2,
        alpha=0.6,
        connectionstyle="arc3,rad=0.08"  # slight curve → less overlap
    )

    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=8,
        font_color="white",
        font_weight="bold"
    )

    plt.title("Project Call Graph (Readable Layout)", color="#38bdf8", fontsize=16)
    plt.axis("off")

    os.makedirs("static", exist_ok=True)
    plt.savefig("static/call_graph.png", dpi=160, bbox_inches="tight")
    plt.close()

    print(f"✅ Improved graph generated ({len(G.nodes)} nodes)")