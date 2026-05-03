import os
import random
import pandas as pd
import numpy as np
from PIL import Image

def generate_dummy_data(num_samples=100, output_dir="data"):
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    data = []
    
    for i in range(num_samples):
        # Generate a random dummy image (e.g. noise or simple colored square)
        img_name = f"gold_sample_{i}.jpg"
        img_path = os.path.join(images_dir, img_name)
        
        # Creating a random colored image to simulate an image
        color = tuple(np.random.randint(0, 255, size=3).tolist())
        img = Image.new('RGB', (300, 300), color=color)
        img.save(img_path)
        
        # Generate random labels
        purity = random.choice([0, 1, 2, 3]) # 14K, 18K, 22K, 24K
        weight = round(random.uniform(2.0, 50.0), 2) # 2g to 50g
        fraud = random.choice([0, 1]) # 0 Genuine, 1 Fake
        item_type = random.choice(list(range(10))) # 0 to 9 types
        
        data.append({
            "image_path": img_name,
            "purity": purity,
            "weight": weight,
            "fraud": fraud,
            "type": item_type
        })
        
    df = pd.DataFrame(data)
    df.to_csv(os.path.join(output_dir, "labels.csv"), index=False)
    print(f"Generated {num_samples} dummy samples in {output_dir}")

if __name__ == "__main__":
    generate_dummy_data(100) # Generating 100 dummy samples
