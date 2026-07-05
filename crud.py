from sqlalchemy import select
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from models import Student
from schemas import StudentCreate, StudentUpdate


#获取学生列表
async def get_students(
        db: AsyncSession
) -> List[Student]:

    stmt = select(Student)
    result = await db.execute(stmt)
    students = result.scalars().all()

    return list(students)


# 查询学生信息
async def get_student(
        db: AsyncSession,
        student_id: int
) -> Optional[Student]:
    try:
        stmt = select(Student).where(Student.id == student_id)
        result = await db.execute(stmt)
        return result.scalars().first()
    except Exception as e:
        print(f"查询学生数据库错误 (ID={student_id}) : {e}")
        raise


# 创建新的学生信息
async def create_student(
        db: AsyncSession,
        student: StudentCreate
) -> Student:
    try:
        new_student = Student(
            name=student.name,
            age=student.age
        )

        db.add(new_student)
        await db.commit()
        await db.refresh(new_student)

        return new_student

    except Exception as e:
        await db.rollback()
        print(f"创建学生数据库错误: {e}")
        raise


# 修改单个学生信息
async def update_student(
        db: AsyncSession,
        student_id: int,
        student_data: StudentUpdate,
) -> Optional[Student]:
    try:
        stmt = select(Student).where(Student.id==student_id)
        result = await db.execute(stmt)
        student = result.scalars().first()

        if student is None:
            return None

        update_data = student_data.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(student, key, val)

        await db.commit()
        await db.refresh(student)

        return student

    except Exception as e:
        await db.rollback()
        print(f"更新学生数据库错误 (ID={student_id}) : {e}")
        raise


# 删除单个学生的信息
async def delete_student(
        db: AsyncSession,
        student_id: int,
) -> Optional[Student]:
    try:
        stmt = select(Student).where(Student.id==student_id)
        result = await db.execute(stmt)
        student = result.scalars().first()

        if student is None:
            return None

        await db.delete(student)
        await db.commit()

        return student
    except Exception as e:
        await db.rollback()
        print(f"删除学生数据库错误 (ID={student_id}) : {e}")
        raise


