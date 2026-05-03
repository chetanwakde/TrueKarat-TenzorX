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
    csv_path = os.path.join(out_dir, "labels.csv")
    
    repo_path = os.path.join(raw_dir, "Tanishq", "Jewellery_Data", "necklace")
    if not os.path.exists(repo_path):
        print(f"Warning: {repo_path} not found.")
        return
        
    images = find_images(repo_path)
    print(f"Found {len(images)} images for Tanishq Necklaces (Type 2)")
    
    if len(images) == 0:
        return
        
    data = []
    
    for idx, img_path in enumerate(images):
        new_filename = f"Tanishq_Necklace_{idx}.jpg"
        dest_path = os.path.join(images_out_dir, new_filename)
        
        try:
            shutil.copy2(img_path, dest_path)
            
            purity = random.choice([0, 1, 2, 3]) 
            weight = round(random.uniform(5.0, 40.0), 2)
            fraud = random.choice([0, 1])
            
            data.append({
                "image_path": new_filename,
                "purity": purity,
                "weight": weight,
                "fraud": fraud,
                "type": 2 # Chain / Necklace
            })
        except Exception as e:
            print(f"Error copying {img_path}: {e}")

    # Append to existing labels.csv
    df_new = pd.DataFrame(data)
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
        
    df_combined.to_csv(csv_path, index=False)
    print(f"Successfully appended {len(df_new)} necklace images! Total images now: {len(df_combined)}")

if __name__ == "__main__":
    main()
