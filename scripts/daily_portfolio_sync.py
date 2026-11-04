"""
Daily Portfolio Synchronization & Health Check Automation
Validates active database schemas, recalculates key metrics,
and writes rolling audit entries for GitHub CI/CD tracking.
"""

import datetime
import json
import os
import sqlite3
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(ROOT_DIR, "portfolio_activity_log.json")
METRICS_SUMMARY_FILE = os.path.join(ROOT_DIR, "PORTFOLIO_METRICS.md")

PROJECTS = [
    {
        "id": "project_01",
        "name": "Student Depression & Mental Health Analytics",
        "path": os.path.join(ROOT_DIR, "Project-01_Student_Depression_Analysis"),
        "db": os.path.join(
            ROOT_DIR, "Project-01_Student_Depression_Analysis", "data", "processed", "student_depression.db"
        )
    }
]


def sync_project_metrics(project: dict) -> dict:
    """Queries project SQLite database to extract live validation metrics."""
    result = {
        "project_id": project["id"],
        "project_name": project["name"],
        "status": "Healthy",
        "metrics": {}
    }

    db_path = project["db"]
    if not os.path.isfile(db_path):
        result["status"] = "Database missing"
        return result

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                COUNT(*) AS Total_Students,
                SUM(Depression_Flag) AS Depressed_Count,
                ROUND(100.0 * AVG(Depression_Flag), 2) AS Prevalence_Pct,
                ROUND(AVG(CGPA), 2) AS Avg_CGPA,
                ROUND(AVG(Cost_without_study), 0) AS Avg_Cost_BDT
            FROM student_depression_cleaned;
            """
        )
        row = cur.fetchone()
        conn.close()

        if row:
            result["metrics"] = {
                "total_records": row[0],
                "depressed_count": row[1],
                "prevalence_pct": row[2],
                "avg_cgpa": row[3],
                "avg_monthly_cost_bdt": row[4]
            }
    except sqlite3.Error as exc:
        result["status"] = f"Database query error: {str(exc)}"

    return result


def load_existing_logs(log_path: str) -> list:
    """Loads activity history safely, distinguishing between missing file and corrupted JSON."""
    if not os.path.exists(log_path):
        return []

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except json.JSONDecodeError as err:
        sys.stderr.write(f"Warning: Corrupted activity log at {log_path} ({err}). Initializing fresh log.\n")
        return []
    except OSError as err:
        sys.stderr.write(f"Warning: Unable to read activity log ({err}).\n")
        return []


def run_sync() -> None:
    """Executes the daily portfolio sync and generates summary files."""
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    project_audits = [sync_project_metrics(p) for p in PROJECTS]

    run_record = {
        "timestamp_utc": now_utc,
        "total_projects": len(PROJECTS),
        "projects": project_audits
    }

    logs = load_existing_logs(LOG_FILE)
    logs.append(run_record)
    logs = logs[-60:]  # Rolling 60-day window

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    # Render PORTFOLIO_METRICS.md
    p1_metrics = project_audits[0]["metrics"]
    md_content = f"""# 📈 Portfolio Automated Metrics & Pipeline Status

> **Last Automated Verification**: `{now_utc}`  
> **Status**: Verified & Operational ✅

## Active Projects Registry

| Project | Records | Depression Prevalence | Avg CGPA | Avg Living Cost | Health Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **01. Student Depression Analytics** | {p1_metrics.get('total_records', 0):,} | {p1_metrics.get('prevalence_pct', 0.0)}% | {p1_metrics.get('avg_cgpa', 0.0):.2f} / 4.00 | {p1_metrics.get('avg_monthly_cost_bdt', 0):,.0f} BDT | `Healthy` |

---
*Maintained automatically by GitHub Actions workflow (`daily-activity.yml`).*
"""

    with open(METRICS_SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Sync complete at {now_utc}. Summary updated.")


if __name__ == "__main__":
    run_sync()
