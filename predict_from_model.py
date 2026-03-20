import sys
import torch
import networkx as nx
from torch_geometric.data import Data
from ml.model import VulnerabilityGNN

if len(sys.argv) != 2:
    print("Usage: python predict_from_cfg.py <CFG.graphml>")
    sys.exit(1)

cfg_path = sys.argv[1]

# Load CFG
G = nx.read_graphml(cfg_path)
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

data = Data(x=x, edge_index=edge_index)

# Load model
model = VulnerabilityGNN()
model.load_state_dict(torch.load("ml/model.pt"))
model.eval()

# Predict
with torch.no_grad():
    score = torch.sigmoid(model(data)).item()

print(f"AI Risk Score: {score:.4f}")
