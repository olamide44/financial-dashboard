import { Chart, Colors } from "chart.js";

export function setupChartDefaults() {
  // plugin for color palettes
  Chart.register(Colors);

  const grid = getComputedStyle(document.documentElement).getPropertyValue("--border").trim() || "#1f2937";
  const text = getComputedStyle(document.documentElement).getPropertyValue("--text-muted").trim() || "#9ca3af";

  Chart.defaults.color = text;
  Chart.defaults.font.family = "Inter, ui-sans-serif, system-ui, sans-serif";
  Chart.defaults.borderColor = grid;

  // Lines
  Chart.defaults.elements.line.tension = 0.2;
  Chart.defaults.elements.line.borderWidth = 2;
  Chart.defaults.elements.point.radius = 0;

  // Layout
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.tooltip.mode = "index";
  Chart.defaults.plugins.tooltip.intersect = false;
}

// Re-apply when theme toggles
export function reapplyChartTheme() {
  setupChartDefaults();
}
