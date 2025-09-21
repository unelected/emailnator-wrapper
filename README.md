# emailnator\-wrapper

Asynchronous and synchronous API wrapper for **EmailNator**.
Provides a small, well-typed SDK to generate temporary Gmail-style addresses and read incoming messages. Designed for both script usage and integration into larger automation/test suites.

---

## Features

* Fully asynchronous core using `httpx.AsyncClient`.
* Optional synchronous wrapper for blocking workflows.
* Automatic XSRF token management (fetch, decode, refresh) via `XsrfManager`.
* Async-aware initialization helpers (metaclasses / factories) so classes can expose `__ainit__`.
* Async-safe singletons (`AsyncSingletonMeta`) where appropriate (HTTP client).
* Configurable via YAML (`config.yaml`) with optional proxy support.
* Clear, Google-style docstrings and type annotations.

---

## Requirements

* Python 3.11+ (works on 3.13).
* Dependencies (typical):

  * `httpx`
  * `PyYAML`
  * `pytest` / `pytest-asyncio` for tests

---

## Installation

```bash
pip install email-wrapper
```

---

## Configuration

`emailnator/config/config.yaml` (example):

```yaml
BASE_URL: https://www.emailnator.com
TIMEOUT: 15
USE_HTTP2: true
USER_AGENT: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
GMAIL_CONFIG:
  - dotGmail
  - plusGmail
PROXY: null
```

**Notes**

* `PROXY: null` sets `config.PROXY` to `None`. Do **not** use the literal string `"None"` — `httpx` will reject that as an invalid proxy URL.
* Keep credentials / secrets out of the YAML in public repos.

---

## Quickstart — Asynchronous (recommended)

Save the example below as `examples/async_example.py`.

```python
# Copyright (C) 2025 unelected
#
# This file is part of account_generator.
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
Example usage of the asynchronous AsyncEmailGenerator.

This script demonstrates:
  1. Creating the asynchronous AsyncEmailGenerator (awaitable constructor).
  2. Generating a single temporary email address.
  3. Retrieving messages for that address.
  4. Printing results.
"""
import asyncio

from emailnator.asyncio.email_generator import AsyncEmailGenerator


async def generate_email_and_get_messages() -> None:
    """
    Initialize the async generator, produce an email and fetch messages.
    """
    generator = await AsyncEmailGenerator()
    email_list = await generator.generate_email()
    email = email_list[0]
    messages = await generator.get_messages(email)
    print(f"Email: {email}\nMessages: {messages}")


if __name__ == "__main__":
    asyncio.run(generate_email_and_get_messages())
```

---

## Quickstart — Synchronous wrapper

Save as `examples/sync_example.py`.

```python
# Copyright (C) 2025 unelected
#
# This file is part of account_generator.
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
Synchronous example using EmailGenerator wrapper.

This demonstrates creating the blocking wrapper and using it to generate
an email and retrieve messages in a non-async program.
"""
from emailnator.sync.email_generator import EmailGenerator

def main() -> None:
    gen = EmailGenerator()
    email = gen.generate_email()
    messages = gen.get_messages(email)
    print(f"Email: {email}\nMessages: {messages}")

if __name__ == "__main__":
    main()
```

---

## Public API overview

* `emailnator.asyncio.email_generator.AsyncEmailGenerator`
  High-level async facade. Use `await AsyncEmailGenerator()`.

* `emailnator.asyncio.generators.Generators`
  Endpoint wrapper for `/generate-email`. Provides `generate_email()` and `generate_bulk_emails()`.

* `emailnator.asyncio.message_getter.MessageGetter`
  Fetch and parse messages for a given temporary email address.

* `emailnator.asyncio.builders.AsyncEmailnatorClient`
  HTTP client singleton (uses `AsyncSingletonMeta`). Exposes `get_client()`, `get_headers()`, `refresh_token()`.

* `emailnator.asyncio.builders.helpers.xsrf_token_service.XsrfManager`
  Encapsulates XSRF lifecycle: `ensure_token()`, `refresh()`, `get_token()`, `get_headers()`.

* `emailnator.config.config`
  Loads `config.yaml` to `config` object with attributes `BASE_URL`, `TIMEOUT`, `USE_HTTP2`, `USER_AGENT`, `GMAIL_CONFIG`, `PROXY`.

---

## Behavior notes & gotchas

* **Await the constructor** if using metaclass-based `__ainit__`: `obj = await ClassName()`. If you forget `await`, you get a coroutine object with no attributes.
* **Proxy value** in YAML must be `null` for no proxy. String `"None"` will break `httpx`.
* **Cloudflare / Bot protection**: EmailNator may be behind challenges (403/419). Temporary addresses and token flows can be blocked by anti-bot measures — the library attempts to read `XSRF-TOKEN` cookie, but if the site requires JavaScript challenges, consider using a Playwright-based flow or proper proxies.
* **Event loop management**: Avoid calling `asyncio.run()` inside already-running event loops. For synchronous wrapper, use a dedicated factory that creates its own loop safely.

---

## Error handling & common troubleshooting

* `coroutine object has no attribute '...'` — forgot `await` on constructor.
* `RuntimeWarning: coroutine was never awaited` — coroutine was created and not awaited; search for returns of coroutines.
* `ValueError: Unknown scheme for proxy URL "None"` — `config.PROXY` is the string `"None"`, fix YAML to `null` or code to coerce `None`.
* HTTP 419 / Page Expired — XSRF token missing or expired; check `XsrfManager` and cookie extraction.
* HTTP 403 Cloudflare — site-side bot protection.

---

## Contributing

* Fork, branch `feature/...`, implement, add tests, open PR.
* Keep changes backwards-compatible for public API unless you bump major version.
* Follow project style: type annotations, Google-style docstrings, tests.

---

## License

This project is licensed under GNU Affero General Public License v3 (AGPL-3.0).

---

## Files to include in the repo

* `README.md` (this file)
* `pyproject.toml` / `setup.cfg` with dependencies and dev extras
* `emailnator/config/config.yaml` example
* `examples/async_example.py`
* `examples/sync_example.py`
* `tests/` with unit & async tests

---

## Contact

Open an issue or submit a pull request for help, bug reports, or enhancements.
