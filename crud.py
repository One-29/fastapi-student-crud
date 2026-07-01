from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional


from models import Student
from schemas import StudentCreate, StudentUpdate


#获取学生列表
def get_students(
        db: Session
):
    return db.query(Student).all()


# 查询学生信息
def get_student(
        db: Session,
        student_id: int
) -> Optional[Student]:
    try:
        stmt = select(Student).where(Student.id == student_id)
        return db.scalars(stmt).first()
    except Exception as e:
        print(f"查询学生数据库错误 (ID={student_id}) : {e}")
        raise


# 创建新的学生信息
def create_student(
        db: Session,
        student: StudentCreate
) -> Student:
    try:
        new_student = Student(
            name=student.name,
            age=student.age
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return new_student

    except Exception as e:
        db.rollback()
        print(f"创建学生数据库错误: {e}")
        raise


# 修改单个学生信息
def update_student(
        db: Session,
        student_id: int,
        student_data: StudentUpdate,
) -> Optional[Student]:
    try:
        stmt = select(Student).where(Student.id==student_id)
        student = db.scalars(stmt).first()

        if student is None:
            return None

        update_data = student_data.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(student, key, val)

        db.commit()
        db.refresh(student)

        return student

    except Exception as e:
        db.rollback()
        print(f"更新学生数据库错误 (ID={student_id}) : {e}")
        raise


# 删除单个学生的信息
def delete_student(
        db: Session,
        student_id: int,
) -> Optional[Student]:
    try:
        stmt = select(Student).where(Student.id==student_id)
        student = db.scalars(stmt).first()

        if student is None:
            return None

        db.delete(student)
        db.commit()

        return student
    except Exception as e:
        db.rollback()
        print(f"删除学生数据库错误 (ID={student_id}) : {e}")
        raise


