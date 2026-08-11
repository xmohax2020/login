from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_designs_endpoint():
    response = client.get('/designs')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
