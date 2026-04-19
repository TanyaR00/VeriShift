"""
train.py — Run this ONCE before starting the backend.
Trains the bias detection model on synthetic data and saves artifacts to output/
Replace synthetic data with real dataset (adult_income_dataset.csv) when available.
"""

import numpy as np
import pandas as pd
from bias_intelligence import run_bias_pipeline

if __name__ == "__main__":
    print("Training VeriShift bias detection model...")
    np.random.seed(42)
    n = 2000

    df = pd.DataFrame({
        "age": np.random.randint(22, 60, n),
        "income": np.random.uniform(20000, 120000, n),
        "gender": np.random.choice(["male", "female"], n, p=[0.6, 0.4]),
        "education": np.random.choice(["high_school", "bachelors", "masters", "phd"], n),
        "employment_status": np.random.choice(["employed", "unemployed", "self_employed"], n),
        "approved": None
    })

    # Intentional gender bias — mirrors real-world loan/hiring discrimination
    # TODO: replace synthetic data with adult_income_dataset.csv
    df["approved"] = (
        (df["income"] > 50000) &
        (df["age"] > 25) &
        ((df["gender"] == "male") | (np.random.rand(n) > 0.4))
    ).astype(int)

    result = run_bias_pipeline(
        df=df,
        target_col="approved",
        sensitive_col="gender",
        model_type="logistic_regression",
        bias_history=[0.18, 0.22, 0.25, 0.28, 0.30]
    )

    print(f"\nModel trained successfully!")
    print(f"Bias Score: {result['bias_score']}")
    print(f"Affected Group: {result['affected_group']}")
    print(f"Trend: {result['trend']}")
    print(f"\nArtifacts saved to output/")
    print("You can now start the backend: uvicorn main:app --reload")
