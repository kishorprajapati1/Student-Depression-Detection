"""
Unit & Edge-Case Tests: Student Depression Data Pipeline
Validates type coercion, boundary logic, anomaly auditing, and classification integrity.
"""

import unittest
from typing import Any, Dict

import sys
import os

# Add scripts directory to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'Project-01_Student_Depression_Analysis', 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

from data_validation_pipeline import (
    classify_cgpa,
    classify_academic_stage,
    classify_living_cost,
    classify_health_risk,
    clean_and_enrich_row,
    parse_numeric,
    EXPECTED_RAW_COLUMNS
)


class TestValidationPipeline(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_valid_row: Dict[str, str] = {
            'Gender': 'Female',
            'Age': '22',
            'Family_background': 'Middle class',
            'Relationship_status': 'Single',
            'Marital_status': 'Unmarried',
            'Living_style': 'Bachelor',
            'Current_semester': '8',
            'CGPA': '3.43',
            'friend_circle': 'Yes',
            'Health_condition': 'Critical',
            'Cost_without_study': '10113',
            'Home_division': 'Chittagong',
            'Depression': 'Yes'
        }
        self.audit_template: Dict[str, Any] = {
            'total_rows_inspected': 0,
            'null_value_counts': {col: 0 for col in EXPECTED_RAW_COLUMNS},
            'whitespace_trimmed_count': 0,
            'out_of_range_age': 0,
            'out_of_range_cgpa': 0,
            'out_of_range_semester': 0,
            'zero_or_negative_cost_count': 0,
            'relationship_marital_discrepancy_count': 0,
        }

    # -------------------------------------------------------------------------
    # 1. Type Coercion & Parse Error Handling Tests
    # -------------------------------------------------------------------------
    def test_parse_numeric_valid_int(self) -> None:
        self.assertEqual(parse_numeric('22', int, 'Age', 1), 22)
        self.assertEqual(parse_numeric(' 25 ', int, 'Age', 2), 25)

    def test_parse_numeric_valid_float_with_comma(self) -> None:
        self.assertEqual(parse_numeric('10,500.50', float, 'Cost', 1), 10500.50)

    def test_parse_numeric_invalid_string_raises_value_error(self) -> None:
        with self.assertRaises(ValueError) as context:
            parse_numeric('invalid_number', float, 'CGPA', 42)
        self.assertIn("Row 42", str(context.exception))
        self.assertIn("CGPA='invalid_number'", str(context.exception))

    def test_parse_numeric_empty_string_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            parse_numeric('', int, 'Age', 1)

    # -------------------------------------------------------------------------
    # 2. Boundary & Classification Integrity Tests
    # -------------------------------------------------------------------------
    def test_classify_cgpa_tiers(self) -> None:
        self.assertEqual(classify_cgpa(4.00), ('High Distinction (3.80 - 4.00)', 1))
        self.assertEqual(classify_cgpa(3.80), ('High Distinction (3.80 - 4.00)', 1))
        self.assertEqual(classify_cgpa(3.79), ('First Class (3.50 - 3.79)', 2))
        self.assertEqual(classify_cgpa(3.50), ('First Class (3.50 - 3.79)', 2))
        self.assertEqual(classify_cgpa(3.49), ('Second Class Upper (3.00 - 3.49)', 3))
        self.assertEqual(classify_cgpa(3.00), ('Second Class Upper (3.00 - 3.49)', 3))
        self.assertEqual(classify_cgpa(2.99), ('Pass / Needs Support (< 3.00)', 4))
        self.assertEqual(classify_cgpa(2.00), ('Pass / Needs Support (< 3.00)', 4))

    def test_classify_academic_stage(self) -> None:
        self.assertEqual(classify_academic_stage(0), ('Pre-University / Foundation', 0))
        self.assertEqual(classify_academic_stage(1), ('Early Stage (Sem 1-4)', 1))
        self.assertEqual(classify_academic_stage(4), ('Early Stage (Sem 1-4)', 1))
        self.assertEqual(classify_academic_stage(5), ('Mid Stage (Sem 5-8)', 2))
        self.assertEqual(classify_academic_stage(8), ('Mid Stage (Sem 5-8)', 2))
        self.assertEqual(classify_academic_stage(9), ('Graduating / Extended (Sem 9+)', 3))
        self.assertEqual(classify_academic_stage(13), ('Graduating / Extended (Sem 9+)', 3))

    def test_classify_living_cost(self) -> None:
        self.assertEqual(classify_living_cost(4999), ('Low (< 5,000 BDT)', 1))
        self.assertEqual(classify_living_cost(5000), ('Moderate (5,000 - 12,000 BDT)', 2))
        self.assertEqual(classify_living_cost(12000), ('Moderate (5,000 - 12,000 BDT)', 2))
        self.assertEqual(classify_living_cost(12001), ('High (12,001 - 20,000 BDT)', 3))
        self.assertEqual(classify_living_cost(20000), ('High (12,001 - 20,000 BDT)', 3))
        self.assertEqual(classify_living_cost(20001), ('Very High (> 20,000 BDT)', 4))

    def test_classify_health_risk(self) -> None:
        self.assertEqual(classify_health_risk('Critical'), ('Severe Clinical Risk', 1))
        self.assertEqual(classify_health_risk('Abnormal'), ('Elevated Risk', 2))
        self.assertEqual(classify_health_risk('Normal'), ('Low Risk', 3))
        self.assertEqual(classify_health_risk('Good'), ('Optimal / Healthy', 4))
        self.assertEqual(classify_health_risk('UnknownCondition'), ('Unknown / Unspecified', 5))

    # -------------------------------------------------------------------------
    # 3. Record Enrichment & Audit Flagging Tests
    # -------------------------------------------------------------------------
    def test_clean_and_enrich_valid_row(self) -> None:
        cleaned = clean_and_enrich_row(self.sample_valid_row, 1, self.audit_template)
        self.assertEqual(cleaned['Student_ID'], 'STU-00001')
        self.assertEqual(cleaned['Age'], 22)
        self.assertEqual(cleaned['CGPA'], 3.43)
        self.assertEqual(cleaned['Depression_Flag'], 1)
        self.assertEqual(cleaned['CGPA_Tier'], 'Second Class Upper (3.00 - 3.49)')
        self.assertEqual(cleaned['CGPA_Tier_Sort'], 3)
        self.assertEqual(cleaned['Health_Risk_Category'], 'Severe Clinical Risk')
        self.assertEqual(cleaned['Health_Risk_Sort'], 1)
        self.assertEqual(self.audit_template['out_of_range_cgpa'], 0)

    def test_audit_flags_out_of_range_cgpa(self) -> None:
        invalid_cgpa_row = self.sample_valid_row.copy()
        invalid_cgpa_row['CGPA'] = '4.50'  # Beyond 4.0 scale
        clean_and_enrich_row(invalid_cgpa_row, 2, self.audit_template)
        self.assertEqual(self.audit_template['out_of_range_cgpa'], 1)

    def test_audit_flags_relationship_marital_discrepancy(self) -> None:
        discrepant_row = self.sample_valid_row.copy()
        discrepant_row['Relationship_status'] = 'Single'
        discrepant_row['Marital_status'] = 'Married'
        clean_and_enrich_row(discrepant_row, 3, self.audit_template)
        self.assertEqual(self.audit_template['relationship_marital_discrepancy_count'], 1)

    def test_whitespace_is_trimmed_and_audited(self) -> None:
        whitespace_row = self.sample_valid_row.copy()
        whitespace_row['Gender'] = '  Female  '
        cleaned = clean_and_enrich_row(whitespace_row, 4, self.audit_template)
        self.assertEqual(cleaned['Gender'], 'Female')
        self.assertGreater(self.audit_template['whitespace_trimmed_count'], 0)

    def test_zero_living_cost_is_audited(self) -> None:
        zero_cost_row = self.sample_valid_row.copy()
        zero_cost_row['Cost_without_study'] = '0'
        clean_and_enrich_row(zero_cost_row, 5, self.audit_template)
        self.assertEqual(self.audit_template['zero_or_negative_cost_count'], 1)


if __name__ == '__main__':
    unittest.main()
