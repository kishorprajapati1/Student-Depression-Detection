"""
Student Depression Analysis - Machine Learning Predictive Pipeline
===================================================================
Purpose:
  Trains, validates, and deploys predictive classification models (Logistic Regression
  and Random Forest) to score depression risk probabilities for university students.
  
Outputs Generated:
  1. data/processed/student_depression_ml_scored.csv (Enriched Fact table with risk scores & tiers)
  2. data/processed/ml_feature_importance.csv (Quantified driver weights for Power BI tornado visual)
  3. data/processed/ml_model_metrics.json (Cross-validation accuracy, precision, recall, F1, ROC-AUC)
  4. SQLite database updates: Populates Fact_Student_Assessment with ML scores and creates
     Dim_ML_Feature_Importance and Dim_ML_Model_Metrics tables.

Architectural Rationale:
  Descriptive analytics tell university leadership *what* happened in past surveys.
  This ML scoring pipeline transforms the Power BI dashboard into an early-warning system,
  assigning each student an actionable Risk Tier and Intervention Priority.
"""

from __future__ import annotations

import csv
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Repository Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
CLEANED_CSV_PATH = DATA_DIR / "student_depression_cleaned.csv"
SCORED_CSV_PATH = DATA_DIR / "student_depression_ml_scored.csv"
FEATURE_IMPORTANCE_PATH = DATA_DIR / "ml_feature_importance.csv"
METRICS_JSON_PATH = DATA_DIR / "ml_model_metrics.json"
DATABASE_PATH = DATA_DIR / "student_depression.db"

# Model Configuration
RANDOM_STATE = 42
CV_FOLDS = 5

NUMERICAL_FEATURES: List[str] = ["Age", "Current_semester", "CGPA", "Cost_without_study"]
CATEGORICAL_FEATURES: List[str] = [
    "Gender",
    "Family_background",
    "Relationship_status",
    "Marital_status",
    "Living_style",
    "friend_circle",
    "Health_condition",
    "Home_division",
]
TARGET_COLUMN = "Depression_Flag"


def assign_risk_tier(probability: float) -> Tuple[str, int, str]:
    """
    Categorizes depression probability into clinically actionable risk tiers.

    Returns:
        (Risk_Tier, Risk_Tier_Sort, Intervention_Priority)
    """
    if probability >= 0.85:
        return "Critical Risk", 4, "Immediate Clinical Referral"
    elif probability >= 0.60:
        return "High Risk", 3, "Counseling Center Outreach"
    elif probability >= 0.30:
        return "Moderate Risk", 2, "Academic Advisor Check-in"
    else:
        return "Low Risk", 1, "Routine Wellness Monitoring"


def evaluate_models(
    X: pd.DataFrame,
    y: pd.Series,
    preprocessor: ColumnTransformer,
) -> Tuple[str, Dict[str, Any], Any]:
    """
    Compares Logistic Regression and Random Forest using 5-fold Stratified Cross-Validation.
    Selects the model with highest F1 and ROC-AUC for deployment.
    """
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    candidates = {
        "Logistic_Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "Random_Forest": RandomForestClassifier(
            n_estimators=100, max_depth=6, min_samples_leaf=4, random_state=RANDOM_STATE
        ),
    }

    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    comparison_results: Dict[str, Dict[str, float]] = {}

    for name, estimator in candidates.items():
        from sklearn.pipeline import Pipeline
        pipeline = Pipeline([("prep", preprocessor), ("clf", estimator)])
        cv_scores = cross_validate(pipeline, X, y, cv=cv, scoring=scoring)
        comparison_results[name] = {
            "Accuracy": float(np.mean(cv_scores["test_accuracy"])),
            "Precision": float(np.mean(cv_scores["test_precision"])),
            "Recall": float(np.mean(cv_scores["test_recall"])),
            "F1_Score": float(np.mean(cv_scores["test_f1"])),
            "ROC_AUC": float(np.mean(cv_scores["test_roc_auc"])),
        }
        logging.info(
            "%s - F1: %.4f | ROC-AUC: %.4f | Accuracy: %.4f",
            name,
            comparison_results[name]["F1_Score"],
            comparison_results[name]["ROC_AUC"],
            comparison_results[name]["Accuracy"],
        )

    # Select best model based on F1-Score
    best_name = max(comparison_results, key=lambda k: comparison_results[k]["F1_Score"])
    best_estimator = candidates[best_name]
    logging.info("Selected Champion Model: %s", best_name)

    return best_name, comparison_results, best_estimator


def train_and_score_dataset(
    df: pd.DataFrame,
    best_estimator: Any,
    preprocessor: ColumnTransformer,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Trains champion model, generates out-of-fold calibrated probabilities,
    and extracts feature importance rankings.
    """
    from sklearn.pipeline import Pipeline
    pipeline = Pipeline([("prep", preprocessor), ("clf", best_estimator)])

    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET_COLUMN]

    # Generate cross-validated probability predictions (avoids data leakage in scoring)
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    predicted_probs = cross_val_predict(pipeline, X, y, cv=cv, method="predict_proba")[:, 1]
    predicted_binary = (predicted_probs >= 0.50).astype(int)

    # Fit pipeline on full dataset for final feature importance extraction
    pipeline.fit(X, y)

    # Enrich dataset with ML columns
    enriched_df = df.copy()
    enriched_df["Predicted_Depression"] = predicted_binary
    enriched_df["Predicted_Depression_Label"] = enriched_df["Predicted_Depression"].map({1: "Yes", 0: "No"})
    enriched_df["Depression_Risk_Score"] = np.round(predicted_probs, 4)

    tier_tuples = [assign_risk_tier(p) for p in predicted_probs]
    enriched_df["Risk_Tier"] = [t[0] for t in tier_tuples]
    enriched_df["Risk_Tier_Sort"] = [t[1] for t in tier_tuples]
    enriched_df["Intervention_Priority"] = [t[2] for t in tier_tuples]

    # Assign confusion matrix outcomes for diagnostic reporting
    outcomes = []
    for actual, pred in zip(y, predicted_binary):
        if actual == 1 and pred == 1:
            outcomes.append("True Positive")
        elif actual == 0 and pred == 0:
            outcomes.append("True Negative")
        elif actual == 0 and pred == 1:
            outcomes.append("False Positive")
        else:
            outcomes.append("False Negative")
    enriched_df["Prediction_Outcome"] = outcomes

    # Extract Feature Importances
    cat_feature_names = pipeline.named_steps["prep"].named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES)
    all_feature_names = NUMERICAL_FEATURES + list(cat_feature_names)

    if hasattr(pipeline.named_steps["clf"], "feature_importances_"):
        raw_weights = pipeline.named_steps["clf"].feature_importances_
    else:
        raw_weights = np.abs(pipeline.named_steps["clf"].coef_[0])

    # Categorize features for high-level Power BI slicing
    def categorize_feature(fname: str) -> str:
        if "Health_condition" in fname:
            return "Physical Health"
        elif any(k in fname for k in ["Relationship_status", "Marital_status", "friend_circle"]):
            return "Social & Relationship"
        elif any(k in fname for k in ["CGPA", "Current_semester"]):
            return "Academic Performance"
        elif any(k in fname for k in ["Cost_without_study", "Family_background"]):
            return "Financial Status"
        else:
            return "Demographic / Geographic"

    importance_df = pd.DataFrame({
        "Feature_Key": range(1, len(all_feature_names) + 1),
        "Feature_Variable": all_feature_names,
        "Feature_Category": [categorize_feature(f) for f in all_feature_names],
        "Importance_Weight": np.round(raw_weights, 4),
    })
    importance_df = importance_df.sort_values(by="Importance_Weight", ascending=False).reset_index(drop=True)
    importance_df["Importance_Rank"] = range(1, len(importance_df) + 1)
    importance_df["Feature_Key"] = range(1, len(importance_df) + 1)

    # Compute overall confusion matrix counts
    confusion_counts = pd.Series(outcomes).value_counts().to_dict()

    return enriched_df, importance_df, confusion_counts


def update_sqlite_database(
    scored_df: pd.DataFrame,
    importance_df: pd.DataFrame,
    metrics_summary: Dict[str, Any],
) -> None:
    """
    Updates the local SQLite database:
      1. Replaces Fact_Student_Assessment with ML-enriched metrics
      2. Creates and populates Dim_ML_Feature_Importance
      3. Creates and populates Dim_ML_Model_Metrics
    """
    if not DATABASE_PATH.exists():
        logging.error("SQLite database not found at %s. Run ETL pipeline first.", DATABASE_PATH)
        raise FileNotFoundError(f"Database not found at {DATABASE_PATH}")

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Update Fact_Student_Assessment with ML columns
        # First check if ML columns exist
        cursor.execute("PRAGMA table_info(Fact_Student_Assessment);")
        existing_cols = {row[1] for row in cursor.fetchall()}

        new_cols = [
            ("Predicted_Depression", "INTEGER"),
            ("Predicted_Depression_Label", "TEXT"),
            ("Depression_Risk_Score", "REAL"),
            ("Risk_Tier", "TEXT"),
            ("Risk_Tier_Sort", "INTEGER"),
            ("Intervention_Priority", "TEXT"),
            ("Prediction_Outcome", "TEXT"),
        ]

        for col_name, col_type in new_cols:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE Fact_Student_Assessment ADD COLUMN {col_name} {col_type};")

        # Update rows via batch update
        update_data = [
            (
                int(row["Predicted_Depression"]),
                str(row["Predicted_Depression_Label"]),
                float(row["Depression_Risk_Score"]),
                str(row["Risk_Tier"]),
                int(row["Risk_Tier_Sort"]),
                str(row["Intervention_Priority"]),
                str(row["Prediction_Outcome"]),
                str(row["Student_ID"]),
            )
            for _, row in scored_df.iterrows()
        ]

        cursor.executemany(
            """
            UPDATE Fact_Student_Assessment
            SET Predicted_Depression = ?,
                Predicted_Depression_Label = ?,
                Depression_Risk_Score = ?,
                Risk_Tier = ?,
                Risk_Tier_Sort = ?,
                Intervention_Priority = ?,
                Prediction_Outcome = ?
            WHERE Student_ID = ?;
            """,
            update_data,
        )

        # Create Dim_ML_Feature_Importance table
        cursor.execute("DROP TABLE IF EXISTS Dim_ML_Feature_Importance;")
        cursor.execute(
            """
            CREATE TABLE Dim_ML_Feature_Importance (
                Feature_Key INTEGER PRIMARY KEY,
                Feature_Variable TEXT NOT NULL,
                Feature_Category TEXT NOT NULL,
                Importance_Weight REAL NOT NULL,
                Importance_Rank INTEGER NOT NULL
            );
            """
        )

        cursor.executemany(
            """
            INSERT INTO Dim_ML_Feature_Importance (Feature_Key, Feature_Variable, Feature_Category, Importance_Weight, Importance_Rank)
            VALUES (?, ?, ?, ?, ?);
            """,
            [
                (
                    int(r["Feature_Key"]),
                    str(r["Feature_Variable"]),
                    str(r["Feature_Category"]),
                    float(r["Importance_Weight"]),
                    int(r["Importance_Rank"]),
                )
                for _, r in importance_df.iterrows()
            ],
        )

        # Create Dim_ML_Model_Metrics table
        cursor.execute("DROP TABLE IF EXISTS Dim_ML_Model_Metrics;")
        cursor.execute(
            """
            CREATE TABLE Dim_ML_Model_Metrics (
                Metric_Name TEXT PRIMARY KEY,
                Metric_Value REAL NOT NULL,
                Metric_Format TEXT NOT NULL,
                Description TEXT NOT NULL
            );
            """
        )

        champion_metrics = metrics_summary["Champion_Model_Performance"]
        confusion = metrics_summary["Confusion_Matrix"]

        metric_rows = [
            ("Accuracy", champion_metrics["Accuracy"], "0.0%", "Overall percentage of correct predictions"),
            ("Precision", champion_metrics["Precision"], "0.0%", "Proportion of positive identifications that were correct"),
            ("Recall", champion_metrics["Recall"], "0.0%", "Proportion of actual positives identified correctly"),
            ("F1_Score", champion_metrics["F1_Score"], "0.000", "Harmonic mean of precision and recall"),
            ("ROC_AUC", champion_metrics["ROC_AUC"], "0.000", "Area under receiver operating characteristic curve"),
            ("True_Positives", float(confusion.get("True Positive", 0)), "#,##0", "Students with depression correctly flagged"),
            ("True_Negatives", float(confusion.get("True Negative", 0)), "#,##0", "Students without depression correctly flagged"),
            ("False_Positives", float(confusion.get("False Positive", 0)), "#,##0", "Healthy students incorrectly flagged"),
            ("False_Negatives", float(confusion.get("False Negative", 0)), "#,##0", "Depressed students missed by model"),
        ]

        cursor.executemany(
            "INSERT INTO Dim_ML_Model_Metrics VALUES (?, ?, ?, ?);",
            metric_rows,
        )

        conn.commit()
    logging.info("SQLite database updated with ML predictions, feature importances, and model metrics.")


def run_pipeline() -> Dict[str, Any]:
    """Orchestrates end-to-end ML data loading, cross-validation, scoring, and persistence."""
    logging.info("Starting Machine Learning Predictive Pipeline...")

    if not CLEANED_CSV_PATH.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at {CLEANED_CSV_PATH}")

    df = pd.read_csv(CLEANED_CSV_PATH)
    logging.info("Loaded cleaned dataset: %d records, %d columns", len(df), len(df.columns))

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), NUMERICAL_FEATURES),
        ("cat", OneHotEncoder(drop="first", sparse_output=False), CATEGORICAL_FEATURES),
    ])

    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET_COLUMN]

    best_name, comparison_results, best_estimator = evaluate_models(X, y, preprocessor)
    scored_df, importance_df, confusion_counts = train_and_score_dataset(df, best_estimator, preprocessor)

    # Save artifacts
    scored_df.to_csv(SCORED_CSV_PATH, index=False)
    importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)
    logging.info("Saved scored dataset to %s", SCORED_CSV_PATH)
    logging.info("Saved feature importance rankings to %s", FEATURE_IMPORTANCE_PATH)

    metrics_summary: Dict[str, Any] = {
        "Champion_Model": best_name,
        "Validation_Strategy": f"{CV_FOLDS}-Fold Stratified Cross-Validation",
        "Comparison_Summary": comparison_results,
        "Champion_Model_Performance": comparison_results[best_name],
        "Confusion_Matrix": confusion_counts,
        "Risk_Tier_Distribution": scored_df["Risk_Tier"].value_counts().to_dict(),
    }

    with open(METRICS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)
    logging.info("Saved ML model metrics to %s", METRICS_JSON_PATH)

    update_sqlite_database(scored_df, importance_df, metrics_summary)

    logging.info("ML Predictive Pipeline completed successfully!")
    return metrics_summary


if __name__ == "__main__":
    run_pipeline()
