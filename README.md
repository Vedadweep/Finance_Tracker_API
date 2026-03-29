# Personal Finance Tracker API

A production-grade RESTful API built with **FastAPI** and **SQLAlchemy** for tracking personal income, expenses, and budgets — with real-time budget overspend detection.


---

## Features

- **User Management** — Create and manage user accounts
- **Transaction Tracking** — Log income and expenses with categories
- **Budget Management** — Set monthly budgets per category
- **Analytics** — Monthly summaries with income/expense breakdown by category
- **Overspend Alerts** — Automatically flag when budget limits are exceeded
- **Auto-generated API Docs** — Swagger UI at `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Validation | Pydantic v2 |
| Testing | Pytest + TestClient |
| CI/CD | GitHub Actions |

---

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Vedadweep/finance-tracker-api.git
cd finance-tracker-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` to explore the API interactively.

---

## API Endpoints

### Users
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/users/` | Create a new user |
| GET | `/api/v1/users/{user_id}` | Get user by ID |
| GET | `/api/v1/users/` | List all users |
| DELETE | `/api/v1/users/{user_id}` | Delete user |

### Transactions
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/transactions/{user_id}` | Log a transaction |
| GET | `/api/v1/transactions/{user_id}` | Get all transactions (filter by category/type) |
| GET | `/api/v1/transactions/{user_id}/summary` | Monthly income/expense summary |
| DELETE | `/api/v1/transactions/{user_id}/{txn_id}` | Delete a transaction |

### Budgets
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/budgets/{user_id}` | Set a monthly budget |
| GET | `/api/v1/budgets/{user_id}/status` | Check budget status (overspend detection) |
| GET | `/api/v1/budgets/{user_id}` | List all budgets |
| DELETE | `/api/v1/budgets/{user_id}/{budget_id}` | Delete a budget |

---

## Example Usage

**Create a user:**
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Vedadweep", "email": "veda@example.com"}'
```

**Log an expense:**
```bash
curl -X POST "http://localhost:8000/api/v1/transactions/1" \
  -H "Content-Type: application/json" \
  -d '{"amount": 500, "category": "Food", "type": "expense", "description": "Dinner"}'
```

**Check budget status:**
```bash
curl "http://localhost:8000/api/v1/budgets/1/status?month=3&year=2026"
```

---

## Running Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

Tests cover: user creation, duplicate prevention, transaction CRUD, monthly summaries, budget creation, duplicate detection, and overspend alerts. Coverage target: **>80%**.

---

## Project Structure

```
finance-tracker-api/
├── app/
│   ├── main.py               # FastAPI app & route registration
│   ├── models/
│   │   ├── database.py       # DB engine & session setup
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py        # Pydantic request/response schemas
│   └── routers/
│       ├── users.py          # User endpoints
│       ├── transactions.py   # Transaction endpoints + analytics
│       └── budgets.py        # Budget endpoints + overspend logic
├── tests/
│   └── test_api.py           # Pytest unit tests (13 test cases)
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI pipeline
├── requirements.txt
└── README.md
```
