-- =============================================================================
-- SCRIPT 01: DDL SCHEMA & STAR SCHEMA ARCHITECTURE
-- Project: Student Depression Analytics & Risk Modeling
-- Compatible with: PostgreSQL, SQL Server, SQLite, MySQL
-- =============================================================================

-- 1. STAGING TABLE (Denormalized Raw Layer)
DROP TABLE IF EXISTS stg_student_depression;

CREATE TABLE stg_student_depression (
    Student_ID             VARCHAR(20) PRIMARY KEY,
    Gender                 VARCHAR(10) NOT NULL,
    Age                    INT NOT NULL,
    Family_background      VARCHAR(30) NOT NULL,
    Relationship_status    VARCHAR(30) NOT NULL,
    Marital_status         VARCHAR(30) NOT NULL,
    Living_style           VARCHAR(30) NOT NULL,
    Current_semester       INT NOT NULL,
    CGPA                   DECIMAL(3, 2) NOT NULL,
    friend_circle          VARCHAR(5) NOT NULL,
    Health_condition       VARCHAR(20) NOT NULL,
    Cost_without_study     DECIMAL(10, 2) NOT NULL,
    Home_division          VARCHAR(30) NOT NULL,
    Depression             VARCHAR(5) NOT NULL,
    Depression_Flag        INT NOT NULL,
    CGPA_Tier              VARCHAR(40) NOT NULL,
    CGPA_Tier_Sort         INT NOT NULL,
    Academic_Stage         VARCHAR(40) NOT NULL,
    Academic_Stage_Sort    INT NOT NULL,
    Cost_Bracket           VARCHAR(40) NOT NULL,
    Cost_Bracket_Sort      INT NOT NULL,
    Health_Risk_Category   VARCHAR(40) NOT NULL,
    Health_Risk_Sort       INT NOT NULL
);

-- =============================================================================
-- STAR SCHEMA ARCHITECTURE (Dimensional Model for Enterprise BI)
-- =============================================================================

-- DIMENSION 1: Demographics & Domestic Profile
DROP TABLE IF EXISTS Dim_Demographics;
CREATE TABLE Dim_Demographics (
    Demographic_Key        INT PRIMARY KEY,
    Gender                 VARCHAR(10) NOT NULL,
    Age                    INT NOT NULL,
    Family_background      VARCHAR(30) NOT NULL,
    Relationship_status    VARCHAR(30) NOT NULL,
    Marital_status         VARCHAR(30) NOT NULL,
    Living_style           VARCHAR(30) NOT NULL
);

-- DIMENSION 2: Academic Profile
DROP TABLE IF EXISTS Dim_Academic;
CREATE TABLE Dim_Academic (
    Academic_Key           INT PRIMARY KEY,
    Current_semester       INT NOT NULL,
    Academic_Stage         VARCHAR(40) NOT NULL,
    Academic_Stage_Sort    INT NOT NULL
);

-- DIMENSION 3: Health & Social Risk
DROP TABLE IF EXISTS Dim_Health_Social;
CREATE TABLE Dim_Health_Social (
    Health_Social_Key      INT PRIMARY KEY,
    Health_condition       VARCHAR(20) NOT NULL,
    Health_Risk_Category   VARCHAR(40) NOT NULL,
    Health_Risk_Sort       INT NOT NULL,
    friend_circle          VARCHAR(5) NOT NULL
);

-- DIMENSION 4: Geography (Divisions of Bangladesh)
DROP TABLE IF EXISTS Dim_Geography;
CREATE TABLE Dim_Geography (
    Geography_Key          INT PRIMARY KEY,
    Home_division          VARCHAR(30) NOT NULL,
    Zone                   VARCHAR(20) NOT NULL -- East, Central, West, North, South
);

-- FACT TABLE: Student Survey Responses & Risk Measurements
DROP TABLE IF EXISTS Fact_Student_Assessment;
CREATE TABLE Fact_Student_Assessment (
    Assessment_ID          VARCHAR(20) PRIMARY KEY,
    Demographic_Key        INT NOT NULL,
    Academic_Key           INT NOT NULL,
    Health_Social_Key      INT NOT NULL,
    Geography_Key          INT NOT NULL,
    CGPA                   DECIMAL(3, 2) NOT NULL,
    CGPA_Tier              VARCHAR(40) NOT NULL,
    CGPA_Tier_Sort         INT NOT NULL,
    Monthly_Living_Cost    DECIMAL(10, 2) NOT NULL,
    Cost_Bracket           VARCHAR(40) NOT NULL,
    Cost_Bracket_Sort      INT NOT NULL,
    Depression_Reported    VARCHAR(5) NOT NULL,
    Depression_Flag        INT NOT NULL, -- 1 = Positive, 0 = Negative
    High_Risk_Flag         INT NOT NULL  -- 1 if Critical health or Abnormal + Single
);
