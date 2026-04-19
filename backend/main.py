from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.schemas import PredictionInput, TwinInput, PredictionOutput, ExplanationOutput
from backend.services.prediction_service import predict
from backend.services.twin_service import create_twin
from backend.services.explanation_service import explain
from backend.services.streaming_service import process_stream, get_recent_stream

app = FastAPI(title="VeriShift API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict", response_model=PredictionOutput)
def predict_endpoint(data: PredictionInput):
    return predict(data)

@app.post("/create-twin")
def create_twin_endpoint(data: TwinInput):
    twin_result = create_twin(data)
    explanation_result = explain(
        original_prediction=twin_result["original_prediction"],
        twin_prediction=twin_result["twin_prediction"],
        changed_field=twin_result["changed_field"],
        original_confidence=twin_result["original_confidence"],
        twin_confidence=twin_result["twin_confidence"]
    )
    return {**twin_result, **explanation_result.model_dump()}

@app.post("/explain")
def explain_endpoint(data: TwinInput):
    twin_result = create_twin(data)
    explanation_result = explain(
        original_prediction=twin_result["original_prediction"],
        twin_prediction=twin_result["twin_prediction"],
        changed_field=twin_result["changed_field"],
        original_confidence=twin_result["original_confidence"],
        twin_confidence=twin_result["twin_confidence"]
    )
    return {**twin_result, **explanation_result.model_dump()}

@app.post("/stream-prediction")
def stream_prediction_endpoint(data: PredictionInput):
    return process_stream(data)

@app.get("/stream-prediction")
def get_stream_predictions():
    # Helper endpoint to fetch recent streams for the dashboard
    return get_recent_stream()
