import os
import sys
import pytest

# Add project root to sys.path so `app` package can be found when running tests
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Ensure log folder exists before FastAPI app initializes its logger
os.makedirs(os.path.join(ROOT_DIR, "logs"), exist_ok=True)

# Avoid database creation in tests to not require PostgreSQL server.
os.environ["SKIP_DB_CREATE"] = "true"

from fastapi.testclient import TestClient
from app.main import app
from app.utils.security import generate_device_token
from app.utils.auth import hash_password, verify_password, create_access_token


def test_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "NodeTrace API is running"}


def test_generate_device_token_format():
    token = generate_device_token()
    assert token.startswith("NT-DEV-")
    assert len(token) == len("NT-DEV-") + 32


def test_password_hash_and_verify():
    password = "TestPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_create_access_token_returns_jwt():
    token = create_access_token({"sub": "testuser"}, expires_minutes=1)
    assert isinstance(token, str)
    assert token.count(".") == 2
