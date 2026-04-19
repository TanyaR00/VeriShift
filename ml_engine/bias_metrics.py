"""
bias_metrics.py
===============
Core bias detection module.

Functions:
  compute_bias_metrics(df)  →  dict with SPD, EOD, group accuracy
  compute_bias_score(...)   →  { bias_score, risk, affected_group }
"""

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix


def _group_mask(df: pd.DataFrame, sensitive_col: str, group_val):
    """Return boolean mask for a group."""
    return df[sensitive_col] == group_val


def statistical_parity_difference(y_pred: np.ndarray,
                                   groups: np.ndarray) -> dict:
    """
    SPD = P(Ŷ=1 | Male) - P(Ŷ=1 | Female)

    Ideal = 0
    Negative → females receive fewer positive predictions
    """
    unique = np.unique(groups)
    rates = {}
    for g in unique:
        mask = groups == g
        rates[str(g)] = float(round(y_pred[mask].mean(), 4))

    groups_list = list(rates.keys())
    if len(groups_list) < 2:
        spd = 0.0
    else:
        # SPD = privileged_rate - unprivileged_rate
        # Male assumed privileged
        male_rate   = rates.get("Male",   rates.get("1", 0.0))
        female_rate = rates.get("Female", rates.get("0", 0.0))
        spd = round(male_rate - female_rate, 4)

    return {
        "spd": spd,
        "group_positive_rates": rates
    }


def equal_opportunity_difference(y_true: np.ndarray,
                                  y_pred: np.ndarray,
                                  groups: np.ndarray) -> dict:
    """
    EOD = TPR(Male) - TPR(Female)

    TPR = True Positive Rate (recall among actual positives)
    Ideal = 0
    """
    unique = np.unique(groups)
    tprs = {}
    for g in unique:
        mask = groups == g
        actual_pos = y_true[mask] == 1
        if actual_pos.sum() == 0:
            tprs[str(g)] = 0.0
        else:
            tprs[str(g)] = float(round(y_pred[mask][actual_pos].mean(), 4))

    male_tpr   = tprs.get("Male",   tprs.get("1", 0.0))
    female_tpr = tprs.get("Female", tprs.get("0", 0.0))
    eod = round(male_tpr - female_tpr, 4)

    return {
        "eod": eod,
        "group_tpr": tprs
    }


def group_accuracy(y_true: np.ndarray,
                   y_pred: np.ndarray,
                   groups: np.ndarray) -> dict:
    """
    Accuracy computed separately for each group.
    Reveals if model performs differently across groups.
    """
    unique = np.unique(groups)
    acc = {}
    for g in unique:
        mask = groups == g
        acc[str(g)] = round(float(accuracy_score(y_true[mask], y_pred[mask])), 4)
    return acc


def compute_bias_metrics(df: pd.DataFrame,
                          sensitive_col: str = "sex",
                          target_col: str = "income",
                          pred_col: str = "prediction") -> dict:
    """
    Main bias detection function — call this from your API.

    Args:
        df: DataFrame with columns [sensitive_col, target_col, pred_col]
        sensitive_col: Column with group labels (e.g. 'sex')
        target_col: Actual labels (0/1)
        pred_col: Model predictions (0/1)

    Returns:
        {
            "statistical_parity": float,
            "equal_opportunity": float,
            "group_accuracy": { "Male": float, "Female": float },
            "group_positive_rates": { "Male": float, "Female": float },
            "group_tpr": { "Male": float, "Female": float }
        }
    """
    y_true = df[target_col].values.astype(int)
    y_pred = df[pred_col].values.astype(int)
    groups = df[sensitive_col].values

    spd_result = statistical_parity_difference(y_pred, groups)
    eod_result = equal_opportunity_difference(y_true, y_pred, groups)
    acc_result = group_accuracy(y_true, y_pred, groups)

    return {
        "statistical_parity": spd_result["spd"],
        "equal_opportunity": eod_result["eod"],
        "group_accuracy": acc_result,
        "group_positive_rates": spd_result["group_positive_rates"],
        "group_tpr": eod_result["group_tpr"]
    }


def compute_bias_score(statistical_parity: float,
                        equal_opportunity: float,
                        psi: float = 0.0,
                        group_accuracy: dict = None) -> dict:
    """
    Combines bias metrics into a single actionable score.

    Formula: bias_score = (|SPD| + |EOD| + PSI) / 3
    Risk:    LOW < 0.1 ≤ MEDIUM < 0.2 ≤ HIGH

    Returns:
        { "bias_score": float, "risk": str, "affected_group": str }
    """
    spd = abs(statistical_parity)
    eod = abs(equal_opportunity)
    score = round((spd + eod + abs(psi)) / 3, 4)

    if score < 0.1:
        risk = "LOW"
    elif score < 0.2:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    # Affected group = whichever has the lower positive rate
    affected_group = "female"
    if group_accuracy:
        affected_group = min(group_accuracy, key=group_accuracy.get).lower()

    return {
        "bias_score": score,
        "risk": risk,
        "affected_group": affected_group
    }


if __name__ == "__main__":
    # Quick smoke test
    np.random.seed(0)
    n = 500
    test_df = pd.DataFrame({
        "sex":        np.random.choice(["Male", "Female"], n, p=[0.6, 0.4]),
        "income":     np.random.randint(0, 2, n),
        "prediction": np.random.randint(0, 2, n),
    })
    # Inject bias: females predicted positive less often
    test_df.loc[test_df["sex"] == "Female", "prediction"] = \
        np.random.choice([0, 1], (test_df["sex"] == "Female").sum(), p=[0.75, 0.25])

    metrics = compute_bias_metrics(test_df)
    print("Bias Metrics:", metrics)

    score = compute_bias_score(
        metrics["statistical_parity"],
        metrics["equal_opportunity"]
    )
    print("Bias Score:", score)
