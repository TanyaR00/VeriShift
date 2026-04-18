from shared.schemas import TwinInput, ExplanationOutput

def explain(data: TwinInput) -> ExplanationOutput:
    """
    Returns a dummy explanation for the twin logic.
    """
    # TODO: connect ml_engine
    # Example: from ml_engine.models import explain_difference as ml_explain
    # return ml_explain(data)
    
    # Dummy logic to illustrate what changed
    original_prediction = 1 if data.original.income > 50000 else 0
    twin_prediction = 0 if data.original.income > 50000 else 1
    
    dummy_text = f"Changing {data.changed_field} to '{data.changed_value}' altered the prediction based on historical patterns."
    
    return ExplanationOutput(
        original_prediction=original_prediction,
        twin_prediction=twin_prediction,
        changed_field=data.changed_field,
        explanation=dummy_text
    )
