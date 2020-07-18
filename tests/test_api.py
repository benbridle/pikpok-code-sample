import requests
import pytest

API_URL = "http://localhost:8004/api"


def assert_error(response, status_code, error_type):
    assert response.status_code == status_code
    assert response.json()["error"]["type"] == error_type


def test_generate_random_profile_image():
    r = requests.get(f"{API_URL}/generators/profile_image")
    r.raise_for_status()
    assert "image" in r.json()
    image_string = r.json()["image"]
    assert len(image_string) == 172


def test_create_account():
    ENDPOINT_URL = f"{API_URL}/accounts/"

    r = requests.post(ENDPOINT_URL)
    assert_error(r, 400, "MissingBodyError")

    r = requests.post(ENDPOINT_URL, json={"email_address": "test@mail.com"})
    assert_error(r, 400, "MissingFieldError")

    r = requests.post(ENDPOINT_URL, json={"email_address": "test@mail.com", "password": "test"})
    assert r.status_code == 201
    assert r.json() is not None

    r = requests.post(ENDPOINT_URL, json={"email_address": "test@mail.com", "password": "test"})
    assert_error(r, 409, "ResourceAlreadyExistsError")
