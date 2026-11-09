from __future__ import annotations

import asyncio
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse

import httpx
from curl_cffi.requests import AsyncSession

from url_security import validate_public_http_url

REDDIT_HOST_RE = re.compile(r"(?:^|\.)(?:reddit\.com|redd\.it|v\.redd\.it)$", re.IGNORECASE)
CHROME_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)


class _DownloadLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        values = {key.lower(): value or "" for key, value in attrs}
        href = html.unescape(values.get("href", "")).strip()
        classes = set(values.get("class", "").lower().split())
        if href and ("download-button" in classes or "download.php" in href.lower()):
            self.links.append(href)


def _extract_rapidsave_download_url(page: str) -> str | None:
    parser = _DownloadLinkParser()
    parser.feed(page)
    for href in parser.links:
        absolute = urljoin("https://rapidsave.com/", href)
        parsed = urlparse(absolute)
        if parsed.scheme == "https" and (parsed.hostname or "").lower() in {
            "rapidsave.com", "www.rapidsave.com"
        }:
            return absolute
    return None


def _safe_filename_from_url(url: str) -> str:
    name = Path(urlparse(url).path).name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    if not name or name.lower().endswith(".php"):
        name = "reddit-video.mp4"
    elif not Path(name).suffix:
        name += ".mp4"
    return name[:180]


async def _resolve_with_rapidsave(post_url: str) -> str:
    endpoint = "https://rapidsave.com/info?url=" + quote(post_url, safe="")
    await validate_public_http_url(endpoint)
    headers = {
        "User-Agent": CHROME_UA,
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://rapidsave.com/",
    }
    async with AsyncSession(impersonate="chrome", timeout=25) as browser:
        response = await browser.get(endpoint, headers=headers)
    if response.status_code >= 400:
        raise RuntimeError(f"RapidSave resolver returned HTTP {response.status_code}.")
    content_type = response.headers.get("content-type", "").lower()
    if "json" in content_type:
        try:
            payload = response.json()
        except Exception:
            payload = {}
        data = payload.get("data") if isinstance(payload, dict) else None
        if isinstance(data, dict):
            for key in ("download_url", "url"):
                value = data.get(key)
                if isinstance(value, str) and value.startswith("https://"):
                    return value
    download_url = _extract_rapidsave_download_url(response.text)
    if download_url:
        return download_url
    raise RuntimeError(
        "RapidSave returned a page but no downloadable media link. "
        "The public resolver may have changed or may not support this post."
    )


async def _download_media(
    url: str,
    destination: Path,
    max_bytes: int,
    timeout_seconds: int,
) -> None:
    current_url = url
    headers = {
        "User-Agent": CHROME_UA,
        "Accept": "video/*,application/octet-stream,*/*;q=0.8",
        "Referer": "https://rapidsave.com/",
    }
    timeout = httpx.Timeout(
        float(timeout_seconds), connect=20.0, read=60.0, write=30.0, pool=20.0
    )
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            for _ in range(8):
                await validate_public_http_url(current_url)
                async with client.stream("GET", current_url, headers=headers) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise RuntimeError("Media redirect did not include a Location header.")
                        current_url = urljoin(current_url, location)
                        continue
                    if response.status_code >= 400:
                        raise RuntimeError(f"Media host returned HTTP {response.status_code}.")
                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" in content_type or "application/xhtml" in content_type:
                        raise RuntimeError(
                            "RapidSave download link returned HTML instead of media bytes."
                        )
                    length = response.headers.get("content-length")
                    if length and int(length) > max_bytes:
                        raise RuntimeError(
                            f"File exceeds configured {max_bytes // (1024 * 1024)} MB limit."
                        )
                    written = 0
                    with destination.open("wb") as output:
                        async for chunk in response.aiter_bytes(1024 * 1024):
                            if not chunk:
                                continue
                            written += len(chunk)
                            if written > max_bytes:
                                raise RuntimeError(
                                    f"File exceeds configured {max_bytes // (1024 * 1024)} MB limit."
                                )
                            output.write(chunk)
                    if written <= 0:
                        raise RuntimeError("The media endpoint returned an empty file.")
                    return
            raise RuntimeError("Media download exceeded the redirect limit.")
    except Exception:
        destination.unlink(missing_ok=True)
        raise


async def download_reddit(
    url: str,
    output_dir: Path,
    max_bytes: int,
    timeout_seconds: int = 600,
) -> tuple[Path, str, str] | None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if not REDDIT_HOST_RE.search(host):
        return None
    if host == "v.redd.it":
        raise RuntimeError(
            "This is a direct Reddit video CDN URL. Send the Reddit post/share URL "
            "so the resolver can locate both video and audio tracks."
        )

    await validate_public_http_url(url)
    download_url = await _resolve_with_rapidsave(url)
    filename = _safe_filename_from_url(download_url)
    destination = output_dir / filename
    await _download_media(download_url, destination, max_bytes, timeout_seconds)
    return destination, destination.name, "RapidSave public resolver"
