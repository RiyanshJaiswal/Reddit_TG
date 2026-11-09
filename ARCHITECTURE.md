# Architecture

## Scope

This document describes the proposed Reddit integration for a private Telegram bot. It is a design description, not a claim that Reddit OAuth or API access is currently operational.

## Request flow

```text
Operator
  |
  | sends one Reddit post URL
  v
Private Telegram bot
  |
  v
URL validation and post identification
  |
  v
OAuth token manager (to be implemented after Reddit approval)
  |
  v
Approved Reddit Data API endpoints
  |
  v
Post metadata / permitted media references
  |
  v
Media retrieval where permitted
  |
  v
Telegram response to the same operator
```

## OAuth design principles

The implementation will be selected to match the access method Reddit approves. It will not assume that app-only authentication is permitted for this use case.

- Keep client credentials and tokens exclusively on the private server.
- Use an OAuth flow explicitly authorized for the application.
- Request only the minimum approved scopes.
- Validate token expiry and handle authorization errors without retry storms.
- Never place secrets in Telegram messages, client-side code, logs, or Git history.
- Provide a clear failure when content is unavailable or access is denied.

## Request boundaries

- One request corresponds to one manually submitted post URL.
- No scheduled scans, bulk endpoint harvesting, or subreddit crawling.
- No enumeration of users or posts.
- Respect Reddit rate limits and API response restrictions.
- Do not bypass content, age, moderation, or account restrictions.

## Media handling

Reddit post metadata may identify a media host or media representation. The bot will download only content that is accessible under Reddit's rules and the host's terms. API metadata access does not guarantee that a CDN will permit server-side media retrieval.

## Operational isolation

The Reddit integration is isolated from the existing X/Twitter downloader pipeline and its cookie-based configuration. No changes to that pipeline are part of this proposal.
