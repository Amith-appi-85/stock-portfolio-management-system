# Entity-Relationship Diagram (Mermaid)

Paste this block into [mermaid.live](https://mermaid.live) or any Markdown
viewer that supports Mermaid (GitHub, VS Code with Mermaid extension, Notion,
etc.) to render the diagram visually for your report/PPT.

```mermaid
erDiagram
    USERS {
        int user_id PK
        varchar full_name
        varchar email
        varchar username
        varchar password_hash
        enum role
        decimal virtual_balance
        tinyint is_active
        timestamp created_at
        timestamp updated_at
    }

    SECTORS {
        int sector_id PK
        varchar sector_name
        varchar description
        timestamp created_at
    }

    STOCKS {
        int stock_id PK
        varchar ticker_symbol
        varchar company_name
        int sector_id FK
        varchar exchange
        varchar currency
        decimal last_price
        timestamp last_updated
        tinyint is_active
        timestamp created_at
    }

    PORTFOLIO {
        int portfolio_id PK
        int user_id FK
        int stock_id FK
        int quantity
        decimal average_buy_price
        decimal total_invested
        timestamp created_at
        timestamp updated_at
    }

    TRANSACTIONS {
        int transaction_id PK
        int user_id FK
        int stock_id FK
        enum transaction_type
        int quantity
        decimal price_per_share
        decimal total_amount
        timestamp transaction_date
    }

    WATCHLIST {
        int watchlist_id PK
        int user_id FK
        int stock_id FK
        timestamp added_at
    }

    AUDIT_LOG {
        int log_id PK
        int user_id FK
        varchar action
        varchar details
        timestamp created_at
    }

    USERS ||--o{ PORTFOLIO : "holds"
    USERS ||--o{ TRANSACTIONS : "performs"
    USERS ||--o{ WATCHLIST : "tracks"
    USERS ||--o{ AUDIT_LOG : "generates"

    STOCKS ||--o{ PORTFOLIO : "appears_in"
    STOCKS ||--o{ TRANSACTIONS : "traded_in"
    STOCKS ||--o{ WATCHLIST : "watched_via"

    SECTORS ||--o{ STOCKS : "categorizes"
```

## Relationship Summary

| Relationship | Cardinality | Description |
|---|---|---|
| USERS → PORTFOLIO | 1 : N | A user can hold many stocks; each portfolio row belongs to exactly one user |
| STOCKS → PORTFOLIO | 1 : N | A stock can be held by many users |
| USERS → TRANSACTIONS | 1 : N | A user can make many buy/sell transactions |
| STOCKS → TRANSACTIONS | 1 : N | A stock can be involved in many transactions |
| USERS → WATCHLIST | 1 : N | A user can watch many stocks |
| STOCKS → WATCHLIST | 1 : N | A stock can be watched by many users |
| SECTORS → STOCKS | 1 : N | A sector contains many stocks; a stock belongs to one sector |
| USERS → AUDIT_LOG | 1 : N | Each audit entry optionally traces back to the acting user |

**Composite/derived entity:** `PORTFOLIO` and `WATCHLIST` are classic
resolution tables for the underlying **many-to-many** relationship between
`USERS` and `STOCKS` ("a user can own/watch many stocks" and "a stock can be
owned/watched by many users"). `TRANSACTIONS` is the immutable event log
behind that same M:N relationship.
