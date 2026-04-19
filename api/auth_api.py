from api.base_api import BaseApi
from models.auth import LoginRequest, RegisterRequest


class AuthApi:
    def __init__(self, api: BaseApi):
        self.api = api

    def login(self, body: LoginRequest):
        return self.api.post("/auth/token/", json=body.model_dump())

    def refresh(self, refresh_token: str):
        return self.api.post("/auth/token/refresh/", json={"refresh": refresh_token})

    def logout(self, refresh_token: str):
        return self.api.post("/auth/logout/", json={"refresh": refresh_token})

    def register(self, body: RegisterRequest):
        return self.api.post("/users/register/", json=body.model_dump())