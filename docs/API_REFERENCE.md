# API Reference & Contracts

StockPilot exposes a RESTful JSON API using FastAPI. All endpoints (except registration and login) require a valid JSON Web Token (JWT) provided as an `HttpOnly` cookie or an `Authorization: Bearer <token>` header.

> [!TIP]
> **Interactive Documentation**
> When running the server locally, you can view the auto-generated Swagger UI and test endpoints directly at `http://localhost:8000/docs`.

---

## Standard Error Handling

To ensure frontend clients can gracefully handle API failures, I document my failure states first. All API errors follow a standardized JSON structure.

### 401 Unauthorized
Returned when a token is missing, expired, or invalid.
```json
{
  "detail": "Could not validate credentials"
}
```
**Resolution:** The frontend client should clear local user state and redirect to the `/login` route.

### 403 Forbidden
Returned when a user attempts to access a resource that belongs to a different Organization (`org_id` mismatch).
```json
{
  "detail": "Not authorized to access this resource"
}
```
**Resolution:** Prevent UI navigation to resource IDs not owned by the tenant.

### 404 Not Found (or Soft Deleted)
Returned when a resource does not exist, OR when `is_active` is `false` (soft-deleted).
```json
{
  "detail": "Product not found"
}
```
**Resolution:** Display a 404 page or remove the item from the local UI state.

---

## Authentication (`/api/v1/auth`)

### `POST /register`
Creates a new User and a new Organization simultaneously.

**Request Payload:**
```json
{
  "email": "admin@example.com",
  "password": "strongpassword123",
  "full_name": "Jane Doe",
  "org_name": "Jane's Distribution Co."
}
```

**Success (201 Created):**
Returns a JWT access token and sets an `HttpOnly` cookie.

**Failure Cases:**
*   `400 Bad Request`: "Email already registered"

---

## Customers (`/api/v1/customers`)

### `GET /`
Retrieves a paginated list of all *active* customers belonging to the user's organization.

**Success (200 OK):**
```json
[
  {
    "id": "uuid-string",
    "name": "Acme Corp",
    "email": "contact@acme.com",
    "phone": "555-0192",
    "address": "123 Business Rd.",
    "is_active": true
  }
]
```

### `DELETE /{customer_id}`
Soft-deletes a customer.

**Success (204 No Content):**
The record remains in the database to preserve historical invoices, but `is_active` is set to `false`. It will no longer appear in the `GET /` list.

**Failure Cases:**
*   `404 Not Found`: If the customer doesn't exist or is already deleted.
*   `403 Forbidden`: If the customer belongs to a different organization.

---

## Orders & POS (`/api/v1/orders`)

### `POST /`
Creates a new purchase or sales order and automatically updates related inventory levels.

**Request Payload:**
```json
{
  "order_type": "sale",
  "customer_id": "uuid-string",
  "items": [
    {
      "product_id": "uuid-string",
      "quantity": 5,
      "unit_price": 49.99
    }
  ],
  "notes": "Urgent delivery"
}
```

**Failure Cases:**
*   `400 Bad Request`: "Insufficient inventory for product XYZ." (Raised when a sales order requests a quantity higher than the current stock level in the `InventoryItem` table).
*   `422 Unprocessable Entity`: Raised by Pydantic if `quantity` is negative.
