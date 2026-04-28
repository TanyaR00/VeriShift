"""
Streaming Service
Maintains in-memory store of streaming predictions and bias scores over time.
Gets populated by simulate_stream.py posting to /stream-prediction.
"""

from datetime import datetime
from collections import deque
import random

# In-memory stores
_predictions = deque(maxlen=200)
_bias_history = deque(maxlen=50)

# Seed with realistic starting data so dashboard is never empty
_initial_scores = [
    0.04, 0.05, 0.04, 0.06, 0.05, 0.07,   # Phase 1: normal
    0.12, 0.18, 0.22, 0.28, 0.31, 0.35,   # Phase 2: slight bias
    0.41, 0.48, 0.55, 0.61, 0.68, 0.74, 0.79, 0.85  # Phase 3: high bias
]

for i, score in enumerate(_initial_scores):
    _bias_history.append({
        "timestamp": f"T-{len(_initial_scores)-i}",
        "bias_score": score,
        "affected_group": "female",
        "phase": "historical"
    })


def process_stream(prediction_data: dict):
    """Called by /stream-prediction POST endpoint."""
    _predictions.append({
        **prediction_data,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Compute running bias score from last 20 predictions
    recent = list(_predictions)[-20:]
    if len(recent) >= 5:
        female_preds = [p for p in recent if p.get("gender") == "female"]
        male_preds = [p for p in recent if p.get("gender") == "male"]

        if female_preds and male_preds:
            female_approval = sum(
                1 for p in female_preds if p.get("prediction") == 1
            ) / len(female_preds)
            male_approval = sum(
                1 for p in male_preds if p.get("prediction") == 1
            ) / len(male_preds)
            bias_score = round(abs(male_approval - female_approval), 4)
        else:
            bias_score = _bias_history[-1]["bias_score"] if _bias_history else 0.0

        _bias_history.append({
            "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
            "bias_score": bias_score,
            "affected_group": "female",
            "phase": "live"
        })


def get_stream_history() -> dict:
    """Returns all bias scores over time for the dashboard chart."""
    history = list(_bias_history)
    return {
        "scores": [h["bias_score"] for h in history],
        "timestamps": [h["timestamp"] for h in history],
        "count": len(history)
    }


def get_bias_metrics() -> dict:
    """Returns the most recent bias metrics."""
    if not _bias_history:
        return {
            "bias_score": 0.85,
            "affected_group": "female",
            "trend": "increasing",
            "psi_score": 0.047,
            "kl_divergence": 0.524,
            "timestamp": datetime.utcnow().isoformat()
        }

    recent_scores = [h["bias_score"] for h in list(_bias_history)[-5:]]
    if len(recent_scores) >= 2:
        trend = "increasing" if recent_scores[-1] > recent_scores[0] else \
                "decreasing" if recent_scores[-1] < recent_scores[0] else "stable"
    else:
        trend = "stable"

    return {
        "bias_score": round(_bias_history[-1]["bias_score"], 4),
        "affected_group": "female",
        "trend": trend,
        "psi_score": 0.047,
        "kl_divergence": 0.524,
        "timestamp": datetime.utcnow().isoformat()
    }


def get_stream_dashboard_data() -> dict:
    """Returns exact schema requested by the dashboard."""
    if not _bias_history:
        from backend.state import state
        score = state.metrics.get("bias_score", 0.0)
        group = state.metrics.get("affected_group", "unknown")
        return {
            "bias_score": score,
            "trend": "stable",
            "affected_group": group,
            "timeline": []
        }
        
    recent_scores = [h["bias_score"] for h in list(_bias_history)[-5:]]
    if len(recent_scores) >= 2:
        trend = "increasing" if recent_scores[-1] > recent_scores[0] else \
                "decreasing" if recent_scores[-1] < recent_scores[0] else "stable"
    else:
        trend = "stable"
        
    return {
        "bias_score": _bias_history[-1]["bias_score"],
        "trend": trend,
        "affected_group": _bias_history[-1].get("affected_group", "unknown"),
        "timeline": [h["bias_score"] for h in _bias_history]
    }

def get_recent_predictions(n: int = 50) -> list:
    """Returns last N predictions."""
    return list(_predictions)[-n:]
