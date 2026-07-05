import pytest
from crud import get_students, create_student, get_student, update_student, delete_student
from schemas import StudentCreate, StudentUpdate


@pytest.mark.asyncio
async def test_create_student(db_session):
    data = StudentCreate(name="张三", age=20)
    student = await create_student(db_session, data)

    assert student.id is not None
    assert student.name == "张三"
    assert student.age == 20


@pytest.mark.asyncio
async def test_get_student(db_session):
    data = StudentCreate(name="李四", age=22)
    created = await create_student(db_session, data)

    fetched = await get_student(db_session, created.id)
    assert fetched is not None
    assert fetched.name == "李四"


@pytest.mark.asyncio
async def test_get_students(db_session):
    await create_student(db_session, StudentCreate(name="王五", age=24))
    await create_student(db_session, StudentCreate(name="赵六", age=26))

    students = await get_students(db_session)

    assert len(students) == 2
    assert students[0].name == "王五"
    assert students[0].age == 24
    assert students[1].name == "赵六"
    assert students[1].age == 26


@pytest.mark.asyncio
async def test_update_student(db_session):
    created = await create_student(db_session, StudentCreate(name="旧名", age=20))

    update_data = StudentUpdate(name="新名")
    updated = await update_student(db_session, created.id, update_data)

    assert updated is not None
    assert updated.name == "新名"
    assert updated.age == 20  # age 没传，保持不变


@pytest.mark.asyncio
async def test_update_student_partial(db_session):
    created = await create_student(db_session, StudentCreate(name="部分更新", age=25))

    update_data = StudentUpdate(age=30)
    updated = await update_student(db_session, created.id, update_data)

    assert updated is not None
    assert updated.name == "部分更新"
    assert updated.age == 30


@pytest.mark.asyncio
async def test_delete_student(db_session):
    created = await create_student(db_session, StudentCreate(name="待删", age=20))

    deleted = await delete_student(db_session, created.id)
    assert deleted is not None

    fetched = await get_student(db_session, created.id)
    assert fetched is None