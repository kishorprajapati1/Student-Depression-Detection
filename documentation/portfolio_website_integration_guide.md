# Portfolio Website Integration Guide & Web Deployment

**Author**: Kishor Prajapati  
**Website**: [kishorprajapati.com](https://kishorprajapati.com)  
**Project**: Student Mental Health Analytics & Predictive Risk System  

---

## 1. Executive Summary & Web Application Architecture

The interactive web dashboard located in the `docs/` directory is an enterprise-grade client-side application. It is designed to be hosted for free on GitHub Pages, embedded within an `<iframe>` on [kishorprajapati.com](https://kishorprajapati.com), or copied directly into any sub-directory of your portfolio web server.

### Core Architectural Features:
- **Zero Backend Required**: Runs entirely in the browser using the pre-compiled `data.js` payload.
- **Sub-10ms Response Time**: Instant filtering across all 4,464 student records.
- **Professional Clinical Theme**: Dark Navy (`#0B1120`) and Slate (`#1E293B`) palette with zero emojis.
- **Data Privacy & Interview Confidentiality**: Interview Q&A materials and confidential notes are strictly excluded from the web application.

---

## 2. Step-by-Step Deployment Instructions

### Step 1: Push Repository to GitHub
In PowerShell from `d:\PowerBi Projects`:

```powershell
# If you have not yet linked your remote repository:
git remote add origin https://github.com/<your-username>/powerbi-portfolio.git
git branch -M main
git push -u origin main
```

---

### Step 2: Enable GitHub Pages (Free Hosting)
1. Go to your repository on GitHub: `https://github.com/<your-username>/powerbi-portfolio`.
2. Click **Settings** (top navigation tab).
3. In the left sidebar, click **Pages** (under the "Code and automation" section).
4. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`.
   - **Branch**: Select `main` (or `master`).
   - **Folder**: Select `/docs` (this serves the `docs/index.html` application).
5. Click **Save**.
6. Within 1 to 2 minutes, GitHub will publish your interactive dashboard at:
   `https://<your-username>.github.io/powerbi-portfolio/`

---

### Step 3: Embed on Your Portfolio Website (kishorprajapati.com)

You have three clean options to integrate this project into `kishorprajapati.com`:

#### Option A: Direct Iframe Embed (Recommended for Seamless User Experience)
Add this code into your portfolio project page on `kishorprajapati.com`:

```html
<section class="project-showcase">
  <h2>Interactive Analytics Dashboard</h2>
  <p>Live interactive case study with dynamic cohort slicers and machine learning risk scoring.</p>
  
  <div class="dashboard-container" style="position: relative; width: 100%; height: 920px; border-radius: 8px; overflow: hidden; border: 1px solid #334155;">
    <iframe 
      src="https://<your-username>.github.io/powerbi-portfolio/" 
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
      title="Student Mental Health Analytics Dashboard"
      loading="lazy">
    </iframe>
  </div>
</section>
```

#### Option B: Featured Project Card with Live Demo Link
On your main portfolio homepage or CV projects section:

```html
<div class="project-card">
  <span class="badge">Healthcare & Education Analytics</span>
  <h3>Student Mental Health Analytics & Predictive Risk System</h3>
  <p>
    Engineered an end-to-end business intelligence and machine learning solution analyzing 4,464 university students. 
    Built a Kimball Star Schema, automated Python ETL validation, trained a Random Forest model with 97.6% accuracy 
    and 100% precision, and created an interactive clinical triage dashboard.
  </p>
  <div class="project-tech-stack">
    <span>Python ETL</span>
    <span>SQLite Star Schema</span>
    <span>Power BI DAX</span>
    <span>Scikit-Learn</span>
    <span>Interactive Web App</span>
  </div>
  <div class="project-links">
    <a href="https://<your-username>.github.io/powerbi-portfolio/" target="_blank" class="btn btn-primary">
      Launch Live Interactive Dashboard
    </a>
    <a href="https://github.com/<your-username>/powerbi-portfolio" target="_blank" class="btn btn-outline">
      View GitHub Repository
    </a>
  </div>
</div>
```

#### Option C: Custom Subdomain on kishorprajapati.com
If you want the dashboard hosted directly under your brand:
1. In your DNS provider (e.g., Cloudflare, Namecheap, GoDaddy), add a `CNAME` record:
   - **Type**: `CNAME`
   - **Name / Host**: `depression-analytics` (or `bi-projects`)
   - **Target**: `<your-username>.github.io`
2. In your GitHub repository **Settings $\to$ Pages**, enter `depression-analytics.kishorprajapati.com` under **Custom domain** and check **Enforce HTTPS**.

---

## 3. Compliance & Presentation Verification

| Compliance Requirement | Implementation Status | Verification Method |
| :--- | :---: | :--- |
| **No Emojis** | Verified | Automated Unicode scan confirms zero emoji glyphs across HTML, CSS, and JS. |
| **No Plagiarism** | Verified | 100% original copy tailored specifically to Kishor Prajapati's analytical transition. |
| **No Interview Q&A Leakage** | Verified | Interview Q&A remains strictly in `documentation/interview_qa_mastery.md` and is absent from the web app. |
| **All Functions Operational** | Verified | Dynamic slicers, reactive Chart.js charts, pagination, search, and CSV export tested via local HTTP server. |
