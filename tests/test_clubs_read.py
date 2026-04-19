from models.club import ClubResponse, ClubListResponse

CLUB_RESPONSE_FIELDS = {
    "id", "bookTitle", "bookAuthors", "publicationYear",
    "description", "telegramChatLink", "owner", "members",
    "reviews", "created", "modified"
}

CLUB_LIST_FIELDS = {"count", "next", "previous", "results"}


class TestClubReadPositive:
    """TC-CLUB-R01 — TC-CLUB-R04, TC-CLUB-R06"""

    def test_list_status_and_schema(self, club_api, created_club):
        """TC-CLUB-R01: Список клубов — status + schema."""
        response = club_api.get_list()

        assert response.status_code == 200
        ClubListResponse.model_validate(response.json())
        assert set(response.json().keys()) == CLUB_LIST_FIELDS

    def test_list_content(self, club_api, created_club):
        """TC-CLUB-R02: Список клубов — content."""
        response = club_api.get_list()

        assert response.status_code == 200
        data = ClubListResponse.model_validate(response.json())
        assert data.count >= 1
        assert len(data.results) >= 1

    def test_get_by_id_status_and_schema(self, club_api, created_club):
        """TC-CLUB-R03: Клуб по ID — status + schema."""
        response = club_api.get_by_id(created_club["id"])

        assert response.status_code == 200
        ClubResponse.model_validate(response.json())
        assert set(response.json().keys()) == CLUB_RESPONSE_FIELDS

    def test_get_by_id_content(self, club_api, created_club):
        """TC-CLUB-R04: Клуб по ID — content."""
        response = club_api.get_by_id(created_club["id"])

        assert response.status_code == 200
        result = ClubResponse.model_validate(response.json())
        assert result.id == created_club["id"]
        assert result.bookTitle == created_club["bookTitle"]
        assert result.bookAuthors == created_club["bookAuthors"]
        assert result.description == created_club["description"]

    def test_pagination(self, club_api, created_club):
        """TC-CLUB-R06: Пагинация."""
        response = club_api.get_list(page=1, page_size=1)

        assert response.status_code == 200
        data = ClubListResponse.model_validate(response.json())
        assert len(data.results) == 1


class TestClubReadNegative:
    """TC-CLUB-R05"""

    def test_get_nonexistent_club(self, club_api):
        """TC-CLUB-R05: Клуб по несуществующему ID."""
        response = club_api.get_by_id(999999)

        assert response.status_code == 404