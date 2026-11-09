# Existing Reddit resolver: implementation notes

This file describes the resolver copied from the private Telegram downloader repository's `fix/reddit-indianporngirl-adapters` branch for review. It is included as-is to show the actual current implementation; it is not an OAuth implementation.

## Current behavior

- Accepts Reddit post URLs and delegates resolution to RapidSave's public `/info` endpoint.
- Parses a download link from supported HTML anchors or expected JSON fields.
- Validates the submitted URL and resolved media URL with the project's public-HTTP URL guard.
- Downloads media with redirect limits, file-size limits, and empty-response checks.
- Returns a clear error when RapidSave does not provide a downloadable link.

## Known limitations

- This implementation does not call Reddit's Data API.
- It does not implement Reddit OAuth.
- It depends on a third-party public resolver whose response format and availability may change.
- It has not been verified end-to-end against the user's target Reddit share URL. A parser unit-test pass does not prove that the third-party resolver returns media or that a media CDN permits server-side downloads.
- NSFW, age-restricted, removed, private, or otherwise restricted posts may not be accessible. No access-control bypass is intended.

## Tests

`tests/test_reddit_adapter.py` covers parser behavior for representative HTML fragments and an empty/static response. It does not make live network requests and does not test Reddit API authentication or media delivery.

## Dependencies

The adapter imports `httpx`, `curl_cffi`, and the adjacent `url_security.py` module. The broader bot also uses the dependencies listed in the private project's deployment configuration; those deployment files are intentionally not published here.

## Planned next work after Reddit approval

1. Confirm the exact approved API access and OAuth flow.
2. Implement a separate Reddit API client with token handling and minimum necessary scopes.
3. Add mocked unit tests for token acquisition, expiry, API errors, rate limits, and post metadata parsing.
4. Add live integration tests only for content and endpoints Reddit has authorized.
5. Verify actual media bytes and Telegram delivery before describing the feature as working.
