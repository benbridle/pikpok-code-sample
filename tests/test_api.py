import requests

API_URL = "http://localhost:8004/api"


def assert_http_error(response, status_code, error_type):
    assert response.status_code == status_code
    assert response.json()["error"]["type"] == error_type


def test_missing_request_information():
    # Test that API returns errors when incomplete information has been sent
    ENDPOINT_URL = f"{API_URL}/accounts/"

    r = requests.post(ENDPOINT_URL)
    assert_http_error(r, 400, "MissingBodyError")

    r = requests.post(ENDPOINT_URL, json={"email_address": "test@mail.com"})
    assert_http_error(r, 400, "MissingFieldError")

    r = requests.get(ENDPOINT_URL)
    assert_http_error(r, 401, "NoAuthorizationSuppliedError")


def test_generate_random_profile_image():
    r = requests.get(f"{API_URL}/generators/profile_image")
    r.raise_for_status()
    assert "image" in r.json()
    image_string = r.json()["image"]
    assert len(image_string) == 172


def test_create_account():
    ENDPOINT_URL = f"{API_URL}/accounts/"

    r = requests.post(ENDPOINT_URL, json={"email_address": "test@mail.com", "password": "test"})
    assert r.status_code == 201
    assert r.json() is not None

    r = requests.post(ENDPOINT_URL, json={"email_address": "test@mail.com", "password": "test"})
    assert_http_error(r, 409, "ResourceAlreadyExistsError")


def get_authorization_header(email_address, password):
    # Get access token
    r = requests.post(f"{API_URL}/login", json={"email_address": email_address, "password": password})
    access_token = r.json()["token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def test_login():
    ENDPOINT_URL = f"{API_URL}/login"

    r = requests.post(ENDPOINT_URL, json={"email_address": "", "password": ""})
    assert_http_error(r, 403, "InvalidCredentialsError")

    r = requests.post(ENDPOINT_URL, json={"email_address": "test@mail.com", "password": ""})
    assert_http_error(r, 403, "InvalidCredentialsError")

    r = requests.post(ENDPOINT_URL, json={"email_address": "test@mail.com", "password": "test"})
    assert r.status_code == 200
    assert "account" in r.json()
    assert "token" in r.json()


def test_get_account():
    headers = get_authorization_header("test@mail.com", "test")
    r = requests.get(f"{API_URL}/accounts/2", headers=headers)
    assert_http_error(r, 403, "UnauthorizedAccessError")

    r = requests.get(f"{API_URL}/accounts/1", headers=headers)
    assert r.status_code == 200
    assert "id" in r.json()
    assert "profiles" in r.json()


def test_create_profile():
    headers = get_authorization_header("test@mail.com", "test")

    # Make profile for different account than the current one
    r = requests.post(f"{API_URL}/profiles/", json={"account_id": 2, "name": "Test Profile"}, headers=headers)
    assert_http_error(r, 403, "UnauthorizedAccessError")

    # Successfully create a profile
    r = requests.post(f"{API_URL}/profiles/", json={"account_id": 1, "name": "Test Profile"}, headers=headers)
    assert r.status_code == 201
    assert "id" in r.json()
    assert "name" in r.json()
    assert "picture" in r.json()
    assert len(r.json()["picture"]) == 172

    # Fail to make a profile with the same name as an existing profile
    r = requests.post(f"{API_URL}/profiles/", json={"account_id": 1, "name": "Test Profile"}, headers=headers)
    assert_http_error(r, 409, "ResourceAlreadyExistsError")


def test_get_profile():
    headers = get_authorization_header("test@mail.com", "test")

    # Try to fetch a non-existant profile
    r = requests.get(f"{API_URL}/profiles/2", headers=headers)
    assert_http_error(r, 403, "UnauthorizedAccessError")

    # Successfully fetch a profile belonging to the user
    r = requests.get(f"{API_URL}/profiles/1", headers=headers)
    assert r.status_code == 200
    assert "id" in r.json()
    assert "name" in r.json()
