# Reddit Telegram Media Downloader — API Access Review

## Purpose

This repository contains the review-facing technical description for a **private, self-hosted Telegram bot** that accepts individual Reddit post URLs submitted manually by its operator.

The project is seeking Reddit Data API access approval before implementing or enabling Reddit API authentication.

## Current implementation status

- The main Telegram downloader project is maintained separately in a private repository.
- The existing Reddit resolver is experimental and is not represented as a verified or production-ready Reddit API integration.
- Reddit OAuth / Data API access is **not yet implemented or approved** in this review repository.
- No Reddit API credentials, access tokens, refresh tokens, bot tokens, browser cookies, or server secrets are included here.

## Intended workflow after approval

1. The operator sends one Reddit post URL to their private Telegram bot.
2. The service validates and resolves that individual URL.
3. Using an approved Reddit OAuth integration, it requests only the metadata needed for that submitted post.
4. It retrieves media only where Reddit and the underlying media host permit access.
5. It sends the resulting media to the same operator in Telegram.

The service is not designed for automatic subreddit crawling, bulk collection, user profiling, ad targeting, or AI model training.

## Data handling and safeguards

- Requests are initiated manually by the bot operator.
- Use only the minimum OAuth scopes and API access approved by Reddit.
- Respect API rate limits, access restrictions, and Reddit's applicable policies.
- Do not attempt to bypass deleted, private, quarantined, age-gated, or otherwise restricted content controls.
- Do not collect Reddit user profiles or build behavioral datasets.
- Do not sell or commercially redistribute Reddit content.
- Store credentials server-side only; never commit credentials or tokens to source control.
- Avoid logging access tokens, secrets, or unnecessary personal information.
- Honor content removal and access revocation requirements.

## Deployment and source code

The operational Telegram bot is hosted privately. This repository contains a copy of the current experimental Reddit resolver and its parser tests, alongside review documentation. The resolver currently uses a third-party public RapidSave endpoint; it does **not** use Reddit OAuth or Reddit's Data API. The code and tests are included to make the current state inspectable, not to claim that end-to-end Reddit downloads are working. Private deployment configuration, unrelated downloader integrations, cookies, and credentials are not included.

## Contact

The requesting developer can provide additional technical details to Reddit through the official Data Access Request process.
