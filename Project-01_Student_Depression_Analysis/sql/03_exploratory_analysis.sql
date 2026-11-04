-- =============================================================================
-- SCRIPT 03: EXPLORATORY DATA ANALYSIS & CLINICAL RISK QUERIES
-- Project: Student Depression Analytics
-- Purpose: Extract actionable statistical insights for Power BI visuals
-- =============================================================================

-- QUERY 1: Executive KPI Overview
SELECT
    COUNT(*) AS Total_Students_Surveyed,
    SUM(Depression_Flag) AS Depressed_Student_Count,
    COUNT(*) - SUM(Depression_Flag) AS Non_Depressed_Student_Count,
    ROUND(100.0 * AVG(Depression_Flag), 2) AS Overall_Depression_Prevalence_Pct,
    ROUND(AVG(CGPA), 2) AS Average_CGPA,
    ROUND(AVG(Cost_without_study), 2) AS Average_Monthly_Living_Cost_BDT
FROM student_depression_cleaned;

-- QUERY 2: Depression Prevalence by Physical Health Condition (The Top Risk Driver)
SELECT
    Health_condition,
    Health_Risk_Category,
    COUNT(*) AS Student_Count,
    SUM(Depression_Flag) AS Depressed_Count,
    ROUND(100.0 * AVG(Depression_Flag), 2) AS Depression_Rate_Pct,
    ROUND(AVG(CGPA), 2) AS Avg_CGPA,
    ROUND(AVG(Cost_without_study), 2) AS Avg_Monthly_Cost_BDT
FROM student_depression_cleaned
GROUP BY Health_condition, Health_Risk_Category, Health_Risk_Sort
ORDER BY Health_Risk_Sort;

-- QUERY 3: The "Social Buffer" Effect - Friend Circle & Relationship Status
SELECT
    Relationship_status,
    friend_circle AS Has_Friend_Circle,
    COUNT(*) AS Total_Students,
    SUM(Depression_Flag) AS Depressed_Count,
    ROUND(100.0 * AVG(Depression_Flag), 2) AS Depression_Rate_Pct
FROM student_depression_cleaned
GROUP BY Relationship_status, friend_circle
ORDER BY Depression_Rate_Pct DESC;

-- QUERY 4: Academic Performance (CGPA Tiers) vs Depression
SELECT
    CGPA_Tier,
    COUNT(*) AS Total_Students,
    SUM(Depression_Flag) AS Depressed_Students,
    ROUND(100.0 * AVG(Depression_Flag), 2) AS Depression_Rate_Pct,
    ROUND(AVG(Cost_without_study), 2) AS Avg_Living_Cost_BDT
FROM student_depression_cleaned
GROUP BY CGPA_Tier, CGPA_Tier_Sort
ORDER BY CGPA_Tier_Sort;

-- QUERY 5: Financial Burden Analysis - Family Background & Cost Brackets
SELECT
    Family_background,
    Cost_Bracket,
    COUNT(*) AS Student_Count,
    SUM(Depression_Flag) AS Depressed_Count,
    ROUND(100.0 * AVG(Depression_Flag), 2) AS Depression_Rate_Pct,
    ROUND(AVG(Cost_without_study), 0) AS Avg_Cost_BDT
FROM student_depression_cleaned
GROUP BY Family_background, Cost_Bracket, Cost_Bracket_Sort
ORDER BY Family_background, Cost_Bracket_Sort;

-- QUERY 6: Geographical Risk Assessment across Bangladesh Divisions
SELECT
    Home_division,
    COUNT(*) AS Surveyed_Students,
    SUM(Depression_Flag) AS Depressed_Count,
    ROUND(100.0 * AVG(Depression_Flag), 2) AS Depression_Rate_Pct,
    ROUND(AVG(CGPA), 2) AS Avg_CGPA,
    ROUND(AVG(Cost_without_study), 0) AS Avg_Cost_BDT
FROM student_depression_cleaned
GROUP BY Home_division
ORDER BY Depression_Rate_Pct DESC;

-- QUERY 7: High-Risk Cohort Identification (Priority Intervention Group)
-- Definition: Students with Abnormal/Critical Health AND No Friend Circle
SELECT
    Student_ID,
    Gender,
    Age,
    Home_division,
    Family_background,
    Living_style,
    Current_semester,
    CGPA,
    Health_condition,
    Cost_without_study
FROM student_depression_cleaned
WHERE Health_condition IN ('Critical', 'Abnormal')
  AND friend_circle = 'No'
ORDER BY CGPA ASC
LIMIT 15;
