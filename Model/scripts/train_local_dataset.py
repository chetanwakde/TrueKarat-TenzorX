"""
Train YOLO11n coin detector locally using the provided indian_coin_detector dataset.
Trains model, exports to ONNX, and copies best weights to raw_data.
"""
import os
import sys
import shutil
from pathlib import Path
import yaml

# ── Workaround: polars crashes on Snapdragon/ARM with "unknown feature flag: sse3" ──
def _patch_ultralytics_trainer():
    """Patch the trainer to avoid importing polars (crashes on Snapdragon ARM)."""
    try:
        import ultralytics.engine.trainer as trainer_mod
        original_read = trainer_mod.BaseTrainer.read_results_csv

        def patched_read_results_csv(self):
            import csv
            results_csv = self.csv
            if not Path(results_csv).exists():
                return {}
            try:
                with open(results_csv, "r") as f:
                    reader = csv.DictReader(f, skipinitialspace=True)
                    rows = list(reader)
                    if not rows:
                        return {}
                    last_row = rows[-1]
                    return {k.strip(): float(v.strip()) for k, v in last_row.items() if v.strip()}
            except Exception:
                return {}

        trainer_mod.BaseTrainer.read_results_csv = patched_read_results_csv
        print("✅ Patched ultralytics trainer to bypass polars (Snapdragon fix)")
    except Exception as e:
        print(f"⚠️ Could not patch trainer: {e}")

def main():
    BASE_DIR = Path(os.path.dirname(os.path.dirname(__file__)))
    RAW_DATA = BASE_DIR / "raw_data"
    DATASET_DIR = RAW_DATA / "indian_coin_detector.v1i.yolov8"
    DATA_YAML = DATASET_DIR / "data.yaml"
    
    if not DATASET_DIR.exists() or not DATA_YAML.exists():
        print(f"❌ ERROR: Dataset not found at {DATASET_DIR}")
        sys.exit(1)

    # ── Step 1: Fix data.yaml paths to be absolute ──
    print("\n[Step 1] Fixing data.yaml paths...")
    with open(DATA_YAML, "r") as f:
        data = yaml.safe_load(f)
        
    data["path"] = str(DATASET_DIR.absolute())
    # YOLO requires paths relative to 'path' key
    data["train"] = "train/images"
    data["val"] = "valid/images"
    if "test" in data:
        data["test"] = "test/images"
        
    with open(DATA_YAML, "w") as f:
        yaml.dump(data, f)
    print("DONE: data.yaml paths updated.")

    # ── Step 2: Patch ultralytics ──
    _patch_ultralytics_trainer()

    # ── Step 3: Train YOLO11n ──
    print("\n[Step 2] Training YOLO11n for 3 epochs on CPU (Fast Mode)...")
    print("   (Using imgsz=320 to complete quickly on CPU)")
    from ultralytics import YOLO

    model = YOLO("yolo11n.pt")

    results = model.train(
        data=str(DATA_YAML),
        epochs=3,
        imgsz=320,
        batch=16,
        device="cpu",
        project=str(RAW_DATA),
        name="coin_yolo_final",
        exist_ok=True,
        verbose=True,
    )

    # ── Step 4: Export to ONNX ──
    print("\n[Step 3] Exporting model to ONNX format...")
    best_pt = RAW_DATA / "coin_yolo_final" / "weights" / "best.pt"
    
    if not best_pt.exists():
        print(f"\nERROR: No weights found at {best_pt}")
        sys.exit(1)
        
    exported_model = YOLO(str(best_pt))
    export_path = exported_model.export(format="onnx", imgsz=640)
    print(f"DONE: Exported ONNX model to {export_path}")

    # ── Step 5: Copy files ──
    WEIGHTS_PT = RAW_DATA / "coin_yolo.pt"
    WEIGHTS_ONNX = RAW_DATA / "coin_yolo.onnx"
    
    shutil.copy(best_pt, WEIGHTS_PT)
    
    # export_path is the string path to the generated ONNX file
    if export_path and Path(export_path).exists():
        shutil.copy(export_path, WEIGHTS_ONNX)
        print(f"\nSUCCESS! Models saved to:\n   - {WEIGHTS_PT}\n   - {WEIGHTS_ONNX}")
    else:
        print(f"\nWARNING: ONNX export may have failed. Only .pt is available at {WEIGHTS_PT}")

if __name__ == "__main__":
    main()
