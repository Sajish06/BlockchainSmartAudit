import sys
import subprocess
import torch
import networkx as nx
from torch_geometric.data import Data
from ml.model import VulnerabilityGNN

# ---------------- CONFIG ----------------
MODEL_PATH = "ml/model.pt"
CFG_DIR = "graphs/cfg"
RISK_THRESHOLD = 0.7
# ----------------------------------------


def run(cmd):
    subprocess.run(cmd, shell=True, check=True)


def build_graph(contract_name):
    print("[+] Extracting AST")
    run("python extract_ast.py")

    print("[+] Building CFG")
    run("python build_cfg.py")

    cfg_path = f"{CFG_DIR}/{contract_name}.graphml"
    return cfg_path


def load_graph(path):
    G = nx.read_graphml(path)
    node_map = {n: i for i, n in enumerate(G.nodes())}

    features = []
    edges = []

    for _, attrs in G.nodes(data=True):
        features.append([
            int(attrs.get("is_external_call", 0)),
            int(attrs.get("is_state_write", 0)),
            int(attrs.get("is_conditional", 0)),
            int(attrs.get("is_loop", 0)),
            int(attrs.get("is_return", 0)),
        ])

    for src, dst in G.edges():
        edges.append([node_map[src], node_map[dst]])

    x = torch.tensor(features, dtype=torch.float)
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()

    return Data(x=x, edge_index=edge_index)


def infer_risk(cfg_path):
    model = VulnerabilityGNN()
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()

    data = load_graph(cfg_path)

    with torch.no_grad():
        logits = model(data)
        score = torch.sigmoid(logits).item()

    return score


# ---------------- MAIN ----------------
if len(sys.argv) != 2:
    print("Usage: python check_contract.py <Contract.sol>")
    sys.exit(1)

contract_file = sys.argv[1]
contract_name = contract_file.replace(".sol", "")

print(f"[+] Contract loaded: {contract_file}")

cfg_path = build_graph(contract_name)
score = infer_risk(cfg_path)

print(f"[+] AI Risk Score: {score:.2f}")

if score >= RISK_THRESHOLD:
    print("[⚠] High-risk patterns detected (AI prediction only)")
    print("    No exploit executed automatically.")
    print("    Run phase4/scripts/exploit_runner.py manually if needed.")
else:
    print("[✔] Low-risk patterns detected (AI prediction only)")
