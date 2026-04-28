from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from shared.schemas import PredictionInput, TwinInput, PredictionOutput, ExplanationOutput
from backend.services.prediction_service import predict
from backend.services.twin_service import create_twin
from backend.services.explanation_service import (
    generate_twin_analysis,
    generate_governance_summary,
    generate_dataset_insights,
)
from backend.services.streaming_service import process_stream, get_stream_dashboard_data
from backend.state import state
import pandas as pd
import io

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
    
    orig_res = "Approved" if twin_result.get("original_prediction") == 1 else "Rejected"
    twin_res = "Approved" if twin_result.get("twin_prediction") == 1 else "Rejected"
    
    changed_field = twin_result.get("changed_field", data.changed_field)
    
    summary = f"Changing {changed_field} significantly altered the prediction outcome." if twin_result.get("bias_detected") else f"Changing {changed_field} had no effect on the outcome."
    
    return {
        "original_prediction": {
            "result": orig_res,
            "confidence": twin_result.get("original_confidence", 0.0)
        },
        "twin_prediction": {
            "result": twin_res,
            "confidence": twin_result.get("twin_confidence", 0.0)
        },
        "bias_detected": twin_result.get("bias_detected", False),
        "bias_summary": summary,
        "top_factors": [
            {
                "feature": changed_field,
                "impact": twin_result.get("confidence_delta", 0.0)
            }
        ],
        "recommendations": [
            f"Apply reweighing to reduce {changed_field} imbalance"
        ]
    }

@app.post("/explain")
def explain_endpoint(data: TwinInput):
    return create_twin_endpoint(data)

@app.post("/stream-prediction")
def stream_prediction_endpoint(data: PredictionInput):
    process_stream(data.model_dump())
    return {"status": "ok"}

@app.get("/stream-prediction")
def stream_dashboard_endpoint():
    return get_stream_dashboard_data()

@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        elif filename.endswith(".json"):
            df = pd.read_json(io.BytesIO(contents))
        elif filename.endswith(".pdf"):
            import pdfplumber
            rows = []
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                for page in pdf.pages:
                    for table in (page.extract_tables() or []):
                        rows.extend(table)
            if not rows:
                return {"error": "No table found in PDF"}
            df = pd.DataFrame(rows[1:], columns=rows[0])
        else:
            return {"error": "Unsupported format. Use CSV, JSON, XLSX, or PDF."}

        state.active_dataset = df
        row_count = len(df)
        
        missing_total = df.isnull().sum().sum()
        total_cells = df.size
        missing_percentage = round((missing_total / total_cells) * 100, 1) if total_cells > 0 else 0.0

        sensitive_keywords = ["gender", "age", "race", "ethnicity", "religion"]
        sensitive_attrs = [c for c in df.columns if any(k in c.lower() for k in sensitive_keywords)]
        
        gender_col = next((c for c in df.columns if "gender" in c.lower()), None)
        outcome_col = next(
            (c for c in df.columns if any(
                k in c.lower() for k in
                ["predict", "outcome", "label", "approved", "decision", "result"]
            )), None
        )

        bias_score = 0.0
        if gender_col and outcome_col:
            df[outcome_col] = pd.to_numeric(df[outcome_col], errors="coerce")
            grouped = df.groupby(gender_col)[outcome_col].mean().dropna()
            vals = list(grouped.values)
            if len(vals) >= 2:
                bias_score = round(abs(vals[0] - vals[1]), 3)

        state.metrics = {
            "bias_score": bias_score,
            "affected_group": "female" if gender_col else "unknown",
            "missing_percentage": missing_percentage,
            "sensitive_attributes": sensitive_attrs
        }

        return {
          "filename": filename,
          "rows": row_count,
          "sensitive_attributes": sensitive_attrs,
          "missing_percentage": missing_percentage,
          "bias_score": bias_score
        }

    except Exception as e:
        return {"error": str(e)}