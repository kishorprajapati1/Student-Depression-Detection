"""
Web Assets Generator
====================
Compiles verified survey records, ML predictions, and model performance
metrics into a standalone, browser-ready JavaScript payload for the
portfolio website dashboard.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "Project-01_Student_Depression_Analysis" / "data" / "processed"
SCORED_CSV = PROCESSED_DIR / "student_depression_ml_scored.csv"
FEATURE_CSV = PROCESSED_DIR / "ml_feature_importance.csv"
METRICS_JSON = PROCESSED_DIR / "ml_model_metrics.json"

DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_JS = DOCS_DIR / "data.js"


def build_web_data() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(SCORED_CSV)
    feat_df = pd.read_csv(FEATURE_CSV)
    with open(METRICS_JSON, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    # Convert dataframe into clean list of dicts
    records = []
    for _, row in df.iterrows():
        records.append({
            "id": str(row["Student_ID"]),
            "gender": str(row["Gender"]),
            "age": int(row["Age"]),
            "family": str(row["Family_background"]),
            "relationship": str(row["Relationship_status"]),
            "marital": str(row["Marital_status"]),
            "living": str(row["Living_style"]),
            "semester": int(row["Current_semester"]),
            "cgpa": float(row["CGPA"]),
            "friends": str(row["friend_circle"]),
            "health": str(row["Health_condition"]),
            "cost": float(row["Cost_without_study"]),
            "division": str(row["Home_division"]),
            "depression": int(row["Depression_Flag"]),
            "depression_label": str(row["Depression"]),
            "predicted": int(row["Predicted_Depression"]),
            "predicted_label": str(row["Predicted_Depression_Label"]),
            "risk_score": float(row["Depression_Risk_Score"]),
            "risk_tier": str(row["Risk_Tier"]),
            "risk_tier_sort": int(row["Risk_Tier_Sort"]),
            "priority": str(row["Intervention_Priority"]),
            "outcome": str(row["Prediction_Outcome"]),
        })

    features = []
    for _, row in feat_df.iterrows():
        features.append({
            "variable": str(row["Feature_Variable"]).replace("_", " "),
            "category": str(row["Feature_Category"]),
            "weight": float(row["Importance_Weight"]),
            "rank": int(row["Importance_Rank"]),
        })

    js_content = f"""// Auto-generated verified dataset payload for Kishor Prajapati Portfolio
// Generated from verified SQLite and Scikit-Learn ML pipeline
// Total Records: {len(records)}

const STUDENT_RECORDS = {json.dumps(records, separators=(',', ':'))};

const FEATURE_IMPORTANCES = {json.dumps(features, separators=(',', ':'))};

const MODEL_METRICS = {json.dumps(metrics, separators=(',', ':'))};
"""

    with open(OUTPUT_JS, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"Generated {OUTPUT_JS} ({len(records)} records, {len(features)} features)")


if __name__ == "__main__":
    build_web_data()
