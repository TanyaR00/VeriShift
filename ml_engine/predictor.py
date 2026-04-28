"""
ML Engine Predictor — Adapter Layer
Loads trained model artifacts and exposes clean functions
for FastAPI services to call.
"""

import joblib
import numpy as np
import pandas as pd
import os
from shared.schemas import PredictionInput, PredictionOutput

# ── Load model artifacts once at module level ──
# Run ml_engine/bias_intelligence.py first to generate these
_ARTIFACTS_PATH = os.path.join(os.path.dirname(__file__), "..", "output")

try:
    _model = joblib.load(os.path.join(_ARTIFACTS_PATH, "model.joblib"))
    _scaler = joblib.load(os.path.join(_ARTIFACTS_PATH, "scaler.joblib"))
    _encoders = joblib.load(os.path.join(_ARTIFACTS_PATH, "encoders.joblib"))
    _model_loaded = True
    print("[SUCCESS] ML model artifacts loaded successfully")
except FileNotFoundError:
    _model_loaded = False
    print("[WARNING] Model artifacts not found - run bias_intelligence.py first to train and save the model")


def _input_to_dataframe(data: PredictionInput) -> pd.DataFrame:
    """Convert PredictionInput schema to DataFrame for model inference."""
    return pd.DataFrame([{
        "age": data.age,
        "income": data.income,
        "gender": data.gender,
        "education": data.education,
        "employment_status": data.employment_status,
    }])


def _encode_and_scale(df: pd.DataFrame) -> np.ndarray:
    """Apply saved encoders and scaler to raw input DataFrame."""
    df = df.copy()
    for col in ["gender", "education", "employment_status"]:
        if col in _encoders:
            df[col] = _encoders[col].transform(df[col].astype(str))
    return _scaler.transform(df)


def predict_single(data: PredictionInput) -> PredictionOutput:
    """
    Run inference on a single PredictionInput.
    Returns PredictionOutput with prediction, confidence, bias_score.
    TODO: bias_score per-request populated separately by BiasDetector
    """
    if not _model_loaded:
        # Fallback dummy response if model not trained yet
        return PredictionOutput(prediction=1, confidence=0.85, bias_score=0.0)

    df = _input_to_dataframe(data)
    scaled = _encode_and_scale(df)

    prediction = int(_model.predict(scaled)[0])
    confidence = round(float(_model.predict_proba(scaled)[0][prediction]), 4)

    return PredictionOutput(
        prediction=prediction,
        confidence=confidence,
        bias_score=0.0,  # TODO: populate with BiasDetector.overall_bias_score
    )


def predict_twin(original: PredictionInput, changed_field: str, changed_value: str) -> dict:
    """
    Run original + twin prediction.
    Only one field changes — everything else identical.
    Returns both predictions and whether bias was detected.
    """
    if not _model_loaded:
        # Fallback dummy twin response
        return {
            "original_prediction": 0,
            "original_confidence": 0.72,
            "twin_prediction": 1,
            "twin_confidence": 0.89,
            "bias_detected": True,
            "changed_field": changed_field,
            "original_value": getattr(original, changed_field, "unknown"),
            "twin_value": changed_value,
            "confidence_delta": round(0.89 - 0.72, 4),
        }

    orig_result = predict_single(original)

    # Create twin — copy original and change exactly one field
    twin_dict = original.model_dump()
    # Attempt type coercion for numeric fields
    if changed_field in ["age"]:
        try:
            twin_dict[changed_field] = int(changed_value)
        except ValueError:
            twin_dict[changed_field] = changed_value
    elif changed_field in ["income"]:
        try:
            twin_dict[changed_field] = float(changed_value)
        except ValueError:
            twin_dict[changed_field] = changed_value
    else:
        twin_dict[changed_field] = changed_value

    twin_input = PredictionInput(**twin_dict)
    twin_result = predict_single(twin_input)

    return {
        "original_prediction": orig_result.prediction,
        "original_confidence": orig_result.confidence,
        "twin_prediction": twin_result.prediction,
        "twin_confidence": twin_result.confidence,
        "bias_detected": orig_result.prediction != twin_result.prediction,
        "changed_field": changed_field,
        "original_value": getattr(original, changed_field),
        "twin_value": changed_value,
        "confidence_delta": round(twin_result.confidence - orig_result.confidence, 4),
    }
