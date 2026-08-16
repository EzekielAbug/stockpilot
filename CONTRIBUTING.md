# Contributing to StockPilot (Backend)

Welcome to the StockPilot backend repository! I am thrilled you want to contribute. This guide will help you get your local development environment set up and explain my coding standards.

## Local Development Setup

I use Docker to guarantee environment parity across all developers' machines. You do not need to install PostgreSQL or Redis locally—Docker will handle it.

1.  **Clone and Enter:**
    ```bash
    git clone https://github.com/EzekielAbug/stockpilot.git
    cd stockpilot
    ```

2.  **Environment Variables:**
    Create a `.env` file in the root directory. You can copy the contents from `.env.example` if available, or just rely on the defaults provided in `docker-compose.yml` for local development.

3.  **Boot the Stack:**
    ```bash
    docker-compose up -d --build
    ```

4.  **Run Migrations:**
    Initialize your local database schema:
    ```bash
    docker exec stockpilot_api alembic upgrade head
    ```

Your API is now available at `http://localhost:8000`.

---

## Coding Standards

To maintain a clean and readable codebase, we adhere to the following standards:

### 1. Pydantic for Everything
Do not manually parse JSON or extract variables from `request.body()`. Always define a Pydantic schema in `app/schemas/` and inject it into your FastAPI route. This ensures automatic validation and Swagger UI generation.

### 2. Async First
This is an asynchronous codebase. 
*   Always use `async def` for route handlers.
*   Always use `await db.execute(...)` for database queries.
*   Do not use blocking synchronous libraries (e.g., use `httpx` instead of `requests`).

### 3. Inline Comments (The "Why")
Do not write comments explaining *what* the code does (e.g., `# adds 1 to x`). Write comments explaining *why* the code is necessary, especially if it handles a weird edge case or bypasses a limitation.

---

## Git & Pull Request Workflow

1.  **Branching:** Create a feature branch from `main`.
    *   `feature/add-stripe-billing`
    *   `fix/pos-inventory-bug`
2.  **Committing:** Write clear, imperative commit messages.
    *   *Good:* `Add Stripe webhook endpoint`
    *   *Bad:* `fixed the billing thing`
3.  **Pull Requests:** When opening a PR, ensure you include a brief summary of what was changed and, crucially, **how it was tested**.

If you introduce a database schema change, you **must** include the auto-generated Alembic migration file in your PR:
```bash
docker exec stockpilot_api alembic revision --autogenerate -m "Add new table"
```
