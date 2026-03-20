import torch
from torch_geometric.nn import GCNConv, global_mean_pool

class VulnerabilityGNN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(5, 16)
        self.conv2 = GCNConv(16, 32)
        self.fc = torch.nn.Linear(32, 1)

    def forward(self, data):
        x, edge_index, batch = data.x, data.edge_index, data.batch

        x = self.conv1(x, edge_index)
        x = torch.relu(x)

        x = self.conv2(x, edge_index)
        x = torch.relu(x)

        x = global_mean_pool(x, batch)
        return self.fc(x)
