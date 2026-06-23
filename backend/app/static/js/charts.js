/* ============================================================================
   charts.js — Reusable Chart.js helper functions used across
   dashboard, portfolio, analysis, and admin pages.
   ============================================================================ */

const CHART_COLORS = [
  "#0d9488", "#c9a227", "#3b82f6", "#dc2626", "#8b5cf6",
  "#f97316", "#16a34a", "#0ea5e9", "#ec4899", "#6366f1",
];

/**
 * Renders a pie/doughnut chart for portfolio sector allocation.
 * @param {string} canvasId
 * @param {string[]} labels
 * @param {number[]} values
 */
function renderAllocationPieChart(canvasId, labels, values) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  if (!labels || labels.length === 0) {
    ctx.parentElement.insertAdjacentHTML(
      "beforeend",
      '<p class="text-center text-muted mt-3">No holdings yet — buy a stock to see allocation.</p>'
    );
    return null;
  }

  return new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: CHART_COLORS,
        borderWidth: 2,
        borderColor: "#fff",
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom", labels: { boxWidth: 12, padding: 12, font: { size: 11 } } },
        tooltip: {
          callbacks: {
            label: function (context) {
              const value = context.parsed;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
              return `${context.label}: ₹${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })} (${pct}%)`;
            },
          },
        },
      },
      cutout: "60%",
    },
  });
}

/**
 * Renders a grouped bar chart showing monthly investment trend
 * (amount bought vs sold).
 */
function renderInvestmentTrendChart(canvasId, labels, boughtData, soldData) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  if (!labels || labels.length === 0) {
    ctx.parentElement.insertAdjacentHTML(
      "beforeend",
      '<p class="text-center text-muted mt-3">No transaction history yet.</p>'
    );
    return null;
  }

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Invested (Buy)",
          data: boughtData,
          backgroundColor: "#0d9488",
          borderRadius: 4,
        },
        {
          label: "Realized (Sell)",
          data: soldData,
          backgroundColor: "#c9a227",
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, ticks: { callback: (v) => "₹" + v.toLocaleString("en-IN") } },
      },
      plugins: {
        legend: { position: "bottom" },
      },
    },
  });
}

/**
 * Renders a line chart for historical stock price (1m / 6m / 1y).
 * Returns the Chart.js instance so callers can call .destroy() before
 * re-rendering with a new period.
 */
function renderStockPriceChart(canvasId, labels, prices, ticker) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  // Clear any previous "unavailable" message before re-rendering (e.g. on period switch)
  const existingMsg = ctx.parentElement.querySelector(".chart-empty-message");
  if (existingMsg) existingMsg.remove();
  ctx.style.display = "";

  if (!labels || labels.length === 0) {
    ctx.style.display = "none";
    ctx.parentElement.insertAdjacentHTML(
      "beforeend",
      '<p class="text-center text-muted mt-3 chart-empty-message">Historical price data is currently unavailable for this stock.</p>'
    );
    return null;
  }

  return new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: `${ticker} Price`,
        data: prices,
        borderColor: "#38bdf8",
        backgroundColor: "rgba(56,189,248,0.18)",
        fill: true,
        tension: 0.25,
        pointRadius: 0,
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      scales: {
        x: { ticks: { maxTicksLimit: 8 } },
        y: { ticks: { callback: (v) => v.toLocaleString("en-IN") } },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => `Price: ${context.parsed.y.toLocaleString("en-IN")}`,
          },
        },
      },
    },
  });
}

/**
 * Renders a simple bar chart for admin reports (e.g. transaction volume
 * by day, sector distribution counts).
 */
function renderSimpleBarChart(canvasId, labels, values, label, color = "#0d9488") {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: label,
        data: values,
        backgroundColor: color,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } },
      plugins: { legend: { display: false } },
    },
  });
}
