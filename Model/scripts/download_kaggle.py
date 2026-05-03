import os
import subprocess
import sys

def download_dataset(dataset_name, target_dir):
    print(f"Downloading {dataset_name} into {target_dir}...")
    os.makedirs(target_dir, exist_ok=True)
    try:
        # Run kaggle datasets download command
        subprocess.run([
            "kaggle", "datasets", "download", 
            "-d", dataset_name, 
            "-p", target_dir, 
            "--unzip"
        ], check=True)
        print(f"Successfully downloaded and unzipped {dataset_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download {dataset_name}: {e}")
    except FileNotFoundError:
        print("Kaggle CLI not found. Please install it using 'pip install kaggle'.")
        sys.exit(1)

def main():
    # Set the Kaggle API token from the user's provided screenshot
    os.environ["KAGGLE_API_TOKEN"] = "KGAT_79cacaf006933287cdf310c8c1857f09"
    
    # Wait, the Kaggle CLI typically uses KAGGLE_USERNAME and KAGGLE_KEY from kaggle.json.
    # If the Kaggle client supports KAGGLE_API_TOKEN, it will use it.
    # Otherwise, I might need to write the token to ~/.kaggle/kaggle.json or ~/.kaggle/access_token.
    # Let's try setting KAGGLE_API_TOKEN first.
    
    base_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data")
    
    datasets = {
        "sapnilpatel/tanishq-jewellery-dataset": "Tanishq",
        "khanjan88/jewellery-dataset": "Jewellery_Kaggle",
        "tsr564/goldpriceindianmarket": "GoldPrice_Indian",
        "novandraanugrah/xauusd-gold-price-historical-data-2004-2024": "XAU_USD_Historical",
        "jishnukoliyadan/gold-price-1979-present": "GoldPrice_Global"
    }
    
    for dataset, folder_name in datasets.items():
        target = os.path.join(base_dir, folder_name)
        download_dataset(dataset, target)

if __name__ == "__main__":
    main()
