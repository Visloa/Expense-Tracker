from datetime import date

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Expense
from app.schemas import ExpenseCreate, ExpenseResponse

from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy import func

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Expense Tracker API")

@app.get("/")
def root():
    return {
        "message": "Personal Expense Tracker API is running"
    }


@app.post("/expenses", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
):
    new_expense = Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        expense_date=expense.expense_date,
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense

@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
):
    expenses = db.query(Expense).all()

    return expenses

@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    return expense

@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    expense.title = expense_data.title
    expense.amount = expense_data.amount
    expense.category = expense_data.category
    expense.expense_date = expense_data.expense_date

    db.commit()
    db.refresh(expense)

    return expense


@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    db.delete(expense)
    db.commit()

    return {
        "message": "Expense deleted successfully"
    }
    
    
@app.get("/analytics/category")
def category_summary(
    db: Session = Depends(get_db),
):
    results = (
        db.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
        )
        .group_by(Expense.category)
        .all()
    )

    return [
        {
            "category": category,
            "total": total,
        }
        for category, total in results
    ]
    
    
    
@app.get("/analytics/monthly")
def monthly_summary(
    db: Session = Depends(get_db),
):
    results = (
        db.query(
            func.extract("year", Expense.expense_date).label("year"),
            func.extract("month", Expense.expense_date).label("month"),
            func.sum(Expense.amount).label("total"),
        )
        .group_by(
            func.extract("year", Expense.expense_date),
            func.extract("month", Expense.expense_date),
        )
        .order_by(
            func.extract("year", Expense.expense_date),
            func.extract("month", Expense.expense_date),
        )
        .all()
    )

    return [
        {
            "year": int(year),
            "month": int(month),
            "total": total,
        }
        for year, month, total in results
    ]