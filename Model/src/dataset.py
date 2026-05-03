import os
import numpy as np
from PIL import Image
import pandas as pd
import torch
from torch.utils.data import Dataset
import albumentations as A
from albumentations.pytorch import ToTensorV2

class GoldDataset(Dataset):
    def __init__(self, csv_file, img_dir, transform=None):
        self.data_frame = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = os.path.join(self.img_dir, self.data_frame.iloc[idx, 0])
        try:
            image = Image.open(img_name).convert("RGB")
            image = np.array(image)
        except Exception as e:
            raise FileNotFoundError(f"Image not found or unreadable at {img_name}: {e}")

        # Labels
        purity = int(self.data_frame.iloc[idx, 1])
        weight = float(self.data_frame.iloc[idx, 2])
        fraud = int(self.data_frame.iloc[idx, 3])
        item_type = int(self.data_frame.iloc[idx, 4])

        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']

        # Weight needs to be a float tensor with shape [1]
        weight_tensor = torch.tensor([weight], dtype=torch.float32)
        
        return {
            'image': image,
            'purity': torch.tensor(purity, dtype=torch.long),
            'weight': weight_tensor,
            'fraud': torch.tensor(fraud, dtype=torch.float32),  # BCEWithLogits expects float
            'type': torch.tensor(item_type, dtype=torch.long)
        }

def get_train_transforms():
    return A.Compose([
        A.Resize(300, 300),  # EfficientNet-B3 default resolution is typically 300
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
        A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=45, p=0.5),
        A.Blur(blur_limit=3, p=0.1),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])

def get_valid_transforms():
    return A.Compose([
        A.Resize(300, 300),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2(),
    ])
