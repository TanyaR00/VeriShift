"""
Explanation Service
Generates human-readable bias explanations.
Uses Gemini API when available, falls back to template explanations.
"""

import os
from shared.schemas import ExplanationOutput

# TODO: pip install google-generativeai and set GEMINI_API_KEY in .env
_GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    _api_key = os.getenv("GEMINI_API_KEY")
    if _api_key:
        genai.configure(api_key=_api_key)
        _model = genai.GenerativeModel("gemini-pro")
        _GEMINI_AVAILABLE = True
        print("[SUCCESS] Gemini API connected")
    else:
        print("[WARNING] GEMINI_API_KEY not set - using template explanations")
except ImportError:
    print("[WARNING] google-generativeai not installed - using template explanations")


def _template_explanation(changed_field: str, original_prediction: int, twin_prediction: int) -> str:
    """Fallback explanation when Gemini is unavailable."""
    outcome_changed = original_prediction != twin_prediction
    original_label = "approved" if original_prediction == 1 else "rejected"
    twin_label = "approved" if twin_prediction == 1 else "rejected"

    templates = {
        "gender": f"Changing gender caused the outcome to shift from {original_label} to {twin_label}. "
                  f"This indicates the model has learned gender-correlated patterns from historical training data, "
                  f"which is a form of statistical discrimination.",
        "income": f"The income change shifted the prediction from {original_label} to {twin_label}. "
                  f"Income is a strong predictor in this model, but may proxy for protected attributes.",
        "education": f"Education level change moved the outcome from {original_label} to {twin_label}. "
                     f"Educational attainment can reflect systemic inequalities in access to opportunity.",
        "employment_status": f"Employment status change resulted in a shift from {original_label} to {twin_label}. "
                             f"This feature carries significant weight in the model's decision boundary.",
        "age": f"Age change moved the prediction from {original_label} to {twin_label}. "
               f"Age-based variation in outcomes may indicate temporal bias in training data.",
    }

    base = templates.get(changed_field, f"{changed_field} change shifted outcome from {original_label} to {twin_label}.")

    if not outcome_changed:
        base = f"Despite changing {changed_field}, the prediction remained {original_label}. " \
               f"This suggests other features have stronger influence on this individual's outcome."

    return base


def _gemini_explanation(changed_field: str, original_prediction: int, twin_prediction: int,
                         original_confidence: float, twin_confidence: float) -> str:
    """Generate explanation using Gemini API."""
    prompt = f"""
    You are an AI fairness auditor explaining a bias detection result to a non-technical audience.
    
    A counterfactual test was run on an automated decision system:
    - Only the '{changed_field}' attribute was changed
    - Original prediction: {'Approved' if original_prediction == 1 else 'Rejected'} (confidence: {original_confidence:.0%})
    - Twin prediction: {'Approved' if twin_prediction == 1 else 'Rejected'} (confidence: {twin_confidence:.0%})
    
    In 2-3 sentences, explain what this means for fairness, why it might happen, 
    and what risk it poses. Be direct, clear, and avoid jargon.
    Do not use bullet points. Plain prose only.
    """
    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API error: {e}")
        return _template_explanation(changed_field, original_prediction, twin_prediction)


def explain(original_prediction: int, twin_prediction: int, changed_field: str,
            original_confidence: float = 0.0, twin_confidence: float = 0.0) -> ExplanationOutput:
    """
    Generate explanation for why twin prediction differs from original.
    Uses Gemini if available, template fallback otherwise.
    """
    if _GEMINI_AVAILABLE:
        explanation_text = _gemini_explanation(
            changed_field, original_prediction, twin_prediction,
            original_confidence, twin_confidence
        )
    else:
        explanation_text = _template_explanation(changed_field, original_prediction, twin_prediction)

    return ExplanationOutput(
        original_prediction=original_prediction,
        twin_prediction=twin_prediction,
        changed_field=changed_field,
        explanation=explanation_text,
    )
