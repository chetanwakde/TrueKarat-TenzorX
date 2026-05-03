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

def process_yolo(yolo_dir, images_out_dir, data_list, dataset_name):
    splits = ['train', 'valid', 'test']
    count = 0
    for split in splits:
        img_dir = os.path.join(yolo_dir, split, "images")
        if not os.path.exists(img_dir):
            continue
            
        for file in os.listdir(img_dir):
            if not file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
                
            src_path = os.path.join(img_dir, file)
            new_filename = f"NewYolo_{dataset_name}_{split}_{file}"
            dest_path = os.path.join(images_out_dir, new_filename)
            
            try:
                shutil.copy2(src_path, dest_path)
                data_list.append({
                    "image_path": new_filename,
                    "purity": 2,
                    "weight": 10.0,
                    "fraud": 0,
                    "type": 0 # Default ring
                })
                count += 1
            except Exception as e:
                pass
    print(f"Added {count} images from YOLO {dataset_name}")

def process_tanishq(tanishq_dir, images_out_dir, data_list):
    count = 0
    # Necklaces
    necklaces = find_images(os.path.join(tanishq_dir, "Jewellery_Data", "necklace"))
    for idx, img in enumerate(necklaces):
        new_name = f"NewTanishq_Necklace_{idx}.jpg"
        dest_path = os.path.join(images_out_dir, new_name)
        try:
            shutil.copy2(img, dest_path)
            data_list.append({"image_path": new_name, "purity": 2, "weight": 35.0, "fraud": 0, "type": 2})
            count += 1
        except: pass
        
    # Rings
    rings = find_images(os.path.join(tanishq_dir, "Jewellery_Data", "ring"))
    for idx, img in enumerate(rings):
        new_name = f"NewTanishq_Ring_{idx}.jpg"
        dest_path = os.path.join(images_out_dir, new_name)
        try:
            shutil.copy2(img, dest_path)
            data_list.append({"image_path": new_name, "purity": 2, "weight": 5.0, "fraud": 0, "type": 0})
            count += 1
        except: pass
    print(f"Added {count} images from new Tanishq archive.")

def main():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    images_out_dir = os.path.join(out_dir, "images")
    csv_path = os.path.join(out_dir, "labels.csv")
    
    os.makedirs(images_out_dir, exist_ok=True)
    data = []
    
    yolo_dir = os.path.join(raw_dir, "jewellery classifier.v1i.yolov11")
    tanishq_dir = os.path.join(raw_dir, "tanishqarchive_classifier")
    
    if os.path.exists(yolo_dir):
        process_yolo(yolo_dir, images_out_dir, data, "ClassifierV1")
    if os.path.exists(tanishq_dir):
        process_tanishq(tanishq_dir, images_out_dir, data)
        
    if not data:
        print("No new images found.")
        return
        
    df_new = pd.DataFrame(data)
    if os.path.exists(csv_path):
        df_existing = pd.read_csv(csv_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
        
    df_combined.to_csv(csv_path, index=False)
    print(f"Successfully appended {len(df_new)} new dataset images! Total size: {len(df_combined)}")

if __name__ == "__main__":
    main()
