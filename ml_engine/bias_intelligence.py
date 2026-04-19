"""
Bias Intelligence Layer
Detects and tracks bias in automated decision-making models.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
from datetime import datetime
import joblib
import json
import os
import warnings
warnings.filterwarnings("ignore")


class DataPreparator:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()

    def clean(self, df):
        df = df.copy()
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
        return df

    def encode(self, df, target_col):
        df = df.copy()
        for col in df.select_dtypes(include="object").columns:
            if col != target_col:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        return df

    def prepare(self, df, target_col, sensitive_cols):
        df = self.clean(df)
        df = self.encode(df, target_col)
        X = df.drop(columns=[target_col])
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        return (
            pd.DataFrame(X_train_scaled, columns=X.columns),
            pd.DataFrame(X_test_scaled, columns=X.columns),
            y_train.reset_index(drop=True),
            y_test.reset_index(drop=True),
            X_test.reset_index(drop=True),
        )


class ModelBuilder:
    def __init__(self, model_type="logistic_regression"):
        if model_type == "random_forest":
            self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        else:
            self.model = LogisticRegression(max_iter=1000, random_state=42)
        self.model_type = model_type

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
        return self

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)[:, 1]

    def feature_importance(self, feature_names):
        if self.model_type == "random_forest":
            importances = self.model.feature_importances_
        else:
            importances = np.abs(self.model.coef_[0])
        return dict(sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True))


class BiasDetector:
    def __init__(self, predictions, labels, sensitive_col_values):
        self.preds = np.array(predictions)
        self.labels = np.array(labels)
        self.groups = sensitive_col_values

    def statistical_parity_difference(self):
        unique_groups = np.unique(self.groups)
        group_rates = {}
        for g in unique_groups:
            mask = self.groups == g
            group_rates[g] = self.preds[mask].mean()
        groups_list = list(group_rates.keys())
        if len(groups_list) < 2:
            return 0.0, group_rates
        spd = group_rates[groups_list[0]] - group_rates[groups_list[1]]
        return round(float(spd), 4), group_rates

    def equal_opportunity_difference(self):
        unique_groups = np.unique(self.groups)
        tpr_rates = {}
        for g in unique_groups:
            mask = self.groups == g
            actual_pos = (self.labels[mask] == 1)
            if actual_pos.sum() == 0:
                tpr_rates[g] = 0.0
            else:
                tpr_rates[g] = self.preds[mask][actual_pos].mean()
        groups_list = list(tpr_rates.keys())
        if len(groups_list) < 2:
            return 0.0, tpr_rates
        eod = tpr_rates[groups_list[0]] - tpr_rates[groups_list[1]]
        return round(float(eod), 4), tpr_rates

    def group_accuracy(self):
        unique_groups = np.unique(self.groups)
        acc = {}
        for g in unique_groups:
            mask = self.groups == g
            acc[g] = round(accuracy_score(self.labels[mask], self.preds[mask]), 4)
        return acc

    def most_affected_group(self, group_rates):
        return min(group_rates, key=group_rates.get)

    def overall_bias_score(self, spd, eod):
        return round(min(1.0, (abs(spd) + abs(eod)) / 2), 4)


class DriftDetector:
    @staticmethod
    def psi(expected, actual, buckets=10):
        def safe_pct(arr, bins):
            counts, _ = np.histogram(arr, bins=bins)
            pct = counts / len(arr)
            return np.where(pct == 0, 1e-6, pct)
        breakpoints = np.unique(np.percentile(expected, np.linspace(0, 100, buckets + 1)))
        exp_pct = safe_pct(expected, breakpoints)
        act_pct = safe_pct(actual, breakpoints)
        min_len = min(len(exp_pct), len(act_pct))
        exp_pct, act_pct = exp_pct[:min_len], act_pct[:min_len]
        return round(float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))), 4)

    @staticmethod
    def kl_divergence(p, q, bins=10):
        all_vals = np.concatenate([p, q])
        bin_edges = np.linspace(all_vals.min(), all_vals.max(), bins + 1)
        def to_dist(arr):
            counts, _ = np.histogram(arr, bins=bin_edges)
            dist = counts / counts.sum()
            return np.where(dist == 0, 1e-10, dist)
        p_dist, q_dist = to_dist(p), to_dist(q)
        return round(float(np.sum(p_dist * np.log(p_dist / q_dist))), 4)

    @staticmethod
    def track_bias_over_time(bias_history):
        if len(bias_history) < 2:
            return {"trend": "stable", "scores": bias_history}
        scores = np.array(bias_history)
        slope = np.polyfit(range(len(scores)), scores, 1)[0]
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"
        return {
            "trend": trend,
            "slope": round(float(slope), 4),
            "mean_bias": round(float(scores.mean()), 4),
            "scores": bias_history,
        }


def build_output(bias_score, affected_group, trend, psi_score=0.0, kl_divergence=0.0, extras=None):
    """Returns standardized JSON matching BiasMetrics schema exactly."""
    output = {
        "bias_score": bias_score,
        "affected_group": str(affected_group),
        "trend": trend,
        "psi_score": psi_score,
        "kl_divergence": kl_divergence,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if extras:
        output["extras"] = extras
    return output


def run_bias_pipeline(df, target_col, sensitive_col, model_type="logistic_regression", bias_history=None):
    """Full end-to-end bias pipeline. Trains model, detects bias, saves artifacts."""
    preparator = DataPreparator()
    X_train, X_test, y_train, y_test, X_test_raw = preparator.prepare(df, target_col, [sensitive_col])

    builder = ModelBuilder(model_type=model_type)
    builder.train(X_train, y_train)
    predictions = builder.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"      Overall Accuracy: {accuracy:.2%}")

    # Step 3: Bias Detection
    print("[3/5] Running bias detection...")
    if sensitive_col in preparator.label_encoders:
        sensitive_values = preparator.label_encoders[sensitive_col].inverse_transform(
            X_test_raw[sensitive_col].values.astype(int)
        )
    else:
        sensitive_values = X_test_raw[sensitive_col].values
    detector = BiasDetector(predictions, y_test, sensitive_values)

    spd, group_rates = detector.statistical_parity_difference()
    eod, tpr_rates = detector.equal_opportunity_difference()
    group_acc = detector.group_accuracy()
    bias_score = detector.overall_bias_score(spd, eod)
    affected_group = detector.most_affected_group(group_rates)

    probas = builder.predict_proba(X_test)
    past_probas = np.clip(probas + np.random.normal(0, 0.05, probas.shape), 0, 1)
    psi_score = DriftDetector.psi(past_probas, probas)

    unique_groups = np.unique(sensitive_values)
    kl_score = 0.0
    if len(unique_groups) >= 2:
        g1_mask = sensitive_values == unique_groups[0]
        g2_mask = sensitive_values == unique_groups[1]
        kl_score = DriftDetector.kl_divergence(probas[g1_mask], probas[g2_mask])

    history = bias_history or [bias_score]
    time_analysis = DriftDetector.track_bias_over_time(history)
    trend = time_analysis["trend"]

    # Save model artifacts for predictor.py to load
    os.makedirs("output", exist_ok=True)
    joblib.dump(builder.model, "output/model.joblib")
    joblib.dump(preparator.scaler, "output/scaler.joblib")
    joblib.dump(preparator.label_encoders, "output/encoders.joblib")

    return build_output(
        bias_score=bias_score,
        affected_group=str(affected_group).lower(),
        trend=trend,
        psi_score=psi_score,
        kl_divergence=kl_score,
        extras={
            "statistical_parity_difference": spd,
            "equal_opportunity_difference": eod,
            "group_positive_rates": {str(k): round(float(v), 4) for k, v in group_rates.items()},
            "group_accuracy": {str(k): v for k, v in group_acc.items()},
            "overall_accuracy": round(accuracy, 4),
            "feature_importance": builder.feature_importance(X_train.columns.tolist()),
        }
    )


if __name__ == "__main__":
    # Demo run with synthetic data matching VeriShift schema fields
    np.random.seed(42)
    n = 1000
    df = pd.DataFrame({
        "age": np.random.randint(22, 60, n),
        "income": np.random.uniform(20000, 120000, n),
        "gender": np.random.choice(["male", "female"], n, p=[0.6, 0.4]),
        "education": np.random.choice(["high_school", "bachelors", "masters", "phd"], n),
        "employment_status": np.random.choice(["employed", "unemployed", "self_employed"], n),
        "approved": None
    })
    df["approved"] = (
        (df["income"] > 50000) &
        (df["age"] > 25) &
        ((df["gender"] == "male") | (np.random.rand(n) > 0.4))
    ).astype(int)

    result = run_bias_pipeline(df=df, target_col="approved", sensitive_col="gender")
    print(json.dumps({k: result[k] for k in ["bias_score", "affected_group", "trend", "psi_score", "kl_divergence", "timestamp"]}, indent=2))
    print("Model artifacts saved to output/")
