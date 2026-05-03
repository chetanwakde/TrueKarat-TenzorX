<div align="center">
  <img src="https://raw.githubusercontent.com/chetanwakde/TrueKarat-TenzorX/main/Frontend/frontend%202/assets/logo.png" alt="TrueKarat Logo" width="180" height="180" />

  # TrueKarat
  **AI-Powered Multi-Modal Gold Assessment System**

  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![React Native](https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactnative.dev/)
  [![OpenAI CLIP](https://img.shields.io/badge/OpenAI_CLIP-412991?style=for-the-badge&logo=openai&logoColor=white)](https://github.com/openai/CLIP)
  [![YOLOv8](https://img.shields.io/badge/YOLOv8-00FFFF?style=for-the-badge&logo=yolo&logoColor=black)](https://github.com/ultralytics/ultralytics)

  ### 📺 [Watch the Demo Video](https://youtu.be/fF892Zr7XHg?si=b-5Upgyv0BSGkgq0)

  *Democratizing gold valuation for instant lending through Computer Vision and Acoustic Frequency Analysis.*
</div>

---

## 🚀 Overview

**TrueKarat** is a high-precision, production-ready mobile assessment system designed to pre-qualify users for gold loans in seconds—without requiring a physical branch visit. By leveraging a multi-modal fusion of visual scanning and acoustic resonance testing, TrueKarat ensures robust verification of jewelry authenticity and volume.

---

## 💎 Core Innovations

### 1. Coin-Referenced Physical Scaling
TrueKarat eliminates perspective distortion and distance variables by using a standard **₹10 coin (fixed 27mm diameter)** as an absolute physical reference. To achieve this, we built a **custom-trained object detection model (`truekarat.onnx`)** fine-tuned specifically for this application. This ultra-fast ONNX model calculates real-time `px_per_mm` scaling to accurately estimate the volume and weight of the jewelry.

### 2. Multi-Modal Purity Fusion (Vision + Sound)
We combined visual classification with an acoustic "Tap-Test" to validate density and authenticity.
*   **Visual Authenticity (50 pts):** Analyzes surface texture, hallmarks, and structural integrity.
*   **Acoustic Resonance (50 pts):** Uses Fast Fourier Transform (FFT) to detect hollow or counterfeit items based on sound frequency signatures.

### 3. Financial Intelligence Engine
*   **Live Market Sync:** Real-time integration with `GoldAPI.io` for up-to-the-minute 14K, 18K, 22K, and 24K spot prices.
*   **Range-Based Valuation:** Instead of generating misleading "exact" values, TrueKarat calculates realistic "Purity Bands" (e.g., 18K-22K) and "Weight Ranges" (±15%).
*   **Instant RBI-Compliant LTV:** Automatically calculates a 75% Loan-to-Value (LTV) range for instant pre-approval.

---

## 🛠️ Technical Architecture

### 📱 Frontend (Mobile Application)
*   **Framework:** React Native / Expo
*   **Design Language:** Custom "Cosmic Consciousness" theme featuring premium glassmorphism, linear gradients, and a sleek dark-mode aesthetic.
*   **Hardware Integration:** Utilizes `expo-camera` for guided multi-step visual capture and `expo-av` for high-frequency audio recording.

### 🧠 Backend (AI Engine)
*   **API Framework:** FastAPI running on Uvicorn
*   **Audio Processing:** `PyAV` (Advanced FFmpeg wrapper) for high-fidelity M4A/AAC decoding and frequency extraction.
*   **Computer Vision Stack:**
    *   **OpenAI CLIP:** Zero-shot image classification to identify jewelry sub-categories (Ring, Bangle, Necklace, etc.).
    *   **Custom YOLOv8 (`truekarat.onnx`):** Our proprietary, custom-trained ONNX model optimized for high-speed, accurate detection of the ₹10 reference coin.
    *   **OpenCV:** Adaptive Gaussian Thresholding and morphological contour detection for precise boundary extraction.

---

## 📈 Assessment Workflow

1.  **Guided Multi-Angle Scan:** The user is guided through a 4-step physical capture process (Front View, Side Angle, Macro Detail, and Coin Reference).
2.  **Acoustic Tap Test:** The user taps the jewelry, and the app records the resulting resonance frequencies.
3.  **AI Processing:**
    *   `CLIP` identifies the jewelry type.
    *   `YOLO` isolates the coin to calculate spatial scaling.
    *   `OpenCV` estimates the physical volume.
    *   `FFT` validates the acoustic density.
4.  **Instant Financial Report:** Generates a comprehensive report detailing the Estimated Gold Value Range, Maximum Loan Eligibility, and a combined Trust Score.

---

## ⚙️ Local Setup & Deployment

### 1. Backend Initialization (Laptop/Server)
**Important:** Your laptop and mobile device **must be on the same WiFi network or Hotspot** for the app to connect to the backend.

```bash
cd Model
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start the server on all network interfaces
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```
*Note: Make sure your firewall allows incoming connections on port 8000.*

### 2. Frontend Application (APK)
You do not need to build the app from source. We have provided a production-ready APK!

📥 **[Download TrueKarat APK (Build 3)](https://expo.dev/accounts/chetanwakde/projects/truekarat/builds/70b9eeb9-f3bb-4cbc-a420-a5d0e4070a86)**

### 3. Ensuring 100% Connectivity
To ensure the APK successfully communicates with the backend:
1. Connect your Android phone to the **same WiFi network** as your laptop, OR turn on your laptop's Mobile Hotspot and connect your phone to it.
2. Run the backend command exactly as shown above (`--host 0.0.0.0`).
3. Open the TrueKarat app. The app features an **AUTO-DISCOVER network scanner** that will automatically ping common local subnet IPs (e.g., `192.168.x.x:8000`, `172.x.x.x:8000`) to find your backend seamlessly without any manual configuration!

---

<div align="center">
  <i>Built for the TenzorX Hackathon</i>
</div>
