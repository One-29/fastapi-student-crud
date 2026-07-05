from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import crud
from database import get_db
from schemas import StudentCreate, StudentUpdate, StudentResponse


router = APIRouter(
    prefix="/students",
    tags=["student"]
)


@router.get("/", response_model=List[StudentResponse])
async def get_students(
        db: AsyncSession = Depends(get_db)
):
    return await crud.get_students(db)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
        student_id: int,
        db: AsyncSession = Depends(get_db)
):
    student = await crud.get_student(db, student_id)

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(
        student: StudentCreate,
        db: AsyncSession = Depends(get_db)
):
    return await crud.create_student(db, student)


@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(
        student_id: int,
        student_data: StudentUpdate,
        db: AsyncSession = Depends(get_db)
):
    student = await crud.update_student(db, student_id, student_data)

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.delete("/{student_id}", response_model=StudentResponse)
async def delete_student(
        student_id: int,
        db: AsyncSession = Depends(get_db)
):
    student = await crud.delete_student(db, student_id)

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return student