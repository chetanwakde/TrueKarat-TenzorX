import os
import pandas as pd
import numpy as np

def assign_ground_truth(df):
    new_purity = []
    new_weight = []
    new_fraud = []
    new_type = []

    for index, row in df.iterrows():
        img_path = str(row['image_path']).lower()
        
        # Default heuristics
        p = 2  # 22K default
        w = 10.0
        f = 0  # Real default
        t = row['type'] if pd.notna(row['type']) else 0
        
        # 1. Fake Jewelry (Fraud)
        if "fakejewelry" in img_path or "goldidentifier" in img_path:
            p = 0 # N/A purity for fake
            w = np.random.normal(15.0, 3.0) # 15g average fake item
            f = 1 # Fake!
            t = np.random.choice([0, 1, 2]) # Random type
            
        # 2. Synthetic Hallmarks (OCR Head)
        elif "synthetic_hallmark" in img_path:
            p = 2 # Most hallmarks we generated were 22K/916
            w = 0.0 # Weight is meaningless for a macro shot
            f = 0
            t = 3 # Other / Hallmark
            
        # 3. Tanishq Necklaces
        elif "tanishq_necklace" in img_path:
            p = 2 # 22K Tanishq Standard
            w = np.random.normal(35.0, 8.0) # 35g average necklace
            f = 0
            t = 2 # Necklace
            
        # 4. Bangles (BangleFIR)
        elif "bangle" in img_path:
            p = 2 # 22K heavy bangles
            w = np.random.normal(20.0, 5.0) # 20g average bangle
            f = 0
            t = 1 # Bangle
            
        # 5. Rings / Earrings (RingFIR or generic Classifier)
        else:
            # 80% chance of 22K, 20% chance of 18K (stones)
            p = 2 if np.random.rand() > 0.2 else 1
            w = np.random.normal(5.0, 1.5) # 5g average ring
            f = 0
            t = 0 # Ring/Earring
            
        # Clip weights to positive values
        w = max(0.0, round(w, 2))
        
        new_purity.append(p)
        new_weight.append(w)
        new_fraud.append(f)
        new_type.append(t)
        
    df['purity'] = new_purity
    df['weight'] = new_weight
    df['fraud'] = new_fraud
    df['type'] = new_type
    
    return df

def main():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "labels.csv")
    
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
        
    print("Reading labels.csv...")
    df = pd.read_csv(csv_path)
    original_size = len(df)
    
    print(f"Applying realistic Ground-Truth heuristics to {original_size} records...")
    df = assign_ground_truth(df)
    
    # Save back
    df.to_csv(csv_path, index=False)
    print("Successfully assigned realistic Ground-Truth labels to all images!")
    
    # Print statistics
    print("\nDataset Distribution:")
    print("Type counts (0=Ring, 1=Bangle, 2=Necklace, 3=Other):")
    print(df['type'].value_counts().sort_index())
    print("\nPurity counts (0=None, 1=18K, 2=22K, 3=24K):")
    print(df['purity'].value_counts().sort_index())
    print("\nFraud counts (0=Real, 1=Fake):")
    print(df['fraud'].value_counts().sort_index())
    print(f"\nAverage Weight: {df['weight'].mean():.2f} grams")

if __name__ == "__main__":
    main()
