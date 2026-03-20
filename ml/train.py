import torch
from torch_geometric.loader import DataLoader
from dataset import load_dataset
from model import VulnerabilityGNN
from sklearn.model_selection import train_test_split

# Load dataset
dataset = load_dataset()

train_data, test_data = train_test_split(
    dataset, test_size=0.2, random_state=42
)

train_loader = DataLoader(train_data, batch_size=4, shuffle=True)
test_loader = DataLoader(test_data, batch_size=4)

# Model
model = VulnerabilityGNN()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
pos_weight = torch.tensor([3.0])
loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

def evaluate(loader):
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for batch in loader:
            preds = model(batch)
            predicted = (torch.sigmoid(preds) > 0.5).int()
            correct += (predicted == batch.y.int()).sum().item()
            total += batch.y.size(0)

    return correct / total if total > 0 else 0

# Training loop
for epoch in range(20):
    model.train()
    total_loss = 0

    for batch in train_loader:
        optimizer.zero_grad()
        out = model(batch)
        loss = loss_fn(out, batch.y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    acc = evaluate(test_loader)
    print(f"Epoch {epoch+1:02d} | Loss {total_loss:.4f} | Acc {acc:.2f}")

torch.save(model.state_dict(), "model.pt")
print("Model saved to ml/model.pt")


