import os
import torch
import csv
import networkx as nx
from torch_geometric.data import Data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_DIR = os.path.join(BASE_DIR, "graphs", "cfg")

def graph_to_data(graphml_path):
    G = nx.read_graphml(graphml_path)

    node_map = {n: i for i, n in enumerate(G.nodes())}

    edge_index = []
    for src, dst in G.edges():
        edge_index.append([node_map[src], node_map[dst]])

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()

    # Simple node feature: node degree
    features = []
    for _, attrs in G.nodes(data=True):
        features.append([
            attrs.get("is_external_call", 0),
            attrs.get("is_state_write", 0),
            attrs.get("is_conditional", 0),
            attrs.get("is_loop", 0),
            attrs.get("is_return", 0),
        ])

    x = torch.tensor(features, dtype=torch.float)


    return Data(x=x, edge_index=edge_index)

def load_labels():
    labels = {}
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LABEL_FILE = os.path.join(BASE_DIR, "contract_labels.csv")

    with open(LABEL_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels[row["contract"]] = 1
    return labels

def load_dataset():
    data_list = []
    labels = load_labels()

    for file in os.listdir(CFG_DIR):
        if file.endswith(".graphml"):
            graph_path = os.path.join(CFG_DIR, file)

            # 1. Build graph data first
            data = graph_to_data(graph_path)

            # 2. Assign label AFTER data exists
            filename = file.replace(".graphml", ".sol")
            label = labels.get(filename, 0)  # 1 = vulnerable, 0 = safe

            data.y = torch.tensor([[label]], dtype=torch.float)

            # 3. Add to dataset
            data_list.append(data)

    return data_list
