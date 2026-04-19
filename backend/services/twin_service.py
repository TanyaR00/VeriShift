"""
Twin Service
Creates counterfactual 'twin' predictions.
Changes exactly one feature and compares outcomes.
"""

from shared.schemas import TwinInput
from ml_engine.predictor import predict_twin


def create_twin(data: TwinInput) -> dict:
    """
    Generate twin prediction — one field changed, all else identical.
    Calls ml_engine.predictor.predict_twin
    """
    return predict_twin(
        original=data.original,
        changed_field=data.changed_field,
        changed_value=data.changed_value,
    )
