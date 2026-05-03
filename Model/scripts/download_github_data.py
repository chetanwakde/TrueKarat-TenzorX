import os
import subprocess

def clone_repo(repo_url, target_dir):
    if not os.path.exists(target_dir):
        print(f"Cloning {repo_url} into {target_dir}...")
        try:
            subprocess.run(["git", "clone", repo_url, target_dir], check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to clone {repo_url}. Skipping.")
    else:
        print(f"{target_dir} already exists. Skipping clone.")

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data")
    os.makedirs(base_dir, exist_ok=True)
    
    repos = {
        "RingFIR": "https://github.com/skarifahmed/RingFIR.git",
        "NecklaceFIR": "https://github.com/skarifahmed/NecklaceFIR.git",
        "BangleFIR": "https://github.com/iammaidul/BangleFIR.git"
    }
    
    for name, url in repos.items():
        target = os.path.join(base_dir, name)
        clone_repo(url, target)
        
    print("All GitHub datasets processed.")

if __name__ == "__main__":
    main()
