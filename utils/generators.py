import random

from faker import Faker
from pydantic import HttpUrl

from models.club import ClubRequest
from models.auth import RegisterRequest

fake = Faker()


def random_username():
    return f"autotest_{fake.user_name()}_{random.randint(100, 999)}"


def random_password():
    return fake.password(length=12, special_chars=True)


def random_club_request():
    return ClubRequest(
        bookTitle=fake.catch_phrase(),
        bookAuthors=fake.name(),
        publicationYear=fake.random_int(min=1900, max=2025),
        description=fake.text(max_nb_chars=200),
        telegramChatLink=HttpUrl("https://t.me/qa_guru")
    )


def random_register_request():
    return RegisterRequest(
        username=random_username(),
        password=random_password()
    )
