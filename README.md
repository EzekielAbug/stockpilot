

https://github.com/user-attachments/assets/0637151b-ba90-4298-ada8-8d0e4261a0ee

# StockPilot API

> A B2B Inventory SaaS Backend built with FastAPI, PostgreSQL, and Redis.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

> **👉 Looking for the User Interface?**  
> This repository contains the backend engine. The React/Vite Frontend UI repository can be found [here](https://github.com/EzekielAbug/stockpilot-frontend).

## Overview

StockPilot is an Inventory Management and Point-of-Sale (POS) system. It provides a backend API that handles the relationships between Organizations, Customers, Suppliers, Warehouses, and Products.

It is built to be fast, using an asynchronous stack (`asyncpg` + `FastAPI`). It also uses a background worker (`Redis` + `Celery`) to handle heavy tasks so the main server never slows down.

### What does StockPilot do?

StockPilot is a full-stack SaaS platform designed to help distribution businesses run their daily operations. Its core features include:
*   **Point of Sale (POS):** A fast interface for cashiers to ring up sales and instantly deduct inventory.
*   **Multi-Tenant Workspaces:** Complete data isolation. Multiple companies can use the platform at the same time without ever seeing each other's data.
*   **B2B Relationship Management:** Easily track wholesale Suppliers (who you buy from) and retail Customers (who you sell to).
*   **Safe Data Deletion:** I use "Soft Deletes" to ensure that even if a product is discontinued, historical invoices and past orders are never broken.

## Quick Start (Local Development)

The fastest way to spin up the entire stack locally (FastAPI, PostgreSQL database, Redis cache, and Celery worker) is via Docker Compose.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EzekielAbug/stockpilot.git
   cd stockpilot
   ```

2. **Start the containers:**
   ```bash
   docker-compose up -d --build
   ```

3. **Run database migrations:**
   ```bash
   docker exec stockpilot_api alembic upgrade head
   ```

The API will now be running at `http://localhost:8000`. 
You can view the interactive Swagger Documentation at `http://localhost:8000/docs`.

## Security Posture

StockPilot takes data isolation and security seriously:
*   **Multi-Tenancy:** Every resource is tied to an `org_id`. The API layer strictly validates that users can only access and modify records belonging to their authenticated organization.
*   **Authentication Flow:** I utilize short-lived JSON Web Tokens (JWT) for access control, paired with HTTP-only, secure cookies for seamless frontend integration without exposing tokens to XSS vulnerabilities.
*   **Password Hashing:** Passwords are never stored in plaintext. They are hashed using `bcrypt` via the `passlib` context.
*   **CORS Configuration:** Explicitly controlled Cross-Origin Resource Sharing ensures only authorized frontend domains can interact with the API.

## Documentation Index

To dive deeper into the architecture and design decisions, please refer to the following documents:

*   **[System Architecture (ERD & Data Flow)](docs/ARCHITECTURE.md)**: Visual diagrams of the database schema and background worker flow, plus future roadmap plans.
*   **[API Reference](docs/API_REFERENCE.md)**: Detailed breakdown of the core API contracts, failure cases, and endpoint logic.
*   **[Architecture Decision Records (ADRs)](docs/ADR.md)**: Explanations of *why* I chose soft-deletes over hard-deletes, and why I chose my asynchronous stack.
*   **[Contributing Guide](CONTRIBUTING.md)**: Onboarding instructions for new engineers, linting rules, and git workflows.

---
*Developed by Ezekiel Abug.*
