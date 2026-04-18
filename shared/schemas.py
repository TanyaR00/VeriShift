from pydantic import BaseModel

class PredictionInput(BaseModel):
    age: int
    income: float
    gender: str          # "male" or "female"
    education: str       # "high_school", "bachelors", "masters", "phd"
    employment_status: str  # "employed", "unemployed", "self_employed"

class TwinInput(BaseModel):
    original: PredictionInput
    changed_field: str   # name of the ONE field being changed
    changed_value: str   # new value for that field

class PredictionOutput(BaseModel):
    prediction: int      # 0 = rejected, 1 = approved
    confidence: float
    bias_score: float

class BiasMetrics(BaseModel):
    bias_score: float
    affected_group: str
    trend: str           # "stable", "increasing", "decreasing"
    psi_score: float
    kl_divergence: float
    timestamp: str

class ExplanationOutput(BaseModel):
    original_prediction: int
    twin_prediction: int
    changed_field: str
    explanation: str     # dummy text for now
