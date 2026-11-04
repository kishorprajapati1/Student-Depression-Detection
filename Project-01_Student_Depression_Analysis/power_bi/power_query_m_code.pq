// =============================================================================
// POWER QUERY (M CODE): ENTERPRISE STAR SCHEMA WITH ML INTEGRATION
// Project: Student Depression Analytics & Predictive Risk Modeling
// =============================================================================

// -----------------------------------------------------------------------------
// 1. PARAMETER: pDataFilePath
// Purpose: Eliminates hardcoded absolute paths so the model can be refreshed
//          on any machine or environment without modifying transformation code.
// -----------------------------------------------------------------------------
let
    pDataFilePath = "d:\PowerBi Projects\Project-01_Student_Depression_Analysis\data\processed\student_depression_ml_scored.csv" 
        meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
in
    pDataFilePath


// -----------------------------------------------------------------------------
// 2. QUERY: stg_StudentDepression (Base Ingestion & Type Enforcement)
// -----------------------------------------------------------------------------
let
    Source = Csv.Document(
        File.Contents(pDataFilePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    SetDataTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"Student_ID", type text},
        {"Gender", type text},
        {"Age", Int64.Type},
        {"Family_background", type text},
        {"Relationship_status", type text},
        {"Marital_status", type text},
        {"Living_style", type text},
        {"Current_semester", Int64.Type},
        {"CGPA", type number},
        {"friend_circle", type text},
        {"Health_condition", type text},
        {"Cost_without_study", type number},
        {"Home_division", type text},
        {"Depression", type text},
        {"Depression_Flag", Int64.Type},
        {"CGPA_Tier", type text},
        {"CGPA_Tier_Sort", Int64.Type},
        {"Academic_Stage", type text},
        {"Academic_Stage_Sort", Int64.Type},
        {"Cost_Bracket", type text},
        {"Cost_Bracket_Sort", Int64.Type},
        {"Health_Risk_Category", type text},
        {"Health_Risk_Sort", Int64.Type},
        {"Predicted_Depression", Int64.Type},
        {"Predicted_Depression_Label", type text},
        {"Depression_Risk_Score", type number},
        {"Risk_Tier", type text},
        {"Risk_Tier_Sort", Int64.Type},
        {"Intervention_Priority", type text},
        {"Prediction_Outcome", type text}
    })
in
    SetDataTypes


// -----------------------------------------------------------------------------
// 3. DIMENSION: Dim_Demographics
// -----------------------------------------------------------------------------
let
    Source = stg_StudentDepression,
    SelectColumns = Table.SelectColumns(Source, {
        "Gender", "Age", "Family_background", "Relationship_status", 
        "Marital_status", "Living_style"
    }),
    RemoveDuplicates = Table.Distinct(SelectColumns),
    AddSurrogateKey = Table.AddIndexColumn(RemoveDuplicates, "Demographic_Key", 1, 1, Int64.Type)
in
    AddSurrogateKey


// -----------------------------------------------------------------------------
// 4. DIMENSION: Dim_Academic
// -----------------------------------------------------------------------------
let
    Source = stg_StudentDepression,
    SelectColumns = Table.SelectColumns(Source, {
        "Current_semester", "Academic_Stage", "Academic_Stage_Sort"
    }),
    RemoveDuplicates = Table.Distinct(SelectColumns),
    AddSurrogateKey = Table.AddIndexColumn(RemoveDuplicates, "Academic_Key", 1, 1, Int64.Type)
in
    AddSurrogateKey


// -----------------------------------------------------------------------------
// 5. DIMENSION: Dim_Health_Social
// -----------------------------------------------------------------------------
let
    Source = stg_StudentDepression,
    SelectColumns = Table.SelectColumns(Source, {
        "Health_condition", "Health_Risk_Category", "Health_Risk_Sort", "friend_circle"
    }),
    RemoveDuplicates = Table.Distinct(SelectColumns),
    AddSurrogateKey = Table.AddIndexColumn(RemoveDuplicates, "Health_Social_Key", 1, 1, Int64.Type)
in
    AddSurrogateKey


// -----------------------------------------------------------------------------
// 6. DIMENSION: Dim_Geography
// -----------------------------------------------------------------------------
let
    Source = stg_StudentDepression,
    SelectColumns = Table.SelectColumns(Source, {"Home_division"}),
    RemoveDuplicates = Table.Distinct(SelectColumns),
    AddZone = Table.AddColumn(RemoveDuplicates, "Zone", each 
        if [Home_division] = "Dhaka" or [Home_division] = "Mymensingh" then "Central"
        else if [Home_division] = "Chittagong" or [Home_division] = "Sylhet" then "Eastern"
        else if [Home_division] = "Rajshahi" or [Home_division] = "Rangpur" then "Northern"
        else "South-Western", type text),
    AddSurrogateKey = Table.AddIndexColumn(AddZone, "Geography_Key", 1, 1, Int64.Type)
in
    AddSurrogateKey


// -----------------------------------------------------------------------------
// 7. FACT TABLE: Fact_Student_Assessment
// -----------------------------------------------------------------------------
let
    Source = stg_StudentDepression,

    // Merge Demographic Key
    MergeDemo = Table.NestedJoin(Source, {"Gender", "Age", "Family_background", "Relationship_status", "Marital_status", "Living_style"}, Dim_Demographics, {"Gender", "Age", "Family_background", "Relationship_status", "Marital_status", "Living_style"}, "Dim_Demographics", JoinKind.LeftOuter),
    ExpandDemo = Table.ExpandTableColumn(MergeDemo, "Dim_Demographics", {"Demographic_Key"}, {"Demographic_Key"}),

    // Merge Academic Key
    MergeAcademic = Table.NestedJoin(ExpandDemo, {"Current_semester"}, Dim_Academic, {"Current_semester"}, "Dim_Academic", JoinKind.LeftOuter),
    ExpandAcademic = Table.ExpandTableColumn(MergeAcademic, "Dim_Academic", {"Academic_Key"}, {"Academic_Key"}),

    // Merge Health Social Key
    MergeHealth = Table.NestedJoin(ExpandAcademic, {"Health_condition", "friend_circle"}, Dim_Health_Social, {"Health_condition", "friend_circle"}, "Dim_Health_Social", JoinKind.LeftOuter),
    ExpandHealth = Table.ExpandTableColumn(MergeHealth, "Dim_Health_Social", {"Health_Social_Key"}, {"Health_Social_Key"}),

    // Merge Geography Key
    MergeGeo = Table.NestedJoin(ExpandHealth, {"Home_division"}, Dim_Geography, {"Home_division"}, "Dim_Geography", JoinKind.LeftOuter),
    ExpandGeo = Table.ExpandTableColumn(MergeGeo, "Dim_Geography", {"Geography_Key"}, {"Geography_Key"}),

    // Fact Table Columns (including ML Risk Scores and Early Intervention Priority)
    SelectFactColumns = Table.SelectColumns(ExpandGeo, {
        "Student_ID", "Demographic_Key", "Academic_Key", "Health_Social_Key", "Geography_Key",
        "CGPA", "CGPA_Tier", "CGPA_Tier_Sort", "Cost_without_study", "Cost_Bracket", "Cost_Bracket_Sort",
        "Depression", "Depression_Flag",
        "Predicted_Depression", "Predicted_Depression_Label", "Depression_Risk_Score",
        "Risk_Tier", "Risk_Tier_Sort", "Intervention_Priority", "Prediction_Outcome"
    })
in
    SelectFactColumns


// -----------------------------------------------------------------------------
// 8. ML DIMENSION: Dim_ML_Feature_Importance
// Purpose: Enables Tornado & Bar visual of driving factors directly in Power BI
// -----------------------------------------------------------------------------
let
    pFeatureFilePath = Text.Replace(pDataFilePath, "student_depression_ml_scored.csv", "ml_feature_importance.csv"),
    Source = Csv.Document(
        File.Contents(pFeatureFilePath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    SetDataTypes = Table.TransformColumnTypes(PromoteHeaders, {
        {"Feature_Key", Int64.Type},
        {"Feature_Variable", type text},
        {"Feature_Category", type text},
        {"Importance_Weight", type number},
        {"Importance_Rank", Int64.Type}
    })
in
    SetDataTypes
