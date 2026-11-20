import pytest
from fastapi.testclient import TestClient

from app.main import app, get_service
from app.service import TaskService


@pytest.fixture
def client():
    service = TaskService()  # uma instância limpa por teste
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()