import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import wandb
from tqdm import tqdm
from model import TrueKaratModel
from dataset import GoldDataset, get_train_transforms

def train():
    # Initialize wandb
    wandb.init(project="truekarat-gold-assessment", name="efficientnet-b3-multitask")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Hyperparameters
    batch_size = 16
    epochs = 1
    learning_rate = 1e-4

    # Model
    model = TrueKaratModel(num_purity_classes=4, num_type_classes=10).to(device)

    # Losses
    criterion_purity = nn.CrossEntropyLoss()
    criterion_weight = nn.MSELoss()
    criterion_fraud = nn.BCEWithLogitsLoss()
    criterion_type = nn.CrossEntropyLoss()

    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Dataset and Dataloader
    # Assuming dummy data is in ../data
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    csv_file = os.path.join(data_dir, 'labels.csv')
    img_dir = os.path.join(data_dir, 'images')
    
    if not os.path.exists(csv_file):
        print(f"Labels file not found at {csv_file}. Please run generate_dummy_data.py first.")
        return

    dataset = GoldDataset(csv_file=csv_file, img_dir=img_dir, transform=get_train_transforms())
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")
        for batch in progress_bar:
            images = batch['image'].to(device)
            purity = batch['purity'].to(device)
            weight = batch['weight'].to(device)
            fraud = batch['fraud'].unsqueeze(1).to(device) # BCEWithLogits expects shape [batch_size, 1]
            item_type = batch['type'].to(device)

            optimizer.zero_grad()

            purity_logits, weight_pred, fraud_logits, type_logits = model(images)

            # Calculate individual losses
            loss_purity = criterion_purity(purity_logits, purity)
            loss_weight = criterion_weight(weight_pred, weight)
            loss_fraud = criterion_fraud(fraud_logits, fraud)
            loss_type = criterion_type(type_logits, item_type)

            # Combined loss (can be weighted)
            loss = loss_purity + 0.5 * loss_weight + loss_fraud + loss_type

            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            
            wandb.log({
                "loss_purity": loss_purity.item(),
                "loss_weight": loss_weight.item(),
                "loss_fraud": loss_fraud.item(),
                "loss_type": loss_type.item(),
                "total_loss": loss.item()
            })

            progress_bar.set_postfix({'loss': loss.item()})

    print("Training complete. Exporting to ONNX...")
    
    # Export to ONNX
    model.eval()
    dummy_input = torch.randn(1, 3, 300, 300).to(device)
    onnx_path = os.path.join(os.path.dirname(__file__), '..', 'truekarat.onnx')
    
    torch.onnx.export(
        model, 
        dummy_input, 
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['purity', 'weight', 'fraud', 'type'],
        dynamic_axes={'input': {0: 'batch_size'},
                      'purity': {0: 'batch_size'},
                      'weight': {0: 'batch_size'},
                      'fraud': {0: 'batch_size'},
                      'type': {0: 'batch_size'}}
    )
    
    print(f"ONNX model saved to {onnx_path}")
    wandb.finish()

if __name__ == "__main__":
    train()
