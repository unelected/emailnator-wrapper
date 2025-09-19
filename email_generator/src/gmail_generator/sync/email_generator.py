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
Synchronous interface for the Emailnator API wrapper.

This module defines the `EmailGenerator` class, which provides a blocking
(synchronous) wrapper around the asynchronous `AsyncEmailGenerator`.  
It allows generating temporary email addresses and retrieving their messages
without requiring an asynchronous runtime.

Typical Usage example:
    from gmail_generator.sync.email_generator import EmailGenerator
    gen = EmailGenerator()
    email = gen.generate_email()
    print(email)
    messages = gen.get_messages(email)
    print(messages)
    bulk = gen.generate_bulk_emails("200")
    print(bulk)
"""
import asyncio

from typing import Literal

from gmail_generator.asyncio.email_generator import AsyncEmailGenerator


class EmailGenerator:
    """
    Synchronous wrapper for generating temporary email addresses
    and retrieving their associated messages.

    This class provides a blocking interface to the asynchronous
    `AsyncEmailGenerator`, making it convenient to use in codebases
    that are not async-aware.

    Attributes:
        _loop (asyncio.AbstractEventLoop):
            Event loop used to execute asynchronous operations
            in a synchronous context.
        _async (AsyncEmailGenerator):
            Internal asynchronous generator instance responsible for
            performing the actual operations.
    """
    def __init__(self) -> None:
        """
        Initialize the synchronous email generator.

        This sets up an internal instance of `AsyncEmailGenerator`
        to handle the underlying asynchronous operations, which are
        then exposed through synchronous wrappers.
        """
        try:
            self._loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop: asyncio.AbstractEventLoop= asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        self._async: AsyncEmailGenerator = self._loop.run_until_complete(
            AsyncEmailGenerator()
        )


    def generate_email(self) -> str:
        """
        Generate a new email address synchronously.

        This method runs the asynchronous `generate_email` from
        `AsyncEmailGenerator` in a blocking manner using `asyncio.run`.

        Returns:
            str: A newly generated email address.

        Raises:
            RuntimeError: If the underlying async generator fails to return
            at least one email.
        """
        return self._loop.run_until_complete(
            self._async.generate_email()
        )

    def get_messages(self, email: str) -> list[str]:
        """
        Retrieve messages for a given email address synchronously.

        This method runs the asynchronous `get_messages` from
        `AsyncEmailGenerator` in a blocking manner using `asyncio.run`.

        Args:
            email (str): The email address to fetch messages for.

        Returns:
            list[str]: A list of message contents linked to the email.

        Raises:
            RuntimeError: If message retrieval fails or the response is invalid.
        """
        return self._loop.run_until_complete(
            self._async.get_messages(email)
        )

    def generate_bulk_emails(
            self,
            emails_number: Literal["100", "200", "300"] = "100"
    ) -> list[str]:
        """
        Generate multiple email addresses synchronously.

        This method runs the asynchronous `generate_bulk_emails` from
        `AsyncEmailGenerator` in a blocking manner using `asyncio.run`.

        Args:
            emails_number (Literal["100", "200", "300"], optional):  
                The number of email addresses to generate.  
                Must be one of: `"100"`, `"200"`, or `"300"`.  
                Defaults to `"100"`.

        Returns:
            list[str]: A list of newly generated email addresses.

        Raises:
            RuntimeError: If the underlying async generator fails to return
            a valid list of emails.
        """
        return self._loop.run_until_complete(
            self._async.generate_bulk_emails(emails_number)
        )
