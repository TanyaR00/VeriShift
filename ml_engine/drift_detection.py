"""
drift_detection.py
==================
Live Bias Drift Engine — tracks how bias changes over time in a running system.

Functions:
  detect_bias_drift(old_data, new_data)  →  { psi, kl_divergence, bias_trend }
  update_bias_history(record)            →  appends to in-memory + JSON log
  get_bias_trend(history)               →  "increasing" / "decreasing" / "stable"
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime


# ── In-memory time series store (replace with DB in production) ────────────
_bias_history = []   # list of { timestamp, bias_score, spd, eod, psi }


# ── 1. Population Stability Index ─────────────────────────────────────────

def population_stability_index(expected: np.ndarray,
                                actual: np.ndarray,
                                buckets: int = 10) -> float:
    """
    PSI compares past vs current prediction distributions.

    PSI < 0.1  → No significant shift  ✅
    PSI 0.1–0.2 → Moderate shift       ⚠️
    PSI > 0.2  → Significant drift     🔴

    Args:
        expected: Prediction probabilities from baseline (past)
        actual:   Prediction probabilities from current window
        buckets:  Number of bins

    Returns:
        PSI score (float)
    """
    expected = np.array(expected, dtype=float)
    actual   = np.array(actual,   dtype=float)

    # Build bins from expected distribution
    breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
    breakpoints = np.unique(breakpoints)
    if len(breakpoints) < 2:
        return 0.0

    def _safe_pct(arr, bins):
        counts, _ = np.histogram(arr, bins=bins)
        pct = counts / max(len(arr), 1)
        return np.where(pct == 0, 1e-8, pct)

    exp_pct = _safe_pct(expected, breakpoints)
    act_pct = _safe_pct(actual,   breakpoints)

    min_len = min(len(exp_pct), len(act_pct))
    exp_pct = exp_pct[:min_len]
    act_pct = act_pct[:min_len]

    psi = float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))
    return round(psi, 4)


# ── 2. KL Divergence ──────────────────────────────────────────────────────

def kl_divergence(p: np.ndarray,
                   q: np.ndarray,
                   bins: int = 10) -> float:
    """
    KL Divergence between male and female prediction distributions.

    Lower = groups are treated similarly.
    Higher = groups receive very different prediction distributions.

    Args:
        p: Prediction probabilities for group 1 (e.g. Male)
        q: Prediction probabilities for group 2 (e.g. Female)

    Returns:
        KL divergence (float, non-negative)
    """
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)

    all_vals = np.concatenate([p, q])
    if len(all_vals) == 0:
        return 0.0

    bin_edges = np.linspace(all_vals.min(), all_vals.max() + 1e-9, bins + 1)

    def _to_dist(arr, edges):
        counts, _ = np.histogram(arr, bins=edges)
        dist = counts / max(counts.sum(), 1)
        return np.where(dist == 0, 1e-10, dist)

    p_dist = _to_dist(p, bin_edges)
    q_dist = _to_dist(q, bin_edges)

    kl = float(np.sum(p_dist * np.log(p_dist / q_dist)))
    return round(max(kl, 0.0), 4)   # KL is always ≥ 0


# ── 3. Trend Analysis ─────────────────────────────────────────────────────

def get_bias_trend(history: list) -> str:
    """
    Determines if bias is increasing, decreasing, or stable
    using linear regression slope over recorded bias scores.

    Args:
        history: List of dicts with key "bias_score", or list of floats

    Returns:
        "increasing" | "decreasing" | "stable"
    """
    if len(history) < 2:
        return "insufficient_data"

    if isinstance(history[0], dict):
        scores = np.array([h["bias_score"] for h in history], dtype=float)
    else:
        scores = np.array(history, dtype=float)

    x = np.arange(len(scores))
    slope = float(np.polyfit(x, scores, 1)[0])

    if slope > 0.005:
        return "increasing"
    elif slope < -0.005:
        return "decreasing"
    else:
        return "stable"


# ── 4. Time-based Bias Store ──────────────────────────────────────────────

def update_bias_history(record: dict, log_path: str = "bias_history.json"):
    """
    Appends a bias snapshot to the in-memory history and persists to JSON.

    Args:
        record: { bias_score, spd, eod, psi, ... }
        log_path: Path to JSON log file
    """
    global _bias_history

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        **{k: round(float(v), 4) if isinstance(v, (int, float, np.floating)) else v
           for k, v in record.items()}
    }
    _bias_history.append(entry)

    # Persist to file
    history = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append(entry)
    with open(log_path, "w") as f:
        json.dump(history, f, indent=2)


def load_bias_history(log_path: str = "bias_history.json") -> list:
    """Load persisted bias history from JSON."""
    if not os.path.exists(log_path):
        return []
    with open(log_path, "r") as f:
        return json.load(f)


# ── 5. Main Drift Detection Function ─────────────────────────────────────

def detect_bias_drift(old_data: dict, new_data: dict) -> dict:
    """
    Core drift detection — call this from your API endpoint.

    Args:
        old_data: {
            "predictions": [0.3, 0.7, ...],      ← baseline probabilities
            "male_predictions":   [0.6, 0.8, ...],
            "female_predictions": [0.3, 0.4, ...]
        }
        new_data: Same structure for current window

    Returns:
        {
            "psi": float,
            "kl_divergence": float,
            "bias_trend": "increasing" | "decreasing" | "stable",
            "drift_status": "stable" | "moderate_drift" | "significant_drift"
        }
    """
    old_preds  = np.array(old_data.get("predictions", []))
    new_preds  = np.array(new_data.get("predictions", []))

    male_old   = np.array(old_data.get("male_predictions",   []))
    female_old = np.array(old_data.get("female_predictions", []))
    male_new   = np.array(new_data.get("male_predictions",   []))
    female_new = np.array(new_data.get("female_predictions", []))

    # PSI: overall distribution shift
    psi = population_stability_index(old_preds, new_preds) if len(old_preds) and len(new_preds) else 0.0

    # KL: group distribution divergence in current window
    kl = kl_divergence(male_new, female_new) if len(male_new) and len(female_new) else 0.0

    # Trend from stored history
    history = load_bias_history()
    trend = get_bias_trend(history) if history else "insufficient_data"

    # Drift classification
    if psi < 0.1:
        drift_status = "stable"
    elif psi < 0.2:
        drift_status = "moderate_drift"
    else:
        drift_status = "significant_drift"

    return {
        "psi": psi,
        "kl_divergence": kl,
        "bias_trend": trend,
        "drift_status": drift_status
    }


# ── 6. Streaming helper: process a single incoming record ─────────────────

def process_stream_record(record: dict,
                           window: list,
                           window_size: int = 100) -> dict:
    """
    Processes one streaming prediction record.
    Maintains a sliding window and computes live drift.

    Args:
        record: { "gender": "female", "prediction": 0, "probability": 0.3 }
        window: Mutable list acting as sliding window buffer
        window_size: How many records to compare at a time

    Returns:
        drift snapshot dict (or None if window not full yet)
    """
    window.append(record)

    if len(window) < window_size * 2:
        return {"status": "buffering", "buffer_size": len(window)}

    # Split into old (baseline) and new (current) halves
    old_window = window[-window_size * 2 : -window_size]
    new_window = window[-window_size:]

    def _extract(win, key="probability"):
        return [r.get(key, r.get("prediction", 0)) for r in win]

    def _group(win, gender):
        return [r.get("probability", r.get("prediction", 0))
                for r in win if r.get("gender", "").lower() == gender.lower()]

    old_data = {
        "predictions":        _extract(old_window),
        "male_predictions":   _group(old_window, "Male"),
        "female_predictions": _group(old_window, "Female"),
    }
    new_data = {
        "predictions":        _extract(new_window),
        "male_predictions":   _group(new_window, "Male"),
        "female_predictions": _group(new_window, "Female"),
    }

    return detect_bias_drift(old_data, new_data)


if __name__ == "__main__":
    np.random.seed(42)
    n = 200

    old = {
        "predictions":        np.random.beta(2, 5, n).tolist(),
        "male_predictions":   np.random.beta(3, 4, n//2).tolist(),
        "female_predictions": np.random.beta(1, 6, n//2).tolist(),
    }
    new = {
        "predictions":        np.random.beta(3, 3, n).tolist(),   # shifted
        "male_predictions":   np.random.beta(4, 3, n//2).tolist(),
        "female_predictions": np.random.beta(1, 7, n//2).tolist(),
    }

    result = detect_bias_drift(old, new)
    print("Drift Detection Result:")
    print(json.dumps(result, indent=2))
