from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from domain.services.password_service import passwordService


class Argon2PasswordService(passwordService):
    def __init__(self):
        self.ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self.ph.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        try:
            self.ph.verify(hashed_password, password)
            return True
        except VerifyMismatchError:
            return False
