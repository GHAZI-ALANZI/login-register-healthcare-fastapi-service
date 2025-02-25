import pytest
import random
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, engine, get_db
from models import User, RoleEnum
from auth import hash_password

# Create a new test database session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Fixture to create a fresh test database session."""
    Base.metadata.drop_all(bind=engine)  # ❌ Drop all tables before each test
    Base.metadata.create_all(bind=engine)  # ✅ Recreate tables
    db = TestSessionLocal()

    try:
        #  Create a default admin user for testing
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=hash_password("Admin@123"),
            department="IT",
            role=RoleEnum.Admin
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        yield db  #  Provide the test database session
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    """Fixture to create a test client for API requests."""
    return TestClient(app)

#  Test Successful Login
def test_login_success(client):
    response = client.post("/login", data={"username": "admin", "password": "Admin@123"})
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"

#  Test Login Failure (Wrong Password)
def test_login_invalid_password(client):
    response = client.post("/login", data={"username": "admin", "password": "WrongPass@123"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid username or password"

#  Test Registering a New User (Admin Only)
def test_register_user(client):
    """Test registering a new user with unique username and email"""
    # Admin login to get token
    login_response = client.post("/login", data={"username": "admin", "password": "Admin@123"})
    token = login_response.json()["access_token"]

    # Generate unique user details
    unique_id = random.randint(1000, 9999)
    username = f"doctor{unique_id}"
    email = f"doctor{unique_id}@example.com"

    # Register a new user
    response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": "Doctor@123",
            "confirm_password": "Doctor@123",
            "department": "Cardiology",
            "role": "Doctor"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == username

#  Test Getting All Users (Admin Only)
def test_get_users(client):
    """Test retrieving all users (Admin Only)"""
    login_response = client.post("/login", data={"username": "admin", "password": "Admin@123"})
    token = login_response.json()["access_token"]

    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    json_response = response.json()
    assert isinstance(json_response, list)
    assert len(json_response) > 0  # ✅ Should have at least one user (Admin)

#  Test Non-Admin User Cannot Register Another User
def test_register_user_not_admin(client):
    """Test that a non-admin user cannot register another user"""
    # Register a doctor first
    unique_id = random.randint(1000, 9999)
    username = f"doctor{unique_id}"
    email = f"doctor{unique_id}@example.com"

    admin_token = client.post("/login", data={"username": "admin", "password": "Admin@123"}).json()["access_token"]

    client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": "Doctor@123",
            "confirm_password": "Doctor@123",
            "department": "Surgery",
            "role": "Doctor"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Login as the doctor
    login_response = client.post("/login", data={"username": username, "password": "Doctor@123"})
    token = login_response.json()["access_token"]

    # Try registering another user
    response = client.post(
        "/register",
        json={
            "username": f"employee{unique_id}",
            "email": f"employee{unique_id}@example.com",
            "password": "Employee@123",
            "confirm_password": "Employee@123",
            "department": "IT",
            "role": "Employee"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only admins can create users"

#  Test Deleting a User (Admin Only)
def test_delete_user(client):
    """Test that an admin can delete a user"""
    admin_token = client.post("/login", data={"username": "admin", "password": "Admin@123"}).json()["access_token"]

    # Register a new user
    unique_id = random.randint(1000, 9999)
    register_response = client.post(
        "/register",
        json={
            "username": f"employee{unique_id}",
            "email": f"employee{unique_id}@example.com",
            "password": "Employee@123",
            "confirm_password": "Employee@123",
            "department": "HR",
            "role": "Employee"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    user_id = register_response.json()["id"]

    # Delete the registered user
    response = client.delete(f"/user/delete/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

#  Test Non-Admin Cannot Delete Users
def test_delete_user_not_admin(client):
    """Test that a non-admin cannot delete users"""
    admin_token = client.post("/login", data={"username": "admin", "password": "Admin@123"}).json()["access_token"]

    # Register a doctor
    unique_id = random.randint(1000, 9999)
    doctor_username = f"doctor{unique_id}"
    doctor_email = f"doctor{unique_id}@example.com"

    client.post(
        "/register",
        json={
            "username": doctor_username,
            "email": doctor_email,
            "password": "Doctor@123",
            "confirm_password": "Doctor@123",
            "department": "Surgery",
            "role": "Doctor"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Login as the doctor
    doctor_token = client.post("/login", data={"username": doctor_username, "password": "Doctor@123"}).json()["access_token"]

    # Try deleting another user
    response = client.delete(f"/user/delete/3", headers={"Authorization": f"Bearer {doctor_token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Only admins can delete users"
