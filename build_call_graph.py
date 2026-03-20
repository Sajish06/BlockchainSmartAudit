import os
import json
import networkx as nx

AST_DIR = "ast_json"
OUT_DIR = "graphs/call_graph"

os.makedirs(OUT_DIR, exist_ok=True)

def extract_functions(ast):
    functions = {}
    
    def visit(node):
        if isinstance(node, dict):
            if node.get("nodeType") == "FunctionDefinition":
                func_name = node.get("name") or "constructor"
                functions[node["id"]] = func_name
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for item in node:
                visit(item)
    visit(ast)
    return functions

def extract_calls(ast, functions):
    edges = []
    
    def visit(node, current_func=None):
        if isinstance(node, dict):
            if node.get("nodeType") == "FunctionDefinition":
                current_func = functions[node["id"]]
            
            if node.get("nodeType") == "FunctionCall":
                expression = node.get("expression", {})
                if expression.get("nodeType") == "Identifier":
                    called = expression.get("name")
                    if current_func and called:
                        edges.append((current_func, called))
            
            for child in node.values():
                visit(child, current_func)
                
        elif isinstance(node, list):
            for item in node:
                visit(item, current_func)
    
    visit(ast)
    return edges

for file in os.listdir(AST_DIR):
    if file.endswith(".json"):
        path = os.path.join(AST_DIR, file)
        with open(path, "r") as f:
            ast = json.load(f)
        
        functions = extract_functions(ast)
        edges = extract_calls(ast, functions)
        
        G = nx.DiGraph()
        for func in functions.values():
            G.add_node(func)
        for src, dst in edges:
            G.add_edge(src, dst)
        
        outpath = os.path.join(OUT_DIR, file)
        nx.write_graphml(G, outpath.replace(".json", ".graphml"))
        
        print(f"[OK] Call graph built for {file}")
