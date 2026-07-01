from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import StudentCreate, StudentUpdate, StudentResponse


router = APIRouter(
    prefix="/students",
    tags=["student"]
)


@router.get("/", response_model=List[StudentResponse])
def get_students(
        db: Session = Depends(get_db)
):
    return crud.get_students(db)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
        student_id: int,
        db: Session = Depends(get_db)
):
    student = crud.get_student(db, student_id)

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=StudentResponse, status_code=201)
def create_student(
        student: StudentCreate,
        db: Session = Depends(get_db)
):
    return crud.create_student(db, student)


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
        student_id: int,
        student_data: StudentUpdate,
        db: Session = Depends(get_db)
):
    student = crud.update_student(db, student_id, student_data)

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.delete("/{student_id}", response_model=StudentResponse)
def delete_student(
        student_id: int,
        db: Session = Depends(get_db)
):
    student = crud.delete_student(db, student_id)

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return student