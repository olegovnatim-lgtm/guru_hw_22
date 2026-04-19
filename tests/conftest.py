import logging

import pytest

from config import BASE_URL
from api.base_api import BaseApi
from api.auth_api import AuthApi
from api.club_api import ClubApi
from models.auth import LoginRequest, TokenResponse
from utils.generators import random_register_request, random_club_request

logger = logging.getLogger(__name__)


def pytest_configure(config):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )


# ──────────────────── Базовые клиенты ────────────────────

@pytest.fixture(scope="session")
def api():
    return BaseApi(base_url=BASE_URL)


@pytest.fixture(scope="session")
def auth_client(api) -> AuthApi:
    """AuthApi без авторизации — для регистрации и логина."""
    return AuthApi(api)


# ──────────────────── Основной пользователь ────────────────────

@pytest.fixture(scope="session")
def test_user(auth_client):
    body = random_register_request()
    response = auth_client.register(body)
    assert response.status_code == 201  # <-- было 200
    return {"username": body.username, "password": body.password}


@pytest.fixture(scope="session")
def auth_token(auth_client, test_user):
    """JWT-токен основного пользователя."""
    body = LoginRequest(username=test_user["username"], password=test_user["password"])
    response = auth_client.login(body)
    assert response.status_code == 200
    token = TokenResponse.model_validate(response.json())
    return token


@pytest.fixture(scope="session")
def club_api(auth_token) -> ClubApi:
    """ClubApi с авторизацией основного пользователя."""
    api = BaseApi(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {auth_token.access}"}
    )
    return ClubApi(api)


# ──────────────────── Второй пользователь (для тестов доступа) ────────────────────

@pytest.fixture(scope="session")
def another_user(auth_client):
    body = random_register_request()
    response = auth_client.register(body)
    assert response.status_code == 201  # <-- было 200
    return {"username": body.username, "password": body.password}


@pytest.fixture(scope="session")
def another_club_api(auth_client, another_user):
    """ClubApi с авторизацией второго пользователя."""
    body = LoginRequest(username=another_user["username"], password=another_user["password"])
    response = auth_client.login(body)
    token = TokenResponse.model_validate(response.json())

    api = BaseApi(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {token.access}"}
    )
    return ClubApi(api)


# ──────────────────── Неавторизованный ClubApi ────────────────────

@pytest.fixture(scope="session")
def unauth_club_api(api):
    """ClubApi без авторизации — для негативных тестов."""
    return ClubApi(api)


# ──────────────────── Фикстуры данных ────────────────────

@pytest.fixture
def created_club(club_api):
    """Создаёт клуб перед тестом и удаляет после."""
    club = random_club_request()

    response = club_api.create(club)
    assert response.status_code == 201

    club_data = response.json()
    yield club_data

    delete_response = club_api.delete(club_data["id"])
    if delete_response.status_code != 204:
        logger.warning(f"Cleanup failed: club {club_data['id']}")


@pytest.fixture
def registered_user(auth_client):
    body = random_register_request()
    response = auth_client.register(body)
    assert response.status_code == 201  # <-- было 200
    return {"username": body.username, "password": body.password}