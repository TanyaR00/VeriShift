"""
Explanation Service
Generates human-readable bias explanations.
Uses Gemini API as the AI governance layer, falls back to deterministic templates.
"""

import os
import json
import time
from dotenv import load_dotenv

load_dotenv("backend/.env")

_GEMINI_AVAILABLE = False
_model = None

try:
    import google.generativeai as genai
    _api_key = os.getenv("GEMINI_API_KEY")
    if _api_key and _api_key != "YOUR_API_KEY_HERE":
        genai.configure(api_key=_api_key)
        # Use gemini-1.5-flash and force JSON output for structured governance data
        _model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"})
        _GEMINI_AVAILABLE = True
        print("[SUCCESS] Gemini API connected for governance")
    else:
        print("[WARNING] GEMINI_API_KEY not set - using deterministic fallbacks")
except ImportError:
    print("[WARNING] google-generativeai not installed - using deterministic fallbacks")

# --- CACHE FOR DASHBOARD ---
_governance_cache = {
    "last_updated": 0,
    "last_bias_score": None,
    "response": None
}

def _get_risk_level(bias_score: float) -> str:
    """Deterministic risk level before Gemini processing."""
    if bias_score > 0.15:
        return "Critical"
    elif bias_score > 0.05:
        return "Medium"
    return "Low"

def _safe_json_parse(text: str, fallback: dict) -> dict:
    try:
        # Sometimes models wrap JSON in markdown blocks even with JSON mime type
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Failed to parse Gemini JSON: {e}")
        return fallback

# -----------------------------------------------------
# 1. TWIN ANALYSIS (For /create-twin)
# -----------------------------------------------------

def generate_twin_analysis(metrics: dict) -> dict:
    """Generates structured analysis for Twin Simulation."""
    bias_score = metrics.get("confidence_delta", 0.0)
    risk_level = _get_risk_level(abs(bias_score))
    
    fallback = {
        "bias_explanation": f"Changing {metrics.get('changed_field')} altered the confidence by {bias_score*100:.0f}%.",
        "risk_level": risk_level,
        "recommendations": ["Review model features", "Apply reweighing technique"],
        "executive_summary": "Simulation indicates potential bias."
    }

    if not _GEMINI_AVAILABLE:
        return fallback

    prompt = f"""
    You are an AI fairness auditor. Analyze this counterfactual simulation:
    - Changed Feature: {metrics.get('changed_field')}
    - Original Prediction: {metrics.get('original_prediction')} (confidence {metrics.get('original_confidence', 0.0):.0%})
    - Twin Prediction: {metrics.get('twin_prediction')} (confidence {metrics.get('twin_confidence', 0.0):.0%})
    - Confidence Delta: {metrics.get('confidence_delta', 0.0):.0%}
    - Bias Detected: {metrics.get('bias_detected')}
    
    Provide a professional, concise, audit-oriented analysis.
    Output ONLY a valid JSON object matching this schema:
    {{
        "bias_explanation": "string (why this happened and what it means)",
        "risk_level": "{risk_level}",
        "recommendations": ["string", "string"],
        "executive_summary": "string (1 sentence summary)"
    }}
    """
    try:
        response = _model.generate_content(prompt)
        return _safe_json_parse(response.text, fallback)
    except Exception as e:
        print(f"Gemini Twin Error: {e}")
        return fallback

# -----------------------------------------------------
# 2. GOVERNANCE SUMMARY (For /stream-prediction)
# -----------------------------------------------------

def generate_governance_summary(metrics: dict) -> dict:
    """Generates structured analysis for Live Dashboard. Uses caching."""
    global _governance_cache
    
    current_bias = metrics.get("bias_score", 0.0)
    current_time = time.time()
    
    # Cache invalidation: re-run if 30s passed OR bias score changed by more than 0.05
    if _governance_cache["response"] is not None:
        time_elapsed = current_time - _governance_cache["last_updated"]
        bias_delta = abs(current_bias - (_governance_cache["last_bias_score"] or 0.0))
        if time_elapsed < 30 and bias_delta < 0.05:
            return _governance_cache["response"]

    risk_level = _get_risk_level(current_bias)
    
    fallback = {
        "governance_summary": f"System operating at {risk_level} risk level. Bias score is {current_bias:.2f}.",
        "recommended_action": "Continue monitoring" if risk_level == "Low" else "Investigate drift immediately.",
        "risk_level": risk_level
    }

    if not _GEMINI_AVAILABLE:
        _governance_cache = {"last_updated": current_time, "last_bias_score": current_bias, "response": fallback}
        return fallback

    prompt = f"""
    You are an enterprise AI governance system monitoring live bias drift.
    Current Live Metrics:
    - Current Bias Score: {current_bias:.2f}
    - Affected Group: {metrics.get('affected_group', 'N/A')}
    - Trend: {metrics.get('trend', 'stable')}
    
    Provide a concise, real-time audit summary.
    Output ONLY a valid JSON object matching this schema:
    {{
        "governance_summary": "string (1-2 sentences on system health)",
        "recommended_action": "string (short mitigation step)",
        "risk_level": "{risk_level}"
    }}
    """
    try:
        response = _model.generate_content(prompt)
        parsed = _safe_json_parse(response.text, fallback)
        _governance_cache = {"last_updated": current_time, "last_bias_score": current_bias, "response": parsed}
        return parsed
    except Exception as e:
        print(f"Gemini Dashboard Error: {e}")
        _governance_cache = {"last_updated": current_time, "last_bias_score": current_bias, "response": fallback}
        return fallback

# -----------------------------------------------------
# 3. DATASET INSIGHTS (For /upload-dataset)
# -----------------------------------------------------

def generate_dataset_insights(metrics: dict) -> dict:
    """Generates structured analysis for Dataset Uploads."""
    bias_score = metrics.get("bias_score", 0.0)
    risk_level = _get_risk_level(bias_score)
    sensitive_attrs = metrics.get("sensitive_attributes", [])
    
    fallback = {
        "dataset_risk_profile": f"Initial analysis shows a {risk_level.lower()} risk profile.",
        "sensitive_attribute_summary": f"Detected {len(sensitive_attrs)} sensitive attributes: {', '.join(sensitive_attrs)}",
        "recommended_mitigation": "Balance representation across groups before training."
    }

    if not _GEMINI_AVAILABLE:
        return fallback

    prompt = f"""
    You are an AI fairness auditor analyzing a newly uploaded dataset.
    Dataset Metrics:
    - Sensitive Attributes Detected: {sensitive_attrs}
    - Missing Values: {metrics.get('missing_percentage', 0.0)}%
    - Baseline Bias Score: {bias_score:.2f}
    - Calculated Risk Level: {risk_level}
    
    Identify potential bias hotspots and risk factors. Do not make speculative claims.
    Output ONLY a valid JSON object matching this schema:
    {{
        "dataset_risk_profile": "string (brief assessment of dataset quality and bias risk)",
        "sensitive_attribute_summary": "string (implications of the detected attributes)",
        "recommended_mitigation": "string (data-level mitigation step)"
    }}
    """
    try:
        response = _model.generate_content(prompt)
        return _safe_json_parse(response.text, fallback)
    except Exception as e:
        print(f"Gemini Upload Error: {e}")
        return fallback
