# Architecture Decision Records (ADR)

This document captures the context, consequences, and reasoning behind major architectural decisions made during the development of the StockPilot backend.

---

## ADR-001: Asynchronous PostgreSQL Engine (`asyncpg`)

**Status:** Accepted

**Context:**
Point-of-Sale (POS) systems require extremely fast, high-concurrency database reads and writes. A cashier scanning items needs sub-second response times, and traditional synchronous WSGI applications (like Flask + `psycopg2`) can easily bottle-neck when the thread pool is exhausted during peak business hours.

**Decision:**
I chose FastAPI as my web framework and paired it specifically with the `asyncpg` PostgreSQL driver. All SQLAlchemy database sessions are instantiated using `AsyncSession`.

**Consequences:**
*   **Positive:** The FastAPI event loop is never blocked waiting for network I/O to the database. We can handle thousands of concurrent requests using minimal server resources.
*   **Negative:** Developers must remember to use `await` on every database execution and use `select()` rather than the legacy `query()` API in SQLAlchemy 2.0.

---

## ADR-002: Soft Deletes vs. Hard Deletes

**Status:** Accepted

**Context:**
In a business accounting application, historical records must be immutable. If a company stops selling a specific "Keyboard" and deletes it from the database, any old invoice that referenced that Keyboard's `product_id` would break or lose context.

**Decision:**
I implemented a "Soft Delete" pattern for critical catalog entities (`Products`, `Customers`, `Suppliers`, `Warehouses`). We added an `is_active` boolean column to these tables.
When a user clicks "Delete" in the UI, I execute a SQL `UPDATE` to set `is_active = False` rather than a SQL `DELETE`. 

**Consequences:**
*   **Positive:** Relational integrity is perfectly preserved. Historical orders will always be able to join against the `products` table to fetch the name and SKU of discontinued items.
*   **Negative:** All standard `GET` API endpoints must explicitly add `.where(Model.is_active == True)` to prevent deleted items from showing up in active UI dropdowns.

**Revisit Trigger:** 
If the database size grows excessively due to soft-deleted records, I may need to implement a scheduled Celery task to archive/move soft-deleted records older than 7 years (standard accounting retention period) into cold storage.

---

## ADR-003: Background Processing with Celery

**Status:** Accepted

**Context:**
User registration requires sending a welcome email. Uploading a bulk CSV of inventory requires parsing and validating potentially thousands of rows. Doing this inside the HTTP request loop would cause the user's browser to hang and potentially time out.

**Decision:**
I introduced Redis and Celery into the stack. Heavy I/O tasks (like `send_welcome_email`) are dispatched to the Redis broker using `.delay()`, allowing the HTTP response to return `201 Created` instantly.

**Consequences:**
*   **Positive:** Snappy user experience. HTTP requests finish in milliseconds regardless of background work.
*   **Negative:** Increased infrastructure complexity. We now must monitor and deploy a separate Celery worker container alongside the main API container.
