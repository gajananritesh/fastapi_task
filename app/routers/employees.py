from fastapi import APIRouter, Depends, status, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.schemas import RegisterEmployeeRequest
from app.database import get_db
from app.models import EmployeeModel



router = APIRouter(prefix='/employees', tags=['employees'])



@router.get("/", status_code=status.HTTP_200_OK)
def get_employees(skip: int = Query(default=0, ge=0, description="Offset: number of records to skip"),
                limit: int = Query(default=5, ge=1, le=100, description="Limit: max records to return"),
                db: Session = Depends(get_db)):
    return db.query(EmployeeModel).offset(skip).limit(limit).all()


@router.get("/{employee_id}", status_code=status.HTTP_200_OK)
def get_employee_by_id(employee_id: int = Path(..., gt=0, description="The ID of the employee to retrieve"),
                       db: Session = Depends(get_db)):
    return db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new item")
def create_employee(emp_data: RegisterEmployeeRequest, db: Session = Depends(get_db)):
    existing_email_user = (db.query(EmployeeModel).filter(EmployeeModel.email == emp_data.email).first())
    if existing_email_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use by another employee.",)
    
    db_item = EmployeeModel(**emp_data.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{employee_id}", status_code=status.HTTP_200_OK, summary="Replace an item completely (PUT)")
def update_employee_put(
    emp_data: RegisterEmployeeRequest,
    employee_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)):

    emp_query = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    
    existing_email_user = (db.query(EmployeeModel).filter(EmployeeModel.email == emp_data.email, EmployeeModel.id != employee_id).first())
    if existing_email_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already in use by another employee.",)
    
    update_data = emp_data.model_dump()
    for field, value in update_data.items():
        setattr(emp_query, field, value)
    db.commit()
    db.refresh(emp_query)
    return emp_query


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an item")
def delete_emp(employee_id: int = Path(..., gt=0),
                db: Session = Depends(get_db)) -> None:
    
    emp_query = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
    db.delete(emp_query)
    db.commit()