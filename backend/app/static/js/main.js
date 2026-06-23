/* ============================================================================
   main.js — General UI behavior shared across all pages
   ============================================================================ */

document.addEventListener("DOMContentLoaded", function () {
  // Mobile sidebar toggle
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.querySelector(".sidebar");
  const backdrop = document.querySelector(".sidebar-backdrop");

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", function () {
      sidebar.classList.toggle("show");
      if (backdrop) backdrop.classList.toggle("show");
    });
  }
  if (backdrop) {
    backdrop.addEventListener("click", function () {
      sidebar.classList.remove("show");
      backdrop.classList.remove("show");
    });
  }

  // Auto-dismiss flash alerts after 5 seconds
  document.querySelectorAll(".alert-dismissible").forEach(function (alertEl) {
    setTimeout(function () {
      const alertInstance = bootstrap.Alert.getOrCreateInstance(alertEl);
      alertInstance.close();
    }, 5000);
  });

  // Enable Bootstrap tooltips everywhere
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltipTriggerList.forEach(function (el) {
    new bootstrap.Tooltip(el);
  });
});

/* Utility: format a number as currency string */
function formatCurrency(value, decimals = 2) {
  const num = parseFloat(value);
  if (isNaN(num)) return "0.00";
  return num.toLocaleString("en-IN", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/* Utility: simple debounce for search inputs */
function debounce(fn, delay = 300) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}
