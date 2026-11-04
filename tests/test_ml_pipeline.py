"""
Unit Tests for Student Depression Machine Learning Predictive Pipeline
======================================================================
Tests mathematical bounds, risk tier categorization, feature importance rankings,
and out-of-fold prediction outputs.
"""

import json
import sqlite3
import unittest
from pathlib import Path

import pandas as pd

import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT_DIR / "Project-01_Student_Depression_Analysis" / "data" / "processed"
SCRIPTS_DIR = ROOT_DIR / "Project-01_Student_Depression_Analysis" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from depression_ml_pipeline import assign_risk_tier
SCORED_CSV = PROCESSED_DIR / "student_depression_ml_scored.csv"
FEATURE_IMPORTANCE_CSV = PROCESSED_DIR / "ml_feature_importance.csv"
METRICS_JSON = PROCESSED_DIR / "ml_model_metrics.json"
DATABASE_PATH = PROCESSED_DIR / "student_depression.db"


class TestMLPipeline(unittest.TestCase):
    """Test suite verifying ML outputs, boundary conditions, and model integrity."""

    def test_assign_risk_tier_boundary_critical(self):
        tier, sort_key, priority = assign_risk_tier(0.85)
        self.assertEqual(tier, "Critical Risk")
        self.assertEqual(sort_key, 4)
        self.assertEqual(priority, "Immediate Clinical Referral")

    def test_assign_risk_tier_boundary_high(self):
        tier, sort_key, priority = assign_risk_tier(0.60)
        self.assertEqual(tier, "High Risk")
        self.assertEqual(sort_key, 3)
        self.assertEqual(priority, "Counseling Center Outreach")

    def test_assign_risk_tier_boundary_moderate(self):
        tier, sort_key, priority = assign_risk_tier(0.30)
        self.assertEqual(tier, "Moderate Risk")
        self.assertEqual(sort_key, 2)
        self.assertEqual(priority, "Academic Advisor Check-in")

    def test_assign_risk_tier_boundary_low(self):
        tier, sort_key, priority = assign_risk_tier(0.29)
        self.assertEqual(tier, "Low Risk")
        self.assertEqual(sort_key, 1)
        self.assertEqual(priority, "Routine Wellness Monitoring")

    def test_assign_risk_tier_extremes(self):
        tier_zero, sort_zero, _ = assign_risk_tier(0.0)
        tier_one, sort_one, _ = assign_risk_tier(1.0)
        self.assertEqual(tier_zero, "Low Risk")
        self.assertEqual(sort_zero, 1)
        self.assertEqual(tier_one, "Critical Risk")
        self.assertEqual(sort_one, 4)

    def test_scored_dataset_integrity(self):
        self.assertTrue(SCORED_CSV.exists(), "Scored CSV does not exist")
        df = pd.read_csv(SCORED_CSV)
        self.assertEqual(len(df), 4464, "Row count must remain 4,464")

        # Required ML output columns
        expected_cols = [
            "Predicted_Depression",
            "Predicted_Depression_Label",
            "Depression_Risk_Score",
            "Risk_Tier",
            "Risk_Tier_Sort",
            "Intervention_Priority",
            "Prediction_Outcome",
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing ML column: {col}")
            self.assertEqual(df[col].isnull().sum(), 0, f"Column {col} contains null values")

        # Probability bounds
        self.assertTrue((df["Depression_Risk_Score"] >= 0.0).all(), "Risk score cannot be negative")
        self.assertTrue((df["Depression_Risk_Score"] <= 1.0).all(), "Risk score cannot exceed 1.0")

    def test_feature_importance_validity(self):
        self.assertTrue(FEATURE_IMPORTANCE_CSV.exists(), "Feature importance CSV does not exist")
        df = pd.read_csv(FEATURE_IMPORTANCE_CSV)
        self.assertGreater(len(df), 0, "Feature importance must not be empty")

        # Verify weights sum close to 1.0 (for tree feature importances)
        total_weight = df["Importance_Weight"].sum()
        self.assertAlmostEqual(total_weight, 1.0, delta=0.05)

        # Verify ranks are monotonically increasing from 1
        self.assertEqual(list(df["Importance_Rank"]), list(range(1, len(df) + 1)))

    def test_metrics_json_structure(self):
        self.assertTrue(METRICS_JSON.exists(), "Model metrics JSON does not exist")
        with open(METRICS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("Champion_Model", data)
        self.assertIn("Champion_Model_Performance", data)
        perf = data["Champion_Model_Performance"]
        for metric in ["Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC"]:
            self.assertIn(metric, perf)
            self.assertGreater(perf[metric], 0.85, f"{metric} should exceed 85% on this benchmark")

    def test_sqlite_ml_tables_and_columns(self):
        self.assertTrue(DATABASE_PATH.exists(), "SQLite database does not exist")
        with sqlite3.connect(DATABASE_PATH) as conn:
            cur = conn.cursor()

            # Check Fact table has ML columns
            cur.execute("PRAGMA table_info(Fact_Student_Assessment);")
            cols = {row[1] for row in cur.fetchall()}
            for expected in ["Predicted_Depression", "Depression_Risk_Score", "Risk_Tier"]:
                self.assertIn(expected, cols)

            # Check Dim_ML_Feature_Importance
            cur.execute("SELECT COUNT(*) FROM Dim_ML_Feature_Importance;")
            count = cur.fetchone()[0]
            self.assertGreater(count, 0)

            # Check Dim_ML_Model_Metrics
            cur.execute("SELECT Metric_Name, Metric_Value FROM Dim_ML_Model_Metrics;")
            metrics_dict = dict(cur.fetchall())
            self.assertIn("Accuracy", metrics_dict)
            self.assertIn("F1_Score", metrics_dict)


if __name__ == "__main__":
    unittest.main()
