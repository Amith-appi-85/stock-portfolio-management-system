/* ============================================================================
   trading.js — Buy/Sell modal logic, live price preview, and stock search
   autocomplete used on the Portfolio, Watchlist, and Analysis pages.
   ============================================================================ */

/**
 * Populates the Buy/Sell modal fields when a "Trade" button is clicked.
 * Expects the modal to have inputs with IDs: tradeStockId, tradeTicker,
 * tradePrice, tradeQuantity, tradeAction, tradeModalTitle.
 */
function openTradeModal(stockId, ticker, currentPrice, action) {
  document.getElementById("tradeStockId").value = stockId;
  document.getElementById("tradeTicker").textContent = ticker;
  document.getElementById("tradePrice").textContent = formatCurrency(currentPrice);
  document.getElementById("tradePriceHidden").value = currentPrice;
  document.getElementById("tradeQuantity").value = 1;
  document.getElementById("tradeAction").value = action;
  document.getElementById("tradeModalTitle").textContent =
    (action === "buy" ? "Buy " : "Sell ") + ticker;

  const submitBtn = document.getElementById("tradeSubmitBtn");
  submitBtn.textContent = action === "buy" ? "Confirm Buy" : "Confirm Sell";
  submitBtn.className = "btn " + (action === "buy" ? "btn-success" : "btn-danger");

  updateTradeTotal();

  const form = document.getElementById("tradeForm");
  form.action = action === "buy" ? "/portfolio/buy" : "/portfolio/sell";

  const modalEl = document.getElementById("tradeModal");
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
  modal.show();
}

/** Recomputes the displayed total cost whenever quantity changes. */
function updateTradeTotal() {
  const price = parseFloat(document.getElementById("tradePriceHidden").value) || 0;
  const qty = parseInt(document.getElementById("tradeQuantity").value) || 0;
  const total = price * qty;
  const totalEl = document.getElementById("tradeTotal");
  if (totalEl) totalEl.textContent = formatCurrency(total);
}

document.addEventListener("DOMContentLoaded", function () {
  const qtyInput = document.getElementById("tradeQuantity");
  if (qtyInput) {
    qtyInput.addEventListener("input", updateTradeTotal);
  }

  // ---------------- Live stock search (Analysis page) ----------------
  const searchInput = document.getElementById("stockSearchInput");
  const searchResultsBox = document.getElementById("stockSearchResults");

  if (searchInput && searchResultsBox) {
    const performSearch = debounce(function () {
      const term = searchInput.value.trim();
      if (term.length === 0) {
        searchResultsBox.innerHTML = "";
        searchResultsBox.classList.add("d-none");
        return;
      }
      fetch(`/analysis/api/search?q=${encodeURIComponent(term)}`)
        .then((res) => res.json())
        .then((data) => {
          renderSearchResults(data.results);
        })
        .catch(() => {
          searchResultsBox.innerHTML = '<div class="p-2 text-muted">Search failed. Try again.</div>';
          searchResultsBox.classList.remove("d-none");
        });
    }, 300);

    searchInput.addEventListener("input", performSearch);

    document.addEventListener("click", function (e) {
      if (!searchResultsBox.contains(e.target) && e.target !== searchInput) {
        searchResultsBox.classList.add("d-none");
      }
    });
  }

  function renderSearchResults(results) {
    if (!results || results.length === 0) {
      searchResultsBox.innerHTML = '<div class="p-3 text-muted small">No stocks found.</div>';
      searchResultsBox.classList.remove("d-none");
      return;
    }
    const html = results
      .map(
        (stock) => `
        <a href="/analysis/stock/${stock.stock_id}" class="search-result-item d-flex justify-content-between align-items-center p-2 text-decoration-none border-bottom">
          <div>
            <span class="ticker-badge text-primary">${stock.ticker_symbol}</span>
            <div class="small text-muted">${stock.company_name}</div>
          </div>
          <span class="badge bg-light text-dark">${stock.sector_name || "N/A"}</span>
        </a>`
      )
      .join("");
    searchResultsBox.innerHTML = html;
    searchResultsBox.classList.remove("d-none");
  }
});
