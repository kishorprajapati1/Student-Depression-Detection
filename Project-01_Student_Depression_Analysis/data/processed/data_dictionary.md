# Data Dictionary: Student Depression & Mental Health Dataset

## 1. Dataset Metadata
- **Source**: University Student Psychological & Socioeconomic Survey (Bangladesh)
- **Granularity**: 1 row per surveyed student
- **Total Record Count**: 4,464 records
- **Primary Key**: `Student_ID` (Generated surrogate key: `STU-00001` through `STU-04464`)
- **Target Variable**: `Depression` (`Yes` / `No`) & `Depression_Flag` (`1` / `0`)

---

## 2. Field Specifications

| Column Name | Data Type | Nullable | Domain / Allowed Values | Business Definition & Description |
| :--- | :--- | :--- | :--- | :--- |
| **`Student_ID`** | String (Varchar 20) | No | `STU-00001` - `STU-04464` | Unique surrogate identifier assigned to each surveyed student. |
| **`Gender`** | String (Varchar 10) | No | `Female` (2,462), `Male` (2,002) | Self-identified biological gender. |
| **`Age`** | Integer | No | `17` - `28` years (Avg: 22.6) | Chronological age of the student. |
| **`Family_background`** | String (Varchar 30) | No | `Lower Middle class`, `Middle class`, `Rich class` | Socioeconomic status category of the student's family. |
| **`Relationship_status`** | String (Varchar 30) | No | `Single`, `Complicated`, `In a Relationship` | Emotional/romantic relationship status. |
| **`Marital_status`** | String (Varchar 30) | No | `Unmarried`, `Married`, `Separated` | Legal/civil marital status. Note: 201 students report Single + Married (see anomaly note). |
| **`Living_style`** | String (Varchar 30) | No | `Bachelor` (mess/hostel/rented flat), `Family` (residing with parents/family) | Current living arrangement during university studies. |
| **`Current_semester`** | Integer | No | `0` to `13` | Current semester of undergraduate enrollment. 0 = pre-commencement/intake; 13 = extended/thesis term. |
| **`CGPA`** | Decimal (3,2) | No | `2.25` - `4.00` (Avg: 3.41) | Cumulative Grade Point Average on a 4.00 grading scale. |
| **`friend_circle`** | String (Varchar 5) | No | `Yes` (3,215), `No` (1,249) | Self-reported presence of an active peer support social circle. |
| **`Health_condition`** | String (Varchar 20) | No | `Critical`, `Abnormal`, `Normal`, `Good` | Physical health status self-reported or clinically logged. Deterministic factor in depression. |
| **`Cost_without_study`** | Decimal (10,2) | No | `0` - `32,000` BDT (Avg: 11,243) | Estimated monthly non-tuition living expenditure (rent, food, transit, personal) in Bangladeshi Taka. |
| **`Home_division`** | String (Varchar 30) | No | 8 Administrative Divisions of Bangladesh | Geographic origin of the student: Dhaka, Chittagong, Rajshahi, Khulna, Sylhet, Rangpur, Barisal, Mymensingh. |
| **`Depression`** | String (Varchar 5) | No | `Yes` (1,201), `No` (3,263) | Primary clinical outcome indicator: Positive or Negative for depressive symptoms. |
| **`Depression_Flag`** | Integer | No | `1` (Positive), `0` (Negative) | Binary encoded indicator for optimized DAX calculations (`SUM`, `AVG`). |
| **`CGPA_Tier`** | String (Varchar 40) | No | 4 Academic Tiers | Derived classification: High Distinction, First Class, Second Class Upper, Pass/Needs Support. |
| **`CGPA_Tier_Sort`** | Integer | No | `1` - `4` | Sort key for `CGPA_Tier` to ensure non-alphabetical visual order. |
| **`Academic_Stage`** | String (Varchar 40) | No | 4 Stages | Derived grouping: Foundation (0), Early Stage (1-4), Mid Stage (5-8), Graduating/Extended (9+). |
| **`Academic_Stage_Sort`** | Integer | No | `0` - `3` | Sort key for `Academic_Stage`. |
| **`Cost_Bracket`** | String (Varchar 40) | No | 4 Expense Brackets | Low (<5k), Moderate (5k-12k), High (12k-20k), Very High (>20k BDT). |
| **`Cost_Bracket_Sort`** | Integer | No | `1` - `4` | Sort key for `Cost_Bracket`. |
| **`Health_Risk_Category`**| String (Varchar 40) | No | 4 Risk Levels | Severe Clinical Risk (Critical), Elevated Risk (Abnormal), Low Risk (Normal), Optimal (Good). |
| **`Health_Risk_Sort`** | Integer | No | `1` - `4` | Sort key for `Health_Risk_Category`. |

---

## 3. Data Integrity & Anomaly Notes

1. **UTF-8 BOM Header**: The raw CSV file contains a byte-order mark (`\ufeff`) on the header line. The ingestion script cleanly strips this with `utf-8-sig` encoding.
2. **Relationship vs. Marital Status Cross-Attribute Nuance**:
   - 201 respondents answered `Single` under `Relationship_status` and `Married` under `Marital_status`.
   - In sociological survey methodology, young adults frequently view `Relationship_status` as their active dating life (e.g. spouse lives in another town, emotionally disconnected, or separated in practice) while answering `Married` legally.
   - We preserved raw data integrity without manual alteration and added this observation to the quality audit report.
3. **Zero Living Cost Entries**: Two records reported `0` under `Cost_without_study`. These correspond to students living with extended family with zero out-of-pocket expenses.
