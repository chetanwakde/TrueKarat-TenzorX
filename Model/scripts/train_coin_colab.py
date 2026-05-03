"""
=========================================================
🔥 YOLO ₹10 COIN DETECTOR - GOOGLE COLAB TRAINING SCRIPT 🔥
=========================================================

INSTRUCTIONS:
1. Go to https://colab.research.google.com/ and create a "New Notebook".
2. Go to "Runtime" -> "Change runtime type" -> Select "T4 GPU" (Free).
3. Copy and paste ALL the code below into a single Colab cell and run it!
4. It will prompt you for a Roboflow API key. 
   - Go to https://app.roboflow.com/
   - Create a free account.
   - Go to this dataset: https://universe.roboflow.com/ft-india-10/indian-rupee-10-04t1e/dataset/1
   - Click "Download Dataset" -> Select "YOLOv8" format -> "Show Download Code".
   - Copy your API key and paste it into the Colab prompt.
5. Wait for training to finish (usually 10-15 minutes on a GPU).
6. Download the `best.pt` file it generates and place it in your TenzorX raw_data folder:
   `c:/Users/cheta/.antigravity/TenzorX/Model/raw_data/coin_yolo.pt`
"""

# Install required libraries
import os
os.system("pip install ultralytics roboflow")

from roboflow import Roboflow
from ultralytics import YOLO
import getpass

# 1. Authenticate and Download Dataset
print("\n🔑 Please enter your Roboflow API Key:")
api_key = getpass.getpass()

rf = Roboflow(api_key=api_key)
# Using a highly-rated public dataset for the 10 Rupee Coin
project = rf.workspace("ft-india-10").project("indian-rupee-10-04t1e")
version = project.version(1)
dataset = version.download("yolov8")

# 2. Train YOLO11 Nano Model
print("\n🚀 Starting YOLO11 Training...")

# Initialize YOLO11 nano model (fastest, perfect for mobile/realtime)
model = YOLO('yolo11n.pt') 

# Train the model on the downloaded dataset
results = model.train(
    data=f"{dataset.location}/data.yaml",
    epochs=50,          # 50 epochs is usually enough for a single class
    imgsz=640,          # standard YOLO resolution
    batch=16,           # standard batch size
    patience=10,        # stop early if no improvement
    device=0,           # use GPU
    project="coin_detector",
    name="run_1"
)

# 3. Export weights
weights_path = "coin_detector/run_1/weights/best.pt"
print(f"\n✅ Training Complete! Your model is saved at: {weights_path}")
print("⬇️ You can download it from the left sidebar in Colab (folder icon -> coin_detector -> run_1 -> weights -> best.pt)")
