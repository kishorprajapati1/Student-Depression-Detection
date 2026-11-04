/**
 * Project 01: Student Mental Health & Predictive Risk System
 * Controller & Reactive Visual Engine
 * Author: Kishor Prajapati (kishorprajapati.com)
 * No Emojis, Clean Clinical Architecture
 */

(function () {
  "use strict";

  // Application State
  const state = {
    records: STUDENT_RECORDS || [],
    features: FEATURE_IMPORTANCES || [],
    metrics: MODEL_METRICS || {},
    filters: {
      division: "All",
      gender: "All",
      health: "All",
      tier: "All",
      stage: "All",
    },
    searchQuery: "",
    currentPage: 1,
    pageSize: 15,
    charts: {},
  };

  // DOM Elements
  const els = {
    divisionFilter: document.getElementById("filter-division"),
    genderFilter: document.getElementById("filter-gender"),
    healthFilter: document.getElementById("filter-health"),
    tierFilter: document.getElementById("filter-tier"),
    stageFilter: document.getElementById("filter-stage"),
    btnReset: document.getElementById("btn-reset-filters"),
    filterSummary: document.getElementById("filter-summary-text"),

    kpiTotal: document.getElementById("kpi-total-val"),
    kpiPrevalence: document.getElementById("kpi-prev-val"),
    kpiCritical: document.getElementById("kpi-crit-val"),
    kpiCgpa: document.getElementById("kpi-cgpa-val"),
    kpiCost: document.getElementById("kpi-cost-val"),

    tabBtns: document.querySelectorAll(".tab-btn"),
    tabPanels: document.querySelectorAll(".tab-panel"),

    tableBody: document.getElementById("roster-table-body"),
    tableSearch: document.getElementById("table-search"),
    btnExportCsv: document.getElementById("btn-export-csv"),
    pageInfo: document.getElementById("page-info"),
    btnPrevPage: document.getElementById("btn-prev-page"),
    btnNextPage: document.getElementById("btn-next-page"),
  };

  // Initialize
  function init() {
    populateFilterOptions();
    attachEventListeners();
    initCharts();
    render();
  }

  // Populate Dropdown Options
  function populateFilterOptions() {
    const divisions = [...new Set(state.records.map((r) => r.division))].sort();
    divisions.forEach((div) => {
      const opt = document.createElement("option");
      opt.value = div;
      opt.textContent = div;
      els.divisionFilter.appendChild(opt);
    });
  }

  // Event Listeners
  function attachEventListeners() {
    // Slicers
    els.divisionFilter.addEventListener("change", (e) => {
      state.filters.division = e.target.value;
      state.currentPage = 1;
      render();
    });

    els.genderFilter.addEventListener("change", (e) => {
      state.filters.gender = e.target.value;
      state.currentPage = 1;
      render();
    });

    els.healthFilter.addEventListener("change", (e) => {
      state.filters.health = e.target.value;
      state.currentPage = 1;
      render();
    });

    els.tierFilter.addEventListener("change", (e) => {
      state.filters.tier = e.target.value;
      state.currentPage = 1;
      render();
    });

    els.stageFilter.addEventListener("change", (e) => {
      state.filters.stage = e.target.value;
      state.currentPage = 1;
      render();
    });

    els.btnReset.addEventListener("click", () => {
      state.filters.division = "All";
      state.filters.gender = "All";
      state.filters.health = "All";
      state.filters.tier = "All";
      state.filters.stage = "All";
      state.searchQuery = "";
      els.divisionFilter.value = "All";
      els.genderFilter.value = "All";
      els.healthFilter.value = "All";
      els.tierFilter.value = "All";
      els.stageFilter.value = "All";
      els.tableSearch.value = "";
      state.currentPage = 1;
      render();
    });

    // Tab Navigation
    els.tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetTab = btn.getAttribute("data-tab");
        els.tabBtns.forEach((b) => b.classList.remove("active"));
        els.tabPanels.forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`tab-${targetTab}`).classList.add("active");

        // Resize charts to fit new visibility
        Object.values(state.charts).forEach((c) => c && c.resize());
      });
    });

    // Table Search & Pagination
    els.tableSearch.addEventListener("input", (e) => {
      state.searchQuery = e.target.value.trim().toLowerCase();
      state.currentPage = 1;
      renderTable();
    });

    els.btnPrevPage.addEventListener("click", () => {
      if (state.currentPage > 1) {
        state.currentPage--;
        renderTable();
      }
    });

    els.btnNextPage.addEventListener("click", () => {
      const filtered = getFilteredRecords();
      const maxPages = Math.ceil(filtered.length / state.pageSize);
      if (state.currentPage < maxPages) {
        state.currentPage++;
        renderTable();
      }
    });

    els.btnExportCsv.addEventListener("click", exportFilteredCsv);
  }

  // Filter Engine
  function getFilteredRecords() {
    return state.records.filter((r) => {
      if (state.filters.division !== "All" && r.division !== state.filters.division) return false;
      if (state.filters.gender !== "All" && r.gender !== state.filters.gender) return false;
      if (state.filters.health !== "All" && r.health !== state.filters.health) return false;
      if (state.filters.tier !== "All" && r.risk_tier !== state.filters.tier) return false;

      if (state.filters.stage !== "All") {
        if (state.filters.stage === "Early" && r.semester > 3) return false;
        if (state.filters.stage === "Mid" && (r.semester < 4 || r.semester > 7)) return false;
        if (state.filters.stage === "Senior" && r.semester < 8) return false;
      }

      if (state.searchQuery) {
        const q = state.searchQuery;
        const matchesId = r.id.toLowerCase().includes(q);
        const matchesDiv = r.division.toLowerCase().includes(q);
        const matchesLiving = r.living.toLowerCase().includes(q);
        if (!matchesId && !matchesDiv && !matchesLiving) return false;
      }

      return true;
    });
  }

  // Master Render Cycle
  function render() {
    const filtered = getFilteredRecords();
    renderKPIs(filtered);
    updateCharts(filtered);
    renderTable();
    updateFilterSummary(filtered);
  }

  function updateFilterSummary(filtered) {
    const total = state.records.length;
    const count = filtered.length;
    els.filterSummary.textContent = `Showing ${count.toLocaleString()} of ${total.toLocaleString()} records (${((count / total) * 100).toFixed(1)}%)`;
  }

  // Render KPIs
  function renderKPIs(records) {
    const count = records.length;
    if (count === 0) {
      els.kpiTotal.textContent = "0";
      els.kpiPrevalence.textContent = "0.0%";
      els.kpiCritical.textContent = "0";
      els.kpiCgpa.textContent = "0.00";
      els.kpiCost.textContent = "0 BDT";
      return;
    }

    const depressedCount = records.filter((r) => r.depression === 1).length;
    const prevRate = (depressedCount / count) * 100;
    const critCount = records.filter((r) => r.risk_tier === "Critical Risk").length;

    const avgCgpa = records.reduce((acc, r) => acc + r.cgpa, 0) / count;
    const avgCost = records.reduce((acc, r) => acc + r.cost, 0) / count;

    els.kpiTotal.textContent = count.toLocaleString();
    els.kpiPrevalence.textContent = `${prevRate.toFixed(1)}%`;
    els.kpiCritical.textContent = critCount.toLocaleString();
    els.kpiCgpa.textContent = `${avgCgpa.toFixed(2)} / 4.00`;
    els.kpiCost.textContent = `${Math.round(avgCost).toLocaleString()} BDT`;
  }

  // Initialize Chart.js
  function initCharts() {
    Chart.defaults.color = "#94a3b8";
    Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";

    // 1. Health Condition Chart
    const ctxHealth = document.getElementById("chart-health").getContext("2d");
    state.charts.health = new Chart(ctxHealth, {
      type: "bar",
      data: {
        labels: ["Critical", "Abnormal", "Normal", "Good"],
        datasets: [
          {
            label: "Depression Rate (%)",
            data: [0, 0, 0, 0],
            backgroundColor: ["#ef4444", "#f97316", "#38bdf8", "#10b981"],
            borderRadius: 4,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Depression Rate: ${ctx.raw.toFixed(1)}%`,
            },
          },
        },
        scales: {
          x: {
            max: 100,
            ticks: { callback: (val) => `${val}%` },
            grid: { color: "#1e293b" },
          },
          y: { grid: { display: false } },
        },
      },
    });

    // 2. Division Prevalence Chart
    const ctxDivision = document.getElementById("chart-division").getContext("2d");
    state.charts.division = new Chart(ctxDivision, {
      type: "bar",
      data: {
        labels: [],
        datasets: [
          {
            label: "Prevalence (%)",
            data: [],
            backgroundColor: "#38bdf8",
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Depression Rate: ${ctx.raw.toFixed(1)}%`,
            },
          },
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            ticks: { callback: (val) => `${val}%` },
            grid: { color: "#1e293b" },
          },
        },
      },
    });

    // 3. Social Isolation Disparity Chart
    const ctxSocial = document.getElementById("chart-social").getContext("2d");
    state.charts.social = new Chart(ctxSocial, {
      type: "bar",
      data: {
        labels: ["Single (No Friends)", "Single (With Friends)", "In Relationship (No Friends)", "In Relationship (With Friends)"],
        datasets: [
          {
            label: "Depression Rate (%)",
            data: [0, 0, 0, 0],
            backgroundColor: ["#ef4444", "#f97316", "#f59e0b", "#10b981"],
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Depression Rate: ${ctx.raw.toFixed(1)}%`,
            },
          },
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            max: 60,
            ticks: { callback: (val) => `${val}%` },
            grid: { color: "#1e293b" },
          },
        },
      },
    });

    // 4. Feature Importance Tornado Chart
    const ctxFeatures = document.getElementById("chart-features").getContext("2d");
    const topFeatures = state.features.slice(0, 8);
    state.charts.features = new Chart(ctxFeatures, {
      type: "bar",
      data: {
        labels: topFeatures.map((f) => f.variable),
        datasets: [
          {
            label: "Importance Weight",
            data: topFeatures.map((f) => (f.weight * 100).toFixed(1)),
            backgroundColor: "#38bdf8",
            borderRadius: 4,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Predictive Weight: ${ctx.raw}%`,
            },
          },
        },
        scales: {
          x: {
            ticks: { callback: (val) => `${val}%` },
            grid: { color: "#1e293b" },
          },
          y: { grid: { display: false } },
        },
      },
    });

    // 5. Risk Tier Distribution
    const ctxTiers = document.getElementById("chart-tiers").getContext("2d");
    state.charts.tiers = new Chart(ctxTiers, {
      type: "doughnut",
      data: {
        labels: ["Critical Risk", "High Risk", "Moderate Risk", "Low Risk"],
        datasets: [
          {
            data: [0, 0, 0, 0],
            backgroundColor: ["#ef4444", "#f97316", "#f59e0b", "#10b981"],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right" },
        },
        cutout: "70%",
      },
    });
  }

  // Update Dynamic Charts based on filtered subset
  function updateCharts(records) {
    if (records.length === 0) return;

    // 1. Health Condition Rates
    const healthCategories = ["Critical", "Abnormal", "Normal", "Good"];
    const healthRates = healthCategories.map((cat) => {
      const subset = records.filter((r) => r.health === cat);
      if (subset.length === 0) return 0;
      const dep = subset.filter((r) => r.depression === 1).length;
      return (dep / subset.length) * 100;
    });
    state.charts.health.data.datasets[0].data = healthRates;
    state.charts.health.update();

    // 2. Division Rates
    const divisions = [...new Set(records.map((r) => r.division))].sort();
    const divRates = divisions.map((div) => {
      const subset = records.filter((r) => r.division === div);
      const dep = subset.filter((r) => r.depression === 1).length;
      return (dep / subset.length) * 100;
    });
    state.charts.division.data.labels = divisions;
    state.charts.division.data.datasets[0].data = divRates;
    state.charts.division.update();

    // 3. Social Buffer Disparity
    const calcSocialRate = (rel, friends) => {
      const subset = records.filter((r) => r.relationship === rel && r.friends === friends);
      if (subset.length === 0) return 0;
      const dep = subset.filter((r) => r.depression === 1).length;
      return (dep / subset.length) * 100;
    };
    const socialRates = [
      calcSocialRate("Single", "No"),
      calcSocialRate("Single", "Yes"),
      calcSocialRate("In a Relationship", "No"),
      calcSocialRate("In a Relationship", "Yes"),
    ];
    state.charts.social.data.datasets[0].data = socialRates;
    state.charts.social.update();

    // 4. Risk Tier Distribution
    const tierCounts = [
      records.filter((r) => r.risk_tier === "Critical Risk").length,
      records.filter((r) => r.risk_tier === "High Risk").length,
      records.filter((r) => r.risk_tier === "Moderate Risk").length,
      records.filter((r) => r.risk_tier === "Low Risk").length,
    ];
    state.charts.tiers.data.datasets[0].data = tierCounts;
    state.charts.tiers.update();
  }

  // Render Student Roster Table
  function renderTable() {
    const filtered = getFilteredRecords();
    const count = filtered.length;
    const maxPages = Math.ceil(count / state.pageSize) || 1;

    if (state.currentPage > maxPages) state.currentPage = maxPages;
    if (state.currentPage < 1) state.currentPage = 1;

    const startIdx = (state.currentPage - 1) * state.pageSize;
    const pageRecords = filtered.slice(startIdx, startIdx + state.pageSize);

    els.tableBody.innerHTML = "";
    if (pageRecords.length === 0) {
      els.tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 2rem; color: #64748b;">No matching records found</td></tr>`;
    } else {
      pageRecords.forEach((r) => {
        const tr = document.createElement("tr");

        let badgeClass = "badge-low";
        if (r.risk_tier === "Critical Risk") badgeClass = "badge-critical";
        else if (r.risk_tier === "High Risk") badgeClass = "badge-high";
        else if (r.risk_tier === "Moderate Risk") badgeClass = "badge-moderate";

        tr.innerHTML = `
          <td><strong>${r.id}</strong></td>
          <td>${r.gender}, ${r.age}</td>
          <td>${r.division}</td>
          <td>${r.semester}</td>
          <td>${r.cgpa.toFixed(2)}</td>
          <td>${r.health}</td>
          <td><strong>${(r.risk_score * 100).toFixed(1)}%</strong></td>
          <td><span class="badge ${badgeClass}">${r.risk_tier}</span></td>
          <td>${r.priority}</td>
        `;
        els.tableBody.appendChild(tr);
      });
    }

    els.pageInfo.textContent = `Page ${state.currentPage} of ${maxPages} (${count.toLocaleString()} students)`;
    els.btnPrevPage.disabled = state.currentPage <= 1;
    els.btnNextPage.disabled = state.currentPage >= maxPages;
  }

  // Export Filtered Records as CSV
  function exportFilteredCsv() {
    const filtered = getFilteredRecords();
    if (filtered.length === 0) return;

    const headers = ["Student_ID", "Gender", "Age", "Division", "Semester", "CGPA", "Health", "Living", "Depression_Actual", "Risk_Probability", "Risk_Tier", "Intervention_Priority"];
    const rows = filtered.map((r) => [
      r.id,
      r.gender,
      r.age,
      `"${r.division}"`,
      r.semester,
      r.cgpa,
      `"${r.health}"`,
      `"${r.living}"`,
      r.depression_label,
      r.risk_score,
      `"${r.risk_tier}"`,
      `"${r.priority}"`,
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `student_depression_filtered_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // Start application
  document.addEventListener("DOMContentLoaded", init);
})();
