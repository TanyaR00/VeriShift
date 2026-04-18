from shared.schemas import PredictionInput, PredictionOutput

def predict(data: PredictionInput) -> PredictionOutput:
    """
    Returns a dummy prediction based on the input data.
    """
    # TODO: connect ml_engine
    # Example: from ml_engine.models import predict as ml_predict
    # return ml_predict(data)
    
    # Dummy logic: if income > 50000, approve (1), else reject (0)
    prediction = 1 if data.income > 50000 else 0
    confidence = 0.85
    bias_score = 0.02
    
    return PredictionOutput(
        prediction=prediction,
        confidence=confidence,
        bias_score=bias_score
    )
