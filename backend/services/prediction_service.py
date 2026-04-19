"""
Prediction Service
Calls ml_engine predictor for real inference.
Falls back to dummy if model not trained yet.
"""

from shared.schemas import PredictionInput, PredictionOutput
from ml_engine.predictor import predict_single


def predict(data: PredictionInput) -> PredictionOutput:
    """
    Run model inference on input data.
    Calls ml_engine.predictor.predict_single
    """
    return predict_single(data)
