from __future__ import annotations

import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit


class UnsafeURL(ValueError):
    """Raised when a submitted URL could reach a non-public network."""


async def validate_public_http_url(url: str) -> None:
    """Reject malformed URLs and hosts that resolve to non-public IP addresses.

    This is a preflight guard for user-controlled URLs. It is defense in depth:
    clients that perform their own DNS lookups (notably yt-dlp/FFmpeg) still
    need an outbound network policy to completely eliminate DNS-rebinding and
    redirect-based SSRF.
    """
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise UnsafeURL("The URL is malformed.") from exc

    if parsed.scheme.lower() not in {"http", "https"}:
        raise UnsafeURL("Only HTTP and HTTPS URLs are supported.")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeURL("URLs containing embedded credentials are not allowed.")

    hostname = (parsed.hostname or "").rstrip(".").lower()
    if not hostname:
        raise UnsafeURL("The URL must include a hostname.")
    if hostname == "localhost" or hostname.endswith((".localhost", ".local", ".internal", ".test")):
        raise UnsafeURL("Local or internal hostnames are not allowed.")

    service_port = port or (443 if parsed.scheme.lower() == "https" else 80)
    addresses: set[str] = set()

    try:
        literal = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            loop = asyncio.get_running_loop()
            records = await asyncio.wait_for(
                loop.getaddrinfo(
                    hostname,
                    service_port,
                    type=socket.SOCK_STREAM,
                    proto=socket.IPPROTO_TCP,
                ),
                timeout=5,
            )
        except (OSError, asyncio.TimeoutError) as exc:
            raise UnsafeURL("The hostname could not be resolved.") from exc

        for record in records:
            addresses.add(record[4][0].split("%", 1)[0])
    else:
        addresses.add(str(literal))

    if not addresses:
        raise UnsafeURL("The hostname did not resolve to an IP address.")

    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise UnsafeURL("The hostname resolved to an invalid IP address.") from exc
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        if not ip.is_global:
            raise UnsafeURL("Downloads to private, local, reserved, or link-local IP addresses are blocked.")
