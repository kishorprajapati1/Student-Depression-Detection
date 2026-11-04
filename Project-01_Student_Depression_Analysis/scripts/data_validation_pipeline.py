"""
=============================================================================
STUDENT DEPRESSION DATASET: VALIDATION & CLEANING PIPELINE
Author: Portfolio Project 1 (Power BI Career Transition Track)
Purpose: Validate, audit, clean, and enrich raw student depression dataset
=============================================================================
"""

import csv
import os
import json
import sqlite3
from collections import defaultdict, Counter

# Configure paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
RAW_CSV_PATH = os.path.join(PROJECT_DIR, 'data', 'raw', 'student_depression_raw.csv')
CLEANED_CSV_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'student_depression_cleaned.csv')
SQLITE_DB_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'student_depression.db')
AUDIT_REPORT_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'data_quality_audit.json')


def run_pipeline():
    print("=" * 70)
    print("STEP 1: INGESTION & STRUCTURAL INTEGRITY CHECK")
    print("=" * 70)

    if not os.path.exists(RAW_CSV_PATH):
        raise FileNotFoundError(f"Raw CSV not found at: {RAW_CSV_PATH}")

    with open(RAW_CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        raw_header = next(reader)
        raw_rows = list(reader)

    total_raw_rows = len(raw_rows)
    print(f"Raw rows ingested: {total_raw_rows}")
    print(f"Header fields ({len(raw_header)}): {raw_header}")

    # Expected column list
    expected_columns = [
        'Gender', 'Age', 'Family_background', 'Relationship_status',
        'Marital_status', 'Living_style', 'Current_semester', 'CGPA',
        'friend_circle', 'Health_condition', 'Cost_without_study',
        'Home_division', 'Depression'
    ]
    assert raw_header == expected_columns, f"Header mismatch: {raw_header} vs {expected_columns}"

    print("=" * 70)
    print("STEP 2: DATA VALIDATION & QUALITY AUDIT")
    print("=" * 70)

    audit_metrics = {
        'total_rows_inspected': total_raw_rows,
        'null_value_counts': {col: 0 for col in expected_columns},
        'whitespace_trimmed_count': 0,
        'out_of_range_age': 0,
        'out_of_range_cgpa': 0,
        'out_of_range_semester': 0,
        'zero_cost_count': 0,
        'logical_conflict_relationship_marital': 0
    }

    cleaned_records = []
    
    for idx, row in enumerate(raw_rows, start=1):
        cleaned_row = {}
        for col_name, val in zip(expected_columns, row):
            val_stripped = val.strip()
            if val != val_stripped:
                audit_metrics['whitespace_trimmed_count'] += 1
            if not val_stripped:
                audit_metrics['null_value_counts'][col_name] += 1
            cleaned_row[col_name] = val_stripped

        # Type conversion & range checks
        age = int(cleaned_row['Age'])
        if age < 15 or age > 40:
            audit_metrics['out_of_range_age'] += 1

        cgpa = float(cleaned_row['CGPA'])
        if cgpa < 0.0 or cgpa > 4.0:
            audit_metrics['out_of_range_cgpa'] += 1

        semester = int(cleaned_row['Current_semester'])
        if semester < 0 or semester > 16:
            audit_metrics['out_of_range_semester'] += 1

        cost = float(cleaned_row['Cost_without_study'])
        if cost == 0:
            audit_metrics['zero_cost_count'] += 1

        # Logical check: Single vs Married
        if cleaned_row['Relationship_status'] == 'Single' and cleaned_row['Marital_status'] == 'Married':
            audit_metrics['logical_conflict_relationship_marital'] += 1

        # Enrichment: Create Derived Features for Power BI & SQL
        # 1. Student_ID (Deterministic Surrogate Key)
        student_id = f"STU-{idx:05d}"
        cleaned_row['Student_ID'] = student_id

        # 2. Binary Depression Flag (1 = Yes, 0 = No) for straightforward DAX aggregation
        cleaned_row['Depression_Flag'] = 1 if cleaned_row['Depression'] == 'Yes' else 0

        # 3. CGPA Performance Tier
        if cgpa >= 3.80:
            cleaned_row['CGPA_Tier'] = 'High Distinction (3.80 - 4.00)'
            cleaned_row['CGPA_Tier_Sort'] = 1
        elif cgpa >= 3.50:
            cleaned_row['CGPA_Tier'] = 'First Class (3.50 - 3.79)'
            cleaned_row['CGPA_Tier_Sort'] = 2
        elif cgpa >= 3.00:
            cleaned_row['CGPA_Tier'] = 'Second Class Upper (3.00 - 3.49)'
            cleaned_row['CGPA_Tier_Sort'] = 3
        else:
            cleaned_row['CGPA_Tier'] = 'Pass / Needs Support (< 3.00)'
            cleaned_row['CGPA_Tier_Sort'] = 4

        # 4. Academic Stage Classification
        if semester == 0:
            cleaned_row['Academic_Stage'] = 'Pre-University / Foundation'
            cleaned_row['Academic_Stage_Sort'] = 0
        elif semester <= 4:
            cleaned_row['Academic_Stage'] = 'Early Stage (Sem 1-4)'
            cleaned_row['Academic_Stage_Sort'] = 1
        elif semester <= 8:
            cleaned_row['Academic_Stage'] = 'Mid Stage (Sem 5-8)'
            cleaned_row['Academic_Stage_Sort'] = 2
        else:
            cleaned_row['Academic_Stage'] = 'Graduating / Extended (Sem 9+)'
            cleaned_row['Academic_Stage_Sort'] = 3

        # 5. Living Cost Bracket
        if cost < 5000:
            cleaned_row['Cost_Bracket'] = 'Low (< 5,000 BDT)'
            cleaned_row['Cost_Bracket_Sort'] = 1
        elif cost <= 12000:
            cleaned_row['Cost_Bracket'] = 'Moderate (5,000 - 12,000 BDT)'
            cleaned_row['Cost_Bracket_Sort'] = 2
        elif cost <= 20000:
            cleaned_row['Cost_Bracket'] = 'High (12,001 - 20,000 BDT)'
            cleaned_row['Cost_Bracket_Sort'] = 3
        else:
            cleaned_row['Cost_Bracket'] = 'Very High (> 20,000 BDT)'
            cleaned_row['Cost_Bracket_Sort'] = 4

        # 6. Clinical Risk Level (Composite)
        hc = cleaned_row['Health_condition']
        if hc == 'Critical':
            cleaned_row['Health_Risk_Category'] = 'Severe Clinical Risk'
            cleaned_row['Health_Risk_Sort'] = 1
        elif hc == 'Abnormal':
            cleaned_row['Health_Risk_Category'] = 'Elevated Risk'
            cleaned_row['Health_Risk_Sort'] = 2
        elif hc == 'Normal':
            cleaned_row['Health_Risk_Category'] = 'Low Risk'
            cleaned_row['Health_Risk_Sort'] = 3
        else:
            cleaned_row['Health_Risk_Category'] = 'Optimal / Healthy'
            cleaned_row['Health_Risk_Sort'] = 4

        cleaned_records.append(cleaned_row)

    print("Audit Summary:")
    print(json.dumps(audit_metrics, indent=2))

    # Save audit report to JSON
    with open(AUDIT_REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(audit_metrics, f, indent=2)
    print(f"Audit report saved to: {AUDIT_REPORT_PATH}")

    print("=" * 70)
    print("STEP 3: EXPORTING CLEANED & ENRICHED DATASET")
    print("=" * 70)

    enriched_header = list(cleaned_records[0].keys())
    with open(CLEANED_CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=enriched_header)
        writer.writeheader()
        writer.writerows(cleaned_records)

    print(f"Cleaned CSV exported to: {CLEANED_CSV_PATH}")
    print(f"Total cleaned rows: {len(cleaned_records)}, Columns: {len(enriched_header)}")

    print("=" * 70)
    print("STEP 4: POPULATING SQLITE ANALYTICS REPOSITORY")
    print("=" * 70)

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS student_depression_cleaned;")
    cursor.execute("""
        CREATE TABLE student_depression_cleaned (
            Student_ID TEXT PRIMARY KEY,
            Gender TEXT NOT NULL,
            Age INTEGER NOT NULL,
            Family_background TEXT NOT NULL,
            Relationship_status TEXT NOT NULL,
            Marital_status TEXT NOT NULL,
            Living_style TEXT NOT NULL,
            Current_semester INTEGER NOT NULL,
            CGPA REAL NOT NULL,
            friend_circle TEXT NOT NULL,
            Health_condition TEXT NOT NULL,
            Cost_without_study REAL NOT NULL,
            Home_division TEXT NOT NULL,
            Depression TEXT NOT NULL,
            Depression_Flag INTEGER NOT NULL,
            CGPA_Tier TEXT NOT NULL,
            CGPA_Tier_Sort INTEGER NOT NULL,
            Academic_Stage TEXT NOT NULL,
            Academic_Stage_Sort INTEGER NOT NULL,
            Cost_Bracket TEXT NOT NULL,
            Cost_Bracket_Sort INTEGER NOT NULL,
            Health_Risk_Category TEXT NOT NULL,
            Health_Risk_Sort INTEGER NOT NULL
        );
    """)

    insert_sql = f"""
        INSERT INTO student_depression_cleaned (
            {', '.join(enriched_header)}
        ) VALUES ({', '.join(['?'] * len(enriched_header))});
    """

    data_tuples = [tuple(r[col] for col in enriched_header) for r in cleaned_records]
    cursor.executemany(insert_sql, data_tuples)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM student_depression_cleaned;")
    db_row_count = cursor.fetchone()[0]
    print(f"SQLite DB populated: {SQLITE_DB_PATH} with {db_row_count} rows.")

    conn.close()
    print("Validation and Cleaning Pipeline Completed Successfully.")


if __name__ == '__main__':
    run_pipeline()
