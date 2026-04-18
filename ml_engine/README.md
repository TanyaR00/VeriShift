# 🔍 Unbiased AI — Bias Intelligence Layer

Afifa's ML module for the **Unbiased AI Decision System**.  
Detects and tracks bias in automated decisions (hiring, loans, healthcare).

---

## 📁 Project Structure

```
unbiased-ai/
├── bias_engine/
│   └── bias_intelligence.py   ← Main ML module (ALL steps here)
├── output/
│   └── bias_report.json       ← Generated after running
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

```bash
pip install -r requirements.txt
```

---

## ▶️ Run

```bash
cd bias_engine
python bias_intelligence.py
```

---

## 📦 What It Does

| Step | What |
|------|------|
| 1️⃣ Dataset Prep | Cleans missing values, encodes features |
| 2️⃣ Model Building | Logistic Regression or Random Forest |
| 3️⃣ Bias Detection | SPD, EOD, Group Accuracy |
| 4️⃣ Twin Validation | Counterfactual fairness test |
| 5️⃣ Drift Detection | PSI, KL Divergence, Time Trends |
| 6️⃣ JSON Output | Backend-ready metrics |

---

## 🔗 Backend Output Format

```json
{
  "bias_score": 0.32,
  "affected_group": "female",
  "trend": "increasing"
}
```

---

## 🧪 Using Your Own Data

```python
from bias_engine.bias_intelligence import run_bias_pipeline
import pandas as pd

df = pd.read_csv("your_data.csv")
result = run_bias_pipeline(
    df=df,
    target_col="outcome_column",
    sensitive_col="gender",         # or "race", "age_group", etc.
    model_type="logistic_regression"
)
print(result)
```
