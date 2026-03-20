import os
import csv

DATASET_DIR = "dataset/smartbugs/dataset"
OUT_FILE = "contract_labels.csv"

with open(OUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["contract", "vulnerability"])

    for vuln in os.listdir(DATASET_DIR):
        vuln_path = os.path.join(DATASET_DIR, vuln)
        if os.path.isdir(vuln_path):
            for file in os.listdir(vuln_path):
                if file.endswith(".sol"):
                    writer.writerow([file, vuln])

print("contract_labels.csv generated")
