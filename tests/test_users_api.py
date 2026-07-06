

# 先测试post部分，如果报错，利于阅读和清理
async def test_post_students(client):
    response = await client.post(
        "/students/",
        json={"name":"isOne", "age":19}
    )
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "isOne"
    assert data["age"] == 19
    assert "id" in data


async def test_get_student(client):
    post_stu = await  client.post(
        "/students/",
        json={"name": "红烧鱼", "age": 29}
    )
    student_id = post_stu.json()["id"]

    response = await client.get(f"/students/{student_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "红烧鱼"
    assert data["age"] == 29


async def test_get_student_not_found(client):
    response = await client.get("/students/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


async def test_get_students_empty(client):
    response = await client.get("/students/")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_students_with_data(client):
    await client.post("/students/", json={"name": "测试", "age": 20})
    response = await client.get("/students/")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_update_student(client):
    post_stu = await client.post(
        "/students/",
        json={"name": "更新前", "age": 22}
    )
    student_id = post_stu.json()["id"]

    response = await client.patch(
        f"/students/{student_id}",
        json={"name": "更新后"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "更新后"
    assert data["age"] == 22


async def test_update_student_not_found(client):
    response = await client.patch(
        "/students/999",
        json={"name": "不存在"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"


async def test_delete_student(client):
    post_stu = await client.post(
        "/students/",
        json={"name": "待删除", "age": 18}
    )
    student_id = post_stu.json()["id"]

    response = await client.delete(f"/students/{student_id}")
    assert response.status_code == 200

    response = await client.get(f"/students/{student_id}")
    assert response.status_code == 404


async def test_delete_student_not_found(client):
    response = await client.delete(
        "/students/999"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"



