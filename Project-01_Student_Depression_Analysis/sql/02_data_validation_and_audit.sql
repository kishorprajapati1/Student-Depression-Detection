-- =============================================================================
-- SCRIPT 02: DATA QUALITY AUDIT & ANOMALY DETECTION QUERIES
-- Project: Student Depression Analytics
-- Purpose: Verify completeness, boundary constraints, and consistency
-- =============================================================================

-- TEST 1: Completeness & Null Checks
SELECT
    COUNT(*) AS Total_Records,
    SUM(CASE WHEN Student_ID IS NULL OR Student_ID = '' THEN 1 ELSE 0 END) AS Null_Student_ID,
    SUM(CASE WHEN Gender IS NULL OR Gender = '' THEN 1 ELSE 0 END) AS Null_Gender,
    SUM(CASE WHEN Age IS NULL THEN 1 ELSE 0 END) AS Null_Age,
    SUM(CASE WHEN CGPA IS NULL THEN 1 ELSE 0 END) AS Null_CGPA,
    SUM(CASE WHEN Health_condition IS NULL OR Health_condition = '' THEN 1 ELSE 0 END) AS Null_Health,
    SUM(CASE WHEN Depression IS NULL OR Depression = '' THEN 1 ELSE 0 END) AS Null_Depression
FROM student_depression_cleaned;

-- TEST 2: Range & Boundary Validation
SELECT
    'Age Bounds (15 - 35)' AS Constraint_Name,
    COUNT(*) AS Violation_Count
FROM student_depression_cleaned
WHERE Age < 15 OR Age > 35

UNION ALL

SELECT
    'CGPA Bounds (0.00 - 4.00)' AS Constraint_Name,
    COUNT(*) AS Violation_Count
FROM student_depression_cleaned
WHERE CGPA < 0.00 OR CGPA > 4.00

UNION ALL

SELECT
    'Semester Bounds (0 - 14)' AS Constraint_Name,
    COUNT(*) AS Violation_Count
FROM student_depression_cleaned
WHERE Current_semester < 0 OR Current_semester > 14

UNION ALL

SELECT
    'Living Cost Non-Negative' AS Constraint_Name,
    COUNT(*) AS Violation_Count
FROM student_depression_cleaned
WHERE Cost_without_study < 0;

-- TEST 3: Duplicate Row & Primary Key Uniqueness
SELECT
    Student_ID,
    COUNT(*) AS Occurrence_Count
FROM student_depression_cleaned
GROUP BY Student_ID
HAVING COUNT(*) > 1;

-- TEST 4: Domain Cardinality & Categorical Integrity
SELECT 'Gender' AS Field, Gender AS Value, COUNT(*) AS Count FROM student_depression_cleaned GROUP BY Gender
UNION ALL
SELECT 'Depression' AS Field, Depression AS Value, COUNT(*) AS Count FROM student_depression_cleaned GROUP BY Depression
UNION ALL
SELECT 'Family_background' AS Field, Family_background AS Value, COUNT(*) AS Count FROM student_depression_cleaned GROUP BY Family_background
UNION ALL
SELECT 'Health_condition' AS Field, Health_condition AS Value, COUNT(*) AS Count FROM student_depression_cleaned GROUP BY Health_condition;

-- TEST 5: Cross-Attribute Logical Consistency (Relationship vs Marital Status)
SELECT
    Relationship_status,
    Marital_status,
    COUNT(*) AS Student_Count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM student_depression_cleaned), 2) AS Pct_Of_Total
FROM student_depression_cleaned
GROUP BY Relationship_status, Marital_status
ORDER BY Student_Count DESC;
