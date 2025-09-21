from typing import Literal

from emailnator.asyncio.email_generator import AsyncEmailGenerator

class EmailGenerator:
    _async: AsyncEmailGenerator
    _loop: object

    def __init__(self) -> None: ...
    @property
    def async_client(self) -> AsyncEmailGenerator: ...
    def generate_email(self) -> str: ...
    def get_messages(self, email: str) -> list[str]: ...
    def generate_bulk_emails(
        self, 
        emails_number: Literal["100", "200", "300"] = "100"
    ) -> list[str]: ...
