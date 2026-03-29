from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.models import Budget, Transaction, User, TransactionType
from app.schemas.schemas import BudgetCreate, BudgetResponse, BudgetStatus

router = APIRouter()


def get_user_or_404(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(user_id: int, budget: BudgetCreate, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    existing = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category == budget.category,
        Budget.month == budget.month,
        Budget.year == budget.year
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Budget for this category/month already exists")
    db_budget = Budget(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.get("/{user_id}/status", response_model=list[BudgetStatus])
def get_budget_status(user_id: int, month: int, year: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    budgets = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.month == month,
        Budget.year == year
    ).all()

    result = []
    for b in budgets:
        spent = sum(
            t.amount for t in db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.category == b.category,
                Transaction.type == TransactionType.EXPENSE
            ).all()
        )
        result.append(BudgetStatus(
            category=b.category,
            limit_amount=b.limit_amount,
            spent=spent,
            remaining=max(0, b.limit_amount - spent),
            is_exceeded=spent > b.limit_amount
        ))
    return result


@router.get("/{user_id}", response_model=list[BudgetResponse])
def list_budgets(user_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    return db.query(Budget).filter(Budget.user_id == user_id).all()


@router.delete("/{user_id}/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(user_id: int, budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    db.delete(budget)
    db.commit()
