# Analytics backend

Python 3.9 / FastAPI service for analytics queries, integrations, and reporting.

## Local tests

1. Install Python 3.9 and Poetry 1.x.
2. Run `poetry install --no-root`.
3. Run `cp .defaults .env`.
4. Run `poetry run pytest`.

The environment template contains empty credentials. Tests use mocks.
Nine existing async tests are skipped because their marker is `sasyncio`.

## Local services

Runtime requires MongoDB, ClickHouse, and Redis. Configure credentials locally.
The backend and data processor use the `platform_default` queue.
Internal API authentication uses the `platform-api-key` header and
`PLATFORM_API_KEY` configuration variable.

Test identities and credentials are synthetic. Do not send fixture values to
external services. Third-party dependencies and bundled source retain their
original attribution. The project is licensed under MIT; see LICENSE.

## Repository

https://github.com/RahulNaidu710/analytics-backend

## Package scope

This standalone backend contains no production credentials or customer records.
Test identities and keys are intentionally synthetic and must not be used against
external services. The consumer-email-domain tests use FAKE_TEST_ONLY@gmail.com
only to exercise the Gmail-domain rule; all other fixture emails use example.com.

The generated browser capture SDK and source map are omitted. The static files
are import-compatible placeholders, not a working browser SDK. See static/README.md.
Analytics APIs and tests are retained.
