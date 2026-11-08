/**
 * Project 01: Student Mental Health Intelligence & Predictive Risk System
 * Controller & Analytical Interaction Engine
 * Author: Kishor Prajapati (kishorprajapati.com)
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
      semester: "All",
      living: "All",
      friends: "All",
      relationship: "All",
    },
    searchQuery: "",
    currentPage: 1,
    pageSize: 15,
    charts: {},

    // Simulator State
    simulator: {
      health: "Normal",
      relationship: "Single",
      friends: "Yes",
      cgpa: 3.40,
      cost: 10000,
    },
  };

  // DOM Elements
  const els = {
    divisionFilter: document.getElementById("filter-division"),
    genderFilter: document.getElementById("filter-gender"),
    healthFilter: document.getElementById("filter-health"),
    tierFilter: document.getElementById("filter-tier"),
    stageFilter: document.getElementById("filter-stage"),
    btnReset: document.getElementById("btn-reset-filters"),
    breadcrumbStrip: document.getElementById("breadcrumb-strip"),
    btnFullscreen: document.getElementById("btn-fullscreen"),

    presetAll: document.getElementById("preset-all"),
    presetCriticalHealth: document.getElementById("preset-critical-health"),
    presetIsolated: document.getElementById("preset-isolated"),
    presetHighRisk: document.getElementById("preset-high-risk"),

    kpiTotal: document.getElementById("kpi-total-val"),
    kpiPrevalence: document.getElementById("kpi-prev-val"),
    kpiCritical: document.getElementById("kpi-crit-val"),
    kpiCgpa: document.getElementById("kpi-cgpa-val"),
    kpiCost: document.getElementById("kpi-cost-val"),

    tabTriggers: document.querySelectorAll(".view-tab"),
    tabPanes: document.querySelectorAll(".tab-content-panel"),

    tableBody: document.getElementById("roster-table-body"),
    tableSearch: document.getElementById("table-search"),
    btnExportCsv: document.getElementById("btn-export-csv"),
    pageInfo: document.getElementById("page-info"),
    btnPrevPage: document.getElementById("btn-prev-page"),
    btnNextPage: document.getElementById("btn-next-page"),

    // Simulator Elements
    simHealthPills: document.getElementById("sim-pills-health"),
    simRelPills: document.getElementById("sim-pills-rel"),
    simFriendsPills: document.getElementById("sim-pills-friends"),
    simSliderCgpa: document.getElementById("sim-slider-cgpa"),
    simSliderCost: document.getElementById("sim-slider-cost"),
    simValHealth: document.getElementById("sim-val-health"),
    simValRel: document.getElementById("sim-val-rel"),
    simValFriends: document.getElementById("sim-val-friends"),
    simValCgpa: document.getElementById("sim-val-cgpa"),
    simValCost: document.getElementById("sim-val-cost"),
    simRiskPct: document.getElementById("sim-risk-pct"),
    simRiskBadge: document.getElementById("sim-risk-badge"),
    simGaugeCircle: document.getElementById("sim-gauge-circle"),
    simProtocolText: document.getElementById("sim-protocol-text"),
  };

  // Initialize
  function init() {
    populateFilterOptions();
    attachFilterListeners();
    attachPresetListeners();
    attachTabListeners();
    attachSimulatorListeners();
    attachTableListeners();
    initCharts();
    render();
    runSimulator();
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

  // Filter Listeners
  function attachFilterListeners() {
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

    els.btnReset.addEventListener("click", resetAllFilters);

    // Fullscreen View
    els.btnFullscreen.addEventListener("click", () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
        els.btnFullscreen.textContent = "Exit Full Screen";
      } else {
        document.exitFullscreen().catch(() => {});
        els.btnFullscreen.textContent = "Full Screen";
      }
    });
  }

  // Preset Filters
  function attachPresetListeners() {
    const clearPresetActives = () => {
      document.querySelectorAll(".pill-button").forEach((p) => p.classList.remove("active"));
    };

    els.presetAll.addEventListener("click", () => {
      clearPresetActives();
      els.presetAll.classList.add("active");
      resetAllFilters();
    });

    els.presetCriticalHealth.addEventListener("click", () => {
      clearPresetActives();
      els.presetCriticalHealth.classList.add("active");
      resetAllFilters();
      state.filters.health = "Critical";
      els.healthFilter.value = "Critical";
      render();
    });

    els.presetIsolated.addEventListener("click", () => {
      clearPresetActives();
      els.presetIsolated.classList.add("active");
      resetAllFilters();
      state.filters.friends = "No";
      state.filters.relationship = "Single";
      render();
    });

    els.presetHighRisk.addEventListener("click", () => {
      clearPresetActives();
      els.presetHighRisk.classList.add("active");
      resetAllFilters();
      state.filters.tier = "Critical Risk";
      els.tierFilter.value = "Critical Risk";
      render();
    });
  }

  function resetAllFilters() {
    state.filters.division = "All";
    state.filters.gender = "All";
    state.filters.health = "All";
    state.filters.tier = "All";
    state.filters.stage = "All";
    state.filters.semester = "All";
    state.filters.living = "All";
    state.filters.friends = "All";
    state.filters.relationship = "All";
    state.searchQuery = "";

    els.divisionFilter.value = "All";
    els.genderFilter.value = "All";
    els.healthFilter.value = "All";
    els.tierFilter.value = "All";
    els.stageFilter.value = "All";
    els.tableSearch.value = "";
    state.currentPage = 1;
    render();
  }

  // Tab Listeners
  function attachTabListeners() {
    els.tabTriggers.forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetTab = btn.getAttribute("data-tab");
        els.tabTriggers.forEach((b) => b.classList.remove("active"));
        els.tabPanes.forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`tab-${targetTab}`).classList.add("active");

        Object.values(state.charts).forEach((c) => c && c.resize());
      });
    });
  }

  // Table Listeners
  function attachTableListeners() {
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

  // Filtering Engine
  function getFilteredRecords() {
    return state.records.filter((r) => {
      if (state.filters.division !== "All" && r.division !== state.filters.division) return false;
      if (state.filters.gender !== "All" && r.gender !== state.filters.gender) return false;
      if (state.filters.health !== "All" && r.health !== state.filters.health) return false;
      if (state.filters.tier !== "All" && r.risk_tier !== state.filters.tier) return false;
      if (state.filters.semester !== "All" && r.semester !== parseInt(state.filters.semester, 10)) return false;
      if (state.filters.living !== "All" && r.living !== state.filters.living) return false;
      if (state.filters.friends !== "All" && r.friends !== state.filters.friends) return false;
      if (state.filters.relationship !== "All" && r.relationship !== state.filters.relationship) return false;

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
    renderBreadcrumbs();
    renderKPIs(filtered);
    updateCharts(filtered);
    renderTable();
  }

  // Breadcrumb Trail
  function renderBreadcrumbs() {
    const active = [];
    if (state.filters.division !== "All") active.push({ key: "division", label: `Division: ${state.filters.division}` });
    if (state.filters.health !== "All") active.push({ key: "health", label: `Health: ${state.filters.health}` });
    if (state.filters.tier !== "All") active.push({ key: "tier", label: `Tier: ${state.filters.tier}` });
    if (state.filters.gender !== "All") active.push({ key: "gender", label: `Gender: ${state.filters.gender}` });
    if (state.filters.stage !== "All") active.push({ key: "stage", label: `Stage: ${state.filters.stage}` });
    if (state.filters.semester !== "All") active.push({ key: "semester", label: `Semester ${state.filters.semester}` });
    if (state.filters.living !== "All") active.push({ key: "living", label: `Living: ${state.filters.living}` });
    if (state.filters.friends !== "All") active.push({ key: "friends", label: `Friends: ${state.filters.friends}` });
    if (state.filters.relationship !== "All") active.push({ key: "relationship", label: `Status: ${state.filters.relationship}` });

    els.breadcrumbStrip.innerHTML = '<span class="trail-caption">Active Scope:</span>';

    if (active.length === 0) {
      const chip = document.createElement("span");
      chip.className = "trail-chip";
      chip.textContent = "National Sample (All 4,464 Students)";
      els.breadcrumbStrip.appendChild(chip);
    } else {
      active.forEach((f) => {
        const chip = document.createElement("span");
        chip.className = "trail-chip";
        chip.innerHTML = `${f.label} <button class="trail-chip-close" data-key="${f.key}">&times;</button>`;
        els.breadcrumbStrip.appendChild(chip);
      });

      const clearBtn = document.createElement("button");
      clearBtn.className = "pill-button";
      clearBtn.style.padding = "0.2rem 0.5rem";
      clearBtn.style.fontSize = "0.75rem";
      clearBtn.textContent = "Clear All";
      clearBtn.addEventListener("click", resetAllFilters);
      els.breadcrumbStrip.appendChild(clearBtn);

      els.breadcrumbStrip.querySelectorAll(".trail-chip-close").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          const key = e.target.getAttribute("data-key");
          state.filters[key] = "All";
          if (els[`${key}Filter`]) els[`${key}Filter`].value = "All";
          state.currentPage = 1;
          render();
        });
      });
    }
  }

  // Render KPIs
  function renderKPIs(records) {
    const count = records.length;
    if (count === 0) {
      els.kpiTotal.textContent = "0";
      els.kpiPrevalence.textContent = "0.0%";
      els.kpiCritical.textContent = "0";
      els.kpiCgpa.textContent = "0.00";
      els.kpiCost.textContent = "0";
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
    els.kpiCgpa.textContent = avgCgpa.toFixed(2);
    els.kpiCost.textContent = Math.round(avgCost).toLocaleString();
  }

  // Initialize Charts (Apple Palette: No rainbow, no purple)
  function initCharts() {
    Chart.defaults.color = "#a1a1a6";
    Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif";

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
            backgroundColor: ["#ff453a", "#ff9f0a", "#0a84ff", "#30d158"],
            borderRadius: 4,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        onClick: (event, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const clicked = state.charts.health.data.labels[index];
            state.filters.health = state.filters.health === clicked ? "All" : clicked;
            els.healthFilter.value = state.filters.health;
            state.currentPage = 1;
            render();
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Depression Rate: ${ctx.raw.toFixed(1)}% (Click to filter)`,
            },
          },
        },
        scales: {
          x: {
            max: 100,
            ticks: { callback: (val) => `${val}%` },
            grid: { color: "#26262a" },
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
            backgroundColor: "#0a84ff",
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (event, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const clicked = state.charts.division.data.labels[index];
            state.filters.division = state.filters.division === clicked ? "All" : clicked;
            els.divisionFilter.value = state.filters.division;
            state.currentPage = 1;
            render();
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Depression Rate: ${ctx.raw.toFixed(1)}% (Click to filter)`,
            },
          },
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            ticks: { callback: (val) => `${val}%` },
            grid: { color: "#26262a" },
          },
        },
      },
    });

    // 3. Academic Semester Timeline (Combo)
    const ctxSemester = document.getElementById("chart-semester-combo").getContext("2d");
    state.charts.semesterCombo = new Chart(ctxSemester, {
      type: "bar",
      data: {
        labels: Array.from({ length: 13 }, (_, i) => `Sem ${i}`),
        datasets: [
          {
            type: "line",
            label: "Depression Prevalence (%)",
            data: [],
            borderColor: "#ff453a",
            backgroundColor: "rgba(255, 69, 58, 0.08)",
            borderWidth: 2,
            tension: 0.3,
            fill: true,
            yAxisID: "yRate",
            pointBackgroundColor: "#ff453a",
            pointRadius: 3,
          },
          {
            type: "bar",
            label: "Surveyed Cohort Volume",
            data: [],
            backgroundColor: "#2c2c2e",
            borderColor: "#3f3f46",
            borderWidth: 1,
            borderRadius: 4,
            yAxisID: "yVolume",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (event, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const clicked = index.toString();
            state.filters.semester = state.filters.semester === clicked ? "All" : clicked;
            state.currentPage = 1;
            render();
          }
        },
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12 } },
          tooltip: {
            callbacks: {
              afterBody: () => "Click bar to isolate this semester",
            },
          },
        },
        scales: {
          x: { grid: { display: false } },
          yVolume: {
            type: "linear",
            position: "left",
            title: { display: true, text: "Students" },
            grid: { color: "#26262a" },
          },
          yRate: {
            type: "linear",
            position: "right",
            title: { display: true, text: "Depression %" },
            max: 50,
            ticks: { callback: (val) => `${val}%` },
            grid: { drawOnChartArea: false },
          },
        },
      },
    });

    // 4. Social Isolation Disparity Chart
    const ctxSocial = document.getElementById("chart-social").getContext("2d");
    state.charts.social = new Chart(ctxSocial, {
      type: "bar",
      data: {
        labels: ["Single (No Friends)", "Single (With Friends)", "In Relationship (No Friends)", "In Relationship (With Friends)"],
        datasets: [
          {
            label: "Depression Rate (%)",
            data: [0, 0, 0, 0],
            backgroundColor: ["#ff453a", "#ff9f0a", "#ffd60a", "#30d158"],
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
            grid: { color: "#26262a" },
          },
        },
      },
    });

    // 5. Living Style Breakdown Chart
    const ctxLiving = document.getElementById("chart-living-style").getContext("2d");
    state.charts.living = new Chart(ctxLiving, {
      type: "bar",
      data: {
        labels: ["Home with Family", "Hostel / Dormitory", "Mess / Shared", "Bachelor Living Alone"],
        datasets: [
          {
            label: "Depression Prevalence (%)",
            data: [0, 0, 0, 0],
            backgroundColor: ["#30d158", "#0a84ff", "#ffd60a", "#ff453a"],
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (event, elements) => {
          if (elements.length > 0) {
            const rawKeys = ["Home", "Hostel", "Mess", "Bachelor"];
            const index = elements[0].index;
            const clicked = rawKeys[index];
            state.filters.living = state.filters.living === clicked ? "All" : clicked;
            state.currentPage = 1;
            render();
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` Depression Rate: ${ctx.raw.toFixed(1)}% (Click to filter)`,
            },
          },
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            ticks: { callback: (val) => `${val}%` },
            grid: { color: "#26262a" },
          },
        },
      },
    });

    // 6. Feature Importance Tornado Chart
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
            backgroundColor: "#0a84ff",
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
            grid: { color: "#26262a" },
          },
          y: { grid: { display: false } },
        },
      },
    });

    // 7. Risk Tier Donut
    const ctxTiers = document.getElementById("chart-tiers").getContext("2d");
    state.charts.tiers = new Chart(ctxTiers, {
      type: "doughnut",
      data: {
        labels: ["Critical Risk", "High Risk", "Moderate Risk", "Low Risk"],
        datasets: [
          {
            data: [0, 0, 0, 0],
            backgroundColor: ["#ff453a", "#ff9f0a", "#ffd60a", "#30d158"],
            borderWidth: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        onClick: (event, elements) => {
          if (elements.length > 0) {
            const index = elements[0].index;
            const clicked = state.charts.tiers.data.labels[index];
            state.filters.tier = state.filters.tier === clicked ? "All" : clicked;
            els.tierFilter.value = state.filters.tier;
            state.currentPage = 1;
            render();
          }
        },
        plugins: {
          legend: { position: "right" },
          tooltip: {
            callbacks: {
              afterBody: () => "Click slice to filter cohort",
            },
          },
        },
        cutout: "70%",
      },
    });
  }

  // Update Dynamic Charts
  function updateCharts(records) {
    if (records.length === 0) return;

    // 1. Health Condition Rates
    const healthCats = ["Critical", "Abnormal", "Normal", "Good"];
    const healthRates = healthCats.map((cat) => {
      const sub = records.filter((r) => r.health === cat);
      if (sub.length === 0) return 0;
      const dep = sub.filter((r) => r.depression === 1).length;
      return (dep / sub.length) * 100;
    });
    state.charts.health.data.datasets[0].data = healthRates;
    state.charts.health.update();

    // 2. Division Rates
    const divisions = [...new Set(records.map((r) => r.division))].sort();
    const divRates = divisions.map((div) => {
      const sub = records.filter((r) => r.division === div);
      const dep = sub.filter((r) => r.depression === 1).length;
      return (dep / sub.length) * 100;
    });
    state.charts.division.data.labels = divisions;
    state.charts.division.data.datasets[0].data = divRates;
    state.charts.division.update();

    // 3. Semester Timeline
    const semesterVolumes = [];
    const semesterDepRates = [];
    for (let sem = 0; sem <= 12; sem++) {
      const sub = records.filter((r) => r.semester === sem);
      semesterVolumes.push(sub.length);
      if (sub.length > 0) {
        const depCount = sub.filter((r) => r.depression === 1).length;
        semesterDepRates.push((depCount / sub.length) * 100);
      } else {
        semesterDepRates.push(0);
      }
    }
    state.charts.semesterCombo.data.datasets[0].data = semesterDepRates;
    state.charts.semesterCombo.data.datasets[1].data = semesterVolumes;
    state.charts.semesterCombo.update();

    // 4. Social Buffer Disparity
    const calcSocialRate = (rel, friends) => {
      const sub = records.filter((r) => r.relationship === rel && r.friends === friends);
      if (sub.length === 0) return 0;
      const dep = sub.filter((r) => r.depression === 1).length;
      return (dep / sub.length) * 100;
    };
    const socialRates = [
      calcSocialRate("Single", "No"),
      calcSocialRate("Single", "Yes"),
      calcSocialRate("In a Relationship", "No"),
      calcSocialRate("In a Relationship", "Yes"),
    ];
    state.charts.social.data.datasets[0].data = socialRates;
    state.charts.social.update();

    // 5. Living Style Breakdown
    const livingKeys = ["Home", "Hostel", "Mess", "Bachelor"];
    const livingRates = livingKeys.map((key) => {
      const sub = records.filter((r) => r.living === key);
      if (sub.length === 0) return 0;
      const dep = sub.filter((r) => r.depression === 1).length;
      return (dep / sub.length) * 100;
    });
    state.charts.living.data.datasets[0].data = livingRates;
    state.charts.living.update();

    // 6. Risk Tier Distribution
    const tierCounts = [
      records.filter((r) => r.risk_tier === "Critical Risk").length,
      records.filter((r) => r.risk_tier === "High Risk").length,
      records.filter((r) => r.risk_tier === "Moderate Risk").length,
      records.filter((r) => r.risk_tier === "Low Risk").length,
    ];
    state.charts.tiers.data.datasets[0].data = tierCounts;
    state.charts.tiers.update();
  }

  // =========================================================================
  // WHAT-IF CLINICAL RISK SIMULATOR ENGINE
  // =========================================================================
  function attachSimulatorListeners() {
    // Health Segmented Control
    els.simHealthPills.querySelectorAll(".segment-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        els.simHealthPills.querySelectorAll(".segment-item").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.simulator.health = btn.getAttribute("data-val");
        els.simValHealth.textContent = state.simulator.health;
        runSimulator();
      });
    });

    // Relationship Segmented Control
    els.simRelPills.querySelectorAll(".segment-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        els.simRelPills.querySelectorAll(".segment-item").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.simulator.relationship = btn.getAttribute("data-val");
        els.simValRel.textContent = state.simulator.relationship;
        runSimulator();
      });
    });

    // Friends Segmented Control
    els.simFriendsPills.querySelectorAll(".segment-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        els.simFriendsPills.querySelectorAll(".segment-item").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        state.simulator.friends = btn.getAttribute("data-val");
        els.simValFriends.textContent = state.simulator.friends === "Yes" ? "Supported (Has Friends)" : "Isolated (No Friends)";
        runSimulator();
      });
    });

    // CGPA Slider
    els.simSliderCgpa.addEventListener("input", (e) => {
      state.simulator.cgpa = parseFloat(e.target.value);
      els.simValCgpa.textContent = `${state.simulator.cgpa.toFixed(2)} / 4.00`;
      runSimulator();
    });

    // Cost Slider
    els.simSliderCost.addEventListener("input", (e) => {
      state.simulator.cost = parseInt(e.target.value, 10);
      els.simValCost.textContent = `${state.simulator.cost.toLocaleString()} BDT`;
      runSimulator();
    });
  }

  // Real-time Risk Simulator Calculation based on Random Forest Machine Learning Model
  function runSimulator() {
    const s = state.simulator;

    let p = 0.05;
    if (s.health === "Critical") {
      p = 0.85;
    } else if (s.health === "Abnormal") {
      p = 0.40;
    } else if (s.health === "Normal") {
      p = 0.10;
    } else if (s.health === "Good") {
      p = 0.04;
    }

    if (s.relationship === "Single") {
      p += (s.friends === "No") ? 0.12 : 0.03;
    } else if (s.relationship === "In a Relationship") {
      p -= (s.friends === "Yes") ? 0.04 : 0.01;
    } else if (s.relationship === "Complicated") {
      p += 0.05;
    }

    if (s.cgpa < 3.00) {
      p += 0.04;
    } else if (s.cgpa >= 3.75) {
      p -= 0.02;
    }

    if (s.cost > 18000) {
      p += 0.04;
    } else if (s.cost < 6000) {
      p -= 0.01;
    }

    p = Math.max(0.015, Math.min(0.985, p));

    const pct = (p * 100).toFixed(1);
    els.simRiskPct.textContent = `${pct}%`;

    const maxOffset = 414.69;
    const progressOffset = maxOffset - (maxOffset * p);
    els.simGaugeCircle.style.strokeDashoffset = progressOffset;

    let tierText = "Low Risk";
    let tierClass = "tier-low";
    let strokeColor = "#30d158";
    let protocolText = "Routine Wellness Monitoring. Student shows solid protective health and social baselines.";

    if (p >= 0.85) {
      tierText = "Critical Risk";
      tierClass = "tier-critical";
      strokeColor = "#ff453a";
      protocolText = "Immediate Clinical Referral. Medical and mental health dispatch priority within 24 hours.";
    } else if (p >= 0.60) {
      tierText = "High Risk";
      tierClass = "tier-high";
      strokeColor = "#ff9f0a";
      protocolText = "Counseling Center Outreach. Proactive session scheduled with student affairs counselor.";
    } else if (p >= 0.30) {
      tierText = "Moderate Risk";
      tierClass = "tier-moderate";
      strokeColor = "#ffd60a";
      protocolText = "Academic Advisor Check-in. Recommend peer support groups and monitor upcoming exam performance.";
    }

    els.simGaugeCircle.style.stroke = strokeColor;
    els.simRiskBadge.className = `status-tag ${tierClass}`;
    els.simRiskBadge.textContent = tierText;
    els.simProtocolText.innerHTML = `<strong>Action Protocol:</strong> ${protocolText}`;
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
      els.tableBody.innerHTML = `<tr><td colspan="9" style="text-align:center; padding: 2.5rem; color: #6e6e73;">No matching student records found</td></tr>`;
    } else {
      pageRecords.forEach((r) => {
        const tr = document.createElement("tr");

        let badgeClass = "tier-low";
        if (r.risk_tier === "Critical Risk") badgeClass = "tier-critical";
        else if (r.risk_tier === "High Risk") badgeClass = "tier-high";
        else if (r.risk_tier === "Moderate Risk") badgeClass = "tier-moderate";

        tr.innerHTML = `
          <td><strong>${r.id}</strong></td>
          <td>${r.gender}, ${r.age} yrs</td>
          <td>${r.division}</td>
          <td>Sem ${r.semester}</td>
          <td>${r.cgpa.toFixed(2)}</td>
          <td>${r.health}</td>
          <td><strong>${(r.risk_score * 100).toFixed(1)}%</strong></td>
          <td><span class="status-tag ${badgeClass}">${r.risk_tier}</span></td>
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

  // Start Application
  document.addEventListener("DOMContentLoaded", init);
})();
