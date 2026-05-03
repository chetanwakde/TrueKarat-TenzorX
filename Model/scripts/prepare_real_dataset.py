import os
import shutil
import random
import pandas as pd

def find_images(directory):
    valid_exts = {'.jpg', '.jpeg', '.png'}
    image_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in valid_exts:
                image_paths.append(os.path.join(root, file))
    return image_paths

def main():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    images_out_dir = os.path.join(out_dir, "images")
    
    os.makedirs(images_out_dir, exist_ok=True)
    
    # Mapping of repo name to Type label (from src/api.py)
    # 0: Ring, 1: Bangle, 2: Necklace
    repo_mapping = {
        "RingFIR": 0,
        "BangleFIR": 1,
        "NecklaceFIR": 2
    }
    
    data = []
    
    print("Preparing real dataset...")
    
    for repo_name, type_label in repo_mapping.items():
        repo_path = os.path.join(raw_dir, repo_name)
        if not os.path.exists(repo_path):
            print(f"Warning: {repo_path} not found. Did you run download_github_data.py?")
            continue
            
        images = find_images(repo_path)
        print(f"Found {len(images)} images for {repo_name} (Type {type_label})")
        
        for idx, img_path in enumerate(images):
            # Create a unique filename
            new_filename = f"{repo_name}_{idx}.jpg"
            dest_path = os.path.join(images_out_dir, new_filename)
            
            try:
                # Copy image
                shutil.copy2(img_path, dest_path)
                
                # Assign dummy values for the other heads since these datasets only have Type
                purity = random.choice([0, 1, 2, 3]) # 14K, 18K, 22K, 24K
                weight = round(random.uniform(5.0, 40.0), 2)
                fraud = random.choice([0, 1])
                
                data.append({
                    "image_path": new_filename,
                    "purity": purity,
                    "weight": weight,
                    "fraud": fraud,
                    "type": type_label
                })
            except Exception as e:
                print(f"Error copying {img_path}: {e}")

    df = pd.DataFrame(data)
    csv_path = os.path.join(out_dir, "labels.csv")
    df.to_csv(csv_path, index=False)
    print(f"Successfully created {csv_path} with {len(df)} real images!")

if __name__ == "__main__":
    main()
