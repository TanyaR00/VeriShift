"""
Bias Intelligence Layer
========================
Unbiased AI Decision System — Afifa's ML Module
Detects and tracks bias in automated decision-making models.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
import json
import warnings
warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────
# STEP 1: DATASET PREPARATION
# ─────────────────────────────────────────────

class DataPreparator:
    """Cleans, encodes, and prepares dataset for bias analysis."""

    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently."""
        df = df.copy()
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
        return df

    def encode(self, df: pd.DataFrame, target_col: str, sensitive_cols: list) -> pd.DataFrame:
        """Label encode categoricals, scale numerics. Keep sensitive cols readable."""
        df = df.copy()
        for col in df.select_dtypes(include="object").columns:
            if col != target_col:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        return df

    def prepare(self, df: pd.DataFrame, target_col: str, sensitive_cols: list):
        """Full pipeline: clean → encode → split."""
        df = self.clean(df)
        df = self.encode(df, target_col, sensitive_cols)

        X = df.drop(columns=[target_col])
        y = df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features (keep sensitive col indices for analysis)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return (
            pd.DataFrame(X_train_scaled, columns=X.columns),
            pd.DataFrame(X_test_scaled, columns=X.columns),
            y_train.reset_index(drop=True),
            y_test.reset_index(drop=True),
            X_test.reset_index(drop=True),   # unscaled test for group analysis
        )


# ─────────────────────────────────────────────
# STEP 2: MODEL BUILDING (Explainable)
# ─────────────────────────────────────────────

class ModelBuilder:
    """Builds simple, explainable models."""

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
        """Return top features for explainability."""
        if self.model_type == "random_forest":
            importances = self.model.feature_importances_
        else:
            importances = np.abs(self.model.coef_[0])
        return dict(sorted(
            zip(feature_names, importances),
            key=lambda x: x[1], reverse=True
        ))


# ─────────────────────────────────────────────
# STEP 3: BIAS DETECTION (CORE)
# ─────────────────────────────────────────────

class BiasDetector:
    """
    Detects bias using:
    - Statistical Parity Difference
    - Equal Opportunity Difference
    - Group-wise Accuracy
    """

    def __init__(self, predictions, labels, sensitive_col_values):
        self.preds = np.array(predictions)
        self.labels = np.array(labels)
        self.groups = sensitive_col_values  # e.g., array of "male"/"female"

    def statistical_parity_difference(self):
        """
        SPD = P(Ŷ=1 | A=privileged) - P(Ŷ=1 | A=unprivileged)
        Ideal = 0. Negative = unprivileged group gets fewer positive outcomes.
        """
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
        """
        EOD = TPR(privileged) - TPR(unprivileged)
        Measures if both groups have equal True Positive Rates.
        """
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
        """Per-group accuracy breakdown."""
        unique_groups = np.unique(self.groups)
        acc = {}
        for g in unique_groups:
            mask = self.groups == g
            acc[g] = round(accuracy_score(self.labels[mask], self.preds[mask]), 4)
        return acc

    def most_affected_group(self, group_rates):
        """Returns the group with the lowest positive prediction rate."""
        return min(group_rates, key=group_rates.get)

    def overall_bias_score(self, spd, eod):
        """Composite bias score (0 = fair, 1 = maximally biased)."""
        return round(min(1.0, (abs(spd) + abs(eod)) / 2), 4)


# ─────────────────────────────────────────────
# STEP 4: TWIN VALIDATION
# ─────────────────────────────────────────────

class TwinValidator:
    """
    Counterfactual / Twin test:
    Only 1 sensitive feature changes — everything else stays the same.
    Checks if prediction flips → bias detected.
    """

    def __init__(self, model, scaler, feature_names):
        self.model = model
        self.scaler = scaler
        self.feature_names = feature_names

    def validate(self, sample: dict, sensitive_feature: str, new_value):
        """
        Creates a 'twin' of the sample with only the sensitive feature changed.
        Returns both predictions and flags if they differ.
        """
        original = pd.DataFrame([sample])
        twin = original.copy()
        twin[sensitive_feature] = new_value

        # Must be realistic — only 1 feature changed
        changed_cols = [c for c in original.columns if not original[c].equals(twin[c])]
        assert len(changed_cols) == 1, "Only 1 feature should change in twin test!"

        orig_scaled = self.scaler.transform(original)
        twin_scaled = self.scaler.transform(twin)

        orig_pred = self.model.predict(orig_scaled)[0]
        twin_pred = self.model.predict(twin_scaled)[0]

        return {
            "original_prediction": int(orig_pred),
            "twin_prediction": int(twin_pred),
            "bias_detected": orig_pred != twin_pred,
            "changed_feature": sensitive_feature,
            "original_value": sample[sensitive_feature],
            "twin_value": new_value,
        }


# ─────────────────────────────────────────────
# STEP 5: DRIFT DETECTION (LIVE SYSTEM)
# ─────────────────────────────────────────────

class DriftDetector:
    """
    Detects distribution shifts using:
    - PSI (Population Stability Index)
    - KL Divergence
    - Time-based bias tracking
    """

    @staticmethod
    def psi(expected: np.ndarray, actual: np.ndarray, buckets: int = 10) -> float:
        """
        PSI < 0.1  → No significant change
        PSI 0.1–0.2 → Moderate change
        PSI > 0.2  → Significant drift
        """
        def safe_pct(arr, bins):
            counts, _ = np.histogram(arr, bins=bins)
            pct = counts / len(arr)
            pct = np.where(pct == 0, 1e-6, pct)
            return pct

        breakpoints = np.percentile(expected, np.linspace(0, 100, buckets + 1))
        breakpoints = np.unique(breakpoints)

        exp_pct = safe_pct(expected, breakpoints)
        act_pct = safe_pct(actual, breakpoints)

        min_len = min(len(exp_pct), len(act_pct))
        exp_pct, act_pct = exp_pct[:min_len], act_pct[:min_len]

        psi_value = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
        return round(float(psi_value), 4)

    @staticmethod
    def kl_divergence(p: np.ndarray, q: np.ndarray, bins: int = 10) -> float:
        """
        KL Divergence between two group distributions.
        Lower = more similar distributions.
        """
        def to_dist(arr, bin_edges):
            counts, _ = np.histogram(arr, bins=bin_edges)
            dist = counts / counts.sum()
            return np.where(dist == 0, 1e-10, dist)

        all_vals = np.concatenate([p, q])
        bin_edges = np.linspace(all_vals.min(), all_vals.max(), bins + 1)

        p_dist = to_dist(p, bin_edges)
        q_dist = to_dist(q, bin_edges)

        kl = np.sum(p_dist * np.log(p_dist / q_dist))
        return round(float(kl), 4)

    @staticmethod
    def track_bias_over_time(bias_history: list) -> dict:
        """
        Analyzes trend from a list of bias scores over time.
        Returns trend direction and summary stats.
        """
        if len(bias_history) < 2:
            return {"trend": "insufficient_data", "scores": bias_history}

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
            "max_bias": round(float(scores.max()), 4),
            "min_bias": round(float(scores.min()), 4),
            "scores": bias_history,
        }


# ─────────────────────────────────────────────
# STEP 6: OUTPUT — BACKEND-READY JSON
# ─────────────────────────────────────────────

def build_output(bias_score, affected_group, trend, extras=None) -> dict:
    """Returns the standardized JSON output for backend integration."""
    output = {
        "bias_score": bias_score,
        "affected_group": affected_group,
        "trend": trend,
    }
    if extras:
        output.update(extras)
    return output


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def run_bias_pipeline(df: pd.DataFrame, target_col: str, sensitive_col: str,
                       model_type="logistic_regression", bias_history=None):
    """
    Full end-to-end Bias Intelligence Pipeline.

    Args:
        df: Input DataFrame
        target_col: Name of the label/outcome column
        sensitive_col: Column to analyze for bias (e.g., 'gender', 'race')
        model_type: 'logistic_regression' or 'random_forest'
        bias_history: Optional list of past bias scores for trend tracking

    Returns:
        dict with all bias metrics + backend-ready output
    """
    print("=" * 55)
    print("  🔍 BIAS INTELLIGENCE LAYER — Starting Pipeline")
    print("=" * 55)

    # Step 1: Prepare Data
    print("\n[1/5] Preparing dataset...")
    preparator = DataPreparator()
    X_train, X_test, y_train, y_test, X_test_raw = preparator.prepare(
        df, target_col, [sensitive_col]
    )

    # Step 2: Build Model
    print(f"[2/5] Building {model_type} model...")
    builder = ModelBuilder(model_type=model_type)
    builder.train(X_train, y_train)
    predictions = builder.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"      Overall Accuracy: {accuracy:.2%}")

    # Step 3: Bias Detection
    print("[3/5] Running bias detection...")
    sensitive_values = X_test_raw[sensitive_col].values
    if set(sensitive_values).issubset({0, 1}):
        sensitive_values = np.where(sensitive_values == 1, "Male", "Female")

    detector = BiasDetector(predictions, y_test, sensitive_values)

    spd, group_rates = detector.statistical_parity_difference()
    eod, tpr_rates = detector.equal_opportunity_difference()
    group_acc = detector.group_accuracy()
    bias_score = detector.overall_bias_score(spd, eod)
    affected_group = detector.most_affected_group(group_rates)

    print(f"      Statistical Parity Difference : {spd}")
    print(f"      Equal Opportunity Difference  : {eod}")
    print(f"      Bias Score                    : {bias_score}")
    print(f"      Affected Group                : {affected_group}")

    # Step 5: Drift Detection
    print("[4/5] Checking drift...")
    probas = builder.predict_proba(X_test)
    # Simulate past predictions for PSI demo
    past_probas = probas + np.random.normal(0, 0.05, probas.shape)
    past_probas = np.clip(past_probas, 0, 1)

    psi_score = DriftDetector.psi(past_probas, probas)
    drift_detector = DriftDetector()

    # KL divergence between groups
    unique_groups = np.unique(sensitive_values)
    kl_score = 0.0
    if len(unique_groups) >= 2:
        g1_mask = sensitive_values == unique_groups[0]
        g2_mask = sensitive_values == unique_groups[1]
        kl_score = DriftDetector.kl_divergence(probas[g1_mask], probas[g2_mask])

    # Time tracking
    history = bias_history or [bias_score]
    time_analysis = DriftDetector.track_bias_over_time(history)
    trend = time_analysis["trend"]

    print(f"      PSI Score     : {psi_score} {'⚠️ DRIFT' if psi_score > 0.2 else '✅ Stable'}")
    print(f"      KL Divergence : {kl_score}")
    print(f"      Bias Trend    : {trend}")

    # Step 6: Final Output
    print("[5/5] Building output...")
    output = build_output(
        bias_score=bias_score,
        affected_group=str(affected_group),
        trend=trend,
        extras={
            "statistical_parity_difference": spd,
            "equal_opportunity_difference": eod,
            "group_positive_rates": {str(k): round(float(v), 4) for k, v in group_rates.items()},
            "group_true_positive_rates": {str(k): round(float(v), 4) for k, v in tpr_rates.items()},
            "group_accuracy": {str(k): v for k, v in group_acc.items()},
            "overall_accuracy": round(accuracy, 4),
            "psi_score": psi_score,
            "kl_divergence": kl_score,
            "drift_status": "drift_detected" if psi_score > 0.2 else "stable",
            "time_analysis": time_analysis,
            "feature_importance": builder.feature_importance(X_train.columns.tolist()),
        }
    )

    print("\n" + "=" * 55)
    print("  ✅ Pipeline Complete — Output Ready for Backend")
    print("=" * 55)
    print(json.dumps({
        "bias_score": output["bias_score"],
        "affected_group": output["affected_group"],
        "trend": output["trend"]
    }, indent=2))

    return output


# ─────────────────────────────────────────────
# DEMO RUN (with synthetic data)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    np.random.seed(42)
    n = 1000

    # Synthetic hiring dataset
    df = pd.DataFrame({
        "age": np.random.randint(22, 60, n),
        "education_years": np.random.randint(10, 20, n),
        "experience_years": np.random.randint(0, 20, n),
        "test_score": np.random.normal(70, 15, n).clip(0, 100),
        "gender": np.random.choice(["male", "female"], n, p=[0.6, 0.4]),
        "race": np.random.choice(["group_A", "group_B", "group_C"], n),
        "hired": None
    })

    # Introduce intentional gender bias
    df["hired"] = (
        (df["test_score"] > 65) &
        (df["experience_years"] > 3) &
        ((df["gender"] == "male") | (np.random.rand(n) > 0.4))
    ).astype(int)

    # Introduce some missing values
    df.loc[np.random.choice(n, 50, replace=False), "test_score"] = np.nan
    df.loc[np.random.choice(n, 30, replace=False), "experience_years"] = np.nan

    # Simulate historical bias scores for trend
    historical_bias = [0.18, 0.22, 0.25, 0.28, 0.30]

    result = run_bias_pipeline(
        df=df,
        target_col="hired",
        sensitive_col="gender",
        model_type="logistic_regression",
        bias_history=historical_bias
    )

    # Save output
    with open("output/bias_report.json", "w") as f:
        # Convert numpy types for JSON serialization
        def convert(obj):
            if isinstance(obj, (np.integer,)): return int(obj)
            if isinstance(obj, (np.floating,)): return float(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            return obj
        json.dump(result, f, indent=2, default=convert)

    print("\n📁 Full report saved to output/bias_report.json")
