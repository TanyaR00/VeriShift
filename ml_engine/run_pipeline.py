"""
run_pipeline.py
===============
Runs the complete VeriShift ML pipeline end-to-end.
Use this to test everything works before pushing to GitHub.
"""

import json
import numpy as np
import pandas as pd

from preprocessing  import preprocess
from model          import train, evaluate_with_bias, predict
from bias_metrics   import compute_bias_metrics, compute_bias_score
from drift_detection import detect_bias_drift, update_bias_history


def run_full_pipeline():
    print("=" * 60)
    print("  VeriShift — Bias Intelligence Pipeline")
    print("=" * 60)

    # ── 1. Train ──────────────────────────────────────────────────
    print("\n[1/4] Training model...")
    train_result = train(model_type="logistic_regression", raw_path="adult_raw.csv")
    print(f"      Accuracy: {train_result['accuracy']:.2%}")

    # ── 2. Evaluate + collect predictions ─────────────────────────
    print("\n[2/4] Running bias detection...")
    X_train, X_test, y_train, y_test, X_test_raw, _ = preprocess("adult_raw.csv")
    result_df = evaluate_with_bias(X_test, y_test, X_test_raw)

    bias_metrics = compute_bias_metrics(result_df, sensitive_col="sex",
                                         target_col="income", pred_col="prediction")
    print(f"      SPD : {bias_metrics['statistical_parity']}")
    print(f"      EOD : {bias_metrics['equal_opportunity']}")
    print(f"      Group Accuracy: {bias_metrics['group_accuracy']}")

    # ── 3. Bias score ──────────────────────────────────────────────
    score_result = compute_bias_score(
        statistical_parity=bias_metrics["statistical_parity"],
        equal_opportunity=bias_metrics["equal_opportunity"],
        group_accuracy=bias_metrics["group_accuracy"]
    )
    print(f"\n      Bias Score  : {score_result['bias_score']}")
    print(f"      Risk        : {score_result['risk']}")
    print(f"      Affected    : {score_result['affected_group']}")

    # ── 4. Drift detection ─────────────────────────────────────────
    print("\n[3/4] Checking drift...")
    np.random.seed(42)
    n = 300
    old_data = {
        "predictions":        np.random.beta(2, 5, n).tolist(),
        "male_predictions":   np.random.beta(3, 4, n//2).tolist(),
        "female_predictions": np.random.beta(1, 6, n//2).tolist(),
    }
    new_data = {
        "predictions":        np.random.beta(3, 3, n).tolist(),
        "male_predictions":   np.random.beta(4, 3, n//2).tolist(),
        "female_predictions": np.random.beta(1, 7, n//2).tolist(),
    }
    drift = detect_bias_drift(old_data, new_data)

    # Store in history
    update_bias_history({
        "bias_score": score_result["bias_score"],
        "spd": bias_metrics["statistical_parity"],
        "eod": bias_metrics["equal_opportunity"],
        "psi": drift["psi"]
    })

    print(f"      PSI           : {drift['psi']}")
    print(f"      KL Divergence : {drift['kl_divergence']}")
    print(f"      Drift Status  : {drift['drift_status']}")

    # ── 5. Final JSON output ───────────────────────────────────────
    print("\n[4/4] Final output (backend-ready JSON):")
    final_output = {
        "bias_score":    score_result["bias_score"],
        "risk":          score_result["risk"],
        "affected_group": score_result["affected_group"],
        "trend":         drift["bias_trend"],
        "metrics": {
            "statistical_parity_difference": bias_metrics["statistical_parity"],
            "equal_opportunity_difference":  bias_metrics["equal_opportunity"],
            "group_accuracy":                bias_metrics["group_accuracy"],
            "psi":                           drift["psi"],
            "kl_divergence":                 drift["kl_divergence"],
            "drift_status":                  drift["drift_status"]
        }
    }

    print(json.dumps(final_output, indent=2))

    # ── 6. Twin validation demo ────────────────────────────────────
    print("\n[bonus] Twin validation (same person, sex flipped):")
    person = {
        "age": 32, "workclass": "Private", "education": "Bachelors",
        "education_num": 13, "marital_status": "Never-married",
        "occupation": "Prof-specialty", "relationship": "Not-in-family",
        "race": "White", "sex": "Male", "capital_gain": 0,
        "capital_loss": 0, "hours_per_week": 45, "native_country": "United-States"
    }
    twin = {**person, "sex": "Female"}

    pred_orig = predict(person)
    pred_twin = predict(twin)

    print(f"  Male   → {pred_orig['label']} (prob: {pred_orig['probability']})")
    print(f"  Female → {pred_twin['label']} (prob: {pred_twin['probability']})")
    bias_flip = pred_orig["prediction"] != pred_twin["prediction"]
    print(f"  Prediction flipped? {'YES ⚠️  BIAS DETECTED' if bias_flip else 'NO ✅'}")

    print("\n" + "=" * 60)
    print("  Pipeline complete ✅")
    print("=" * 60)
    return final_output


if __name__ == "__main__":
    run_full_pipeline()
