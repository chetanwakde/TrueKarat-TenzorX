import os
import sys
try:
    from roboflow import Roboflow
except ImportError:
    print("Please run: pip install roboflow")
    sys.exit(1)

def main():
    api_key = "yHVhuV8hnf2y2DNTEWVx"
    rf = Roboflow(api_key=api_key)
    
    base_dir = os.path.join(os.path.dirname(__file__), "..", "raw_data")
    os.makedirs(base_dir, exist_ok=True)
    
    # Target projects: (workspace, project, version)
    # Note: we use version=1 by default, or you can fetch versions dynamically
    projects = [
        ("tectalik", "jewellery-classifier", 1),
        ("jewellery", "jewellerydataset_onlystorepics", 1),
        ("valuable-object-detection", "jewelry-dkgqg", 1),
        ("project-ggr8t", "gold-identifier-sstbu", 1)
    ]
    
    for workspace, project, version in projects:
        print(f"Downloading Roboflow dataset: {workspace}/{project}")
        try:
            proj = rf.workspace(workspace).project(project)
            # Default export format for YOLO is 'yolov8'
            dataset = proj.version(version).download("yolov8", location=os.path.join(base_dir, project))
            print(f"Successfully downloaded {project}")
        except Exception as e:
            print(f"Failed to download {workspace}/{project}: {e}")

if __name__ == "__main__":
    main()
