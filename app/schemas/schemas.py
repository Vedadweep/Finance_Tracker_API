from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.models import TransactionType


# --- User Schemas ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Transaction Schemas ---
class TransactionCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    type: TransactionType
    date: Optional[datetime] = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    category: str
    description: Optional[str]
    type: TransactionType
    date: datetime

    class Config:
        from_attributes = True

class TransactionSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    by_category: dict


# --- Budget Schemas ---
class BudgetCreate(BaseModel):
    category: str
    limit_amount: float
    month: int
    year: int

class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    limit_amount: float
    month: int
    year: int

    class Config:
        from_attributes = True

class BudgetStatus(BaseModel):
    category: str
    limit_amount: float
    spent: float
    remaining: float
    is_exceeded: bool
