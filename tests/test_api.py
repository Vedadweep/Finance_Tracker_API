import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


# --- Health ---
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# --- Users ---
def test_create_user():
    response = client.post("/api/v1/users/", json={"name": "Vedadweep", "email": "veda@example.com"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "veda@example.com"
    assert data["name"] == "Vedadweep"

def test_duplicate_user_email():
    client.post("/api/v1/users/", json={"name": "A", "email": "a@example.com"})
    response = client.post("/api/v1/users/", json={"name": "B", "email": "a@example.com"})
    assert response.status_code == 400

def test_get_nonexistent_user():
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404


# --- Transactions ---
def create_test_user():
    r = client.post("/api/v1/users/", json={"name": "Test User", "email": "test@test.com"})
    return r.json()["id"]

def test_create_transaction():
    uid = create_test_user()
    response = client.post(f"/api/v1/transactions/{uid}", json={
        "amount": 500.0,
        "category": "Food",
        "type": "expense",
        "description": "Lunch"
    })
    assert response.status_code == 201
    assert response.json()["amount"] == 500.0

def test_transaction_summary():
    uid = create_test_user()
    client.post(f"/api/v1/transactions/{uid}", json={"amount": 10000, "category": "Salary", "type": "income"})
    client.post(f"/api/v1/transactions/{uid}", json={"amount": 3000, "category": "Rent", "type": "expense"})
    response = client.get(f"/api/v1/transactions/{uid}/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_income"] == 10000
    assert data["total_expenses"] == 3000
    assert data["net_balance"] == 7000

def test_filter_transactions_by_category():
    uid = create_test_user()
    client.post(f"/api/v1/transactions/{uid}", json={"amount": 200, "category": "Food", "type": "expense"})
    client.post(f"/api/v1/transactions/{uid}", json={"amount": 1000, "category": "Salary", "type": "income"})
    response = client.get(f"/api/v1/transactions/{uid}?category=Food")
    assert response.status_code == 200
    assert len(response.json()) == 1


# --- Budgets ---
def test_create_budget():
    uid = create_test_user()
    response = client.post(f"/api/v1/budgets/{uid}", json={
        "category": "Food", "limit_amount": 5000, "month": 3, "year": 2026
    })
    assert response.status_code == 201
    assert response.json()["limit_amount"] == 5000

def test_duplicate_budget_rejected():
    uid = create_test_user()
    payload = {"category": "Food", "limit_amount": 5000, "month": 3, "year": 2026}
    client.post(f"/api/v1/budgets/{uid}", json=payload)
    response = client.post(f"/api/v1/budgets/{uid}", json=payload)
    assert response.status_code == 400

def test_budget_status_exceeded():
    uid = create_test_user()
    client.post(f"/api/v1/budgets/{uid}", json={"category": "Food", "limit_amount": 200, "month": 3, "year": 2026})
    client.post(f"/api/v1/transactions/{uid}", json={"amount": 500, "category": "Food", "type": "expense"})
    response = client.get(f"/api/v1/budgets/{uid}/status?month=3&year=2026")
    assert response.status_code == 200
    status = response.json()[0]
    assert status["is_exceeded"] is True
    assert status["spent"] == 500
