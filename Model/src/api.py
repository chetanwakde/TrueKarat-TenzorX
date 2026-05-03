"""
TrueKarat v3 — Multi-Modal Gold Assessment API

3 Sensors:
  1. CAMERA  → CLIP classifies jewelry type + rejects non-gold objects
             → OpenCV detects ₹10 coin (27mm ref) to estimate dimensions → weight
  2. MIC     → FFT audio analysis on tap sound to estimate karat/purity
  3. COMBINED → merges all signals into confidence score + valuation
"""

import os, base64, io, json, time
import urllib.request
import numpy as np
import cv2
from PIL import Image
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="TrueKarat Gold Assessment API v3")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ─── Constants ────────────────────────────────────────────────────────────────
GOLD_API_KEY = "goldapi-7f65ccc46432f0eb94ae2067147f4694-io"
GOLD_API_URL = "https://www.goldapi.io/api/XAU/INR"

COIN_DIAMETER_MM = 27.0  # ₹10 coin

JEWELRY_LABELS = [
    "a gold ring", "a gold bangle or kada",
    "a gold chain or necklace", "a gold earring or jhumka",
    "a gold pendant or locket", "a gold bracelet",
    "a gold coin or gold bar", "a gold mangalsutra",
    "a gold anklet or payal", "a gold nose ring or nath",
]
REJECTION_LABELS = [
    "a laptop or computer screen", "a piece of paper or document",
    "a mobile phone", "a pen or pencil", "a metal pin or screw",
    "a plastic object", "a wooden object", "a fabric or cloth",
    "a human hand with no jewelry", "an empty table or surface",
]
ALL_LABELS = JEWELRY_LABELS + REJECTION_LABELS

TYPE_NAMES = [
    "Ring", "Bangle / Kada", "Chain / Necklace", "Earring / Jhumka",
    "Pendant / Locket", "Bracelet", "Coin / Bar", "Mangalsutra",
    "Anklet / Payal", "Nose Ring / Nath",
]

# Weight estimation ranges per type (min, max, typical_mean)
WEIGHT_RANGES = {
    0: (1.5, 12.0, 5.0),    # Ring
    1: (10.0, 50.0, 25.0),  # Bangle
    2: (10.0, 80.0, 35.0),  # Necklace
    3: (1.0, 10.0, 4.0),    # Earring
    4: (1.5, 8.0, 3.5),     # Pendant
    5: (5.0, 35.0, 15.0),   # Bracelet
    6: (5.0, 50.0, 10.0),   # Coin/Bar
    7: (10.0, 50.0, 22.0),  # Mangalsutra
    8: (8.0, 40.0, 18.0),   # Anklet
    9: (0.5, 4.0, 1.5),     # Nose ring
}

# Gold density by karat (g/cm³)
GOLD_DENSITY = {"24K": 19.3, "22K": 17.7, "18K": 15.6, "14K": 13.1}

# Purity multiplier for pricing
PURITY_MULT = {"14K": 14/24, "18K": 18/24, "22K": 22/24, "24K": 1.0}

# ─── CLIP Model (lazy load) ──────────────────────────────────────────────────
_clip_pipeline = None

def get_clip():
    global _clip_pipeline
    if _clip_pipeline is None:
        print("Loading CLIP model (first time, ~1 min)...")
        from transformers import pipeline
        _clip_pipeline = pipeline(
            "zero-shot-image-classification",
            model="openai/clip-vit-base-patch32",
            device=-1,  # CPU
        )
        print("CLIP loaded!")
    return _clip_pipeline

# ─── Gold Price (cached) ─────────────────────────────────────────────────────
_price_cache = {"price": None, "ts": 0}

def get_live_gold_prices():
    if _price_cache["price"] and (time.time() - _price_cache["ts"]) < 300:
        return _price_cache["price"]
    try:
        req = urllib.request.Request(
            GOLD_API_URL,
            headers={"x-access-token": GOLD_API_KEY, "Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=4)
        data = json.loads(resp.read().decode())
        
        prices = {
            "24K": round(data.get("price_gram_24k", data["price"] / 31.1035), 2),
            "22K": round(data.get("price_gram_22k", data["price"] / 31.1035 * (22/24)), 2),
            "18K": round(data.get("price_gram_18k", data["price"] / 31.1035 * (18/24)), 2),
            "14K": round(data.get("price_gram_14k", data["price"] / 31.1035 * (14/24)), 2)
        }
        
        _price_cache["price"] = prices
        _price_cache["ts"] = time.time()
        return prices
    except Exception:
        return {"24K": 7800.0, "22K": 7150.0, "18K": 5850.0, "14K": 4550.0}

# ─── Visual Analysis (CLIP + OpenCV + Color) ─────────────────────────────────

def analyze_gold_color(image_bytes: bytes) -> dict:
    """HSV color analysis to verify presence of gold-colored metal."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w = img.shape[:2]
    total_px = h * w

    # Gold color ranges (covers yellow-gold to rose-gold)
    lower1 = np.array([10, 60, 80])
    upper1 = np.array([35, 255, 255])
    mask1 = cv2.inRange(hsv, lower1, upper1)

    # Bright metallic (white gold / reflections)
    lower2 = np.array([0, 0, 180])
    upper2 = np.array([180, 40, 255])
    mask2 = cv2.inRange(hsv, lower2, upper2)

    gold_px = cv2.countNonZero(mask1)
    metallic_px = cv2.countNonZero(mask2)
    gold_ratio = gold_px / total_px
    metallic_ratio = metallic_px / total_px

    # Score: strong gold color = boost, no gold = penalty
    if gold_ratio > 0.15:
        color_score = 25  # strong gold color boost
    elif gold_ratio > 0.05:
        color_score = 10
    elif gold_ratio > 0.01:
        color_score = 0
    else:
        color_score = -30  # no gold color = heavy penalty

    return {
        "gold_ratio": round(gold_ratio * 100, 2),
        "metallic_ratio": round(metallic_ratio * 100, 2),
        "color_score": color_score,
    }


def classify_image(image_bytes: bytes) -> dict:
    """Use CLIP + color analysis to classify and verify gold jewelry."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    clip = get_clip()
    results = clip(img, candidate_labels=ALL_LABELS)

    scores = {r["label"]: r["score"] for r in results}
    jewelry_score = sum(scores.get(l, 0) for l in JEWELRY_LABELS)
    rejection_score = sum(scores.get(l, 0) for l in REJECTION_LABELS)

    jewelry_results = [(l, scores.get(l, 0)) for l in JEWELRY_LABELS]
    jewelry_results.sort(key=lambda x: x[1], reverse=True)
    top_label, top_score = jewelry_results[0]
    type_idx = JEWELRY_LABELS.index(top_label)

    # Color verification — ONLY used for gating, NOT for score boosting
    color = analyze_gold_color(image_bytes)
    
    # Confidence is PURE CLIP score — no color inflation
    clip_conf = top_score * 100

    is_jewelry = (jewelry_score > rejection_score
                  and top_score > 0.08
                  and color["gold_ratio"] > 0.5)

    return {
        "is_jewelry": is_jewelry,
        "type_idx": type_idx,
        "type_name": TYPE_NAMES[type_idx],
        "confidence": round(clip_conf, 1),
        "clip_raw": round(clip_conf, 1),
        "gold_color_pct": color["gold_ratio"],
        "jewelry_score": round(jewelry_score * 100, 1),
        "rejection_score": round(rejection_score * 100, 1),
    }


# ─── YOLO Coin Detection Model ───────────────────────────────────────
try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

_yolo_model = None
_YOLO_WEIGHTS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "raw_data", "coin_yolo.pt")
if not os.path.exists(_YOLO_WEIGHTS):
    _YOLO_WEIGHTS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "raw_data", "coin_yolo.onnx")

def get_yolo_model():
    global _yolo_model
    if _yolo_model is not None:
        return _yolo_model
    
    if YOLO is None:
        print("WARNING: ultralytics is not installed. YOLO inference will fail.")
        return None
        
    if os.path.exists(_YOLO_WEIGHTS):
        try:
            print(f"Loading YOLO coin detector from {_YOLO_WEIGHTS}...")
            _yolo_model = YOLO(_YOLO_WEIGHTS, task='detect')
            return _yolo_model
        except Exception as e:
            print(f"Failed to load YOLO model: {e}")
            return None
    else:
        print(f"WARNING: YOLO coin detector not found at {_YOLO_WEIGHTS}. Run training script first.")
        return None

def estimate_weight_from_coin(image_bytes: bytes, type_idx: int) -> dict:
    """Detect ₹10 coin using trained YOLO object detection."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    lo, hi, mean = WEIGHT_RANGES[type_idx]
    
    if img is None:
        return {"method": "heuristic", "coin_detected": False, "estimated_weight": mean}

    yolo = get_yolo_model()
    if yolo is None:
        print("YOLO model not loaded. Failing coin detection.")
        return {"method": "yolo", "coin_detected": False, "estimated_weight": mean}
        
    # ── STEP 1: YOLO Inference ──
    # Run at multiple sizes for robustness with phone cameras
    best_conf = 0.0
    best_box = None
    
    for sz in [640, 320]:
        results = yolo.predict(img, imgsz=sz, conf=0.25, verbose=False)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                cls_name = r.names[cls_id]
                conf = float(box.conf[0])
                print(f"YOLO detected: {cls_name} conf={conf:.2f} at imgsz={sz}")
                # Accept '10' preferentially, but any coin class works as size ref
                is_ten = cls_name in ('10', 'Rs10_Coin')
                is_coin = cls_name in ('1', '2', '5', '10', 'emblem', 'Rs10_Coin')
                # Prefer ₹10 coins, but accept any coin if no ₹10 found
                if is_ten and conf > best_conf:
                    best_conf = conf
                    best_box = box.xyxy[0].cpu().numpy()
                elif is_coin and best_conf < 0.1 and conf > best_conf:
                    best_conf = conf
                    best_box = box.xyxy[0].cpu().numpy()
        if best_conf > 0.5:
            break  # Good enough, no need to try other sizes
                
    if best_box is None or best_conf < 0.25:
        print(f"No coin detected by YOLO. Best conf: {best_conf:.2f}")
        return {"method": "yolo", "coin_detected": False, "estimated_weight": mean}
        
    x1, y1, x2, y2 = best_box
    coin_cx = int((x1 + x2) / 2)
    coin_cy = int((y1 + y2) / 2)
    # Average width and height to get diameter, then divide by 2 for radius
    coin_radius_px = int(((x2 - x1) + (y2 - y1)) / 4)
    best_val = best_conf
    
    px_per_mm = (2 * coin_radius_px) / COIN_DIAMETER_MM
    
    # ── STEP 3: Estimate gold jewelry area robustly ──
    # Convert to grayscale and blur to remove noise
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    
    # Adaptive thresholding handles shadows and lighting variations much better than HSV
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 21, 5)
                                   
    # Clean up noise with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Mask out the coin entirely so it's not counted as jewelry
    # We use the bounding box with a 15% margin
    margin = int(coin_radius_px * 0.3)
    cv2.rectangle(thresh, (int(x1) - margin, int(y1) - margin), 
                  (int(x2) + margin, int(y2) + margin), 0, -1)
                  
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    gold_pixels = 0
    if contours:
        # Filter out tiny noise (must be > 2mm^2)
        min_px = (px_per_mm * 2) ** 2
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_px]
        
        if valid_contours:
            # Sort by area descending
            valid_contours = sorted(valid_contours, key=cv2.contourArea, reverse=True)
            
            # If it's a necklace/chain (type 2, 7), sum the top 5 largest parts
            # Otherwise (ring, bangle), just take the single largest contour
            if type_idx in [2, 7]:
                for c in valid_contours[:5]:
                    gold_pixels += cv2.contourArea(c)
            else:
                gold_pixels = cv2.contourArea(valid_contours[0])
                
    if gold_pixels == 0:
        # Fallback to older heuristic if contour logic fails
        gold_pixels = ((px_per_mm * 15) ** 2)  # dummy 15x15mm area
        
    gold_area_mm2 = gold_pixels / (px_per_mm ** 2)
    
    # Estimated average thickness in mm for different jewelry types
    thickness_mm = {
        0: 2.2,  # Ring
        1: 3.5,  # Bangle
        2: 1.8,  # Necklace
        3: 1.5,  # Earring
        4: 2.0,  # Pendant
        5: 2.5,  # Bracelet
        6: 3.0,  # Coin/Bar
        7: 1.5,  # Mangalsutra
        8: 2.0,  # Anklet
        9: 1.0   # Nose ring
    }
    t = thickness_mm.get(type_idx, 2.0)
    
    # V = A * t
    volume_mm3 = gold_area_mm2 * t
    volume_cm3 = volume_mm3 / 1000.0
    
    # Calculate exact weight based on volume and 22K density
    est_weight = volume_cm3 * GOLD_DENSITY["22K"]
    
    # Sanity bounds (don't clamp so strictly to averages, let the math speak, but prevent absurd values)
    est_weight = max(0.5, min(200.0, round(est_weight, 1)))
    
    # ── STEP 4: Draw annotation ──
    overlay = img.copy()
    cv2.circle(overlay, (coin_cx, coin_cy), coin_radius_px, (0, 255, 0), -1)
    cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)
    cv2.circle(img, (coin_cx, coin_cy), coin_radius_px, (255, 255, 255), 3)
    font_scale = max(0.5, coin_radius_px / 80)
    label = f"Rs10 ({best_val:.0%})"
    cv2.putText(img, label, (coin_cx - int(45 * font_scale), coin_cy + int(8 * font_scale)),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)
    
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
    annotated_b64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "method": "template_match",
        "coin_detected": True,
        "match_confidence": round(best_val, 3),
        "coin_x": coin_cx,
        "coin_y": coin_cy,
        "coin_radius_px": coin_radius_px,
        "px_per_mm": round(px_per_mm, 2),
        "gold_area_mm2": round(gold_area_mm2, 1),
        "estimated_weight": est_weight,
        "annotated_image": annotated_b64,
    }

# ─── Audio Analysis (FFT Tap Test) ───────────────────────────────────────────

def analyze_tap_audio(audio_bytes: bytes, sample_rate: int = 44100) -> dict:
    """
    Analyze a tap-test audio recording to estimate gold purity.

    Gold produces a clear, sustained ring when tapped:
    - 24K pure gold: ~5800-6200Hz, long sustain (>0.5s)
    - 22K gold:      ~5000-5800Hz, moderate sustain
    - 18K gold:      ~4200-5000Hz, shorter sustain
    - 14K gold:      ~3500-4200Hz, short sustain
    - Fake/plated:   <3000Hz or no clear peak, dull thud
    """
    # Decode audio using PyAV (supports M4A/AAC from React Native)
    try:
        import av
        container = av.open(io.BytesIO(audio_bytes))
        stream = container.streams.audio[0]
        samples_list = []
        sample_rate = stream.rate
        for frame in container.decode(stream):
            # Convert to mono float32
            arr = frame.to_ndarray()
            if arr.ndim > 1 and arr.shape[0] > 1:
                arr = np.mean(arr, axis=0) # Mix down to mono
            samples_list.append(arr.flatten())
        
        if not samples_list:
            return {"purity": "UNKNOWN", "confidence": 0, "error": "Empty audio stream"}
            
        samples = np.concatenate(samples_list).astype(np.float32)
        
    except ImportError:
        return {"purity": "UNKNOWN", "confidence": 0, "error": "PyAV not installed. Run pip install av"}
    except Exception as e:
        return {"purity": "UNKNOWN", "confidence": 0, "error": f"Audio decode error: {str(e)}"}

    if len(samples) < 1000:
        return {"purity": "UNKNOWN", "confidence": 0, "error": "Audio too short"}

    # Normalize
    samples = samples / (np.max(np.abs(samples)) + 1e-8)

    # Find the tap onset (loudest point)
    onset = np.argmax(np.abs(samples))
    # Analyze the ring after the tap (next 0.5 seconds)
    ring_start = onset + int(0.01 * sample_rate)  # skip 10ms of impact
    ring_end = min(ring_start + int(0.5 * sample_rate), len(samples))
    ring = samples[ring_start:ring_end]

    if len(ring) < 500:
        return {"purity": "UNKNOWN", "confidence": 0, "error": "No ring detected after tap"}

    # FFT
    N = len(ring)
    yf = np.abs(fft(ring))[:N // 2]
    xf = fftfreq(N, 1.0 / sample_rate)[:N // 2]

    # Find dominant peaks above 2000Hz (gold resonance range)
    mask = xf > 2000
    yf_filtered = yf * mask

    peaks, properties = find_peaks(yf_filtered, height=np.max(yf_filtered) * 0.3,
                                    distance=int(200 * N / sample_rate))

    if len(peaks) == 0:
        return {
            "purity": "FAKE / NON-GOLD",
            "karat": "N/A",
            "confidence": 85,
            "dominant_freq": 0,
            "sustain_energy": 0,
            "detail": "No high-frequency resonance detected — likely not gold"
        }

    # Dominant frequency
    dom_idx = peaks[np.argmax(yf_filtered[peaks])]
    dom_freq = xf[dom_idx]

    # Sustain energy (how long the ring lasts)
    energy = np.sum(ring ** 2) / len(ring)

    # Classify purity based on frequency
    if dom_freq >= 5800:
        purity, karat, conf = "99.9%", "24K", min(95, int(60 + energy * 5000))
    elif dom_freq >= 5000:
        purity, karat, conf = "91.6%", "22K", min(92, int(55 + energy * 4000))
    elif dom_freq >= 4200:
        purity, karat, conf = "75.0%", "18K", min(85, int(50 + energy * 3000))
    elif dom_freq >= 3500:
        purity, karat, conf = "58.3%", "14K", min(78, int(45 + energy * 2000))
    else:
        purity, karat, conf = "LOW / PLATED", "N/A", min(70, int(40 + energy * 1000))

    return {
        "purity": purity,
        "karat": karat,
        "confidence": conf,
        "dominant_freq": round(dom_freq, 1),
        "sustain_energy": round(energy * 10000, 2),
        "detail": f"Resonant freq {dom_freq:.0f}Hz → {karat} ({purity})"
    }

# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.post("/analyze_base64")
async def analyze_visual(payload: dict = Body(...)):
    """Camera analysis: CLIP classification + coin-reference weight estimation.
    Accepts optional 'step' (1-4) for multi-angle guided capture.
    """
    try:
        b64 = payload.get("image", "")
        step = payload.get("step", 1)  # 1=front, 2=side, 3=closeup, 4=coin
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        image_bytes = base64.b64decode(b64)
        
        t0 = time.time()

        # ── Step 4: COIN DETECTION ONLY ──
        # NO CLIP here. Step 4 is purely for coin-as-reference dimension estimation.
        # Jewelry type was already confirmed in steps 1-3.
        if step == 4:
            t1 = time.time()
            
            # Use type_idx=0 (Ring) as default — the frontend should pass the
            # type detected in earlier steps, but this is a safe fallback.
            type_idx = payload.get("type_idx", 0)
            
            weight_result = estimate_weight_from_coin(image_bytes, type_idx)
            print(f"Step 4: YOLO coin detection took {time.time()-t1:.1f}s")
            
            if not weight_result.get("coin_detected", False):
                return JSONResponse({
                    "passed": False,
                    "retry_reason": "No coin detected. Place a Rs.10 coin next to the jewelry and retake.",
                    "coin_detected": False,
                })

            est_weight = weight_result["estimated_weight"]
            live_prices = get_live_gold_prices()
            rate_22k = live_prices.get("22K", 7150.0)
            
            # Weight as estimated range (+/- 15%)
            weight_min = est_weight * 0.85
            weight_max = est_weight * 1.15
            
            gold_value_min = int(weight_min * rate_22k)
            gold_value_max = int(weight_max * rate_22k)
            
            loan_eligible_min = int(gold_value_min * 0.75)
            loan_eligible_max = int(gold_value_max * 0.75)

            return JSONResponse({
                "passed": True,
                "coin_detected": True,
                "weight": f"{weight_min:.1f}g - {weight_max:.1f}g",
                "estimated_weight": est_weight,
                "min_value": f"₹{loan_eligible_min:,} - ₹{loan_eligible_max:,}",
                "max_value": f"₹{gold_value_min:,} - ₹{gold_value_max:,}",
                "rate_per_gram": live_prices,
                "weight_method": weight_result["method"],
                "match_confidence": round(weight_result.get("match_confidence", 0), 3),
                "gold_area_mm2": weight_result.get("gold_area_mm2", 0),
                "annotated_image": weight_result.get("annotated_image", None),
            })

        # ── Steps 1-3: CLIP classification ──
        clip_result = classify_image(image_bytes)
        print(f"Step {step}: CLIP took {time.time()-t0:.1f}s")

        if not clip_result["is_jewelry"]:
            return JSONResponse({
                "trustScore": 0,
                "passed": False,
                "retry_reason": "No gold jewelry detected. Point camera at the jewelry.",
                "type": "NOT JEWELRY",
                "coin_detected": False,
                "detail": f"CLIP classified as non-jewelry (rejection score: {clip_result['rejection_score']}%)",
            })

        confidence = clip_result["confidence"]
        
        if confidence < 30:
            return JSONResponse({
                "trustScore": int(confidence),
                "passed": False,
                "retry_reason": "Image too blurry or jewelry too small. Move closer.",
                "type": clip_result["type_name"],
                "coin_detected": False,
            })
        
        return JSONResponse({
            "trustScore": int(confidence),
            "passed": True,
            "type": clip_result["type_name"],
            "coin_detected": False,
            "detail": f"CLIP: {clip_result['type_name']} ({confidence}% conf)",
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/analyze_audio")
async def analyze_audio(payload: dict = Body(...)):
    """Microphone tap-test analysis for purity estimation."""
    try:
        b64 = payload.get("audio", "")
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        audio_bytes = base64.b64decode(b64)

        result = analyze_tap_audio(audio_bytes)

        return JSONResponse({
            "karat": result["karat"],
            "purity": result["purity"],
            "confidence": result["confidence"],
            "dominant_freq": result.get("dominant_freq", 0),
            "detail": result.get("detail", ""),
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/full_assessment")
async def full_assessment(payload: dict = Body(...)):
    """
    Combined multi-modal assessment.
    Expects: { "image": "<base64>", "audio": "<base64>", "type": "<string>" }
    """
    try:
        # Visual
        b64_img = payload.get("image", "")
        frontend_type = payload.get("type", "")
        if "," in b64_img:
            b64_img = b64_img.split(",", 1)[1]
        image_bytes = base64.b64decode(b64_img)

        clip_result = classify_image(image_bytes)
        
        # 1) Override CLIP's step-4 type detection if frontend passed the type from steps 1-3
        if frontend_type and frontend_type != "NOT JEWELRY":
            clip_result["type_name"] = frontend_type
            clip_result["is_jewelry"] = True
            try:
                clip_result["type_idx"] = TYPE_NAMES.index(frontend_type)
            except ValueError:
                pass

        if not clip_result["is_jewelry"]:
            return JSONResponse({
                "trustScore": 0,
                "purity": "N/A", "karat": "N/A",
                "weight": "0.0g",
                "type": "NOT JEWELRY",
                "min_value": 0, "max_value": 0,
                "rate_per_gram": get_live_gold_prices(),
                "spoofing_risk": "HIGH — NOT GOLD JEWELRY",
                "verdict": "REJECTED",
            })

        weight_result = estimate_weight_from_coin(image_bytes, clip_result["type_idx"])
        est_weight = weight_result["estimated_weight"]
        
        # 4) Weight as estimated range (+/- 15%)
        weight_min = est_weight * 0.85
        weight_max = est_weight * 1.15
        weight_range_str = f"{weight_min:.1f}g - {weight_max:.1f}g"

        # Audio (if provided)
        audio_result = None
        karat = "22K"  # default
        b64_audio = payload.get("audio", "")
        if b64_audio:
            if "," in b64_audio:
                b64_audio = b64_audio.split(",", 1)[1]
            audio_bytes = base64.b64decode(b64_audio)
            audio_result = analyze_tap_audio(audio_bytes)
            
        # 50/50 Additive Scoring Model
        visual_score = min(50, int(clip_result["confidence"] / 2))
        audio_score = 0
        
        if audio_result:
            karat = audio_result.get("karat", "N/A")
            # Binary score: 50 if any gold karat is detected, 0 if fake
            if karat != "N/A":
                audio_score = 50
            else:
                audio_score = 0
                
        # 2) Purity band (range) instead of exact karat
        purity_bands = {
            "24K": "22K - 24K",
            "22K": "18K - 22K",
            "18K": "14K - 18K",
            "14K": "10K - 14K",
            "N/A": "N/A"
        }
        karat_range = purity_bands.get(karat, "18K - 22K")
            
        combined_trust = visual_score + audio_score

        # 3) Live Prices from API for 18K, 22K, 24K
        live_prices = get_live_gold_prices()
        rate_22k = live_prices.get("22K", 7150.0)
        
        # Calculate value ranges based on weight ranges and the specific detected karat rate
        rate_used = live_prices.get(karat, rate_22k) if karat != "N/A" else rate_22k
        
        gold_value_min = int(weight_min * rate_used)
        gold_value_max = int(weight_max * rate_used)
        
        # 5) Loan eligible as range (75% of low side to 75% of high side)
        loan_eligible_min = int(gold_value_min * 0.75)
        loan_eligible_max = int(gold_value_max * 0.75)

        if combined_trust > 75:
            verdict, risk = "PRE-APPROVED", "LOW"
        elif combined_trust > 45:
            verdict, risk = "NEEDS VERIFICATION", "MEDIUM"
        else:
            verdict, risk = "LOW CONFIDENCE", "HIGH"

        return JSONResponse({
            "trustScore": combined_trust,
            "purity": karat_range,
            "weight": weight_range_str,
            "type": clip_result["type_name"],
            "min_value": f"₹{loan_eligible_min:,} - ₹{loan_eligible_max:,}",
            "max_value": f"₹{gold_value_min:,} - ₹{gold_value_max:,}",
            "rate_per_gram": live_prices,
            "spoofing_risk": risk,
            "verdict": verdict,
            "coin_detected": weight_result.get("coin_detected", False),
            "weight_method": weight_result["method"],
            "audio_analyzed": audio_result is not None,
            "audio_detail": audio_result.get("detail", "No audio provided") if audio_result else "No audio — using default band",
            "annotated_image": weight_result.get("annotated_image", None),
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/health")
def health():
    prices = get_live_gold_prices()
    return {"status": "ok", "version": "v3-multimodal", "gold_price_22k": prices.get("22K", 7150.0)}


# ─── Ngrok public URL endpoint ────────────────────────────────────────────────
_ngrok_url = None

@app.get("/ngrok_url")
def get_ngrok_url():
    return {"url": _ngrok_url}


if __name__ == "__main__":
    # Pre-load CLIP on startup
    get_clip()
    
    # Start ngrok tunnel for stable public URL
    try:
        from pyngrok import ngrok
        tunnel = ngrok.connect(8000, "http")
        _ngrok_url = tunnel.public_url
        print(f"\n{'='*60}")
        print(f"  NGROK PUBLIC URL: {_ngrok_url}")
        print(f"  Use this URL in the app instead of local IP!")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"Ngrok failed ({e}), using local IP only.")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
