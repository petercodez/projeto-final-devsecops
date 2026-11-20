from datetime import date, timedelta


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_task_success(client):
    response = client.post("/tasks", json={"title": "Estudar DevOps"})
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Estudar DevOps"
    assert body["completed"] is False


def test_create_task_with_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_with_past_due_date_returns_422(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    response = client.post("/tasks", json={"title": "Atrasada", "due_date": yesterday})
    assert response.status_code == 422


def test_get_unknown_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_list_tasks_filters_by_completed(client):
    client.post("/tasks", json={"title": "A"})
    client.post("/tasks", json={"title": "B"})
    client.patch("/tasks/1/complete")

    done = client.get("/tasks", params={"completed": True}).json()
    pending = client.get("/tasks", params={"completed": False}).json()

    assert [t["id"] for t in done] == [1]
    assert [t["id"] for t in pending] == [2]


def test_complete_task_marks_it_as_completed(client):
    client.post("/tasks", json={"title": "Concluir"})
    response = client.patch("/tasks/1/complete")
    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_update_task_changes_fields(client):
    client.post("/tasks", json={"title": "Antigo"})
    response = client.put("/tasks/1", json={"title": "Novo", "description": "detalhe"})
    assert response.status_code == 200
    assert response.json()["title"] == "Novo"
    assert response.json()["description"] == "detalhe"


def test_update_completed_task_returns_409(client):
    client.post("/tasks", json={"title": "Fechada"})
    client.patch("/tasks/1/complete")
    response = client.put("/tasks/1", json={"title": "Tentando editar"})
    assert response.status_code == 409


def test_delete_task_removes_it(client):
    client.post("/tasks", json={"title": "Apagar"})
    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks/1").status_code == 404