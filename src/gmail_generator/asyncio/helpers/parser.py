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
Utility helper functions used across the project.

This module provides stateless helper functions for general use. Currently,
it exposes the `Parser` class with static methods to simplify common tasks,
such as parsing HTTP responses safely as JSON.

Typical Usage Example:
    import httpx
    from helpers import Helpers
    resp = httpx.Response(200, content=b'{"key": ["value"]}')
    Helpers.parse_json_response(resp, "get-items")
    {'key': ['value']}
"""
import httpx


class Parser:
    """
    Utility helpers used across the project.

    A small container for stateless helper functions. Currently this class
    exposes a static method `parse_json_response` that validates an httpx
    response and returns its JSON payload, raising a `RuntimeError` for
    HTTP errors (status >= 400) or invalid JSON.

    Attributes:
        None
    """
    @staticmethod
    async def parse_json_response(
            response: httpx.Response,
            context: str
    ) -> list[str]:
        """
        Parse the JSON content from an HTTP response.

        This function checks the HTTP response for errors and attempts to parse
        its content as JSON. If the response indicates an error (status code >= 400)
        or the content is not valid JSON, a RuntimeError is raised.

        Args:
            response (httpx.Response): The HTTP response object to parse.
            context (str): A string describing the context of the request, used
                in error messages.

        Returns:
            list[str]: The writed JSON content as a dictionary
                mapping strings to lists of strings.

        Raises:
            RuntimeError: If the response status code is 400 or higher.
            RuntimeError: If the response content is not valid JSON.
        """
        if response.status_code >= 400:
            raise RuntimeError(
                f"{context} returned {response.status_code}: {response.text}"
            )
        try:
            if "messageData" in response.text:
                return response.json().get("messageData", "")
            return response.json().get("email", "")
        except ValueError:
            raise RuntimeError(
                f"{context} response is not valid JSON: {response.text[:400]}"
            )
