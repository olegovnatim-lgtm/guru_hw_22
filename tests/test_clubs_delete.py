from utils.generators import random_club_request


class TestClubDeletePositive:
    """TC-CLUB-D01, TC-CLUB-D02"""

    def test_delete_status(self, club_api):
        """TC-CLUB-D01: Удаление владельцем — status + schema."""
        club = random_club_request()
        create_response = club_api.create(club)
        club_id = create_response.json()["id"]

        response = club_api.delete(club_id)

        assert response.status_code == 204
        assert response.text == ""

    def test_delete_content_post_check(self, club_api):
        """TC-CLUB-D02: Удаление владельцем — постпроверка."""
        club = random_club_request()
        create_response = club_api.create(club)
        club_id = create_response.json()["id"]

        club_api.delete(club_id)

        # Клуб больше не существует
        get_response = club_api.get_by_id(club_id)
        assert get_response.status_code == 404


class TestClubDeleteNegative:
    """TC-CLUB-D03 — TC-CLUB-D06"""

    def test_delete_other_users_club(self, club_api, another_club_api):
        """TC-CLUB-D03: Удаление чужого клуба."""
        # Создаём клуб основным пользователем
        club = random_club_request()
        create_response = club_api.create(club)
        club_id = create_response.json()["id"]

        # Пытаемся удалить вторым пользователем
        response = another_club_api.delete(club_id)
        assert response.status_code == 403

        # Клуб на месте
        get_response = club_api.get_by_id(club_id)
        assert get_response.status_code == 200

        # Cleanup
        club_api.delete(club_id)

    def test_delete_unauthorized(self, club_api, unauth_club_api):
        """TC-CLUB-D04: Удаление без авторизации."""
        club = random_club_request()
        create_response = club_api.create(club)
        club_id = create_response.json()["id"]

        response = unauth_club_api.delete(club_id)
        assert response.status_code == 401

        # Cleanup
        club_api.delete(club_id)

    def test_delete_nonexistent_club(self, club_api):
        """TC-CLUB-D05: Удаление несуществующего клуба."""
        response = club_api.delete(999999)

        assert response.status_code == 404

    def test_delete_already_deleted(self, club_api):
        """TC-CLUB-D06: Повторное удаление уже удалённого клуба."""
        club = random_club_request()
        create_response = club_api.create(club)
        club_id = create_response.json()["id"]

        # Первое удаление
        club_api.delete(club_id)

        # Повторное удаление
        response = club_api.delete(club_id)
        assert response.status_code == 404