// =============================================================================
// POWER QUERY (M CODE): DATA INGESTION, TRANSFORMATION & STAR SCHEMA MODELING
// Project: Student Depression Analytics & Risk Modeling
// =============================================================================

// -----------------------------------------------------------------------------
// QUERY 1: Source_StudentDepression (Base Extraction & Type Coercion)
// -----------------------------------------------------------------------------
let
    // 1. Ingest Raw CSV File
    Source = Csv.Document(
        File.Contents("D:\PowerBi Projects\Project-01_Student_Depression_Analysis\data\raw\student_depression_raw.csv"),
        [Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    
    // 2. Promote Headers
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    
    // 3. Trim All Text Columns (Defensive Cleaning against trailing/leading spaces)
    TrimText = Table.TransformColumns(PromoteHeaders, {
        {"Gender", Text.Trim, type text},
        {"Family_background", Text.Trim, type text},
        {"Relationship_status", Text.Trim, type text},
        {"Marital_status", Text.Trim, type text},
        {"Living_style", Text.Trim, type text},
        {"friend_circle", Text.Trim, type text},
        {"Health_condition", Text.Trim, type text},
        {"Home_division", Text.Trim, type text},
        {"Depression", Text.Trim, type text}
    }),
    
    // 4. Strongly Type Each Column
    SetDataTypes = Table.TransformColumnTypes(TrimText, {
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
        {"Depression", type text}
    }),
    
    // 5. Add Student Surrogate Key (STU-00001, etc.)
    AddIndex = Table.AddIndexColumn(SetDataTypes, "Index", 1, 1, Int64.Type),
    AddStudentID = Table.AddColumn(AddIndex, "Student_ID", each "STU-" & Text.PadStart(Text.From([Index]), 5, "0"), type text),
    RemoveIndex = Table.RemoveColumns(AddStudentID, {"Index"}),
    
    // 6. Binary Depression Flag (0 or 1) for High-Performance DAX Aggregations
    AddDepressionFlag = Table.AddColumn(RemoveIndex, "Depression_Flag", each if [Depression] = "Yes" then 1 else 0, Int64.Type),
    
    // 7. CGPA Tier Classification
    AddCGPATier = Table.AddColumn(AddDepressionFlag, "CGPA_Tier", each 
        if [CGPA] >= 3.80 then "High Distinction (3.80 - 4.00)"
        else if [CGPA] >= 3.50 then "First Class (3.50 - 3.79)"
        else if [CGPA] >= 3.00 then "Second Class Upper (3.00 - 3.49)"
        else "Pass / Needs Support (< 3.00)", type text),
        
    AddCGPATierSort = Table.AddColumn(AddCGPATier, "CGPA_Tier_Sort", each 
        if [CGPA] >= 3.80 then 1
        else if [CGPA] >= 3.50 then 2
        else if [CGPA] >= 3.00 then 3
        else 4, Int64.Type),

    // 8. Academic Stage Classification
    AddAcademicStage = Table.AddColumn(AddCGPATierSort, "Academic_Stage", each 
        if [Current_semester] = 0 then "Foundation / Intake (Sem 0)"
        else if [Current_semester] <= 4 then "Early Stage (Sem 1-4)"
        else if [Current_semester] <= 8 then "Mid Stage (Sem 5-8)"
        else "Graduating / Extended (Sem 9+)", type text),
        
    AddAcademicStageSort = Table.AddColumn(AddAcademicStage, "Academic_Stage_Sort", each 
        if [Current_semester] = 0 then 0
        else if [Current_semester] <= 4 then 1
        else if [Current_semester] <= 8 then 2
        else 3, Int64.Type),

    // 9. Cost Bracket Classification (Monthly Living Cost in BDT)
    AddCostBracket = Table.AddColumn(AddAcademicStageSort, "Cost_Bracket", each 
        if [Cost_without_study] < 5000 then "Low (< 5k BDT)"
        else if [Cost_without_study] <= 12000 then "Moderate (5k - 12k BDT)"
        else if [Cost_without_study] <= 20000 then "High (12k - 20k BDT)"
        else "Very High (> 20k BDT)", type text),
        
    AddCostBracketSort = Table.AddColumn(AddCostBracket, "Cost_Bracket_Sort", each 
        if [Cost_without_study] < 5000 then 1
        else if [Cost_without_study] <= 12000 then 2
        else if [Cost_without_study] <= 20000 then 3
        else 4, Int64.Type),

    // 10. Health Clinical Risk Classification
    AddHealthRisk = Table.AddColumn(AddCostBracketSort, "Health_Risk_Category", each 
        if [Health_condition] = "Critical" then "Severe Clinical Risk"
        else if [Health_condition] = "Abnormal" then "Elevated Risk"
        else if [Health_condition] = "Normal" then "Low Risk"
        else "Optimal / Healthy", type text),
        
    AddHealthRiskSort = Table.AddColumn(AddHealthRisk, "Health_Risk_Sort", each 
        if [Health_condition] = "Critical" then 1
        else if [Health_condition] = "Abnormal" then 2
        else if [Health_condition] = "Normal" then 3
        else 4, Int64.Type)
in
    AddHealthRiskSort
