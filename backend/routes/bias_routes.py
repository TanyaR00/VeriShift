from fastapi import APIRouter
from backend.services.streaming_service import get_bias_history, get_current_metrics

router = APIRouter()

@router.get("/bias-metrics")
def bias_metrics():
    return get_current_metrics()

@router.get("/stream-history")
def stream_history():
    return get_bias_history()

@router.post("/stream-prediction")
def stream_prediction(data: dict):
    from backend.services.streaming_service import add_prediction
    add_prediction(data)
    return {"status": "received"}
