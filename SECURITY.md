# Security and data handling

## Secrets

Never commit any of the following:

- Reddit client secrets, access tokens, refresh tokens, or authorization codes
- Telegram bot tokens
- Server passwords, SSH keys, or private keys
- Browser cookies or session exports
- Production environment files
- Signed media URLs or other time-limited bearer links

Use protected server-side secret storage. Rotate any credential that is accidentally exposed.

## Logging

- Never log Authorization headers, OAuth secrets, bot tokens, or cookies.
- Avoid retaining full post payloads when a small set of fields is sufficient.
- Do not log unnecessary Reddit usernames or personal information.
- Keep operational logs access-controlled and retention-limited.

## Access control

The bot is private and intended for its operator. Validate that Telegram requests originate from the configured operator account before processing links or returning media.

## API policy

Use Reddit Data API only after explicit access approval and within the granted permissions. Respect rate limits, content restrictions, removal requests, and the current Reddit Responsible Builder Policy.

Do not bypass authentication, paywalls, moderation restrictions, age gates, or media-host access controls.

## Repository hygiene

This public repository contains review documentation and no production credentials. The operational project, deployment files, secrets, cookies, and unrelated downloader code remain private.
