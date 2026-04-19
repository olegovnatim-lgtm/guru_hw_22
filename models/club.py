from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class ClubRequest(BaseModel):
    bookTitle: str
    bookAuthors: str
    publicationYear: int
    description: str
    telegramChatLink: HttpUrl

    def build(self):
        data = self.model_dump()
        data["telegramChatLink"] = str(data["telegramChatLink"])
        return data


class ClubPatchRequest(BaseModel):
    bookTitle: Optional[str] = None
    bookAuthors: Optional[str] = None
    publicationYear: Optional[int] = None
    description: Optional[str] = None
    telegramChatLink: Optional[HttpUrl] = None

    def build(self):
        data = self.model_dump(exclude_none=True)
        if "telegramChatLink" in data:
            data["telegramChatLink"] = str(data["telegramChatLink"])
        return data


class UserShort(BaseModel):
    id: int
    username: str


class BookReview(BaseModel):
    id: int
    club: int
    user: UserShort
    review: str
    assessment: int
    readPages: int
    created: datetime
    modified: Optional[datetime]


class ClubResponse(BaseModel):
    id: int
    bookTitle: str
    bookAuthors: str
    publicationYear: int
    description: str
    telegramChatLink: str
    owner: int
    members: list[int]
    reviews: list[BookReview]
    created: datetime
    modified: Optional[datetime]


class ClubListResponse(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: list[ClubResponse]