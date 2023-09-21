import random
import string

from faker import Faker

fake = Faker()


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def random_test_public_id() -> str:
    return fake.bothify(text="TC???###")
