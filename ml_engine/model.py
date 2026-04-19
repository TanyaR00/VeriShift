"""
model.py
========
Model training, evaluation, saving and inference.

Functions:
  train()    →  trains and saves model.pkl
  predict()  →  returns prediction for one input
  evaluate() →  accuracy + confusion matrix
"""

import numpy as np
import pandas as pd
import pickle
import json
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from preprocessing import preprocess

MODEL_PATH    = "model.pkl"
ENCODERS_PATH = "encoders.pkl"


# ── Training ──────────────────────────────────────────────────────────────

def train(model_type: str = "logistic_regression",
          raw_path:   str = "adult_raw.csv") -> dict:
    """
    Full training pipeline:
      1. Preprocess dataset
      2. Train model
      3. Evaluate
      4. Save model.pkl

    Args:
        model_type: "logistic_regression" (default) or "random_forest"
        raw_path:   Path to raw CSV

    Returns:
        { accuracy, confusion_matrix, feature_importance, model_path }
    """
    print(f"[model] Training {model_type}...")

    X_train, X_test, y_train, y_test, X_test_raw, encoders = preprocess(raw_path)

    if model_type == "random_forest":
        clf = RandomForestClassifier(
            n_estimators=100, max_depth=8,
            class_weight="balanced", random_state=42, n_jobs=-1
        )
    else:
        clf = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(
                max_iter=2000, class_weight="balanced",
                solver="lbfgs", random_state=42
            ))
        ])

    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    acc    = round(accuracy_score(y_test, y_pred), 4)
    cm     = confusion_matrix(y_test, y_pred).tolist()

    print(f"[model] Accuracy: {acc:.2%}")
    print("[model] Confusion Matrix:")
    print(f"         TN={cm[0][0]}  FP={cm[0][1]}")
    print(f"         FN={cm[1][0]}  TP={cm[1][1]}")
    print("[model] Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["<=50K", ">50K"]))

    # Feature importance
    feature_names = X_train.columns.tolist()
    if model_type == "random_forest":
        importances = clf.feature_importances_
    else:
        importances = np.abs(clf.named_steps["lr"].coef_[0])

    top_features = dict(sorted(
        zip(feature_names, [round(float(v), 4) for v in importances]),
        key=lambda x: x[1], reverse=True
    )[:10])

    # Save model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": clf, "feature_names": feature_names}, f)
    print(f"[model] Saved → {MODEL_PATH}")

    return {
        "accuracy": acc,
        "confusion_matrix": cm,
        "top_features": top_features,
        "model_path": MODEL_PATH,
        "model_type": model_type
    }


# ── Inference ─────────────────────────────────────────────────────────────

def _load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found. Run train() first.")
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def _load_encoders():
    if not os.path.exists(ENCODERS_PATH):
        raise FileNotFoundError(f"Encoders not found. Run preprocess() first.")
    with open(ENCODERS_PATH, "rb") as f:
        return pickle.load(f)


def predict(input_data: dict) -> dict:
    """
    Predict income class for a single person.

    Args:
        input_data: dict with feature values, e.g.:
            {
                "age": 35,
                "workclass": "Private",
                "education": "Bachelors",
                "education_num": 13,
                "marital_status": "Married-civ-spouse",
                "occupation": "Exec-managerial",
                "relationship": "Husband",
                "race": "White",
                "sex": "Male",
                "capital_gain": 0,
                "capital_loss": 0,
                "hours_per_week": 40,
                "native_country": "United-States"
            }

    Returns:
        {
            "prediction": 0 or 1,
            "label": "<=50K" or ">50K",
            "probability": float
        }
    """
    artifact  = _load_model()
    clf       = artifact["model"]
    feat_names = artifact["feature_names"]
    encoders  = _load_encoders()

    from preprocessing import CATEGORICAL_COLS, SENSITIVE_COL
    df = pd.DataFrame([input_data])

    # Encode categoricals
    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            df[col] = "Unknown"
        le = encoders.get(col)
        if le:
            known = set(le.classes_)
            df[col] = df[col].apply(lambda x: x if str(x) in known else le.classes_[0])
            df[col] = le.transform(df[col].astype(str))

    # Encode sex
    if SENSITIVE_COL in df.columns:
        df["sex_encoded"] = (df[SENSITIVE_COL] == "Male").astype(int)
        df = df.drop(columns=[SENSITIVE_COL])

    # Align to training feature order
    for col in feat_names:
        if col not in df.columns:
            df[col] = 0
    df = df[feat_names]

    pred      = int(clf.predict(df)[0])
    prob      = float(clf.predict_proba(df)[0][1])
    label_map = {0: "<=50K", 1: ">50K"}

    return {
        "prediction": pred,
        "label": label_map[pred],
        "probability": round(prob, 4)
    }


# ── Batch Evaluation with Bias Data ───────────────────────────────────────

def evaluate_with_bias(X_test: pd.DataFrame,
                        y_test: pd.Series,
                        X_test_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Run predictions on test set and return a DataFrame
    ready for bias_metrics.compute_bias_metrics().

    Returns:
        DataFrame with columns: sex, income, prediction
    """
    artifact   = _load_model()
    clf        = artifact["model"]
    y_pred     = clf.predict(X_test)

    result_df = X_test_raw[["sex"]].copy()
    result_df["income"]     = y_test.values
    result_df["prediction"] = y_pred
    return result_df


if __name__ == "__main__":
    result = train(model_type="logistic_regression")
    print("\nTraining complete:")
    print(json.dumps({
        "accuracy": result["accuracy"],
        "model_path": result["model_path"],
        "top_features": result["top_features"]
    }, indent=2))

    # Test predict
    sample = {
        "age": 35, "workclass": "Private", "education": "Bachelors",
        "education_num": 13, "marital_status": "Married-civ-spouse",
        "occupation": "Exec-managerial", "relationship": "Husband",
        "race": "White", "sex": "Male", "capital_gain": 0,
        "capital_loss": 0, "hours_per_week": 40, "native_country": "United-States"
    }
    print("\nSample prediction (Male, Bachelors, Exec-managerial):")
    print(json.dumps(predict(sample), indent=2))

    sample["sex"] = "Female"
    print("\nSample prediction (Female, same profile):")
    print(json.dumps(predict(sample), indent=2))
