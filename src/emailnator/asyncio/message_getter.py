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
Module for interacting with the EmailNator API to retrieve email messages.

This module provides the `MessageGetter` class, which is a wrapper around the
EmailNator API for fetching email messages. It uses an HTTP client from `httpx`
and helper utilities from `Helpers` to parse API responses.
"""
import httpx

from emailnator.config.config import config
from emailnator.asyncio.helpers.parser import Parser
from emailnator.asyncio.builders.builders import AsyncEmailnatorClient
from emailnator.asyncio.helpers.metaclass import AsyncInitMeta


class MessageGetter(metaclass=AsyncInitMeta):
    """
    Asynchronous client wrapper for retrieving messages from the EmailNator API.

    This class provides functionality to fetch the list of messages associated
    with a given email address and parse the results using the `Parser` utility.

    Attributes:
        parser (Parser): Parser instance used to process API responses.
        client (httpx.AsyncClient): Asynchronous HTTP client for making requests
            to the EmailNator API.
        headers (dict[str, str]): Default HTTP headers applied to all requests.
    """
    async def __ainit__(self) -> None:
        """
        Asynchronous initializer for the MessageGetter.

        This method initializes the HTTP client, request headers, and parser
        required for interacting with the EmailNator API.
        """
        emailnator_client: AsyncEmailnatorClient = (
            await AsyncEmailnatorClient()
        )
        self.parser: Parser = Parser()
        self.client: httpx.AsyncClient = await emailnator_client.get_client()
        self.headers: dict = await emailnator_client.get_headers()

    async def get_message_list(
        self,
        email: str,
        base_url: str = config.BASE_URL,
    ) -> list[str]:
        """
        Sends a POST request to retrieve a list of messages associated with the specified email.

        Args:
            email (str): The email address for which to fetch the message list.
            base_url (str, optional): The base URL of the API. Defaults to `config.BASE_URL`.

        Returns:
            list[str]: The lists of message strings.

        Raises:
            httpx.HTTPStatusError: If the HTTP request returns an unsuccessful status code.
            ValueError: If the response cannot be parsed as JSON or is missing the expected 'message-list' key.
        """
        get_messages_endpoint: str = "/message-list"
        final_url: str = base_url + get_messages_endpoint

        assert self.client is not None, "No client"
        response: httpx.Response = await self.client.post(
            final_url,
            headers=self.headers,
            json={"email": email}
        )
        return await self.parser.parse_json_response(response, "message-list")
