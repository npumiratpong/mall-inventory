from fastapi.testclient import TestClient
from fastapi import status
import urllib

from models.schemas import Token

from main import app

client = TestClient(app)


def test_login():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {"username":"johndoe", "password":"secret2" }
    response = client.post("/api/v1/login", data=data, headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    data = {"username":"johndoe", "password":"secret" }
    response = client.post("/api/v1/login", data=data, headers=headers)
    assert response.status_code == status.HTTP_200_OK

