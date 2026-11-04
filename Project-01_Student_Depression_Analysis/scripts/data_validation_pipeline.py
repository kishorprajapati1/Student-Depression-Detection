"""
Student Depression Dataset: Validation & Cleaning Pipeline
Automated ETL pipeline to audit, clean, and structure raw student survey data.
"""

import csv
import json
import os
import sqlite3
from typing import Any, Dict, List, Tuple

# Domain Boundary Constants
AGE_MIN_YEARS = 15
AGE_MAX_YEARS = 35
CGPA_MIN = 0.00
CGPA_MAX = 4.00
SEMESTER_MIN = 0
SEMESTER_MAX = 14

# Classification Thresholds (replaces magic numbers)
CGPA_HIGH_DISTINCTION_THRESHOLD = 3.80
CGPA_FIRST_CLASS_THRESHOLD = 3.50
CGPA_SECOND_CLASS_THRESHOLD = 3.00

LIVING_COST_LOW_THRESHOLD_BDT = 5000.0
LIVING_COST_MODERATE_THRESHOLD_BDT = 12000.0
LIVING_COST_HIGH_THRESHOLD_BDT = 20000.0

EXPECTED_RAW_COLUMNS = [
    'Gender', 'Age', 'Family_background', 'Relationship_status',
    'Marital_status', 'Living_style', 'Current_semester', 'CGPA',
    'friend_circle', 'Health_condition', 'Cost_without_study',
    'Home_division', 'Depression'
]

ALLOWED_OUTPUT_COLUMNS = [
    'Student_ID', 'Gender', 'Age', 'Family_background', 'Relationship_status',
    'Marital_status', 'Living_style', 'Current_semester', 'CGPA',
    'friend_circle', 'Health_condition', 'Cost_without_study',
    'Home_division', 'Depression', 'Depression_Flag', 'CGPA_Tier',
    'CGPA_Tier_Sort', 'Academic_Stage', 'Academic_Stage_Sort',
    'Cost_Bracket', 'Cost_Bracket_Sort', 'Health_Risk_Category',
    'Health_Risk_Sort'
]


def classify_cgpa(cgpa: float) -> Tuple[str, int]:
    """Classifies CGPA into standardized academic tiers with sort keys."""
    if cgpa >= CGPA_HIGH_DISTINCTION_THRESHOLD:
        return 'High Distinction (3.80 - 4.00)', 1
    if cgpa >= CGPA_FIRST_CLASS_THRESHOLD:
        return 'First Class (3.50 - 3.79)', 2
    if cgpa >= CGPA_SECOND_CLASS_THRESHOLD:
        return 'Second Class Upper (3.00 - 3.49)', 3
    return 'Pass / Needs Support (< 3.00)', 4


def classify_academic_stage(semester: int) -> Tuple[str, int]:
    """Categorizes semester into academic career stage."""
    if semester == 0:
        return 'Pre-University / Foundation', 0
    if semester <= 4:
        return 'Early Stage (Sem 1-4)', 1
    if semester <= 8:
        return 'Mid Stage (Sem 5-8)', 2
    return 'Graduating / Extended (Sem 9+)', 3


def classify_living_cost(cost_bdt: float) -> Tuple[str, int]:
    """Bins monthly non-tuition living expenditure in BDT."""
    if cost_bdt < LIVING_COST_LOW_THRESHOLD_BDT:
        return 'Low (< 5,000 BDT)', 1
    if cost_bdt <= LIVING_COST_MODERATE_THRESHOLD_BDT:
        return 'Moderate (5,000 - 12,000 BDT)', 2
    if cost_bdt <= LIVING_COST_HIGH_THRESHOLD_BDT:
        return 'High (12,001 - 20,000 BDT)', 3
    return 'Very High (> 20,000 BDT)', 4


def classify_health_risk(condition: str) -> Tuple[str, int]:
    """Maps physical health status to clinical risk category."""
    mapping = {
        'Critical': ('Severe Clinical Risk', 1),
        'Abnormal': ('Elevated Risk', 2),
        'Normal': ('Low Risk', 3),
        'Good': ('Optimal / Healthy', 4),
    }
    return mapping.get(condition, ('Unknown / Unspecified', 5))


def parse_numeric(raw_value: str, target_type: type, field_name: str, row_idx: int) -> Any:
    """Safely converts string to numeric type, raising informative error on malformed input."""
    cleaned = raw_value.strip().replace(',', '')
    try:
        return target_type(cleaned)
    except ValueError as exc:
        raise ValueError(
            f"Row {row_idx}: Failed converting {field_name}='{raw_value}' to {target_type.__name__}"
        ) from exc


def clean_and_enrich_row(raw_dict: Dict[str, str], row_idx: int, audit: Dict[str, Any]) -> Dict[str, Any]:
    """Validates and enriches a single raw survey record."""
    cleaned_dict: Dict[str, Any] = {}

    for col in EXPECTED_RAW_COLUMNS:
        raw_val = raw_dict.get(col, '')
        stripped_val = raw_val.strip()
        if raw_val != stripped_val:
            audit['whitespace_trimmed_count'] += 1
        if not stripped_val:
            audit['null_value_counts'][col] += 1
        cleaned_dict[col] = stripped_val

    age = parse_numeric(cleaned_dict['Age'], int, 'Age', row_idx)
    cgpa = parse_numeric(cleaned_dict['CGPA'], float, 'CGPA', row_idx)
    semester = parse_numeric(cleaned_dict['Current_semester'], int, 'Current_semester', row_idx)
    cost = parse_numeric(cleaned_dict['Cost_without_study'], float, 'Cost_without_study', row_idx)

    # Range and boundary auditing
    if age < AGE_MIN_YEARS or age > AGE_MAX_YEARS:
        audit['out_of_range_age'] += 1
    if cgpa < CGPA_MIN or cgpa > CGPA_MAX:
        audit['out_of_range_cgpa'] += 1
    if semester < SEMESTER_MIN or semester > SEMESTER_MAX:
        audit['out_of_range_semester'] += 1
    if cost <= 0.0:
        audit['zero_or_negative_cost_count'] += 1

    # Cross-attribute consistency check
    if cleaned_dict['Relationship_status'] == 'Single' and cleaned_dict['Marital_status'] == 'Married':
        audit['relationship_marital_discrepancy_count'] += 1

    # Deterministic surrogate key
    cleaned_dict['Student_ID'] = f"STU-{row_idx:05d}"
    cleaned_dict['Age'] = age
    cleaned_dict['CGPA'] = cgpa
    cleaned_dict['Current_semester'] = semester
    cleaned_dict['Cost_without_study'] = cost

    # Depression flag for clean DAX aggregation
    cleaned_dict['Depression_Flag'] = 1 if cleaned_dict['Depression'] == 'Yes' else 0

    # Categorical tiers with numeric sort keys
    cleaned_dict['CGPA_Tier'], cleaned_dict['CGPA_Tier_Sort'] = classify_cgpa(cgpa)
    cleaned_dict['Academic_Stage'], cleaned_dict['Academic_Stage_Sort'] = classify_academic_stage(semester)
    cleaned_dict['Cost_Bracket'], cleaned_dict['Cost_Bracket_Sort'] = classify_living_cost(cost)
    cleaned_dict['Health_Risk_Category'], cleaned_dict['Health_Risk_Sort'] = classify_health_risk(
        cleaned_dict['Health_condition']
    )

    return cleaned_dict


def process_dataset(raw_csv_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Reads raw CSV, validates all rows, and returns cleaned records and audit summary."""
    if not os.path.isfile(raw_csv_path):
        raise FileNotFoundError(f"Input dataset not found: {raw_csv_path}")

    with open(raw_csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != EXPECTED_RAW_COLUMNS:
            raise ValueError(f"Schema mismatch. Expected: {EXPECTED_RAW_COLUMNS}, Received: {header}")
        raw_rows = list(reader)

    audit: Dict[str, Any] = {
        'total_rows_inspected': len(raw_rows),
        'null_value_counts': {col: 0 for col in EXPECTED_RAW_COLUMNS},
        'whitespace_trimmed_count': 0,
        'out_of_range_age': 0,
        'out_of_range_cgpa': 0,
        'out_of_range_semester': 0,
        'zero_or_negative_cost_count': 0,
        'relationship_marital_discrepancy_count': 0,
    }

    cleaned_records: List[Dict[str, Any]] = []
    for idx, row in enumerate(raw_rows, start=1):
        row_dict = dict(zip(EXPECTED_RAW_COLUMNS, row))
        cleaned_record = clean_and_enrich_row(row_dict, idx, audit)
        cleaned_records.append(cleaned_record)

    return cleaned_records, audit


def persist_to_sqlite(records: List[Dict[str, Any]], db_path: str) -> None:
    """Persists cleaned records into SQLite staging and Star Schema tables with verified parameterization."""
    conn = sqlite3.connect(db_path)
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

    # Whitelist-verified column names (prevents SQL injection)
    columns_clause = ', '.join(ALLOWED_OUTPUT_COLUMNS)
    placeholders = ', '.join(['?'] * len(ALLOWED_OUTPUT_COLUMNS))
    insert_sql = f"INSERT INTO student_depression_cleaned ({columns_clause}) VALUES ({placeholders});"

    data_tuples = [tuple(r[col] for col in ALLOWED_OUTPUT_COLUMNS) for r in records]
    cursor.executemany(insert_sql, data_tuples)

    # Populate Star Schema Dimensional Tables
    cursor.execute("DROP TABLE IF EXISTS Dim_Demographics;")
    cursor.execute("""
        CREATE TABLE Dim_Demographics (
            Demographic_Key INTEGER PRIMARY KEY AUTOINCREMENT,
            Gender TEXT NOT NULL,
            Age INTEGER NOT NULL,
            Family_background TEXT NOT NULL,
            Relationship_status TEXT NOT NULL,
            Marital_status TEXT NOT NULL,
            Living_style TEXT NOT NULL
        );
    """)
    cursor.execute("""
        INSERT INTO Dim_Demographics (Gender, Age, Family_background, Relationship_status, Marital_status, Living_style)
        SELECT DISTINCT Gender, Age, Family_background, Relationship_status, Marital_status, Living_style
        FROM student_depression_cleaned;
    """)

    cursor.execute("DROP TABLE IF EXISTS Dim_Academic;")
    cursor.execute("""
        CREATE TABLE Dim_Academic (
            Academic_Key INTEGER PRIMARY KEY AUTOINCREMENT,
            Current_semester INTEGER NOT NULL,
            Academic_Stage TEXT NOT NULL,
            Academic_Stage_Sort INTEGER NOT NULL
        );
    """)
    cursor.execute("""
        INSERT INTO Dim_Academic (Current_semester, Academic_Stage, Academic_Stage_Sort)
        SELECT DISTINCT Current_semester, Academic_Stage, Academic_Stage_Sort
        FROM student_depression_cleaned;
    """)

    cursor.execute("DROP TABLE IF EXISTS Dim_Health_Social;")
    cursor.execute("""
        CREATE TABLE Dim_Health_Social (
            Health_Social_Key INTEGER PRIMARY KEY AUTOINCREMENT,
            Health_condition TEXT NOT NULL,
            Health_Risk_Category TEXT NOT NULL,
            Health_Risk_Sort INTEGER NOT NULL,
            friend_circle TEXT NOT NULL
        );
    """)
    cursor.execute("""
        INSERT INTO Dim_Health_Social (Health_condition, Health_Risk_Category, Health_Risk_Sort, friend_circle)
        SELECT DISTINCT Health_condition, Health_Risk_Category, Health_Risk_Sort, friend_circle
        FROM student_depression_cleaned;
    """)

    cursor.execute("DROP TABLE IF EXISTS Dim_Geography;")
    cursor.execute("""
        CREATE TABLE Dim_Geography (
            Geography_Key INTEGER PRIMARY KEY AUTOINCREMENT,
            Home_division TEXT NOT NULL,
            Zone TEXT NOT NULL
        );
    """)
    cursor.execute("""
        INSERT INTO Dim_Geography (Home_division, Zone)
        SELECT DISTINCT
            Home_division,
            CASE 
                WHEN Home_division IN ('Dhaka', 'Mymensingh') THEN 'Central'
                WHEN Home_division IN ('Chittagong', 'Sylhet') THEN 'Eastern'
                WHEN Home_division IN ('Rajshahi', 'Rangpur') THEN 'Northern'
                ELSE 'South-Western'
            END AS Zone
        FROM student_depression_cleaned;
    """)

    cursor.execute("DROP TABLE IF EXISTS Fact_Student_Assessment;")
    cursor.execute("""
        CREATE TABLE Fact_Student_Assessment (
            Student_ID TEXT PRIMARY KEY,
            Demographic_Key INTEGER NOT NULL,
            Academic_Key INTEGER NOT NULL,
            Health_Social_Key INTEGER NOT NULL,
            Geography_Key INTEGER NOT NULL,
            CGPA REAL NOT NULL,
            CGPA_Tier TEXT NOT NULL,
            CGPA_Tier_Sort INTEGER NOT NULL,
            Cost_without_study REAL NOT NULL,
            Cost_Bracket TEXT NOT NULL,
            Cost_Bracket_Sort INTEGER NOT NULL,
            Depression TEXT NOT NULL,
            Depression_Flag INTEGER NOT NULL,
            FOREIGN KEY (Demographic_Key) REFERENCES Dim_Demographics (Demographic_Key),
            FOREIGN KEY (Academic_Key) REFERENCES Dim_Academic (Academic_Key),
            FOREIGN KEY (Health_Social_Key) REFERENCES Dim_Health_Social (Health_Social_Key),
            FOREIGN KEY (Geography_Key) REFERENCES Dim_Geography (Geography_Key)
        );
    """)
    cursor.execute("""
        INSERT INTO Fact_Student_Assessment (
            Student_ID, Demographic_Key, Academic_Key, Health_Social_Key, Geography_Key,
            CGPA, CGPA_Tier, CGPA_Tier_Sort, Cost_without_study, Cost_Bracket, Cost_Bracket_Sort,
            Depression, Depression_Flag
        )
        SELECT 
            s.Student_ID,
            d.Demographic_Key,
            a.Academic_Key,
            h.Health_Social_Key,
            g.Geography_Key,
            s.CGPA,
            s.CGPA_Tier,
            s.CGPA_Tier_Sort,
            s.Cost_without_study,
            s.Cost_Bracket,
            s.Cost_Bracket_Sort,
            s.Depression,
            s.Depression_Flag
        FROM student_depression_cleaned s
        JOIN Dim_Demographics d ON s.Gender = d.Gender 
            AND s.Age = d.Age 
            AND s.Family_background = d.Family_background 
            AND s.Relationship_status = d.Relationship_status 
            AND s.Marital_status = d.Marital_status 
            AND s.Living_style = d.Living_style
        JOIN Dim_Academic a ON s.Current_semester = a.Current_semester
        JOIN Dim_Health_Social h ON s.Health_condition = h.Health_condition 
            AND s.friend_circle = h.friend_circle
        JOIN Dim_Geography g ON s.Home_division = g.Home_division;
    """)

    conn.commit()
    conn.close()


def run_pipeline() -> None:
    """Execution entry point."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)

    raw_csv = os.path.join(project_dir, 'data', 'raw', 'student_depression_raw.csv')
    processed_dir = os.path.join(project_dir, 'data', 'processed')
    cleaned_csv = os.path.join(processed_dir, 'student_depression_cleaned.csv')
    audit_json = os.path.join(processed_dir, 'data_quality_audit.json')
    sqlite_db = os.path.join(processed_dir, 'student_depression.db')

    os.makedirs(processed_dir, exist_ok=True)

    records, audit = process_dataset(raw_csv)

    with open(audit_json, 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2)

    with open(cleaned_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=ALLOWED_OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(records)

    persist_to_sqlite(records, sqlite_db)
    print(f"Pipeline executed successfully: {len(records)} records processed.")


if __name__ == '__main__':
    run_pipeline()
