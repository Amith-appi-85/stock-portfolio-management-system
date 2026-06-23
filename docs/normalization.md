# Database Normalization — Explanation (1NF, 2NF, 3NF)

This document explains how the schema in `schema.sql` satisfies the first three
normal forms. Use this directly for your DBMS viva.

---

## 1. First Normal Form (1NF)

**Rule:** Every table has a primary key, every column holds a single
(atomic) value, and there are no repeating groups or multi-valued columns.

**How our schema satisfies it:**
- Every table (`users`, `stocks`, `sectors`, `portfolio`, `transactions`,
  `watchlist`) has a single-column surrogate primary key (`user_id`,
  `stock_id`, etc.).
- No column stores multiple values. For example, instead of storing a
  comma-separated list of stocks a user owns inside the `users` table, we
  created a separate `portfolio` table with one row per (user, stock)
  holding. Similarly, a user's watchlist is a separate table with one row
  per (user, stock) pair, not a CSV column.
- Each attribute (e.g. `email`, `ticker_symbol`, `quantity`) holds exactly
  one atomic value per row.

✅ Result: All tables are in 1NF.

---

## 2. Second Normal Form (2NF)

**Rule:** Table must be in 1NF, and every non-key attribute must depend on
the **whole** primary key — no partial dependency on part of a composite key.

**Where this matters in our design:**
- The `portfolio` table conceptually has a composite business key of
  `(user_id, stock_id)` — a holding only makes sense for a specific user
  *and* a specific stock. We enforce this with `UNIQUE (user_id, stock_id)`
  even though we use a surrogate `portfolio_id` as the actual primary key.
  Attributes like `quantity`, `average_buy_price`, and `total_invested`
  depend on **both** `user_id` and `stock_id` together (a quantity means
  nothing without knowing which user *and* which stock it refers to) — not
  on just one of them. So there is no partial dependency.
- Similarly, `watchlist` has a composite uniqueness constraint
  `(user_id, stock_id)`, and `added_at` depends on the combination of both.
- Because every other table (`users`, `stocks`, `sectors`, `transactions`)
  already has a single-column primary key, partial dependency cannot occur
  in those tables by definition — 2NF is automatically satisfied for them
  once 1NF holds.

✅ Result: All tables are in 2NF.

---

## 3. Third Normal Form (3NF)

**Rule:** Table must be in 2NF, and there must be no transitive dependency
— i.e., no non-key attribute should depend on another non-key attribute.

**Key design decision demonstrating 3NF — the `sectors` table:**
- A naive design might store `sector_name` and `sector_description`
  directly inside the `stocks` table. But then `sector_description`
  depends on `sector_name`, which itself is a non-key attribute of
  `stocks` — a transitive dependency
  (`stock_id → sector_name → sector_description`).
- We removed this transitive dependency by extracting sectors into their
  own table: `sectors(sector_id, sector_name, description)`, and `stocks`
  only stores a foreign key `sector_id` referencing it. Now
  `sector_name` and `description` depend only on `sector_id` (the key of
  `sectors`), not transitively through another non-key column of `stocks`.

**Other 3NF checks:**
- In `transactions`, `total_amount` is derived from `quantity × price_per_share`.
  We store it directly (a deliberate denormalization for performance/audit —
  explained below) rather than recomputing it every time, but conceptually
  it depends only on the transaction's own key attributes, not on another
  non-key column.
- In `portfolio`, `total_invested` and `average_buy_price` depend on the
  (user_id, stock_id) combination directly — not on each other transitively
  in a way that creates anomalies, since both are maintained together by
  the application logic on every BUY/SELL.
- `users.role` does not depend on any other non-key column; same for
  `stocks.exchange`, `stocks.currency`, etc.

✅ Result: All tables are in 3NF.

---

## Note on Intentional Denormalization

Two fields are **intentionally** kept slightly denormalized for practical,
performance, and audit reasons — this is a common, defensible real-world
trade-off and a good viva talking point:

1. **`stocks.last_price`** — Technically this could be derived as "the
   latest price fetched from yfinance," but we cache it in the table so
   dashboard/portfolio queries don't need an external API call on every
   page load. It's refreshed periodically by the backend.
2. **`transactions.total_amount`** — Could be computed as
   `quantity * price_per_share`, but storing it directly preserves an
   immutable audit record even if business rules around pricing change
   later, and avoids recomputation on every report query.

This is normalized **data design** with a deliberate, documented caching
strategy — not a normalization flaw.

---

## Functional Dependency Summary (for viva quick reference)

| Table | Primary Key | Functional Dependencies |
|---|---|---|
| sectors | sector_id | sector_id → sector_name, description |
| users | user_id | user_id → full_name, email, username, password_hash, role, virtual_balance |
| stocks | stock_id | stock_id → ticker_symbol, company_name, sector_id, exchange, currency, last_price |
| portfolio | portfolio_id (uq: user_id+stock_id) | (user_id, stock_id) → quantity, average_buy_price, total_invested |
| transactions | transaction_id | transaction_id → user_id, stock_id, type, quantity, price_per_share, total_amount, date |
| watchlist | watchlist_id (uq: user_id+stock_id) | (user_id, stock_id) → added_at |
