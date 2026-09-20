"""Bounded asynchronous REST/WebSocket transport for the documented Decaid API."""

from __future__ import annotations

import base64
import json
import re
from urllib.parse import unquote, urlsplit

import aiohttp

MAX_BYTES = 8 * 1024 * 1024


class DecaidError(Exception):
    """Transport or protocol failure; no credentials or response bodies in logs."""


class DecaidAuthError(DecaidError):
    """Authentication failure."""


def normalize_url(value: str) -> str:
    url = urlsplit(value.strip())
    if (
        url.scheme not in ("http", "https")
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
        or url.path not in ("", "/")
    ):
        raise ValueError("Use http(s)://host:port without path or credentials")
    try:
        port = url.port
    except ValueError as err:
        raise ValueError("Invalid port") from err
    host = url.hostname.lower()
    host = f"[{host}]" if ":" in host else host
    default = 80 if url.scheme == "http" else 443
    return f"{url.scheme}://{host}" + (f":{port}" if port and port != default else "")


def validate_path(path: str, templates: list[str]) -> str:
    """Restrict requests to documented relative routes on the configured origin."""
    decoded = path
    for _ in range(4):
        decoded = unquote(decoded)
    if (
        not path.startswith("/")
        or any(c in decoded for c in ("?", "#", "\\"))
        or any(p in (".", "..", "") for p in decoded.split("/")[1:])
        or any(ord(c) < 32 for c in decoded)
    ):
        raise DecaidError("Invalid API path")
    for template in templates:
        template = "/" + template.lstrip("/")
        pattern = re.sub(r"\\\{[^}]+\\\}", "[^/]+", re.escape(template))
        # The upstream explicitly defines these trailing parameters as catch-all.
        for key in ("filepath", "endpoint"):
            if template.endswith("{" + key + "}"):
                pattern = pattern.rsplit("[^/]+", 1)[0] + ".+"
        if re.fullmatch(pattern, decoded):
            return path
    raise DecaidError("Path/method is not in the bundled API catalogue")


class DecaidClient:
    def __init__(self, session, url, catalog, token=""):
        self.session = session
        self.url = normalize_url(url)
        self.catalog = catalog
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    async def request(
        self, method, path, *, body=None, params=None, body_base64=None, content_type=None
    ):
        if body is not None and body_base64 is not None:
            raise DecaidError("Specify either body or body_base64, not both")
        method = method.upper()
        validate_path(
            path, [o["path"] for o in self.catalog["operations"] if o["method"] == method]
        )
        if path == "/api/v1/derek/answers/stream":
            raise DecaidError("Streaming HTTP endpoint is not supported")
        headers = dict(self.headers)
        kwargs = {}
        if body_base64 is not None:
            try:
                kwargs["data"] = base64.b64decode(body_base64, validate=True)
            except (ValueError, TypeError) as err:
                raise DecaidError("Invalid base64 body") from err
            headers["Content-Type"] = content_type or "application/octet-stream"
        elif content_type and content_type != "application/json":
            if body is not None and not isinstance(body, str):
                raise DecaidError("Non-JSON body must be text or base64")
            kwargs["data"] = body
            headers["Content-Type"] = content_type
        elif body is not None:
            kwargs["json"] = body
        try:
            async with self.session.request(
                method,
                self.url + path,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=45),
                allow_redirects=False,
                **kwargs,
            ) as response:
                if response.status in (401, 403):
                    raise DecaidAuthError(f"Decaid returned HTTP {response.status}")
                if not 200 <= response.status < 300:
                    raise DecaidError(f"Decaid returned HTTP {response.status}")
                chunks, size = [], 0
                async for chunk in response.content.iter_chunked(65536):
                    size += len(chunk)
                    if size > MAX_BYTES:
                        raise DecaidError("Response exceeds 8 MiB limit")
                    chunks.append(chunk)
                raw = b"".join(chunks)
                if not raw:
                    return None
                if "json" in response.content_type:
                    try:
                        return json.loads(raw)
                    except (ValueError, UnicodeError) as err:
                        raise DecaidError("Invalid JSON response") from err
                if response.content_type.startswith("text/"):
                    return raw.decode("utf-8", errors="replace")
                return {
                    "base64": base64.b64encode(raw).decode(),
                    "content_type": response.content_type,
                }
        except (TimeoutError, aiohttp.ClientError) as err:
            # Never retry mutations: the machine may already have executed them.
            raise DecaidError("Decaid connection failed or timed out") from err

    async def websocket(self, path):
        validate_path(path, self.catalog["channels"])
        return await self.session.ws_connect(
            self.url.replace("http", "ws", 1) + path,
            headers=self.headers,
            heartbeat=30,
            max_msg_size=MAX_BYTES,
        )
