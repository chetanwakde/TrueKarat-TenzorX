"""
TrueKarat v2 Training — Balanced multi-task learning.

Key fixes over v1:
  1. 15 epochs (was 1)
  2. Class-weighted CrossEntropyLoss for type & purity heads
  3. Cosine annealing LR scheduler
  4. Validation split (80/20)
  5. Best-model checkpointing
"""
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm
from model import TrueKaratModel
from dataset import GoldDataset, get_train_transforms, get_valid_transforms
import numpy as np
import pandas as pd

def compute_class_weights(csv_path, col, num_classes):
    """Inverse-frequency class weights so minority classes get amplified."""
    df = pd.read_csv(csv_path)
    counts = df[col].value_counts().sort_index()
    total = len(df)
    weights = []
    for c in range(num_classes):
        cnt = counts.get(c, 1)
        weights.append(total / (num_classes * cnt))
    return torch.FloatTensor(weights)


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Paths
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    csv_file = os.path.join(data_dir, 'labels.csv')
    img_dir = os.path.join(data_dir, 'images')

    if not os.path.exists(csv_file):
        print(f"Labels not found: {csv_file}")
        return

    # Hyperparams
    batch_size = 16
    epochs = 5
    lr = 3e-4

    # Class weights
    type_weights = compute_class_weights(csv_file, 'type', 10).to(device)
    purity_weights = compute_class_weights(csv_file, 'purity', 4).to(device)
    print(f"Type class weights: {type_weights}")
    print(f"Purity class weights: {purity_weights}")

    # Model
    model = TrueKaratModel(num_purity_classes=4, num_type_classes=10).to(device)

    # Losses — weighted
    criterion_purity = nn.CrossEntropyLoss(weight=purity_weights)
    criterion_weight = nn.SmoothL1Loss()  # more robust than MSE
    criterion_fraud = nn.BCEWithLogitsLoss()
    criterion_type = nn.CrossEntropyLoss(weight=type_weights)

    # Optimizer + scheduler
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    # Datasets
    full_dataset = GoldDataset(csv_file=csv_file, img_dir=img_dir, transform=get_train_transforms())
    val_size = int(0.2 * len(full_dataset))
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size],
                                     generator=torch.Generator().manual_seed(42))
    # Override val transform
    val_ds.dataset.transform = get_valid_transforms()

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"Train: {train_size} | Val: {val_size}")

    best_val_loss = float('inf')
    onnx_path = os.path.join(os.path.dirname(__file__), '..', 'truekarat.onnx')

    for epoch in range(epochs):
        # ─── Train ───
        model.train()
        train_loss = 0.0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [TRAIN]")
        for batch in pbar:
            images = batch['image'].to(device)
            purity = batch['purity'].to(device)
            weight = batch['weight'].to(device)
            fraud = batch['fraud'].unsqueeze(1).to(device)
            item_type = batch['type'].to(device)

            optimizer.zero_grad()
            p_logits, w_pred, f_logits, t_logits = model(images)

            loss_p = criterion_purity(p_logits, purity)
            loss_w = criterion_weight(w_pred, weight)
            loss_f = criterion_fraud(f_logits, fraud)
            loss_t = criterion_type(t_logits, item_type)

            loss = loss_p + 0.1 * loss_w + loss_f + loss_t
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss += loss.item()
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})

        scheduler.step()

        # ─── Validate ───
        model.eval()
        val_loss = 0.0
        correct_type = 0
        correct_purity = 0
        total = 0
        with torch.no_grad():
            for batch in val_loader:
                images = batch['image'].to(device)
                purity = batch['purity'].to(device)
                weight = batch['weight'].to(device)
                fraud = batch['fraud'].unsqueeze(1).to(device)
                item_type = batch['type'].to(device)

                p_logits, w_pred, f_logits, t_logits = model(images)
                loss_p = criterion_purity(p_logits, purity)
                loss_w = criterion_weight(w_pred, weight)
                loss_f = criterion_fraud(f_logits, fraud)
                loss_t = criterion_type(t_logits, item_type)
                loss = loss_p + 0.1 * loss_w + loss_f + loss_t
                val_loss += loss.item()

                correct_type += (t_logits.argmax(1) == item_type).sum().item()
                correct_purity += (p_logits.argmax(1) == purity).sum().item()
                total += images.size(0)

        avg_train = train_loss / len(train_loader)
        avg_val = val_loss / len(val_loader)
        type_acc = 100 * correct_type / total
        purity_acc = 100 * correct_purity / total

        print(f"  Train Loss: {avg_train:.4f} | Val Loss: {avg_val:.4f} | "
              f"Type Acc: {type_acc:.1f}% | Purity Acc: {purity_acc:.1f}%")

        # Save best
        if avg_val < best_val_loss:
            best_val_loss = avg_val
            torch.save(model.state_dict(), onnx_path.replace('.onnx', '_best.pt'))
            print(f"  ✓ Best model saved (val_loss={avg_val:.4f})")

    # ─── Export best model to ONNX ───
    print("\nLoading best checkpoint and exporting to ONNX...")
    model.load_state_dict(torch.load(onnx_path.replace('.onnx', '_best.pt'), weights_only=True))
    model.eval()

    dummy_input = torch.randn(1, 3, 300, 300).to(device)
    torch.onnx.export(
        model, dummy_input, onnx_path,
        export_params=True, opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['purity', 'weight', 'fraud', 'type'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'purity': {0: 'batch_size'},
            'weight': {0: 'batch_size'},
            'fraud': {0: 'batch_size'},
            'type': {0: 'batch_size'}
        }
    )
    print(f"ONNX exported to {onnx_path}")
    print("Training complete!")


if __name__ == "__main__":
    train()
