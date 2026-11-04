# Dashboard UI/UX Design Specification & Visual Hierarchy

## 1. Visual Theme & Color Palette

To make this project stand out in your portfolio, we avoid default Power BI visual templates. Instead, we implement an **Executive Healthcare & Wellness Dark Theme** designed for high contrast and readability.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        COLOR PALETTE SPECIFICATION                     │
├────────────────────────────────┬─────────┬─────────────────────────────┤
│ Purpose                        │ Hex     │ Usage Context               │
├────────────────────────────────┼─────────┼─────────────────────────────┤
│ Canvas Background              │ #0B1120 │ Deep Navy Background        │
│ Card Container (Surface)       │ #1E293B │ Dark Slate Visual Tiles     │
│ Primary Text (High Contrast)   │ #F8FAFC │ Headers, KPI Large Numbers  │
│ Secondary Text (Muted)         │ #94A3B8 │ Subtitles, Axis Labels      │
│ Primary Accent / Brand         │ #38BDF8 │ Sky Blue (Bars, Selections) │
│ High Risk / Alert (Depression) │ #EF4444 │ Crimson Red (Positive flag) │
│ Safe / Healthy Status          │ #10B981 │ Emerald Green (Normal/Good) │
│ Moderate / Caution             │ #F59E0B │ Amber / Warning Indicator   │
└────────────────────────────────┴─────────┴─────────────────────────────┘
```

---

## 2. Page Architecture (3-Page Executive Suite)

### Page 1: Executive Mental Health Overview (Macro Diagnostic View)
- **Header Strip (Top 80px)**:
  - Title: *Student Depression & Psychological Well-being Analytics*
  - Subtitle: Dynamic DAX metric string (Division, Sample Size, Current Prevalence)
  - Slicer Bar (Right): `Home_division`, `Gender`, `Academic_Stage`
- **KPI Card Row (4 Cards across)**:
  1. **Total Surveyed**: `4,464` (Icon: Academic Cap)
  2. **Depression Prevalence %**: `26.9%` (Dynamic KPI Color: Crimson Alert)
  3. **High-Risk Isolated Cohort**: `1,118` students (Abnormal/Critical + Single/No Friends)
  4. **Average CGPA Benchmark**: `3.41 / 4.00`
- **Main Visual Canvas**:
  - **Visual 1 (Bar Chart - Left)**: *Depression Prevalence by Physical Health Condition* (Critical = 100%, Abnormal = 54.9%, Normal = 4.6%, Good = 0.0%).
  - **Visual 2 (Choropleth/Map or Ranked Bar - Center)**: *Prevalence by Division* (Rangpur 32.0%, Rajshahi 31.6%, Khulna 31.0%, Chittagong 30.5%, etc.).
  - **Visual 3 (100% Stacked Bar - Right)**: *Social Isolation Effect* (`Single + No Friends` vs `In Relationship + Friends`).

---

### Page 2: Academic & Financial Burden Analysis (Micro Drivers)
- **Top Row KPI Split**:
  - Avg Monthly Cost for Depressed Students (`11,840 BDT`) vs Non-Depressed (`11,023 BDT`).
  - CGPA Disparity: Lower-tier students suffer `+16.9%` higher depression rate.
- **Visual Canvas**:
  - **Visual 1 (Scatter / Clustered Column)**: *CGPA vs Monthly Living Cost*, color-coded by Depression status.
  - **Visual 2 (Decomposition Tree / Matrix)**: Root = Depression Rate $\to$ Branch by `Family_background` $\to$ Branch by `Cost_Bracket` $\to$ Branch by `Living_style`.
  - **Visual 3 (Line / Area Chart)**: *Depression Trend across Academic Semesters (Sem 0 to 12)*, displaying the spike during midterm/thesis semesters.

---

### Page 3: Clinical Early Warning & Intervention Matrix (Actionable Operational View)
- **Visual 1 (Heatmap Matrix)**:
  - Rows: `Relationship_status` (`Single`, `Complicated`, `In a Relationship`)
  - Columns: `Health_condition` (`Critical`, `Abnormal`, `Normal`, `Good`)
  - Values: `[Depression Prevalence %]`, conditional formatting gradient.
- **Visual 2 (Interactive Student Cohort Table - Drill-through Enabled)**:
  - Columns: `Student_ID`, `Gender`, `Age`, `Home_division`, `Family_background`, `CGPA`, `Health_condition`, `Cost_without_study`, `Depression`.
  - Conditional formatting: Red alert pill on `Critical` health or `Yes` depression.
- **Right Action Panel (What-If Parameters & Counseling Triage)**:
  - Summary of students requiring immediate institutional mental health counselor outreach.

---

## 3. Power BI Interactive Elements to Showcase in Portfolio

1. **Custom Tooltip Pages**: Hovering over any Division or Health Condition bar pops up a mini card showing the CGPA gap, average living cost, and female vs male ratio.
2. **Bookmark Navigation**: Top navigation pills to seamlessly switch between *Executive Summary*, *Academic Correlates*, and *Triage Action List*.
3. **Clear Slicers Button**: Single-click reset bookmark to clear all cross-filters.
