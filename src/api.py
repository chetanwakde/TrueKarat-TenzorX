import os
import io
import json
import numpy as np
import cv2
import onnxruntime as ort
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

app = FastAPI(title="TrueKarat Remote Gold Assessment API")

# Load ONNX Model
model_path = os.path.join(os.path.dirname(__file__), '..', 'truekarat.onnx')

# We'll load the session lazily on first request or startup
ort_session = None

PURITY_CLASSES = ["14K", "18K", "22K", "24K"]
TYPE_CLASSES = [
    "Ring", "Bangle / Kada", "Chain / Necklace", "Earring / Jhumka", 
    "Pendant / Locket", "Bracelet", "Coin / Bar", "Mangalsutra", 
    "Anklet / Payal", "Nose ring / Nath"
]

def get_ort_session():
    global ort_session
    if ort_session is None:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file {model_path} not found. Please train first.")
        ort_session = ort.InferenceSession(model_path)
    return ort_session

def preprocess_image(image_bytes):
    # Decode image
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize to 300x300
    img = cv2.resize(img, (300, 300))
    
    # Normalize (ImageNet mean/std)
    img = img.astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img = (img - mean) / std
    
    # HWC to CHW
    img = np.transpose(img, (2, 0, 1))
    
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    
    return img

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def calculate_ltv(weight, purity_label):
    # Dummy LTV calculation logic
    # Assume base gold price for 24K is ₹6000 per gram
    rates = {
        "14K": 3500,
        "18K": 4500,
        "22K": 5500,
        "24K": 6000
    }
    rate_per_gram = rates.get(purity_label, 5000)
    
    # LTV is usually 75% of total value
    value = weight * rate_per_gram
    ltv = value * 0.75
    return int(value), int(ltv)

@app.post("/analyze")
async def analyze_gold(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        input_tensor = preprocess_image(image_bytes)
        
        session = get_ort_session()
        
        # Run inference
        ort_inputs = {session.get_inputs()[0].name: input_tensor}
        ort_outs = session.run(None, ort_inputs)
        
        # Parse outputs (order defined in export: purity, weight, fraud, type)
        purity_logits, weight_pred, fraud_logits, type_logits = ort_outs
        
        # Process Purity
        purity_idx = np.argmax(purity_logits, axis=1)[0]
        purity_label = PURITY_CLASSES[purity_idx]
        
        # Process Weight
        est_weight = float(weight_pred[0][0])
        # Provide a range based on a +/- 10% confidence interval
        weight_range = f"{max(0, est_weight * 0.9):.1f}g - {est_weight * 1.1:.1f}g"
        
        # Process Fraud (Genuineness)
        # Logits -> Sigmoid -> 1 = fake, 0 = genuine. So genuineness = 1 - fraud_prob
        fraud_prob = sigmoid(fraud_logits[0][0])
        genuineness_score = int((1.0 - fraud_prob) * 100)
        
        # Spoofing risk logic
        spoofing_risk = "LOW" if genuineness_score > 80 else ("MEDIUM" if genuineness_score > 50 else "HIGH")
        verdict = "PRE-APPROVED" if genuineness_score > 80 else "NEEDS VERIFICATION"
        
        # Process Type
        type_idx = np.argmax(type_logits, axis=1)[0]
        type_label = TYPE_CLASSES[type_idx]
        
        # Financials
        gold_value, loan_eligible = calculate_ltv(est_weight, purity_label)
        
        response = {
            "Type": type_label,
            "Purity_Band": purity_label,
            "Weight_Range": weight_range,
            "Gold_Value": f"₹{gold_value}",
            "Loan_Eligible": f"₹{loan_eligible}",
            "Genuineness": f"{genuineness_score} / 100",
            "Spoofing_Risk": spoofing_risk,
            "Confidence": "HIGH", # A real app would aggregate entropies
            "Verdict": verdict
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
