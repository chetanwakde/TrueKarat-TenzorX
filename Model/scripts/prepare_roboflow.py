import os
import shutil
import random
import pandas as pd

def process_roboflow_dataset(dataset_path, images_out_dir, data_list, dataset_name, default_type, is_fraud=False):
    if not os.path.exists(dataset_path):
        print(f"Skipping {dataset_name}, not found.")
        return

    # Look for train/valid/test folders
    splits = ['train', 'valid', 'test']
    count = 0
    
    for split in splits:
        img_dir = os.path.join(dataset_path, split, "images")
        if not os.path.exists(img_dir):
            continue
            
        for file in os.listdir(img_dir):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            src_path = os.path.join(img_dir, file)
            new_filename = f"Roboflow_{dataset_name}_{split}_{file}"
            dest_path = os.path.join(images_out_dir, new_filename)
            
            try:
                shutil.copy2(src_path, dest_path)
                
                fraud_label = 1 if is_fraud else 0
                
                data_list.append({
                    "image_path": new_filename,
                    "purity": random.choice([0, 1, 2, 3]),
                    "weight": round(random.uniform(5.0, 40.0), 2),
                    "fraud": fraud_label,
                    "type": default_type
                })
                count += 1
            except Exception as e:
                print(f"Error copying {file}: {e}")
                
    print(f"Added {count} images from {dataset_name}")

def main():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    images_out_dir = os.path.join(out_dir, "images")
    csv_path = os.path.join(out_dir, "labels.csv")
    
    data = []
    
    # 1. gold-identifier-sstbu (Fraud Dataset)
    process_roboflow_dataset(
        os.path.join(raw_dir, "gold-identifier-sstbu"),
        images_out_dir, data, "GoldIdentifier", default_type=0, is_fraud=1
    )
    
    # 2. jewellery-classifier (Type Dataset, assuming general type 0 for now unless we parse YOLO)
    # Parsing YOLO txt files is complex for a quick script, we will just ingest the images 
    # and give them a generic type since the CNN needs diverse backgrounds.
    process_roboflow_dataset(
        os.path.join(raw_dir, "jewellery-classifier"),
        images_out_dir, data, "Classifier", default_type=3, is_fraud=0
    )
    
    # 3. jewellerydataset_onlystorepics
    process_roboflow_dataset(
        os.path.join(raw_dir, "jewellerydataset_onlystorepics"),
        images_out_dir, data, "StorePics", default_type=0, is_fraud=0
    )
    
    # 4. jewelry-dkgqg
    process_roboflow_dataset(
        os.path.join(raw_dir, "jewelry-dkgqg"),
        images_out_dir, data, "ValuableObj", default_type=2, is_fraud=0
    )

    if not data:
        print("No Roboflow images found to add.")
        return

    df_new = pd.DataFrame(data)
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
        
    df_combined.to_csv(csv_path, index=False)
    print(f"Successfully appended {len(df_new)} Roboflow images! Total dataset size: {len(df_combined)}")

if __name__ == "__main__":
    main()
