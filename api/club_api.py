from api.base_api import BaseApi
from models.club import ClubRequest, ClubPatchRequest


class ClubApi:
    def __init__(self, api: BaseApi):
        self.api = api

    def create(self, club: ClubRequest):
        return self.api.post("/clubs/", json=club.build())

    def get_by_id(self, club_id: int):
        return self.api.get(f"/clubs/{club_id}/")

    def get_list(self, page=None, page_size=None):
        params = {}
        if page:
            params["page"] = page
        if page_size:
            params["page_size"] = page_size
        return self.api.get("/clubs/", params=params)

    def update(self, club_id: int, club: ClubRequest):
        return self.api.put(f"/clubs/{club_id}/", json=club.build())

    def patch(self, club_id: int, club: ClubPatchRequest):
        return self.api.patch(f"/clubs/{club_id}/", json=club.build())

    def delete(self, club_id: int):
        return self.api.delete(f"/clubs/{club_id}/")