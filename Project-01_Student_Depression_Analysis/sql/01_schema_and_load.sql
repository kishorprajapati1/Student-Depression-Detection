-- =============================================================================
-- SCRIPT 01: DDL SCHEMA & STAR SCHEMA ETL PIPELINE
-- Project: Student Depression Analytics & Risk Modeling
-- Compatible with: SQLite, PostgreSQL, SQL Server, MySQL
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. STAGING TABLE (Denormalized Data Layer)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_student_depression;

CREATE TABLE stg_student_depression (
    Student_ID             VARCHAR(20) PRIMARY KEY,
    Gender                 VARCHAR(10) NOT NULL,
    Age                    INTEGER NOT NULL,
    Family_background      VARCHAR(30) NOT NULL,
    Relationship_status    VARCHAR(30) NOT NULL,
    Marital_status         VARCHAR(30) NOT NULL,
    Living_style           VARCHAR(30) NOT NULL,
    Current_semester       INTEGER NOT NULL,
    CGPA                   DECIMAL(3, 2) NOT NULL,
    friend_circle          VARCHAR(5) NOT NULL,
    Health_condition       VARCHAR(20) NOT NULL,
    Cost_without_study     DECIMAL(10, 2) NOT NULL,
    Home_division          VARCHAR(30) NOT NULL,
    Depression             VARCHAR(5) NOT NULL,
    Depression_Flag        INTEGER NOT NULL,
    CGPA_Tier              VARCHAR(40) NOT NULL,
    CGPA_Tier_Sort         INTEGER NOT NULL,
    Academic_Stage         VARCHAR(40) NOT NULL,
    Academic_Stage_Sort    INTEGER NOT NULL,
    Cost_Bracket           VARCHAR(40) NOT NULL,
    Cost_Bracket_Sort      INTEGER NOT NULL,
    Health_Risk_Category   VARCHAR(40) NOT NULL,
    Health_Risk_Sort       INTEGER NOT NULL
);

-- Note: The staging table is loaded directly from student_depression_cleaned.csv 
-- or populated via data_validation_pipeline.py.

-- -----------------------------------------------------------------------------
-- 2. STAR SCHEMA DIMENSION TABLES
-- -----------------------------------------------------------------------------

-- DIMENSION 1: Demographics & Domestic Profile
DROP TABLE IF EXISTS Dim_Demographics;
CREATE TABLE Dim_Demographics (
    Demographic_Key        INTEGER PRIMARY KEY AUTOINCREMENT,
    Gender                 VARCHAR(10) NOT NULL,
    Age                    INTEGER NOT NULL,
    Family_background      VARCHAR(30) NOT NULL,
    Relationship_status    VARCHAR(30) NOT NULL,
    Marital_status         VARCHAR(30) NOT NULL,
    Living_style           VARCHAR(30) NOT NULL
);

-- DIMENSION 2: Academic Profile
DROP TABLE IF EXISTS Dim_Academic;
CREATE TABLE Dim_Academic (
    Academic_Key           INTEGER PRIMARY KEY AUTOINCREMENT,
    Current_semester       INTEGER NOT NULL,
    Academic_Stage         VARCHAR(40) NOT NULL,
    Academic_Stage_Sort    INTEGER NOT NULL
);

-- DIMENSION 3: Health & Social Network Profile
DROP TABLE IF EXISTS Dim_Health_Social;
CREATE TABLE Dim_Health_Social (
    Health_Social_Key      INTEGER PRIMARY KEY AUTOINCREMENT,
    Health_condition       VARCHAR(20) NOT NULL,
    Health_Risk_Category   VARCHAR(40) NOT NULL,
    Health_Risk_Sort       INTEGER NOT NULL,
    friend_circle          VARCHAR(5) NOT NULL
);

-- DIMENSION 4: Geography (Divisions & Zones of Bangladesh)
DROP TABLE IF EXISTS Dim_Geography;
CREATE TABLE Dim_Geography (
    Geography_Key          INTEGER PRIMARY KEY AUTOINCREMENT,
    Home_division          VARCHAR(30) NOT NULL,
    Zone                   VARCHAR(20) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 3. FACT TABLE: Student Mental Health Assessment
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS Fact_Student_Assessment;
CREATE TABLE Fact_Student_Assessment (
    Student_ID             VARCHAR(20) PRIMARY KEY,
    Demographic_Key        INTEGER NOT NULL,
    Academic_Key           INTEGER NOT NULL,
    Health_Social_Key      INTEGER NOT NULL,
    Geography_Key          INTEGER NOT NULL,
    CGPA                   DECIMAL(3, 2) NOT NULL,
    CGPA_Tier              VARCHAR(40) NOT NULL,
    CGPA_Tier_Sort         INTEGER NOT NULL,
    Cost_without_study     DECIMAL(10, 2) NOT NULL,
    Cost_Bracket           VARCHAR(40) NOT NULL,
    Cost_Bracket_Sort      INTEGER NOT NULL,
    Depression             VARCHAR(5) NOT NULL,
    Depression_Flag        INTEGER NOT NULL,
    FOREIGN KEY (Demographic_Key) REFERENCES Dim_Demographics (Demographic_Key),
    FOREIGN KEY (Academic_Key) REFERENCES Dim_Academic (Academic_Key),
    FOREIGN KEY (Health_Social_Key) REFERENCES Dim_Health_Social (Health_Social_Key),
    FOREIGN KEY (Geography_Key) REFERENCES Dim_Geography (Geography_Key)
);

-- -----------------------------------------------------------------------------
-- 4. ETL POPULATION QUERIES (Transforms Staging Data into Star Schema)
-- -----------------------------------------------------------------------------

-- Populate Dim_Demographics
INSERT INTO Dim_Demographics (Gender, Age, Family_background, Relationship_status, Marital_status, Living_style)
SELECT DISTINCT 
    Gender, Age, Family_background, Relationship_status, Marital_status, Living_style
FROM student_depression_cleaned;

-- Populate Dim_Academic
INSERT INTO Dim_Academic (Current_semester, Academic_Stage, Academic_Stage_Sort)
SELECT DISTINCT 
    Current_semester, Academic_Stage, Academic_Stage_Sort
FROM student_depression_cleaned;

-- Populate Dim_Health_Social
INSERT INTO Dim_Health_Social (Health_condition, Health_Risk_Category, Health_Risk_Sort, friend_circle)
SELECT DISTINCT 
    Health_condition, Health_Risk_Category, Health_Risk_Sort, friend_circle
FROM student_depression_cleaned;

-- Populate Dim_Geography
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

-- Populate Fact_Student_Assessment with Surrogate Foreign Keys
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
JOIN Dim_Demographics d 
    ON s.Gender = d.Gender 
   AND s.Age = d.Age 
   AND s.Family_background = d.Family_background 
   AND s.Relationship_status = d.Relationship_status 
   AND s.Marital_status = d.Marital_status 
   AND s.Living_style = d.Living_style
JOIN Dim_Academic a 
    ON s.Current_semester = a.Current_semester
JOIN Dim_Health_Social h 
    ON s.Health_condition = h.Health_condition 
   AND s.friend_circle = h.friend_circle
JOIN Dim_Geography g 
    ON s.Home_division = g.Home_division;
