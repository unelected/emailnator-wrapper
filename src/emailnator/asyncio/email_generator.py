# Copyright (C) 2025 unelected
#
# This file is part of email_generator.
#
# account_generator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# account_generator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with account_generator. If not, see
# <https://www.gnu.org/licenses/>.

"""
Asynchronous email generator module.

This module provides the `AsyncEmailGenerator` class, an asynchronous
wrapper around the Emailnator API for working with temporary email
addresses. It offers methods to:

    - Generate a single temporary email address.
    - Generate multiple temporary email addresses (limited to `"100"`, `"200"`, or `"300"`).
    - Retrieve messages associated with a given email address.

Typical usage example:
    from emailnator.asyncio.email_generator import AsyncEmailGenerator

    async def main():
        generator = AsyncEmailGenerator()
        email = await generator.generate_email()
        messages = await generator.get_messages(email)
        print(email, messages)
"""
from typing import Literal

from emailnator.asyncio.generators import Generators
from emailnator.asyncio.helpers.metaclass import AsyncInitMeta
from emailnator.asyncio.message_getter import MessageGetter


class AsyncEmailGenerator(metaclass=AsyncInitMeta):
    """
    Asynchronous wrapper for generating temporary email addresses
    and retrieving their associated messages.

    This class provides a high-level interface to the Emailnator API
    through asynchronous methods.

    Attributes:
        generators (Generators): 
        - The underlying generator instance used to create email addresses.
        message_getter (MessageGetter): 
        - The instance responsible for retrieving messages linked to emails.
    """
    async def __ainit__(self) -> None:
        """
        Initialize the asynchronous email generator.

        Sets up the required components for generating temporary email
        addresses and retrieving their associated messages.
        """
        self._generators: Generators = await Generators()
        self._message_getter: MessageGetter = await MessageGetter()

    async def generate_email(self) -> str:
        """
        Generate a new email address asynchronously.

        This method requests a new email address from the underlying
        `Generators` instance and returns the first generated address.

        Returns:
            str: A newly generated email address.

        Raises:
            RuntimeError: If the generator fails to return at least one email.
        """
        return (await self._generators.generate_email())[0]

    async def get_messages(self, email: str) -> list[str]:
        """
        Retrieve messages for a given email address asynchronously.

        This method queries the `MessageGetter` instance to fetch all
        messages associated with the provided email.

        Args:
            email (str): The email address to fetch messages for.

        Returns:
            list[str]: A list of message contents linked to the email.

        Raises:
            RuntimeError: If message retrieval fails or the response is invalid.
        """
        return await self._message_getter.get_message_list(email)

    async def generate_bulk_emails(
            self,
            emails_number: Literal["100", "200", "300"] = "100"
    ) -> list[str]:
        """
        Generate multiple email addresses asynchronously.

        This method requests a batch of email addresses from the underlying
        `Generators` instance. The number of generated emails is restricted
        to specific supported values.

        Args:
            emails_number (Literal["100", "200", "300"], optional):  
                The number of email addresses to generate.  
                Must be one of: `"100"`, `"200"`, or `"300"`.  
                Defaults to `"100"`.

        Returns:
            list[str]: A list of newly generated email addresses.

        Raises:
            RuntimeError: If the generator fails to return a valid list of emails.
        """
        return await self._generators.generate_bulk_emails(emails_number)
