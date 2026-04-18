from shared.schemas import PredictionInput
from streaming.consumer.process_stream import append_prediction, get_recent_predictions

def process_stream(data: PredictionInput) -> dict:
    """
    Processes incoming prediction stream.
    """
    # TODO: connect ml_engine
    append_prediction(data)
    return {"status": "success", "recorded": True}

def get_recent_stream(n: int = 50) -> list:
    """
    Retrieves recent predictions for dashboard.
    """
    return get_recent_predictions(n)
