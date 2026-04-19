"""
preprocessing.py
================
Loads, cleans, encodes and splits the Adult Income dataset.
Sensitive attribute: sex (Male / Female)

Outputs:
  - clean_dataset.csv
  - X_train, X_test, y_train, y_test (returned as DataFrames)
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ── Column names for raw Adult Income dataset ──────────────────────────────
COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "sex",
    "capital_gain", "capital_loss", "hours_per_week", "native_country", "income"
]

CATEGORICAL_COLS = [
    "workclass", "education", "marital_status", "occupation",
    "relationship", "race", "native_country"
]

# sex is kept readable for bias analysis — encoded separately at model stage
SENSITIVE_COL = "sex"
TARGET_COL    = "income"

# Drop fnlwgt (sampling weight — not a real feature)
DROP_COLS = ["fnlwgt"]


def load_dataset(path: str) -> pd.DataFrame:
    """
    Load dataset from CSV.
    Handles both:
      - Raw UCI format (no header, space-padded values)
      - Pre-saved CSV with header
    """
    try:
        df = pd.read_csv(path, header=0)
        # If columns look like real names, use as-is
        if df.columns.tolist() == COLUMNS or "age" in df.columns:
            pass
        else:
            raise ValueError("unexpected header")
    except Exception:
        # Fall back to raw UCI format
        df = pd.read_csv(path, names=COLUMNS, skipinitialspace=True, na_values="?")

    # Strip whitespace from string columns
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()

    # Clean income labels  (">50K." → ">50K")
    if TARGET_COL in df.columns:
        df[TARGET_COL] = df[TARGET_COL].str.replace(".", "", regex=False)

    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing values: mode for categoricals, median for numerics."""
    df = df.copy()
    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode()[0])
    return df


def encode_features(df: pd.DataFrame, encoders: dict = None, fit: bool = True):
    """
    Label-encode categorical columns.
    Pass encoders dict to reuse fitted encoders at inference time.

    Returns: (encoded_df, encoders_dict)
    """
    df = df.copy()
    if encoders is None:
        encoders = {}

    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            continue
        if fit:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            le = encoders[col]
            # Handle unseen labels gracefully
            known = set(le.classes_)
            df[col] = df[col].apply(lambda x: x if x in known else le.classes_[0])
            df[col] = le.transform(df[col].astype(str))

    # Encode sensitive col as numeric (Male=1, Female=0) — kept separate
    if SENSITIVE_COL in df.columns:
        df["sex_encoded"] = (df[SENSITIVE_COL] == "Male").astype(int)

    # Encode target
    if TARGET_COL in df.columns:
        df[TARGET_COL] = (df[TARGET_COL] == ">50K").astype(int)

    return df, encoders


def preprocess(raw_path: str = "adult_raw.csv",
               output_path: str = "clean_dataset.csv",
               test_size: float = 0.2,
               random_state: int = 42):
    """
    Full preprocessing pipeline.

    Returns:
        X_train, X_test, y_train, y_test,
        X_test_raw (unencoded, for bias group analysis),
        encoders (dict, save alongside model)
    """
    print("[preprocessing] Loading dataset...")
    df = load_dataset(raw_path)
    print(f"  Loaded: {df.shape[0]} rows, {df.shape[1]} cols")

    print("[preprocessing] Handling missing values...")
    df = handle_missing(df)
    missing_after = df.isnull().sum().sum()
    print(f"  Missing values remaining: {missing_after}")

    # Drop irrelevant columns
    df = df.drop(columns=[c for c in DROP_COLS if c in df.columns])

    # Save readable version for bias analysis (before encoding)
    df_readable = df.copy()

    print("[preprocessing] Encoding features...")
    df_encoded, encoders = encode_features(df)

    # Feature matrix — keep sex_encoded in X for model, raw sex for bias detection
    feature_cols = [c for c in df_encoded.columns
                    if c not in [TARGET_COL, SENSITIVE_COL]]
    X = df_encoded[feature_cols]
    y = df_encoded[TARGET_COL]

    print("[preprocessing] Splitting train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Keep raw (unencoded) test rows aligned for bias group analysis
    X_test_raw = df_readable.loc[X_test.index].reset_index(drop=True)
    X_train    = X_train.reset_index(drop=True)
    X_test     = X_test.reset_index(drop=True)
    y_train    = y_train.reset_index(drop=True)
    y_test     = y_test.reset_index(drop=True)

    # Save clean dataset
    clean_df = X_train.copy()
    clean_df[TARGET_COL] = y_train
    clean_df.to_csv(output_path, index=False)
    print(f"[preprocessing] Saved → {output_path}")

    # Save encoders
    with open("encoders.pkl", "wb") as f:
        pickle.dump(encoders, f)
    print("[preprocessing] Saved → encoders.pkl")

    print(f"\n  Train size : {len(X_train)}")
    print(f"  Test size  : {len(X_test)}")
    print(f"  Features   : {X_train.shape[1]}")
    print(f"  Target distribution (test):")
    print(f"    >50K  : {y_test.sum()} ({y_test.mean():.1%})")
    print(f"    <=50K : {(1-y_test).sum()} ({(1-y_test).mean():.1%})")

    return X_train, X_test, y_train, y_test, X_test_raw, encoders


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, X_test_raw, encoders = preprocess()
    print("\n[preprocessing] Done ✅")
