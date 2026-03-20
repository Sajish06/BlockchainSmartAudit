import os
import json
import networkx as nx

AST_DIR = "ast_json"
OUT_DIR = "graphs/cfg"

os.makedirs(OUT_DIR, exist_ok=True)

def build_cfg(ast):
    G = nx.DiGraph()
    node_counter = 0
    
    def new_node(node_type):
        nonlocal node_counter
        node_id = f"N{node_counter}"
        node_counter += 1
        G.add_node(
            node_id,
            node_type=node_type,
            # Control flow
            is_conditional=1 if node_type in ["IfStatement"] else 0,
            is_loop=1 if node_type in ["ForStatement", "WhileStatement"] else 0,
            # Calls
            is_external_call=1 if node_type == "FunctionCall" else 0,
            # State changes
            is_state_write=1 if node_type == "Assignment" else 0,
            # Exit points
            is_return=1 if node_type == "Return" else 0,
        )

        return node_id

    def visit(node, parent=None):
        if isinstance(node, dict):
            node_type = node.get("nodeType")
            if node_type in ["IfStatement", "ForStatement", "WhileStatement", 
                             "Return", "ExpressionStatement", "VariableDeclarationStatement"]:
                current = new_node(node_type)
                if parent:
                    G.add_edge(parent, current)
                parent = current
            
            for child in node.values():
                visit(child, parent)
        
        elif isinstance(node, list):
            for item in node:
                visit(item, parent)

    start = new_node("ENTRY")
    visit(ast, start)
    return G

for file in os.listdir(AST_DIR):
    if file.endswith(".json"):
        path = os.path.join(AST_DIR, file)
        with open(path, "r") as f:
            ast = json.load(f)
        
        cfg = build_cfg(ast)
        outpath = os.path.join(OUT_DIR, file.replace(".json",".graphml"))
        nx.write_graphml(cfg, outpath)
        
        print(f"[OK] CFG built for {file}")
