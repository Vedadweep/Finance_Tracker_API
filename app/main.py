from fastapi import FastAPI
from app.routers import users, transactions, budgets
from app.models.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Finance Tracker API",
    description="A RESTful API for tracking personal finances, transactions, and budgets.",
    version="1.0.0"
)

app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["Budgets"])

@app.get("/")
def root():
    return {"message": "Personal Finance Tracker API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
