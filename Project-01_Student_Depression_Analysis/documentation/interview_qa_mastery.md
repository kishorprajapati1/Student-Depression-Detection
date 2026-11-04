# Power BI Developer Career Transition: Interview Q&A & Method Mastery Guide

> **Candidate Persona**: Transitioning from Support Engineer to Power BI / Business Intelligence Developer.  
> **Key Strength**: Strong diagnostic troubleshooting, data integrity validation, root-cause analysis, and customer-first problem solving.

---

## Part 1: "Why This Method?" Architectural Trade-Off Analysis

### Q1: Where should data cleaning occur: Python, SQL, Power Query (M), or DAX?
- **Our Method**: We cleaned and validated data upstream using **Python / SQL**, then finalized data types in **Power Query (M)**, and kept **DAX exclusively for dynamic aggregations**.
- **Is it necessary?**: Yes, according to the official **Roche's Maxim of Data Transformation**: *"Transform data as far upstream as possible and as far downstream as necessary."*
- **Can it be done in an easier way?**: A beginner might just load the raw CSV into Power BI Desktop and create 15 Calculated Columns using DAX `IF(...)`.
- **Why that beginner approach causes bugs & crashes**:
  1. DAX Calculated Columns are evaluated row-by-row during model refresh and stored uncompressed in RAM. They bloat memory and cannot respond dynamically to slicers.
  2. If raw CSV data has trailing spaces (e.g. `"Dhaka "`), DAX string comparisons fail silently or create duplicate legend categories.
  3. Power Query M code executes during the ETL extraction phase and leverages query folding (in SQL databases), producing zero runtime overhead.

---

### Q2: Why build a Star Schema instead of using the raw single table?
- **Our Method**: We mapped the 13 columns into a Star Schema with 1 Fact table (`Fact_Student_Assessment`) and 4 Dimension tables (`Dim_Demographics`, `Dim_Academic`, `Dim_Health_Social`, `Dim_Geography`).
- **Is it necessary?**: For 4,464 rows, a flat table works fine technically, but in an enterprise with 50 million rows, flat tables crash the VertiPaq engine. For a **portfolio project**, hiring managers immediately look at the Relationship View to see if you understand Kimball dimensional modeling.
- **Can it be done in an easier way?**: Leaving it flat is easier, but it immediately brands you as an untrained beginner.
- **Bug Prevention**: A flat table creates ambiguity with bidirectional filtering, circular dependencies, and slow visual rendering. A Star Schema guarantees predictable 1-to-many single-direction filter propagation.

---

### Q3: Why use `DIVIDE(Numerator, Denominator, 0)` instead of `Numerator / Denominator`?
- **Our Method**: Every percentage and prevalence measure uses `DIVIDE([Depressed Students], [Total Students], 0)`.
- **Is it necessary?**: Absolutely mandatory in production DAX.
- **Why?**: The standard division operator `/` returns `NaN` or `Infinity` when the denominator evaluates to `0` (or `BLANK()`). When a user applies extreme slicer combinations that filter the cohort to 0 students, visual cards with `/` crash with an ugly `(Blank)` or visual error. `DIVIDE` intercepts division by zero gracefully and returns the fallback `0`.

---

### Q4: Why use `COUNTROWS('Table')` instead of `COUNT('Table'[Column])`?
- **Our Method**: `Total Students = COUNTROWS('Fact_Student_Assessment')`.
- **Is it necessary?**: Yes. `COUNT('Table'[Column])` inspects a specific column, checks for `NULL` values, and skips them. If that column has missing entries, your student count is wrong. `COUNTROWS` operates directly on table metadata in the VertiPaq memory engine, executing significantly faster with zero chance of missing-row undercounting.

---

### Q5: How did we handle the logical contradiction: 201 students are "Single" in Relationship Status but "Married" in Marital Status?
- **Our Method**: We flagged and quantified it in our automated Data Quality Audit (`data_quality_audit.json`). We documented that survey respondents treat "Relationship Status" as personal emotional/dating status and "Marital Status" as legal status.
- **Can it be done in an easier way?**: You could delete the 201 rows or overwrite them with `"Married"`.
- **Why overwriting or deleting is dangerous (Bug / Integrity Risk)**: Silently altering 201 survey responses introduces sampling bias and falsifies raw survey evidence. In data engineering, real-world data is messy. A true BI professional preserves source integrity, flags anomalies in the audit layer, and documents the business definitions in the Data Dictionary.

---

## Part 2: Top 10 Technical Interview Questions & Scripted Answers

### 1. "Tell me about this Student Depression Detection project."
> *"In this project, I engineered an end-to-end Power BI diagnostic suite analyzing survey data from 4,464 university students in Bangladesh. Coming from a Support Engineering background, my first instinct was to validate data integrity. I built an automated Python and SQL validation pipeline that screened for schema drift, boundary violations, and null values.  
> The core business finding was that physical health condition is the single strongest deterministic predictor of depression—students with critical health conditions exhibited a 100% depression rate, and social isolation amplified risk by 4.8x between isolated singles (44.1%) versus partnered students with friend circles (9.2%).  
> I structured the data into a Kimball Star Schema with dedicated dimensions, implemented 18 production DAX measures using safe `DIVIDE` and `VAR/RETURN` constructs, and designed a 3-page executive dashboard with dynamic titling and drill-through triage."*

### 2. "How did your Support Engineer background help you as a Power BI developer?"
> *"In technical support, your primary job is root-cause analysis, defect triage, and understanding the user's pain point before jumping to conclusions.  
> When building dashboards, that translates directly into three superpowers:  
> 1. **Defensive Data Modeling**: I don't assume data is clean; I audit boundaries and edge cases before writing DAX.  
> 2. **Bug-Free DAX**: I eliminate division-by-zero, handle blanks, and test filter context combinations that users might click.  
> 3. **User-Centric UI**: Instead of cluttering a screen with 15 disconnected charts, I organize visual hierarchy so a university dean or counselor can identify at-risk students within 5 seconds."*

### 3. "What is the difference between Filter Context and Row Context in DAX?"
> *"Row context is the current row being evaluated—for example, inside an iterative function like `SUMX` or in a calculated column. It knows row values but knows nothing about the rest of the table or report slicers.  
> Filter context is the set of all active filters applied to the data model by slicers, visual coordinates, page filters, and `CALCULATE` statements.  
> When you use `CALCULATE`, it initiates **Context Transition**, which converts the current row context into an equivalent filter context."*

### 4. "Why did you use `ALLSELECTED` in your benchmark measure instead of `ALL`?"
> *"In our measure `Overall Cohort Benchmark %`, we wrote:  
> `CALCULATE([Depressed Students], ALLSELECTED('Fact_Student_Assessment'))`.  
> If I had used `ALL`, the measure would calculate the benchmark across the entire database regardless of what slicers the user selected (e.g. even if they filtered to female students only).  
> `ALLSELECTED` removes filters inside the visual (like individual divisions on a bar chart axis) while respecting global page slicers chosen by the user. This allows a dynamic, accurate comparison against the active cohort."*

### 5. "What is Query Folding in Power Query, and why does it matter?"
> *"Query Folding is Power Query's ability to translate M transformations (such as filtering rows, removing columns, or grouping) directly into native SQL queries that execute on the source database server.  
> Instead of pulling 10 million rows across the network into Power BI's memory to filter them, the database server does the heavy lifting and returns only the filtered subset. In enterprise environments, ensuring steps fold prevents refresh timeouts."*

### 6. "How do you ensure your chart categories sort in logical order rather than alphabetical order?"
> *"By configuring the **Sort by Column** feature in Power BI's Model View. For example, our academic tiers ('High Distinction', 'First Class', 'Second Class') would naturally sort alphabetically as 'First Class' first. I created numeric sort keys (`CGPA_Tier_Sort` 1, 2, 3, 4) in the transformation layer, selected the text column in Model View, and assigned its 'Sort by column' property to the numeric key, then hid the numeric key from report view."*

### 7. "How do you optimize a slow Power BI dashboard?"
> *"I use Performance Analyzer in Power BI Desktop to identify the bottleneck across three areas:  
> 1. **DAX Formula Engine**: Simplify complex nested `CALCULATE` statements, replace virtual tables with dimensional filters, and use variables (`VAR`) to store measure results instead of recalculating multiple times.  
> 2. **Visual Rendering**: Limit visual count per page to under 7-8 visual tiles. Cards and visuals with dozens of individual queries saturate thread pools.  
> 3. **VertiPaq Storage Engine**: Remove unused high-cardinality columns (like GUIDs or unnecessary timestamps), split datetime into separate date and time columns, and convert wide flat tables to a star schema to optimize dictionary encoding."*

### 8. "Why did you create a separate `_Measures` table?"
> *"Putting measures inside data tables causes maintenance headaches. In enterprise deployments, having a dedicated disconnected table named `_Measures` (with an underscore so it floats to the very top of the Field pane) organized into display folders ensures any BI developer can find metrics instantly without hunting through dimension columns."*

### 9. "Can you explain the exact findings of the Student Depression project?"
> *"Yes. Out of 4,464 students:  
> 1. **Overall Prevalence**: 26.9% (1,201 students) reported clinical depression symptoms.  
> 2. **Physical Health Dominance**: 100% of students reporting 'Critical' physical health were depressed, and 54.9% of 'Abnormal' health students were depressed. In contrast, 0.0% of students reporting 'Good' health had depression. Physical illness is the primary trigger.  
> 3. **Social Buffering**: Single students without friends had a 44.1% depression rate, while students in a relationship with a friend circle had a 9.2% rate. Strong social ties act as a massive psychological buffer.  
> 4. **Financial Burden**: Students from lower-middle-class backgrounds faced a 30.6% depression rate compared to 17.6% for rich-class students."*

### 10. "What recommendations would you give to university leadership based on this dashboard?"
> *"Three specific institutional interventions:  
> 1. **Automated Early Warning Triage**: Cross-reference university health clinic records with dormitory status. Any student diagnosed with chronic/severe physical health problems who lives alone as a bachelor should receive an automated outreach from student counseling.  
> 2. **First-Year & Transition Mentorship**: Target incoming students (Semester 0-2) with peer buddy programs, as isolated singles have a 44% depression rate.  
> 3. **Emergency Micro-Stipends**: Support lower-middle-class students facing living expense spikes (>12,000 BDT/month), alleviating the financial anxiety that correlates with higher depression."*
