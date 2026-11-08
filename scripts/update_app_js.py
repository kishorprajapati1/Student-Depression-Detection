"""
Update docs/app.js with Apple Light Theme as default and theme switcher
"""
from pathlib import Path

APP_PATH = Path("docs/app.js")
app_text = APP_PATH.read_text(encoding="utf-8")

# Add btnThemeToggle to els
old_els = 'btnFullscreen: document.getElementById("btn-fullscreen"),'
new_els = 'btnFullscreen: document.getElementById("btn-fullscreen"),\n    btnThemeToggle: document.getElementById("btn-theme-toggle"),'

if old_els in app_text and 'btnThemeToggle:' not in app_text:
    app_text = app_text.replace(old_els, new_els)

# Add theme toggle listener in attachFilterListeners
old_fullscreen = """    // Fullscreen View
    els.btnFullscreen.addEventListener("click", () => {"""

new_fullscreen = """    // Theme Switcher (Apple Light Theme Default)
    if (els.btnThemeToggle) {
      els.btnThemeToggle.addEventListener("click", () => {
        const isDark = document.body.classList.toggle("dark-theme");
        els.btnThemeToggle.textContent = isDark ? "Theme: Dark" : "Theme: Light";
        updateChartThemeColors(isDark);
      });
    }

    // Fullscreen View
    els.btnFullscreen.addEventListener("click", () => {"""

if old_fullscreen in app_text and 'Theme Switcher' not in app_text:
    app_text = app_text.replace(old_fullscreen, new_fullscreen)

# Update Chart defaults and colors for Apple Light Theme
old_chart_init = """  // Initialize Charts (Apple Palette: No rainbow, no purple)
  function initCharts() {
    Chart.defaults.color = "#a1a1a6";
    Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif";"""

new_chart_init = """  function updateChartThemeColors(isDark) {
    const gridColor = isDark ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)";
    const textColor = isDark ? "#a1a1a6" : "#6e6e73";
    const volumeBarBg = isDark ? "#2c2c2e" : "#e5e5ea";
    const volumeBarBorder = isDark ? "#3f3f46" : "#d1d1d6";

    Chart.defaults.color = textColor;

    Object.values(state.charts).forEach((chart) => {
      if (!chart) return;
      if (chart.options.scales) {
        Object.values(chart.options.scales).forEach((scale) => {
          if (scale.grid) scale.grid.color = gridColor;
        });
      }
      chart.update();
    });

    if (state.charts.semesterCombo) {
      state.charts.semesterCombo.data.datasets[1].backgroundColor = volumeBarBg;
      state.charts.semesterCombo.data.datasets[1].borderColor = volumeBarBorder;
      state.charts.semesterCombo.update();
    }
  }

  // Initialize Charts (Apple Palette: Clean Light Theme Default)
  function initCharts() {
    Chart.defaults.color = "#6e6e73";
    Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif";"""

if old_chart_init in app_text:
    app_text = app_text.replace(old_chart_init, new_chart_init)

# Replace dark grid lines '#26262a' with 'rgba(0, 0, 0, 0.05)'
app_text = app_text.replace('grid: { color: "#26262a" }', 'grid: { color: "rgba(0, 0, 0, 0.05)" }')

# Replace semester volume bar '#2c2c2e' with '#e5e5ea' and border '#d1d1d6'
app_text = app_text.replace('backgroundColor: "#2c2c2e",\n            borderColor: "#3f3f46",', 'backgroundColor: "#e5e5ea",\n            borderColor: "#d1d1d6",')

# Replace gauge track stroke color for light mode
app_text = app_text.replace('let strokeColor = "#30d158";', 'let strokeColor = "#34c759";')
app_text = app_text.replace('strokeColor = "#ff453a";', 'strokeColor = "#d70015";')
app_text = app_text.replace('strokeColor = "#ff9f0a";', 'strokeColor = "#ff9500";')
app_text = app_text.replace('strokeColor = "#ffd60a";', 'strokeColor = "#b28900";')

APP_PATH.write_text(app_text, encoding="utf-8")
print("Updated docs/app.js with Light Theme chart styling and Theme Switcher")
