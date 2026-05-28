# AGENTS.md

## Project Overview

`libglobalping-unofficial` is an async Python client library for the [GlobalPing API](https://api.globalping.io/). It wraps all measurement endpoints (ping, traceroute, MTR, DNS, HTTP), probe listing, and rate limit checking.

## Tech Stack

- Python 3.11+
- `httpx` — async HTTP client
- `pydantic` v2 — response models and validation
- `pytest` + `pytest-asyncio` + `respx` — testing with mocked HTTP
- Poetry — dependency management

## Project Structure

```
libglobalping/
├── __init__.py       # Public API exports
├── client.py         # GlobalpingClient (async context manager)
├── models.py         # Pydantic models for all API responses
└── exceptions.py     # Typed exception hierarchy
test/
└── test_client.py    # Unit tests with mocked API responses
```

## Conventions

- All public methods on `GlobalpingClient` are `async`.
- Models use Pydantic `Field(alias=...)` to map camelCase API fields to snake_case Python attributes.
- All models set `model_config = {"populate_by_name": True}` so both alias and Python name work.
- Errors from the API (400, 422, 429) are raised as typed exceptions, never raw HTTP errors.
- Polling uses 500ms intervals per API spec guidelines.
- The client sends a `User-Agent` header identifying the library.

## Testing

```bash
python -m pytest test/ -v
```

Tests use `respx` to mock all HTTP calls — no network access required. Each test provides fixture data matching the real API response shapes.

## API Reference

The upstream API spec is at: https://api.globalping.io/v1/spec.yaml
