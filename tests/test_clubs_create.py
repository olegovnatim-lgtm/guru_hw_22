from pydantic import HttpUrl

from models.club import ClubRequest, ClubResponse
from utils.generators import random_club_request

CLUB_RESPONSE_FIELDS = {
    "id", "bookTitle", "bookAuthors", "publicationYear",
    "description", "telegramChatLink", "owner", "members",
    "reviews", "created", "modified"
}


class TestClubCreatePositive:
    """TC-CLUB-C01, TC-CLUB-C02"""

    def test_create_status_and_schema(self, club_api):
        """TC-CLUB-C01: Успешное создание — status + schema."""
        club = random_club_request()

        response = club_api.create(club)

        assert response.status_code == 201
        ClubResponse.model_validate(response.json())

        # Нет лишних полей
        assert set(response.json().keys()) == CLUB_RESPONSE_FIELDS

        # Cleanup
        club_api.delete(response.json()["id"])

    def test_create_content(self, club_api):
        """TC-CLUB-C02: Успешное создание — content."""
        club = random_club_request()

        response = club_api.create(club)

        assert response.status_code == 201
        result = ClubResponse.model_validate(response.json())

        assert result.bookTitle == club.bookTitle
        assert result.bookAuthors == club.bookAuthors
        assert result.publicationYear == club.publicationYear
        assert result.description == club.description
        assert result.reviews == []

        # Cleanup
        club_api.delete(result.id)


class TestClubCreateNegative:
    """TC-CLUB-C03 — TC-CLUB-C07"""

    def test_create_unauthorized(self, unauth_club_api):
        """TC-CLUB-C03: Создание без авторизации."""
        club = random_club_request()

        response = unauth_club_api.create(club)

        assert response.status_code == 401

    def test_create_without_book_title(self, club_api):
        """TC-CLUB-C04: Создание без обязательного поля bookTitle."""
        response = club_api.api.post("/clubs/", json={
            "bookAuthors": "Author",
            "publicationYear": 2024,
            "description": "Test",
            "telegramChatLink": "https://t.me/test"
        })

        assert response.status_code == 400
        assert "bookTitle" in response.json()

    def test_create_invalid_telegram_link(self, club_api):
        """TC-CLUB-C05: Невалидный telegramChatLink."""
        response = club_api.api.post("/clubs/", json={
            "bookTitle": "Test Book",
            "bookAuthors": "Author",
            "publicationYear": 2024,
            "description": "Test",
            "telegramChatLink": "not-a-url"
        })

        assert response.status_code == 400
        assert "telegramChatLink" in response.json()

    def test_create_book_title_too_long(self, club_api):
        """TC-CLUB-C06: bookTitle длиной 256 символов."""
        response = club_api.api.post("/clubs/", json={
            "bookTitle": "a" * 256,
            "bookAuthors": "Author",
            "publicationYear": 2024,
            "description": "Test",
            "telegramChatLink": "https://t.me/test"
        })

        assert response.status_code == 400
        assert "bookTitle" in response.json()

    def test_create_empty_body(self, club_api):
        """TC-CLUB-C07: Пустое тело запроса."""
        response = club_api.api.post("/clubs/", json={})

        assert response.status_code == 400