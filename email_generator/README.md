
# account-generator — Emailnator wrapper (sync & async)

> A Python wrapper around the Emailnator service that provides both **synchronous** and **asynchronous** APIs.
> Designed with a `src/` layout, minimal dependencies, typed code, and a clear separation between async core logic and a lightweight sync wrapper.

---

**Quick summary**

* ✅ Async-first implementation (single source of truth)
* ✅ Thin sync wrappers that call the async core (`asyncio.run(...)`) for convenience
* ✅ Clear package layout (`src/account_generator/{async,sync,core}`)
* ✅ Examples for both sync and async usage
* 🛡️ Licensed under **AGPL-3.0** (see `LICENSE`)

Joke: This README is tighter than a bull's testicles — concise and unshakeable.

---

## Table of contents

1. [Project layout](#project-layout)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Quick start — examples (sync & async)](#quick-start)
5. [API reference](#api-reference)
6. [Design & implementation notes](#design--implementation-notes)
7. [Testing](#testing)
8. [Packaging & publishing](#packaging--publishing)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [Security](#security)
12. [License](#license)

---

## Installation

Use the repo root and install in editable mode during development:

```bash
# from repo root
pip install -e .
```

This uses your `pyproject.toml` / `setup.cfg` / `setup.py` configuration and makes `email_generator` importable.

If you publish to PyPI, users will install with:

```bash
pip install account-generator
```

(Replace with the actual PyPI name you publish under.)

## Quick start

### A. Asynchronous usage (recommended for servers / concurrent tasks)

`examples/async_example.py`:

```py
import asyncio
from account_generator.async.email_generator import AsyncEmailGenerator
from account_generator.generators import Generators
from account_generator.message_getter import MessageGetter

async def main():
    generators = Generators()         # async client implementation
    message_getter = MessageGetter()  # async client implementation

    async_gen = AsyncEmailGenerator(generators, message_getter)
    email = await async_gen.generate_email()
    messages = await async_gen.get_messages(email)
    print("Generated:", email)
    print("Messages:", messages)

if __name__ == "__main__":
    asyncio.run(main())
```

Run:

```bash
python examples/async_example.py
```

### B. Synchronous usage (convenient for scripts)

`examples/sync_example.py`:

```py
from account_generator.sync.email_generator import EmailGenerator
from account_generator.generators import Generators
from account_generator.message_getter import MessageGetter

generators = Generators()         # uses async internals
message_getter = MessageGetter()

gen = EmailGenerator(generators, message_getter)
email = gen.generate_email()
messages = gen.get_messages(email)
print("Generated:", email)
print("Messages:", messages)
```

Run:

```bash
python examples/sync_example.py
```

**Important:** The sync wrapper uses `asyncio.run(...)` internally. Do not call sync wrapper methods from inside an already-running event loop (e.g., inside an async web framework request or Jupyter) — instead use the `AsyncEmailGenerator` directly in those contexts.

---

## API reference (high-level)

### `account_generator.async.email_generator.AsyncEmailGenerator`

```py
class AsyncEmailGenerator:
    def __init__(self, generators: Generators, message_getter: MessageGetter):
        ...

    async def generate_email(self) -> str:
        """Generate an email address and return it."""

    async def get_messages(self, email: str) -> dict[str, list[str]]:
        """Return messages for a given email."""

    async def generate_and_print(self) -> None:
        """Convenience: generate, fetch messages, print them."""
```

### `account_generator.sync.email_generator.EmailGenerator`

```py
class EmailGenerator:
    def __init__(self, generators: Generators, message_getter: MessageGetter):
        ...

    def generate_email(self) -> str:
        """Synchronous wrapper — calls async implementation under the hood."""

    def get_messages(self, email: str) -> dict[str, list[str]]:
        """Synchronous wrapper — calls async implementation under the hood."""

    def generate_and_print(self) -> None:
        """Synchronous convenience wrapper."""
```

### `account_generator.generators.Generators` & `account_generator.message_getter.MessageGetter`

Implementations should provide asynchronous methods (async-first):

```py
class Generators:
    async def generate_email_async(self) -> list[str]:
        """Return list of generated emails (async)."""

class MessageGetter:
    async def get_message_list_async(self, email: str) -> dict[str, list[str]]:
        """Return parsed messages for the email (async)."""
```

You may provide thin compatibility methods (non-async) if desired, but the library expects the async versions.

---

## Design & implementation notes

### Async-first core

* Implement I/O using `httpx.AsyncClient` or `aiohttp`.
* Core business logic is asynchronous (`async def`).
* Sync API is a thin wrapper that runs the async coroutine with `asyncio.run()`.

Why async-first?

* Better scalability: many concurrent I/O tasks without threads.
* Single source of truth reduces duplication.

### Sync wrapper considerations

* `asyncio.run()` creates and closes an event loop each call — this is fine for CLI scripts and simple apps.
* If you need repeated sync calls inside long-running sync code, consider creating a single loop and using `loop.run_until_complete(...)` or using a persistent thread for the loop.
* If you need to call from within an already running loop (e.g., Jupyter, aiohttp request handler), call the async API directly.

### Example: concurrent email generation

```py
# async usage
async def gen_many(n):
    g = AsyncEmailGenerator(Generators(), MessageGetter())
    coros = [g.generate_email() for _ in range(n)]
    results = await asyncio.gather(*coros)
    return results
```

---

## Testing

Use `pytest`. For network calls, mock HTTP requests:

* `respx` (works with `httpx`) for async http mocking
* `pytest-asyncio` for async tests

Example `tests/test_async.py`:

```py
import pytest
import respx
from httpx import Response
from account_generator.async.email_generator import AsyncEmailGenerator

@pytest.mark.asyncio
async def test_generate_email_success(respx_mock):
    respx_mock.get("https://api.emailnator.example/generate").mock(return_value=Response(200, json=["a@ex.com"]))
    gen = AsyncEmailGenerator(Generators(), MessageGetter())
    email = await gen.generate_email()
    assert email.endswith("@ex.com")
```

Run tests:

```bash
pip install -e .[dev]     # dev extras: pytest, pytest-asyncio, respx
pytest -q
```

---

## Packaging & publishing

`pyproject.toml` minimal example (place in project root):

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "account-generator"
version = "0.1.0"
description = "A Python wrapper for the Emailnator service providing sync and async APIs."
readme = "README.md"
requires-python = ">=3.10"
license = { file = "LICENSE" }
authors = [{ name = "Your Name", email = "you@example.com" }]
dependencies = ["httpx>=0.23"]  # or aiohttp, depending on implementation

[tool.setuptools.packages.find]
where = ["src"]
```

Build & publish:

```bash
# build
python -m build

# test upload (twine)
twine upload --repository testpypi dist/*

# real upload
twine upload dist/*
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

* Use `src/` layout correctly: package folder should be `src/account_generator/`, not `src/` imports.
* `pyproject.toml` should include:

  ```toml
  [tool.setuptools.packages.find]
  where = ["src"]
  ```
* During development, run `pip install -e .` from repo root (not from `src/`).

### Sync wrapper inside running event loop (e.g., Jupyter)

* `asyncio.run()` raises `RuntimeError` if loop already running.
* Solutions:

  * Use `AsyncEmailGenerator` directly inside async code.
  * Use `nest_asyncio` in REPL (not recommended for production).
  * Use `anyio` or run async code from thread.

### Rate limits / retries

* Respect Emailnator service rate limits.
* Implement retries with exponential backoff (e.g., `tenacity` or custom).

---

## Contributing

1. Fork the repo.
2. Create feature branch: `git checkout -b feature/awesome`.
3. Run tests and linters locally.
4. Open a Pull Request with a clear description and tests.

Recommended dev tools:

* `pre-commit` (black, isort, flake8)
* `pytest`, `pytest-asyncio`
* `mypy` for static typing

---

## Security

* Do **not** commit API keys. Use env vars or secrets management.
* Validate and sanitize messages before printing/storing.
* Consider adding HMAC/signature verification if Emailnator supports callbacks.

---

## FAQ

**Q:** Can I use this in a Flask/Django app?
**A:** Yes. Use `AsyncEmailGenerator` inside async-capable frameworks (e.g., FastAPI). For WSGI frameworks (sync), use the sync wrapper, but prefer async for heavy I/O.

**Q:** Why not provide both fully separate sync & async implementations?
**A:** That duplicates logic and increases maintenance. Async-first + sync-wrapper keeps a single source of truth.

**Q:** What about Windows compatibility?
**A:** `asyncio` + `httpx` work on Windows. Mind the event-loop policy and process spawning differences for concurrency.

---

## Changelog & roadmap

* `0.1.0` — initial async-first wrapper + sync thin wrapper, tests, docs
* Roadmap:

  * add CLI utility
  * add caching layer (optional)
  * support multiple disposable-email providers (adapter pattern)
  * provide typed stubs and improved docs

---

## Contact / Maintainers

* Maintainer: Your Name — `you@example.com`
* Project: `account-generator` (replace with actual repo URL)

---

## License

This project is licensed under the **GNU Affero General Public License v3** (AGPL-3.0). See `LICENSE` for details.

---

If you want, I can now:

* generate a complete `README.md` file ready to paste into your repo (with the same content),
* generate example files (`examples/async_example.py`, `examples/sync_example.py`),
* or scaffold `pyproject.toml` + recommended `dev` extras (`[project.optional-dependencies] dev = [...]`) for you.
