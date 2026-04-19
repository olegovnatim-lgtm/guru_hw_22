from models.auth import LoginRequest, TokenResponse
from utils.generators import random_register_request


def is_jwt(token: str) -> bool:
    """Проверяет что строка похожа на JWT (3 сегмента через точку)."""
    return isinstance(token, str) and len(token.split(".")) == 3


class TestAuthPositive:
    """TC-AUTH-01, TC-AUTH-02, TC-AUTH-09, TC-AUTH-10"""

    def test_login_status_and_schema(self, auth_client, registered_user):
        """TC-AUTH-01: Успешная авторизация — status + schema."""
        body = LoginRequest(
            username=registered_user["username"],
            password=registered_user["password"]
        )

        response = auth_client.login(body)

        assert response.status_code == 200
        TokenResponse.model_validate(response.json())

        # Нет лишних полей
        expected_fields = {"access", "refresh"}
        assert set(response.json().keys()) == expected_fields

    def test_login_content(self, auth_client, registered_user):
        """TC-AUTH-02: Успешная авторизация — content."""
        body = LoginRequest(
            username=registered_user["username"],
            password=registered_user["password"]
        )

        response = auth_client.login(body)

        assert response.status_code == 200
        data = response.json()
        assert is_jwt(data["access"])
        assert is_jwt(data["refresh"])

    def test_refresh_token_status_and_schema(self, auth_client, registered_user):
        """TC-AUTH-09: Refresh токена — status + schema."""
        body = LoginRequest(
            username=registered_user["username"],
            password=registered_user["password"]
        )
        login_response = auth_client.login(body)
        refresh_token = login_response.json()["refresh"]

        response = auth_client.refresh(refresh_token)

        assert response.status_code == 200
        assert "access" in response.json()

    def test_refresh_token_content(self, auth_client, registered_user):
        """TC-AUTH-10: Refresh токена — content."""
        body = LoginRequest(
            username=registered_user["username"],
            password=registered_user["password"]
        )
        login_response = auth_client.login(body)
        refresh_token = login_response.json()["refresh"]

        response = auth_client.refresh(refresh_token)

        assert response.status_code == 200
        assert is_jwt(response.json()["access"])


class TestAuthNegative:
    """TC-AUTH-03 — TC-AUTH-08, TC-AUTH-11, TC-AUTH-12"""

    def test_login_wrong_password(self, auth_client, registered_user):
        """TC-AUTH-03: Неверный пароль."""
        body = LoginRequest(
            username=registered_user["username"],
            password="WrongPassword!"
        )

        response = auth_client.login(body)

        assert response.status_code == 401
        data = response.json()
        assert "access" not in data
        assert "refresh" not in data

    def test_login_nonexistent_user(self, auth_client):
        """TC-AUTH-04: Несуществующий username."""
        body = LoginRequest(username="ghost_user_xyz_999", password="AnyPass123!")

        response = auth_client.login(body)

        assert response.status_code == 401

    def test_login_without_password(self, auth_client):
        """TC-AUTH-05: Отсутствует поле password."""
        response = auth_client.api.post(
            "/auth/token/",
            json={"username": "testuser"}
        )

        assert response.status_code == 400
        assert "password" in response.json()

    def test_login_without_username(self, auth_client):
        """TC-AUTH-06: Отсутствует поле username."""
        response = auth_client.api.post(
            "/auth/token/",
            json={"password": "SomePass123!"}
        )

        assert response.status_code == 400
        assert "username" in response.json()

    def test_login_empty_body(self, auth_client):
        """TC-AUTH-07: Пустое тело запроса."""
        response = auth_client.api.post("/auth/token/", json={})

        assert response.status_code == 400
        data = response.json()
        assert "username" in data
        assert "password" in data

    def test_login_empty_strings(self, auth_client):
        """TC-AUTH-08: Пустые строки в полях."""
        body = LoginRequest(username="", password="")

        response = auth_client.login(body)

        assert response.status_code == 400

    def test_refresh_invalid_token(self, auth_client):
        """TC-AUTH-11: Refresh с невалидным токеном."""
        response = auth_client.refresh("invalid.token.here")

        assert response.status_code == 401

    def test_logout_and_reuse_token(self, auth_client, registered_user):
        """TC-AUTH-12: Logout — refresh токен становится невалидным."""
        body = LoginRequest(
            username=registered_user["username"],
            password=registered_user["password"]
        )
        login_response = auth_client.login(body)
        refresh_token = login_response.json()["refresh"]

        # Logout
        logout_response = auth_client.logout(refresh_token)
        assert logout_response.status_code == 200

        # Повторный refresh с тем же токеном — должен быть 401
        refresh_response = auth_client.refresh(refresh_token)
        assert refresh_response.status_code == 401