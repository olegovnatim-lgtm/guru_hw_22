from models.auth import RegisterRequest, RegisterResponse
from utils.generators import random_register_request, random_username, random_password


class TestRegistrationPositive:
    """TC-REG-01, TC-REG-02, TC-REG-09, TC-REG-10"""

    def test_register_status_and_schema(self, auth_client):
        """TC-REG-01: Успешная регистрация — status + schema."""
        body = random_register_request()

        response = auth_client.register(body)

        assert response.status_code == 201
        RegisterResponse.model_validate(response.json())

        expected_fields = {"id", "username", "firstName", "lastName", "email", "remoteAddr"}
        assert set(response.json().keys()) == expected_fields

    def test_register_content(self, auth_client):
        """TC-REG-02: Успешная регистрация — content."""
        body = random_register_request()

        response = auth_client.register(body)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == body.username

    def test_register_max_length_username_status_and_schema(self, auth_client):
        """TC-REG-09: Username длиной 150 символов — status + schema."""
        suffix = random_username()[:142]
        username = suffix + "a" * (150 - len(suffix))
        body = RegisterRequest(username=username, password=random_password())

        response = auth_client.register(body)

        assert response.status_code == 201
        RegisterResponse.model_validate(response.json())

    def test_register_max_length_username_content(self, auth_client):
        """TC-REG-10: Username длиной 150 символов — content."""
        suffix = random_username()[:142]
        username = suffix + "b" * (150 - len(suffix))
        body = RegisterRequest(username=username, password=random_password())

        response = auth_client.register(body)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == username
        assert len(data["username"]) == 150


class TestRegistrationNegative:
    """TC-REG-03 — TC-REG-08"""

    def test_register_duplicate_username(self, auth_client, registered_user):
        """TC-REG-03: Регистрация с уже занятым username."""
        body = RegisterRequest(
            username=registered_user["username"],
            password=random_password()
        )

        response = auth_client.register(body)

        assert response.status_code == 400
        data = response.json()
        assert "username" in data
        assert data["username"] == ["A user with that username already exists."]

    def test_register_without_password(self, auth_client):
        """TC-REG-04: Регистрация без поля password."""
        response = auth_client.api.post(
            "/users/register/",
            json={"username": random_username()}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["password"] == ["This field is required."]

    def test_register_without_username(self, auth_client):
        """TC-REG-05: Регистрация без поля username."""
        response = auth_client.api.post(
            "/users/register/",
            json={"password": random_password()}
        )

        assert response.status_code == 400
        data = response.json()
        assert data["username"] == ["This field is required."]

    def test_register_empty_body(self, auth_client):
        """TC-REG-06: Регистрация с пустым телом."""
        response = auth_client.api.post("/users/register/", json={})

        assert response.status_code == 400
        data = response.json()
        assert data["username"] == ["This field is required."]
        assert data["password"] == ["This field is required."]

    def test_register_invalid_username_chars(self, auth_client):
        """TC-REG-07: Username с недопустимыми символами."""
        body = RegisterRequest(username="user name!#$", password=random_password())

        response = auth_client.register(body)

        assert response.status_code == 400
        data = response.json()
        assert "username" in data
        assert "Enter a valid username" in data["username"][0]

    def test_register_username_too_long(self, auth_client):
        """TC-REG-08: Username длиной 151 символ."""
        body = RegisterRequest(username="a" * 151, password=random_password())

        response = auth_client.register(body)

        assert response.status_code == 400
        data = response.json()
        assert "username" in data
        assert "no more than 150 characters" in data["username"][0]