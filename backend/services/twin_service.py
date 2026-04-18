from shared.schemas import TwinInput, PredictionOutput

def create_twin(data: TwinInput) -> PredictionOutput:
    """
    Returns a dummy prediction based on the twin input.
    """
    # TODO: connect ml_engine
    # Example: from ml_engine.models import generate_twin as ml_generate_twin
    # return ml_generate_twin(data)
    
    # Dummy logic: invert the logic of the original for demonstration
    # If original income > 50000 -> 1, let's say twin changes it to < 50000 -> 0
    prediction = 0 if data.original.income > 50000 else 1
    
    # Random confidence and bias for the twin
    confidence = 0.75
    bias_score = 0.05
    
    return PredictionOutput(
        prediction=prediction,
        confidence=confidence,
        bias_score=bias_score
    )
