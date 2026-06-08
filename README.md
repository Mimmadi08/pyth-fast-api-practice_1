# Learning - OMS Order Management REST API

A production-grade REST API built with **Python FastAPI** connected to the **Oracle OMS Database**, providing full CRUD operations on Pre-Order Headers with API Key authentication.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the API](#running-the-api)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Request & Response Examples](#request--response-examples)
- [Error Handling](#error-handling)
- [Testing with Postman](#testing-with-postman)

---

## Overview

This API provides a RESTful interface to the `OMS_ORD_DATA.OMS_PRE_ORDER_HEADERS` table in the Oracle OMS database. It allows teams to:

- Search and retrieve orders with dynamic filters
- Create new pre-order headers
- Update single or multiple orders in one call
- Delete orders
- Find orders that have no associated order lines
- All endpoints are protected with API Key authentication

---

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.9.6 | Core language |
| FastAPI | 0.128.8 | REST API framework |
| Uvicorn | 0.39.0 | ASGI server |
| Pydantic | 2.13.4 | Data validation |
| oracledb | 4.0.1 | Oracle DB driver |

---

## Project Structure

```
pyth-fast-api-practice_1/
│
├── main.py           # Application entry point — registers routes and exception handler
├── database.py       # Oracle DB connection factory
├── schemas.py        # Pydantic request/response models (data contracts)
├── orders.py         # All order-related API routes
├── auth.py           # API Key authentication
├── exceptions.py     # Global exception handler
├── requirements.txt  # All Python dependencies
└── README.md         # This file
```

### File Responsibilities

| File | Responsibility |
|------|---------------|
| `main.py` | Creates FastAPI app, registers global handlers and routers |
| `database.py` | Single place for DB credentials and connection logic |
| `schemas.py` | Defines shape and types of all incoming/outgoing data |
| `orders.py` | All 8 API endpoints — search, CRUD, pagination |
| `auth.py` | Verifies `X-API-Key` header on every protected route |
| `exceptions.py` | Catches unhandled errors — never exposes stack traces |

---

## Prerequisites

Before running this project make sure you have:

- **Python 3.9+** installed on your machine
- **VPN connected** to company network (required to reach Oracle DB)
- **Git** installed
- **Postman** or any API testing tool

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/CharitIT/pyth-rest-api-p1.git
cd pyth-rest-api-p1
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

> ⚠️ Always use a virtual environment — keeps packages isolated from your system Python

### 3. Activate virtual environment

```bash
# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Add venv to .gitignore (first time only)

```bash
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
```

---

## Configuration

### Database Connection

Edit `database.py` with your Oracle DB credentials:

```python
conn = oracledb.connect(
    user="your_username",
    password="your_password",
    dsn="your_host:your_port/your_service_name"
)
```

Current configuration connects to:
- **Host:** `omsddb.cswg.com`
- **Port:** `1521`
- **Service:** `omsd_app`
- **Schema:** `OMS_ORD_DATA`

> ⚠️ **VPN Required** — The Oracle DB is on a remote company server. Always connect to VPN before running the API.

### API Key

Edit `auth.py` to set your API key:

```python
API_KEY = "your-api-key-here"
```

> ⚠️ In production, move credentials to environment variables — never hardcode in source files.

---

## Running the API

### Start the server

```bash
uvicorn main:app --reload
```

- `main` → refers to `main.py`
- `app` → the FastAPI instance inside it
- `--reload` → auto-restarts on file save (use for development only)

### Verify it's running

Open your browser and visit:
- `http://localhost:8000` → health check
- `http://localhost:8000/docs` → interactive Swagger UI (auto-generated)

### Stop the server

```bash
Ctrl + C
```

---

## API Endpoints

Base URL: `http://localhost:8000`

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/orders` | Get paginated list of orders | ✅ Yes |
| `POST` | `/orders` | Create a new order | ✅ Yes |
| `POST` | `/orders/search` | Search orders with dynamic filters | ✅ Yes |
| `GET` | `/orders/no-lines` | Get orders with no order lines | ✅ Yes |
| `GET` | `/orders/{id}` | Get a single order by ID | ✅ Yes |
| `PUT` | `/orders/update/single` | Update one order | ✅ Yes |
| `PUT` | `/orders/update/multi` | Update multiple orders in one call | ✅ Yes |
| `DELETE` | `/orders/{id}` | Delete an order by ID | ✅ Yes |

---

## Authentication

All endpoints require an API Key passed in the request header:

```
X-API-Key: your-api-key-here
```

### Response codes for auth failures

| Scenario | Status Code | Response |
|----------|------------|---------|
| Missing header | `422` | Unprocessable Entity |
| Wrong API key | `401` | Invalid API Key. Access denied. |
| Correct API key | `200` | Success |

---

## Request & Response Examples

### GET /orders — Paginated list

```
GET http://localhost:8000/orders?skip=0&limit=10
Headers: X-API-Key: your-api-key
```

Response:
```json
[
  {
    "order_header_id": 111,
    "order_type": "Regular",
    "store_num": "54034",
    "attrinute2": null,
    "program_type": null,
    "request_delivery_date": "01/25/2022",
    "order_status": "S",
    "customer_dept_num": "40",
    "csor_confirmation_number": 330568
  }
]
```

---

### POST /orders/search — Dynamic search

At least **2 fields** must be provided.

```
POST http://localhost:8000/orders/search?skip=0&limit=10
Headers: X-API-Key: your-api-key
Body:
```

```json
{
  "division_id": 1,
  "channel": "GROUPORDER"
}
```

---

### POST /orders — Create new order

```
POST http://localhost:8000/orders
Headers: X-API-Key: your-api-key
Body:
```

```json
{
  "order_type": "Regular",
  "store_num": "69200",
  "division_id": 1,
  "channel": "GROUPORDER",
  "order_status": "U",
  "customer_notes": "Created via API"
}
```

Response:
```json
{
  "created": true,
  "order_header_id": 114979,
  "order_type": "Regular",
  "store_num": "69200",
  "order_status": "U"
}
```

---

### GET /orders/no-lines — Orders with no lines

```
GET http://localhost:8000/orders/no-lines?order_status=U&order_type=Regular
Headers: X-API-Key: your-api-key
```

Default values: `order_status=U`, `order_type=Regular`

---

### GET /orders/{id} — Get single order

```
GET http://localhost:8000/orders/111
Headers: X-API-Key: your-api-key
```

---

### PUT /orders/update/single — Update one order

```
PUT http://localhost:8000/orders/update/single
Headers: X-API-Key: your-api-key
Body:
```

```json
{
  "order_header_id": 641,
  "order_status": "C",
  "customer_notes": "Updated via API"
}
```

Response:
```json
{
  "updated": true,
  "order_header_id": 641
}
```

---

### PUT /orders/update/multi — Update multiple orders

```
PUT http://localhost:8000/orders/update/multi
Headers: X-API-Key: your-api-key
Body:
```

```json
{
  "orders": [
    {
      "order_header_id": 641,
      "order_status": "C"
    },
    {
      "order_header_id": 876,
      "order_status": "U",
      "channel": "GROUPORDER"
    }
  ]
}
```

Response:
```json
{
  "updated": [641, 876],
  "not_found": [],
  "total_updated": 2
}
```

---

### DELETE /orders/{id} — Delete an order

```
DELETE http://localhost:8000/orders/592
Headers: X-API-Key: your-api-key
```

Response:
```json
{
  "deleted": true,
  "order_header_id": 592
}
```

---

## Error Handling

The API returns consistent error responses across all endpoints:

| Status Code | Meaning | When it happens |
|-------------|---------|----------------|
| `200` | OK | Request successful |
| `400` | Bad Request | No fields to update provided |
| `401` | Unauthorized | Wrong API key |
| `404` | Not Found | Order ID doesn't exist / no results |
| `422` | Unprocessable Entity | Missing required fields or wrong data types |
| `500` | Internal Server Error | Unexpected error — DB connection issues etc. |

### Example error responses

**404 — Order not found:**
```json
{
  "detail": "Order 99999 not found"
}
```

**422 — Missing API key:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["header", "x-api-key"],
      "msg": "Field required"
    }
  ]
}
```

**500 — Unhandled error:**
```json
{
  "error": "Something went wrong",
  "detail": "Please contact support"
}
```

---

## Testing with Postman

1. Download and install [Postman](https://www.postman.com/)
2. Create a new collection called `OMS API`
3. For every request add the header:
   - Key: `X-API-Key`
   - Value: `your-api-key`
4. Make sure VPN is connected before testing
5. Use `http://localhost:8000/docs` for quick interactive testing via Swagger UI

---

## Daily Development Workflow

```bash
# 1. Connect VPN

# 2. Navigate to project
cd /Users/mcihub/Work/C&S/LearningSessions/pyth-fast-api-practice_1

# 3. Activate venv
source venv/bin/activate

# 4. Start server
uvicorn main:app --reload

# 5. After making changes — push to GitHub
git add .
git commit -m "description of changes"
git push
```

---

*Built by Cherry (Meher Charit) — Senior Applications Engineer, C&S Supply Chain Team*
