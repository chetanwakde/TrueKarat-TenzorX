import os
import random
import pandas as pd
import shutil
from icrawler.builtin import BingImageCrawler

def main():
    raw_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data", "FakeJewelry_icrawler")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    images_out_dir = os.path.join(out_dir, "images")
    csv_path = os.path.join(out_dir, "labels.csv")
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(images_out_dir, exist_ok=True)

    queries = [
        "imitation gold bangles",
        "artificial gold jewelry",
        "1 gram gold plated necklace",
        "fake gold ring"
    ]
    
    # Scrape images
    for query in queries:
        print(f"Scraping Bing for: {query}")
        crawler = BingImageCrawler(storage={'root_dir': raw_dir})
        crawler.crawl(keyword=query, max_num=50)

    # Move images to data/images and append to labels.csv
    valid_exts = {'.jpg', '.jpeg', '.png'}
    image_paths = []
    for file in os.listdir(raw_dir):
        ext = os.path.splitext(file)[1].lower()
        if ext in valid_exts:
            image_paths.append(os.path.join(raw_dir, file))
            
    print(f"Successfully scraped {len(image_paths)} fake jewelry images!")
    
    if len(image_paths) == 0:
        return
        
    data = []
    
    for idx, img_path in enumerate(image_paths):
        new_filename = f"FakeJewelry_{idx}.jpg"
        dest_path = os.path.join(images_out_dir, new_filename)
        
        try:
            shutil.copy2(img_path, dest_path)
            
            # Label as Fraud
            data.append({
                "image_path": new_filename,
                "purity": 0, # N/A or low purity
                "weight": round(random.uniform(5.0, 40.0), 2),
                "fraud": 1,  # FAKE
                "type": random.choice([0, 1, 2, 3]) # Random type
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
    print(f"Successfully appended {len(df_new)} FAKE jewelry images! Total images now: {len(df_combined)}")

if __name__ == "__main__":
    main()
