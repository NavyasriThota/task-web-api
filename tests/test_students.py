import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


def build_student(email: str = "navya@example.com"):
    return {
        "first_name": "Navya",
        "last_name": "Sharma",
        "email": email,
        "phone_number": "9876543210",
        "gender": "Female",
        "date_of_birth": "2000-05-15",
        "course": "B.Tech",
        "batch": "2024",
        "address": "Hyderabad",
    }


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_add_new_student(client):
    response = client.post("/api/students", json=build_student("navya1@example.com"))
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "navya1@example.com"
    assert data["student_id"] > 0


def test_add_student_with_existing_email(client):
    payload = build_student("duplicate@example.com")
    client.post("/api/students", json=payload)
    response = client.post("/api/students", json=payload)
    assert response.status_code == 409


def test_retrieve_all_students(client):
    client.post("/api/students", json=build_student("all1@example.com"))
    client.post("/api/students", json=build_student("all2@example.com"))

    response = client.get("/api/students")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["students"]) >= 2


def test_search_using_three_letters(client):
    client.post("/api/students", json=build_student("search1@example.com"))
    response = client.get("/api/students/search?name=nav")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_search_using_partial_name(client):
    payload = build_student("partial@example.com")
    payload["first_name"] = "Rahul"
    payload["last_name"] = "Kumar"
    client.post("/api/students", json=payload)
    response = client.get("/api/students/search?name=rah")
    assert response.status_code == 200
    data = response.json()
    assert any(student["first_name"] == "Rahul" for student in data)


def test_search_without_matching_records(client):
    response = client.get("/api/students/search?name=xyz")
    assert response.status_code == 200
    assert response.json() == []


def test_get_student_by_id(client):
    created = client.post("/api/students", json=build_student("idcheck@example.com")).json()
    response = client.get(f"/api/students/{created['student_id']}")
    assert response.status_code == 200
    assert response.json()["email"] == "idcheck@example.com"


def test_update_student_details(client):
    created = client.post("/api/students", json=build_student("update1@example.com")).json()
    response = client.put(
        f"/api/students/{created['student_id']}",
        json={
            "first_name": "Updated",
            "last_name": "Student",
            "email": "updatedstudent@example.com",
            "phone_number": "1234567890",
            "course": "MCA",
            "batch": "2025",
            "gender": "Male",
        },
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"


def test_update_student_with_duplicate_email(client):
    first = client.post("/api/students", json=build_student("duplicate_update1@example.com")).json()
    second = client.post("/api/students", json=build_student("duplicate_update2@example.com")).json()

    response = client.put(
        f"/api/students/{first['student_id']}",
        json={"email": second["email"]},
    )
    assert response.status_code == 409


def test_delete_student(client):
    created = client.post("/api/students", json=build_student("delete1@example.com")).json()
    response = client.delete(f"/api/students/{created['student_id']}")
    assert response.status_code == 200
    assert "successfully" in response.json()["message"].lower()


def test_delete_non_existing_student(client):
    response = client.delete("/api/students/99999")
    assert response.status_code == 404


def test_invalid_input_validation(client):
    payload = build_student("invalid@example.com")
    payload["first_name"] = ""
    response = client.post("/api/students", json=payload)
    assert response.status_code == 422
