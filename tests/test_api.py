from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["message"] == (
        "Doctor Patient Backend API is running"
    )


def test_get_doctors_requires_authentication():
    response = client.get("/api/v1/doctors")

    assert response.status_code == 401


def test_get_patients_requires_authentication():
    response = client.get("/api/v1/patients/")

    assert response.status_code == 401