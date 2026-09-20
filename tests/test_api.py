import base64
import re

import aiohttp
import pytest
import pytest_asyncio
from aiohttp import web

from custom_components.decaid import load_catalog
from custom_components.decaid.api import (
    DecaidAuthError,
    DecaidClient,
    DecaidError,
    normalize_url,
    validate_path,
)


@pytest_asyncio.fixture
async def server():
    calls = []
    sockets = []

    async def handler(request):
        calls.append((request.method, request.path, await request.read(), dict(request.query)))
        if request.path.startswith("/ws/"):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            sockets.append(ws)
            await ws.send_json({"pressure": 9, "state": {"state": "idle"}})
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await ws.send_str(msg.data)
            return ws
        if request.path == "/api/v1/account/decent":
            return web.Response(status=401)
        if request.path == "/api/v1/machine/state/espresso":
            return web.Response(status=503)
        if request.path == "/api/v1/logs":
            return web.Response(text="test log")
        if request.path == "/api/v1/data/export":
            return web.Response(body=b"\x00\x01\xff", content_type="application/zip")
        if request.path == "/api/v1/machine/state/sleeping":
            raise web.HTTPFound("/elsewhere")
        if request.path == "/api/v1/scale/tare":
            return web.Response(status=204)
        if request.path == "/api/v1/machine/info":
            return web.Response(text="{broken", content_type="application/json")
        return web.json_response({"ok": True})

    app = web.Application()
    app.router.add_route("*", "/{path:.*}", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    async with aiohttp.ClientSession() as session:
        yield DecaidClient(session, f"http://127.0.0.1:{port}", load_catalog()), calls
    for socket in sockets:
        await socket.close()
    await runner.cleanup()


@pytest.mark.parametrize(
    "bad",
    [
        "http://user:secret@host",
        "ftp://host",
        "http://host/api",
        "http://host?token=x",
        "http://host#x",
        "http://host:99999",
    ],
)
def test_url_rejects_ambiguous_origins(bad):
    with pytest.raises(ValueError):
        normalize_url(bad)


def test_url_normalization():
    assert normalize_url("HTTP://HOST:80/") == "http://host"
    assert normalize_url("http://[::1]:8080") == "http://[::1]:8080"


@pytest.mark.parametrize(
    "path",
    [
        "//evil/api/v1/info",
        "/api/v1/../info",
        "/api/v1/%252e%252e/info",
        "/api/v1/info?x=y",
        "/api/v1/store/a/%2F..%2Fsecret",
        "/api/v1/not-existing",
        "https://evil/api/v1/info",
    ],
)
def test_catalog_path_boundary(path):
    with pytest.raises(DecaidError):
        validate_path(path, [o["path"] for o in load_catalog()["operations"]])


def test_all_catalog_routes_are_addressable():
    catalog = load_catalog()
    assert len(catalog["operations"]) == 153
    for op in catalog["operations"]:
        path = re.sub(r"\{[^}]+\}", "test", op["path"])
        assert validate_path(path, [op["path"]]) == path
    for channel in catalog["channels"]:
        path = "/" + re.sub(r"\{[^}]+\}", "test", channel)
        assert validate_path(path, [channel]) == path
    validate_path(
        "/api/v1/webui/skin-assets/test/a/b.css", ["/api/v1/webui/skin-assets/{id}/{filepath}"]
    )


async def test_rest_json_query_binary_and_empty(server):
    client, calls = server
    assert await client.request(
        "PUT", "/api/v1/workflow", body={"context": {"targetYield": 36}}
    ) == {"ok": True}
    assert b"targetYield" in calls[-1][2]
    await client.request("GET", "/api/v1/shots/ids", params={"limit": "5"})
    assert calls[-1][3] == {"limit": "5"}
    assert await client.request("PUT", "/api/v1/scale/tare") is None
    assert await client.request("GET", "/api/v1/logs") == "test log"
    result = await client.request("GET", "/api/v1/data/export")
    assert base64.b64decode(result["base64"]) == b"\x00\x01\xff"
    await client.request(
        "POST", "/api/v1/data/import", body_base64="AAH/", content_type="application/zip"
    )
    assert calls[-1][2] == b"\x00\x01\xff"


async def test_errors_and_no_mutation_retries(server):
    client, calls = server
    with pytest.raises(DecaidAuthError):
        await client.request("GET", "/api/v1/account/decent")
    with pytest.raises(DecaidError, match="503"):
        await client.request("PUT", "/api/v1/machine/state/espresso")
    assert sum(path.endswith("/espresso") for _, path, *_ in calls) == 1
    with pytest.raises(DecaidError, match="302"):
        await client.request("PUT", "/api/v1/machine/state/sleeping")
    assert not any(path == "/elsewhere" for _, path, *_ in calls)
    with pytest.raises(DecaidError, match="Invalid JSON"):
        await client.request("GET", "/api/v1/machine/info")
    with pytest.raises(DecaidError, match="not supported"):
        await client.request("POST", "/api/v1/derek/answers/stream")


async def test_websocket_roundtrip(server):
    client, _ = server
    async with await client.websocket("/ws/v1/machine/snapshot") as ws:
        assert (await ws.receive_json())["pressure"] == 9
        await ws.send_json({"test": "echo"})
        assert await ws.receive_json() == {"test": "echo"}


async def test_size_limit(server, monkeypatch):
    client, _ = server
    monkeypatch.setattr("custom_components.decaid.api.MAX_BYTES", 1)
    with pytest.raises(DecaidError, match="limit"):
        await client.request("GET", "/api/v1/info")


async def test_transport_failure():
    async with aiohttp.ClientSession() as session:
        client = DecaidClient(session, "http://127.0.0.1:1", load_catalog())
        with pytest.raises(DecaidError, match="connection"):
            await client.request("GET", "/api/v1/info")


async def test_ambiguous_body_is_rejected_before_sending(server):
    client, calls = server
    with pytest.raises(DecaidError, match="either"):
        await client.request("PUT", "/api/v1/workflow", body={}, body_base64="AA==")
    assert calls == []
