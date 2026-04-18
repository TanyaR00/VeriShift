from shared.schemas import PredictionInput

# In-memory store
_recent_predictions = []

def append_prediction(data: PredictionInput):
    _recent_predictions.append(data.model_dump())
    if len(_recent_predictions) > 50:
        _recent_predictions.pop(0)

def get_recent_predictions(n: int = 50) -> list:
    return _recent_predictions[-n:]
