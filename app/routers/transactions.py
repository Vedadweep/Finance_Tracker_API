from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime
from app.models.database import get_db
from app.models.models import Transaction, User, TransactionType
from app.schemas.schemas import TransactionCreate, TransactionResponse, TransactionSummary

router = APIRouter()


def get_user_or_404(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(user_id: int, txn: TransactionCreate, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    db_txn = Transaction(
        user_id=user_id,
        amount=txn.amount,
        category=txn.category,
        description=txn.description,
        type=txn.type,
        date=txn.date or datetime.utcnow()
    )
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn)
    return db_txn


@router.get("/{user_id}", response_model=list[TransactionResponse])
def get_transactions(
    user_id: int,
    category: Optional[str] = None,
    type: Optional[TransactionType] = None,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    get_user_or_404(user_id, db)
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if category:
        query = query.filter(Transaction.category == category)
    if type:
        query = query.filter(Transaction.type == type)
    return query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()


@router.get("/{user_id}/summary", response_model=TransactionSummary)
def get_summary(user_id: int, month: Optional[int] = None, year: Optional[int] = None, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if month and year:
        query = query.filter(
            func.strftime("%m", Transaction.date) == f"{month:02d}",
            func.strftime("%Y", Transaction.date) == str(year)
        )
    transactions = query.all()

    total_income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)

    by_category = {}
    for t in transactions:
        by_category[t.category] = by_category.get(t.category, 0) + t.amount

    return TransactionSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=total_income - total_expenses,
        by_category=by_category
    )


@router.delete("/{user_id}/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(user_id: int, transaction_id: int, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    ).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(txn)
    db.commit()
