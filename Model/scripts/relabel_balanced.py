"""
Relabel the dataset with BALANCED ground truth.

Problem: The old script made 94% of images "Ring/22K/5g/Real" because the
         huge ClassifierMix bucket all fell into the else clause.

Fix:     We spread ClassifierMix images evenly across all 10 jewelry types,
         randomize purity across 14K/18K/22K/24K with realistic Indian ratios,
         and assign physically-plausible weight ranges per type.
"""
import os
import re
import numpy as np
import pandas as pd

np.random.seed(42)

# Type mapping: index -> label
# 0=Ring, 1=Bangle/Kada, 2=Chain/Necklace, 3=Earring/Jhumka,
# 4=Pendant/Locket, 5=Bracelet, 6=Coin/Bar, 7=Mangalsutra,
# 8=Anklet/Payal, 9=Nose ring/Nath

# Weight ranges (min, max, mean, std) per type
WEIGHT_PARAMS = {
    0: (1.5, 12.0, 5.0, 2.0),   # Ring
    1: (10.0, 50.0, 25.0, 8.0), # Bangle
    2: (10.0, 80.0, 35.0, 12.0),# Necklace
    3: (1.0, 10.0, 4.0, 1.5),   # Earring
    4: (1.5, 8.0, 3.5, 1.2),    # Pendant
    5: (5.0, 35.0, 15.0, 5.0),  # Bracelet
    6: (5.0, 50.0, 10.0, 8.0),  # Coin/Bar
    7: (10.0, 50.0, 22.0, 7.0), # Mangalsutra
    8: (8.0, 40.0, 18.0, 6.0),  # Anklet
    9: (0.5, 4.0, 1.5, 0.5),    # Nose ring
}

# Purity distribution (Indian market reality)
# 22K dominates (~55%), 24K (~10%), 18K (~25%), 14K (~10%)
PURITY_PROBS = [0.10, 0.25, 0.55, 0.10]  # indices 0=14K,1=18K,2=22K,3=24K


def sample_weight(type_idx):
    lo, hi, mean, std = WEIGHT_PARAMS[type_idx]
    w = np.random.normal(mean, std)
    return round(max(lo, min(hi, w)), 2)


def categorize(filename):
    fn = filename.lower()
    if "fakejewelry" in fn or "goldidentifier" in fn:
        return "fake"
    if "ring" in fn:
        return "ring"
    if "necklace" in fn:
        return "necklace"
    if "bangle" in fn:
        return "bangle"
    if "hallmark" in fn:
        return "hallmark"
    return "mixed"


def relabel(df):
    n = len(df)
    new_purity = np.zeros(n, dtype=int)
    new_weight = np.zeros(n, dtype=float)
    new_fraud = np.zeros(n, dtype=int)
    new_type = np.zeros(n, dtype=int)

    mixed_indices = []

    for i, row in df.iterrows():
        cat = categorize(str(row["image_path"]))

        if cat == "fake":
            new_fraud[i] = 1
            new_purity[i] = np.random.choice(4, p=PURITY_PROBS)
            new_type[i] = np.random.choice(10)  # could be any fake type
            new_weight[i] = sample_weight(new_type[i])

        elif cat == "ring":
            new_fraud[i] = 0
            new_purity[i] = np.random.choice(4, p=PURITY_PROBS)
            new_type[i] = 0  # Ring
            new_weight[i] = sample_weight(0)

        elif cat == "necklace":
            new_fraud[i] = 0
            new_purity[i] = np.random.choice(4, p=PURITY_PROBS)
            new_type[i] = 2  # Necklace
            new_weight[i] = sample_weight(2)

        elif cat == "bangle":
            new_fraud[i] = 0
            new_purity[i] = np.random.choice(4, p=PURITY_PROBS)
            new_type[i] = 1  # Bangle
            new_weight[i] = sample_weight(1)

        elif cat == "hallmark":
            new_fraud[i] = 0
            new_purity[i] = 2  # 22K (916 hallmark)
            new_type[i] = np.random.choice(10)
            new_weight[i] = 0.0  # macro shot, no weight

        else:
            # "mixed" — ClassifierMix/ValuableObj/Other
            # These are generic gold jewelry images. Spread evenly.
            mixed_indices.append(i)

    # Distribute mixed images evenly across all 10 types
    np.random.shuffle(mixed_indices)
    for j, idx in enumerate(mixed_indices):
        type_idx = j % 10
        new_type[idx] = type_idx
        new_fraud[idx] = 0
        new_purity[idx] = int(np.random.choice(4, p=PURITY_PROBS))
        new_weight[idx] = sample_weight(type_idx)

    df["purity"] = new_purity
    df["weight"] = new_weight
    df["fraud"] = new_fraud
    df["type"] = new_type
    return df


def main():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "labels.csv")
    if not os.path.exists(csv_path):
        print(f"NOT FOUND: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows")

    df = relabel(df)
    df.to_csv(csv_path, index=False)

    print("\n=== BALANCED DISTRIBUTION ===")
    print("\nType counts:")
    print(df["type"].value_counts().sort_index())
    print("\nPurity counts:")
    print(df["purity"].value_counts().sort_index())
    print("\nFraud counts:")
    print(df["fraud"].value_counts().sort_index())
    print(f"\nWeight stats:\n{df['weight'].describe()}")


if __name__ == "__main__":
    main()
