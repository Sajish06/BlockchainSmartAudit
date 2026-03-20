# SmartAudit-GNN — AI-Powered Smart Contract Risk Scanner (CFG + GNN)

Smart contracts don’t “crash” when they fail — they often fail **silently** and still look correct on the surface.

**SmartAudit-GNN** is a complete end-to-end software project that analyzes Solidity smart contracts by converting them into **Control Flow Graphs (CFGs)** and running a **Graph Neural Network (GNN)** to produce an **AI-based risk score** for vulnerability patterns.

It is designed as a **security sandbox + ML pipeline**, not a web app.

---

## 🚀 What This Project Does

Given a Solidity contract (`.sol`), the system:

1. **Extracts AST** (structural representation of the code)
2. **Builds a Control Flow Graph (CFG)** (execution behavior representation)
3. **Runs a GNN model** trained on CFG patterns to output an **AI risk score**
4. (Optional) Runs an **exploit demonstration module** on a reference vulnerable contract to prove exploit feasibility

This project focuses on **program-analysis + machine learning**, which is closer to real-world security tooling than plain text-based classification.

---

## ✨ Why This Is Interesting

Most student smart contract “detectors” stop at:
- keyword matching  
- regex rules  
- or simple ML on raw Solidity text  

This project instead uses:
- **graph representations**
- **GNN-based learning**
- **execution-aware features**
- a clean pipeline that resembles real static analysis tools

---

## 🧠 Tech Stack

### Core
- **Solidity** (smart contract source)
- **Python 3.10+ / 3.11+ / 3.12**
- **PyTorch**
- **PyTorch Geometric**
- **NetworkX** (GraphML handling)

### Blockchain Sandbox (Phase 4)
- **Ganache (local blockchain)**
- **Web3.py**
- **solc (multiple versions)**

### Graph & Analysis
- AST extraction via `solc`
- CFG generation (custom script output in GraphML)

---

## 📁 Project Structure (Major Files)


smart_audit/
│
├── contracts/ # Input contracts for analysis (.sol)
│
├── dataset/
│ ├── safe/ # Safe contracts (training/reference)
│ └── vuln/ # Vulnerable contracts (training/reference)
│
├── ast_json/ # AST outputs (generated)
│
├── graphs/
│ ├── cfg/ # Control Flow Graphs (GraphML) (generated)
│ └── call_graph/ # Call graphs (optional) (generated)
│
├── ml/
│ ├── model.py # VulnerabilityGNN architecture
│ ├── dataset.py # Loads CFG graphs + labels into PyG Data
│ ├── train.py # Training loop (produces ml/model.pt)
│ └── model.pt # Saved trained model weights (generated)
│
├── extract_ast.py # Phase 1: Extracts AST JSON from .sol files
├── build_cfg.py # Phase 2: Builds CFG graphs from AST JSON
├── check_contract.py # Phase 3: AI inference on a given contract
│
└── phase4/
├── contracts/ # Reference vulnerable contracts (exploit demo)
└── scripts/
└── exploit_runner.py # Phase 4: exploit verification sandbox


---

## ⚙️ How It Works (High-Level Architecture)


Solidity Contract (.sol)
↓
AST Extraction (solc)
↓
CFG Construction (GraphML)
↓
Graph Neural Network (PyTorch Geometric)
↓
AI Risk Score (0.00 → 1.00)

---

### Why CFG + GNN?
- CFG captures **execution flow**, not just syntax.
- GNN learns patterns like:
  - external call before state update
  - unsafe withdrawal patterns
  - risky branching + state writes
  - suspicious function structures

---

## 🧪 Run Commands (The 3 Main Commands)

> These are the only commands most users need.

---

### 1) Extract AST from Solidity contracts

python extract_ast.py

What it does
Reads .sol files from contracts/
Uses solc to produce AST JSON
Saves results into:
ast_json/<contract>.json

Tech behind it
AST = Abstract Syntax Tree
It captures structure such as:
functions
modifiers
variable declarations
expressions and statements

2) Build CFG graphs from AST
python build_cfg.py

What it does
Reads AST JSON files from ast_json/
Converts them into execution-flow graphs
Saves GraphML files into:
graphs/cfg/<contract>.graphml

Tech behind it
CFG = Control Flow Graph
Nodes represent execution blocks
Edges represent possible execution transitions
Graph contains security-relevant node features such as:
is_external_call
is_state_write
is_conditional
is_loop
is_return

3) Run AI prediction on a specific contract
python check_contract.py MyContract.sol

What it does
Ensures AST + CFG exist (or rebuilds them)
Loads the trained GNN weights from:
ml/model.pt
Runs inference on the CFG
Prints:
AI risk score
high-risk / low-risk interpretation

Tech behind it
Uses PyTorch Geometric graph tensors:
x = node feature matrix
edge_index = graph connectivity
Outputs a probability-like score:
0.00 (low risk) → 1.00 (high risk)

🧨 Optional: Exploit Sandbox (Phase 4)

This module is intentionally separated from AI inference.

python phase4/scripts/exploit_runner.py

What it does
Deploys a reference vulnerable contract (e.g., reentrancy bank)
Deploys attacker contract
Executes exploit on local Ganache blockchain
Confirms exploit success by showing balance drain
Why it exists
AI is a risk signal. Exploits are proof.
This phase demonstrates that:
vulnerabilities are not theoretical
they lead to real fund loss in practice

⚠️ Note: Exploit verification currently runs on a reference vulnerable contract template.
Automatic exploit generation for arbitrary contracts is an open research problem and is future work.

---

### 📊 Output Interpretation

Example output:

[+] AI Risk Score: 0.93
[⚠] High-risk patterns detected (AI prediction only)
Risk score meaning
Score Range	Meaning
0.00 – 0.30	Likely safe patterns
0.30 – 0.70	Suspicious / uncertain
0.70 – 1.00	High-risk patterns

⚠️ The AI score is conservative and may produce false positives, especially for contracts with public state writes.

---

### 🌍 Social Relevance / Real-World Impact

Smart contract vulnerabilities are responsible for:
massive financial losses
protocol hacks
rug pulls
broken DeFi systems

This project contributes toward:
safer blockchain infrastructure
faster vulnerability triage
security automation for developers
reducing the cost of audits for small teams

Even a simple automated risk scanner can help prevent:
loss of user funds
broken governance contracts
unsafe token contracts
insecure DeFi logic

---

### 🔐 Security Notes (Responsible Use)

This tool is designed for education, research, and defensive security

Phase 4 runs on local testnets only

Do not use exploit scripts on real deployed contracts

AI output is a risk signal, not a guarantee of safety

---

### 📌 Key Design Choices
Why not a website/app?

This project is intentionally built as a:

security sandbox

ML pipeline

developer CLI tool

This makes it closer to how real security tools are used.

---

### 🛣️ Roadmap (Future Work)

Multi-class vulnerability prediction
(reentrancy, access control, unchecked call, DoS, etc.)

CFG + CallGraph fusion for richer graphs

Better false-positive reduction using “asset awareness” features

Batch scanning mode for large repositories

JSON/PDF audit report generator
