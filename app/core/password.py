import re

from fastapi_users import InvalidPasswordException


class PasswordValidator:
    """Validates password against security requirements."""

    def __init__(self):
        self._pattern = re.compile(r"^[a-zA-Z0-9]{8,}$")
        self._uppercase_pattern = re.compile(r"[A-Z]")
        self._digit_pattern = re.compile(r"[0-9]")

    def validate(self, password: str) -> None:
        """Run all password checks."""
        self._check_pattern(password)
        self._check_uppercase(password)
        self._check_digit(password)

    def _check_pattern(self, password: str) -> None:
        """Raise if password contains invalid characters or is too short."""
        if not self._pattern.match(password):
            raise InvalidPasswordException(
                reason="Password must be at least 8 characters and contain only latin letters and digits"
            )

    def _check_uppercase(self, password: str) -> None:
        """Raise if password has no uppercase letter."""
        if not self._uppercase_pattern.search(password):
            raise InvalidPasswordException(
                reason="Password must contain at least one uppercase letter"
            )

    def _check_digit(self, password: str) -> None:
        """Raise if password has no digit."""
        if not self._digit_pattern.search(password):
            raise InvalidPasswordException(reason="Password must contain at least one digit")
