import os
import cv2
import numpy as np
import random
import yaml
import shutil
from pathlib import Path
import urllib.request
from ultralytics import YOLO

# ─── Configuration ──────────────────────────────────────────────────────────
BASE_DIR = Path(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = BASE_DIR / "raw_data"
YOLO_DATASET_DIR = DATA_DIR / "synthetic_coin_dataset"
COIN_TEMPLATES = [
    DATA_DIR / "Rs10-Heads.png",
    DATA_DIR / "Rs10-Tails.png"
]
IMG_SIZE = 320
NUM_IMAGES = 200
EPOCHS = 5

def download_backgrounds():
    """Download a few random texture images from public sources."""
    bg_dir = YOLO_DATASET_DIR / "bg_temp"
    bg_dir.mkdir(parents=True, exist_ok=True)
    urls = [
        "https://images.unsplash.com/photo-1594818898109-44704fb548f6?q=80&w=640", # Marble
        "https://images.unsplash.com/photo-1510172951991-856a654063f9?q=80&w=640", # Wood
        "https://images.unsplash.com/photo-1558244661-d248897f7bc4?q=80&w=640", # Fabric
        "https://images.unsplash.com/photo-1550684376-efcbd6e3f031?q=80&w=640", # Dark table
        "https://images.unsplash.com/photo-1588628566587-bf5c4d32e92c?q=80&w=640", # White paper
    ]
    
    bgs = []
    print("Downloading background textures...")
    for i, url in enumerate(urls):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                img_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                if img is not None:
                    bgs.append(img)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            
    # If network fails, generate colored noise backgrounds
    if not bgs:
        for i in range(5):
            bg = np.random.randint(100, 255, (640, 640, 3), dtype=np.uint8)
            bgs.append(bg)
            
    return bgs

def create_synthetic_dataset():
    """Generate images with coins pasted at random locations."""
    print("Generating synthetic YOLO dataset...")
    if YOLO_DATASET_DIR.exists():
        shutil.rmtree(YOLO_DATASET_DIR)
        
    images_dir = YOLO_DATASET_DIR / "images" / "train"
    labels_dir = YOLO_DATASET_DIR / "labels" / "train"
    images_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    
    # Load coins with alpha channel
    coins = []
    for p in COIN_TEMPLATES:
        c = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
        if c is not None and c.shape[2] == 4:
            coins.append(c)
            
    if not coins:
        raise ValueError("Could not load coin templates with alpha channel!")
        
    backgrounds = download_backgrounds()
    
    for i in range(NUM_IMAGES):
        # Pick background
        bg = random.choice(backgrounds).copy()
        h_bg, w_bg = bg.shape[:2]
        
        # Crop background to IMG_SIZE
        if h_bg > IMG_SIZE and w_bg > IMG_SIZE:
            x = random.randint(0, w_bg - IMG_SIZE)
            y = random.randint(0, h_bg - IMG_SIZE)
            bg = bg[y:y+IMG_SIZE, x:x+IMG_SIZE]
        else:
            bg = cv2.resize(bg, (IMG_SIZE, IMG_SIZE))
            
        # Optional: sometimes don't put a coin (negative sample)
        if random.random() < 0.1:
            cv2.imwrite(str(images_dir / f"{i}.jpg"), bg)
            open(str(labels_dir / f"{i}.txt"), 'w').close()
            continue
            
        # Pick coin and augment
        coin = random.choice(coins)
        
        # Random scale
        scale = random.uniform(0.15, 0.4)
        c_w = int(IMG_SIZE * scale)
        c_h = c_w
        coin_resized = cv2.resize(coin, (c_w, c_h), interpolation=cv2.INTER_AREA)
        
        # Random brightness on coin
        alpha = random.uniform(0.7, 1.3)
        bgr = coin_resized[:, :, :3]
        a = coin_resized[:, :, 3]
        bgr = cv2.convertScaleAbs(bgr, alpha=alpha, beta=0)
        coin_resized = np.dstack([bgr, a])
        
        # Random position
        x_offset = random.randint(0, IMG_SIZE - c_w)
        y_offset = random.randint(0, IMG_SIZE - c_h)
        
        # Paste with alpha blending
        for y in range(c_h):
            for x in range(c_w):
                alpha_val = coin_resized[y, x, 3] / 255.0
                if alpha_val > 0.1:
                    bg[y_offset+y, x_offset+x] = (alpha_val * coin_resized[y, x, :3] + 
                                                  (1 - alpha_val) * bg[y_offset+y, x_offset+x])
                    
        # Calculate YOLO bounding box
        cx = (x_offset + c_w / 2) / IMG_SIZE
        cy = (y_offset + c_h / 2) / IMG_SIZE
        w = c_w / IMG_SIZE
        h = c_h / IMG_SIZE
        
        # Save
        cv2.imwrite(str(images_dir / f"{i}.jpg"), bg)
        with open(str(labels_dir / f"{i}.txt"), "w") as f:
            f.write(f"0 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
            
    # Create data.yaml
    yaml_content = {
        'path': str(YOLO_DATASET_DIR.absolute()),
        'train': 'images/train',
        'val': 'images/train', # Use train for val since we just want it to overfit
        'names': {0: 'Rs10_Coin'}
    }
    with open(YOLO_DATASET_DIR / "data.yaml", "w") as f:
        yaml.dump(yaml_content, f)
        
    print(f"Generated {NUM_IMAGES} synthetic training images!")
    return YOLO_DATASET_DIR / "data.yaml"

def train_yolo(data_yaml_path):
    print("\n🚀 Starting YOLO11n Local Training...")
    model = YOLO('yolo11n.pt') 
    
    # Train on CPU
    results = model.train(
        data=str(data_yaml_path),
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=16,
        device='cpu',
        project=str(DATA_DIR),
        name="yolo_coin_run",
        exist_ok=True,
        verbose=False
    )
    
    weights_path = DATA_DIR / "yolo_coin_run" / "weights" / "best.pt"
    target_path = DATA_DIR / "coin_yolo.pt"
    
    if weights_path.exists():
        shutil.copy(weights_path, target_path)
        print(f"✅ SUCCESS! Trained YOLO model saved to: {target_path}")
    else:
        print("❌ ERROR: Training failed to produce best.pt")

if __name__ == "__main__":
    yaml_path = create_synthetic_dataset()
    train_yolo(yaml_path)
    
    # Clean up dataset to save space
    print("Cleaning up synthetic dataset...")
    shutil.rmtree(YOLO_DATASET_DIR)
    print("Done! Restart the TrueKarat backend.")
