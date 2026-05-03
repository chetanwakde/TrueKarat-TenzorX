"""
Train YOLO11n coin detector using Roboflow's indian_coin_detector dataset.
Downloads dataset, trains model, copies best.pt to raw_data/coin_yolo.pt.

Usage:
    python scripts/train_coin_detector.py --api-key YOUR_ROBOFLOW_API_KEY
"""
import os
import sys
import shutil
import argparse
from pathlib import Path

# ── Workaround: polars crashes on Snapdragon/ARM with "unknown feature flag: sse3" ──
# We monkey-patch ultralytics to use csv module instead of polars for saving results.
import csv as _csv_mod

def _patch_ultralytics_trainer():
    """Patch the trainer to avoid importing polars (crashes on Snapdragon ARM)."""
    try:
        import ultralytics.engine.trainer as trainer_mod
        original_read = trainer_mod.BaseTrainer.read_results_csv

        def patched_read_results_csv(self):
            """Read results.csv using stdlib csv instead of polars."""
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
    parser = argparse.ArgumentParser(description="Train YOLO coin detector")
    parser.add_argument("--api-key", type=str, required=True, help="Roboflow API key")
    parser.add_argument("--epochs", type=int, default=30, help="Training epochs (default 30)")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size (default 640)")
    parser.add_argument("--batch", type=int, default=8, help="Batch size (default 8 for CPU)")
    parser.add_argument("--version", type=int, default=3, help="Roboflow dataset version (default 3)")
    args = parser.parse_args()

    BASE_DIR = Path(os.path.dirname(os.path.dirname(__file__)))
    RAW_DATA = BASE_DIR / "raw_data"
    WEIGHTS_TARGET = RAW_DATA / "coin_yolo.pt"

    # ── Step 1: Download dataset from Roboflow ──
    print("\n📦 Step 1: Downloading dataset from Roboflow...")
    from roboflow import Roboflow

    rf = Roboflow(api_key=args.api_key)
    project = rf.workspace("coindetection-tv5vv").project("indian_coin_detector")
    dataset = project.version(args.version).download("yolov8", location=str(RAW_DATA / "coin_dataset"))

    data_yaml = str(RAW_DATA / "coin_dataset" / "data.yaml")
    print(f"✅ Dataset downloaded to {RAW_DATA / 'coin_dataset'}")
    print(f"   data.yaml: {data_yaml}")

    # ── Step 2: Patch ultralytics to avoid polars crash ──
    _patch_ultralytics_trainer()

    # ── Step 3: Train YOLO11n ──
    print(f"\n🚀 Step 2: Training YOLO11n for {args.epochs} epochs on CPU...")
    from ultralytics import YOLO

    model = YOLO("yolo11n.pt")  # pretrained nano model

    results = model.train(
        data=data_yaml,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device="cpu",
        project=str(RAW_DATA),
        name="coin_yolo_train",
        exist_ok=True,
        patience=10,
        verbose=True,
    )

    # ── Step 4: Copy best weights ──
    best_pt = RAW_DATA / "coin_yolo_train" / "weights" / "best.pt"
    last_pt = RAW_DATA / "coin_yolo_train" / "weights" / "last.pt"
    
    src = best_pt if best_pt.exists() else last_pt
    if src.exists():
        shutil.copy(src, WEIGHTS_TARGET)
        print(f"\n✅ SUCCESS! Model saved to: {WEIGHTS_TARGET}")
        print(f"   Source: {src} ({src.stat().st_size / 1024:.0f} KB)")
    else:
        print(f"\n❌ ERROR: No weights found at {best_pt} or {last_pt}")
        sys.exit(1)

    # ── Step 5: Quick validation ──
    print("\n🔍 Step 3: Quick validation...")
    test_model = YOLO(str(WEIGHTS_TARGET))
    
    # Test on a reference coin image if available
    test_images = list((RAW_DATA).glob("Rs10-*.png"))
    if test_images:
        for img_path in test_images:
            res = test_model.predict(str(img_path), imgsz=args.imgsz, conf=0.25, verbose=False)
            detections = len(res[0].boxes) if res else 0
            print(f"   {img_path.name}: {detections} detection(s)")
            if res and len(res[0].boxes) > 0:
                for box in res[0].boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    cls_name = res[0].names[cls_id]
                    print(f"     → class='{cls_name}' conf={conf:.2%}")
    else:
        print("   No Rs10 reference images found for testing.")

    print(f"\n🎉 Done! Restart backend to use the new model.")
    print(f"   Weights: {WEIGHTS_TARGET}")


if __name__ == "__main__":
    main()
