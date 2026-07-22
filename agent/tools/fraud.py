import joblib
import numpy as np
import os

MODEL_PATH = "fraud_model_real.pkl"
SCALER_PATH = "scaler_real.pkl"

_model = None
_scaler = None

def _load_model():
    global _model, _scaler
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            return "Model not found. Train it first in Jupyter."
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
    return "Loaded"

def tool_predict_fraud(input_str):
    status = _load_model()
    if "not found" in status:
        return status
    try:
        parts = [float(x.strip()) for x in input_str.split(',')]
        if len(parts) != 30:
            return f"Error: Need exactly 30 features (Time, V1..V28, Amount). Got {len(parts)}."
        
        # Extract features
        time = parts[0]
        amount = parts[-1]  # Last element is Amount
        v_features = parts[1:29]  # V1 to V28 (28 features)
        
        # Scale ONLY Time and Amount (scaler expects 2 features)
        time_amount = np.array([[time, amount]])
        scaled_time_amount = _scaler.transform(time_amount)
        scaled_time = scaled_time_amount[0][0]
        scaled_amount = scaled_time_amount[0][1]
        
        # Combine: scaled Time, unscaled V1..V28, scaled Amount
        features = np.array([scaled_time] + v_features + [scaled_amount]).reshape(1, -1)
        
        # Predict
        proba = _model.predict_proba(features)[0][1]
        pred_class = 1 if proba > 0.5 else 0
        
        return f"🔍 Fraud Probability: {proba:.4f}\n🚨 Classification: {'FRAUD' if pred_class else 'NORMAL'}"
    except Exception as e:
        return f"Error parsing input: {e}"
