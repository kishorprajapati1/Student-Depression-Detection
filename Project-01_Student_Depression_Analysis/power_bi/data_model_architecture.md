# Power BI Data Model & Architecture Guide

## 1. Architectural Overview: Flat Table vs. Star Schema

As a future Power BI Developer transitioning from Support Engineering, one of the most common mistakes candidates make in technical interviews is leaving data as **a single wide flat table**.

| Architectural Dimension | Flat Table (Beginner) | Star Schema (Enterprise Power BI) |
| :--- | :--- | :--- |
| **Data Engine Performance** | Redundant string columns consume excessive RAM in the VertiPaq engine. | Dimension tables deduplicate text; Fact table stores lean integers and surrogate keys. |
| **Filter Context & DAX** | `CALCULATE` and `ALL` filters must scan wide tables, risking subtle filter-bleed bugs. | Clear 1-to-Many (`1:*`) one-way relationships guarantee predictable filter propagation. |
| **Scalability** | Adding new surveys or semesters duplicates customer/student attributes. | Incremental refresh and new transaction dates attach cleanly to existing dimensions. |
| **UX & Field List** | 25+ columns cluttering a single visual pane, confusing report builders. | Logical folders: Demographics, Academic, Health, Geography, and a dedicated `_Measures` table. |

---

## 2. Dimensional Model Entity-Relationship Diagram

```mermaid
erDiagram
    Dim_Demographics ||--o{ Fact_Student_Assessment : "Demographic_Key"
    Dim_Academic ||--o{ Fact_Student_Assessment : "Academic_Key"
    Dim_Health_Social ||--o{ Fact_Student_Assessment : "Health_Social_Key"
    Dim_Geography ||--o{ Fact_Student_Assessment : "Geography_Key"

    Fact_Student_Assessment {
        string Student_ID PK
        int Demographic_Key FK
        int Academic_Key FK
        int Health_Social_Key FK
        int Geography_Key FK
        float CGPA
        string CGPA_Tier
        int CGPA_Tier_Sort
        float Cost_without_study
        string Cost_Bracket
        int Cost_Bracket_Sort
        string Depression
        int Depression_Flag
        int Predicted_Depression
        string Predicted_Depression_Label
        float Depression_Risk_Score
        string Risk_Tier
        int Risk_Tier_Sort
        string Intervention_Priority
        string Prediction_Outcome
    }

    Dim_Demographics {
        int Demographic_Key PK
        string Gender
        int Age
        string Family_background
        string Relationship_status
        string Marital_status
        string Living_style
    }

    Dim_Academic {
        int Academic_Key PK
        int Current_semester
        string Academic_Stage
        int Academic_Stage_Sort
    }

    Dim_Health_Social {
        int Health_Social_Key PK
        string Health_condition
        string Health_Risk_Category
        int Health_Risk_Sort
        string friend_circle
    }

    Dim_Geography {
        int Geography_Key PK
        string Home_division
        string Zone
    }

    Dim_ML_Feature_Importance {
        int Feature_Key PK
        string Feature_Variable
        string Feature_Category
        float Importance_Weight
        int Importance_Rank
    }

    Dim_ML_Model_Metrics {
        string Metric_Name PK
        float Metric_Value
        string Metric_Format
        string Description
    }
```

---

## 3. Relationship Specifications

1. **`Dim_Demographics[Demographic_Key]` $\to$ `Fact_Student_Assessment[Demographic_Key]`**
   - **Cardinality**: 1-to-Many (`1:*`)
   - **Cross-filter direction**: Single (Dimension filters Fact)
   - **Enforce Referent Integrity**: Enabled

2. **`Dim_Academic[Academic_Key]` $\to$ `Fact_Student_Assessment[Academic_Key]`**
   - **Cardinality**: 1-to-Many (`1:*`)
   - **Cross-filter direction**: Single
   - **Enforce Referent Integrity**: Enabled

3. **`Dim_Health_Social[Health_Social_Key]` $\to$ `Fact_Student_Assessment[Health_Social_Key]`**
   - **Cardinality**: 1-to-Many (`1:*`)
   - **Cross-filter direction**: Single
   - **Enforce Referent Integrity**: Enabled

4. **`Dim_Geography[Geography_Key]` $\to$ `Fact_Student_Assessment[Geography_Key]`**
   - **Cardinality**: 1-to-Many (`1:*`)
   - **Cross-filter direction**: Single
   - **Enforce Referent Integrity**: Enabled

5. **`Dim_ML_Feature_Importance` & `Dim_ML_Model_Metrics`**:
   - Standalone analytical reference tables for feature importance tornado charts and model governance cards (disconnected parameter/reporting tables, filtered dynamically via DAX).

---

## 4. Crucial "Sort By Column" Settings in Power BI Desktop

If you do not configure **Sort by Column**, Power BI sorts textual categories alphabetically (e.g. `Critical Risk` or `High Risk` sorting out of clinical order). This looks unprofessional in a portfolio.

Configure the following column properties in **Model View**:

1. Select `CGPA_Tier` $\to$ Set **Sort by column** = `CGPA_Tier_Sort`
2. Select `Academic_Stage` $\to$ Set **Sort by column** = `Academic_Stage_Sort`
3. Select `Cost_Bracket` $\to$ Set **Sort by column** = `Cost_Bracket_Sort`
4. Select `Health_Risk_Category` $\to$ Set **Sort by column** = `Health_Risk_Sort`
5. Select `Risk_Tier` $\to$ Set **Sort by column** = `Risk_Tier_Sort` (Low Risk $\to$ Moderate Risk $\to$ High Risk $\to$ Critical Risk)

> [!TIP]
> Always hide the `_Sort` columns in the Report View (`IsHidden = True`) so end-users never see redundant helper columns in the field picker.
