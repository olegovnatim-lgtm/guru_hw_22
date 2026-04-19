from pydantic import HttpUrl

from models.club import ClubRequest, ClubPatchRequest, ClubResponse
from utils.generators import random_club_request

CLUB_RESPONSE_FIELDS = {
    "id", "bookTitle", "bookAuthors", "publicationYear",
    "description", "telegramChatLink", "owner", "members",
    "reviews", "created", "modified"
}


class TestClubUpdatePositive:
    """TC-CLUB-U01 — TC-CLUB-U04"""

    def test_put_status_and_schema(self, club_api, created_club):
        """TC-CLUB-U01: PUT обновление — status + schema."""
        club = ClubRequest(
            bookTitle="Анна Каренина",
            bookAuthors="Лев Толстой",
            publicationYear=1878,
            description="Обновлённое описание",
            telegramChatLink=HttpUrl("https://t.me/anna_k")
        )

        response = club_api.update(created_club["id"], club)

        assert response.status_code == 200
        ClubResponse.model_validate(response.json())
        assert set(response.json().keys()) == CLUB_RESPONSE_FIELDS

    def test_put_content(self, club_api, created_club):
        """TC-CLUB-U02: PUT обновление — content."""
        club = ClubRequest(
            bookTitle="Анна Каренина",
            bookAuthors="Лев Толстой",
            publicationYear=1878,
            description="Обновлённое описание",
            telegramChatLink=HttpUrl("https://t.me/anna_k")
        )

        response = club_api.update(created_club["id"], club)

        assert response.status_code == 200
        result = ClubResponse.model_validate(response.json())
        assert result.bookTitle == "Анна Каренина"
        assert result.publicationYear == 1878
        assert result.description == "Обновлённое описание"
        assert result.modified is not None

    def test_patch_status_and_schema(self, club_api, created_club):
        """TC-CLUB-U03: PATCH обновление — status + schema."""
        patch = ClubPatchRequest(description="Только описание изменено")

        response = club_api.patch(created_club["id"], patch)

        assert response.status_code == 200
        ClubResponse.model_validate(response.json())

    def test_patch_content(self, club_api, created_club):
        """TC-CLUB-U04: PATCH обновление — content."""
        original_title = created_club["bookTitle"]
        original_authors = created_club["bookAuthors"]
        original_year = created_club["publicationYear"]

        patch = ClubPatchRequest(description="Только описание изменено")

        response = club_api.patch(created_club["id"], patch)

        assert response.status_code == 200
        result = ClubResponse.model_validate(response.json())
        assert result.description == "Только описание изменено"

        # Остальные поля не изменились
        assert result.bookTitle == original_title
        assert result.bookAuthors == original_authors
        assert result.publicationYear == original_year


class TestClubUpdateNegative:
    """TC-CLUB-U05 — TC-CLUB-U07"""

    def test_update_other_users_club(self, another_club_api, created_club):
        """TC-CLUB-U05: Обновление чужого клуба."""
        club = random_club_request()

        response = another_club_api.update(created_club["id"], club)

        assert response.status_code == 403

    def test_update_unauthorized(self, unauth_club_api, created_club):
        """TC-CLUB-U06: Обновление без авторизации."""
        club = random_club_request()

        response = unauth_club_api.update(created_club["id"], club)

        assert response.status_code == 401

    def test_put_empty_book_title(self, club_api, created_club):
        """TC-CLUB-U07: PUT с пустым bookTitle."""
        response = club_api.api.put(f"/clubs/{created_club['id']}/", json={
            "bookTitle": "",
            "bookAuthors": "Author",
            "publicationYear": 2024,
            "description": "Test",
            "telegramChatLink": "https://t.me/test"
        })

        assert response.status_code == 400
        assert "bookTitle" in response.json()