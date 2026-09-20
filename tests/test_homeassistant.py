"""Exercise the actual Home Assistant loader, config flow and entity platforms."""

import asyncio
from pathlib import Path
from types import MappingProxyType

import aiohttp
from aiohttp import web
from homeassistant import config_entries, loader
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er


async def test_real_homeassistant_setup_commands_and_unload(tmp_path, monkeypatch):
    calls = []
    sockets = []
    by_channel = {}
    workflow = {
        "profile": {"title": "Test", "steps": [], "version": "2"},
        "context": {"targetYield": 36, "targetDoseWeight": 18},
    }
    frames = {
        "/ws/v1/machine/snapshot": {"pressure": 9, "state": {"state": "idle", "substate": "idle"}},
        "/ws/v1/scale/snapshot": {"weight": 20, "battery": 90, "timerValue": 2500},
        "/ws/v1/machine/waterLevels": {"currentLevel": 30, "refillLevel": 10},
        "/ws/v1/machine/shotState": {"event": "state", "state": "idle", "scaleConnected": True},
        "/ws/v1/display": {"brightness": 50, "wakeLockOverride": False},
    }

    async def handler(request):
        if request.path.startswith("/ws/"):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            sockets.append(ws)
            by_channel[request.path] = ws
            await ws.send_json(frames.get(request.path, {}))
            async for _ in ws:
                pass
            return ws
        calls.append((request.method, request.path, await request.read()))
        if request.path == "/api/v1/devices":
            return web.json_response([])
        if request.path == "/api/v1/workflow":
            if request.method == "PUT":
                patch = await request.json()
                for key, value in patch.items():
                    workflow.setdefault(key, {}).update(value)
            return web.json_response(workflow)
        if request.path == "/api/v1/profiles":
            return web.json_response([{"id": "profile:123", "profile": workflow["profile"]}])
        if request.path == "/api/v1/machine/cupWarmer":
            return web.Response(status=404)
        if request.path == "/api/v1/machine/state":
            return web.json_response(frames["/ws/v1/machine/snapshot"])
        if request.path == "/api/v1/display":
            return web.json_response(frames["/ws/v1/display"])
        return web.json_response({})

    app = web.Application()
    app.router.add_route("*", "/{path:.*}", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    url = f"http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}"
    (tmp_path / "custom_components").symlink_to(
        Path(__file__).parents[1] / "custom_components", target_is_directory=True
    )
    hass = HomeAssistant(str(tmp_path))
    loader.async_setup(hass)
    hass.config_entries = config_entries.ConfigEntries(hass, {})
    await hass.config_entries.async_initialize()
    await er.async_load(hass)
    await dr.async_load(hass)
    await ar.async_load(hass)
    session = aiohttp.ClientSession()
    monkeypatch.setattr("custom_components.decaid.async_get_clientsession", lambda hass: session)
    monkeypatch.setattr(
        "custom_components.decaid.config_flow.async_get_clientsession", lambda hass: session
    )
    entry = config_entries.ConfigEntry(
        data={"url": url},
        domain="decaid",
        title="Test Decaid",
        version=1,
        minor_version=1,
        source="user",
        unique_id=url,
        options={},
        discovery_keys=MappingProxyType({}),
        subentries_data=[],
    )
    try:
        await hass.config_entries.async_add(entry)
        await hass.async_block_till_done()
        assert entry.state == ConfigEntryState.LOADED
        for _ in range(100):
            if len(entry.runtime_data.online) == 7:
                break
            await asyncio.sleep(0.01)
        assert hass.states.get("sensor.decaid_pressure").state == "9"
        assert hass.states.get("sensor.decaid_scale_weight").state == "20"
        assert hass.states.get("binary_sensor.decaid_water_low").state == "off"
        assert hass.states.get("select.decaid_brewing_profile") is not None
        registry = er.async_get(hass)
        starts = [e for e in registry.entities.values() if e.unique_id.endswith("_espresso")]
        assert starts and starts[0].disabled_by is not None
        await hass.services.async_call(
            "decaid",
            "set_workflow",
            {
                "entry_id": entry.entry_id,
                "workflow": {"context": {"targetYield": 42}},
            },
            blocking=True,
        )
        assert workflow["context"]["targetYield"] == 42
        assert workflow["context"]["targetDoseWeight"] == 18
        response = await hass.services.async_call(
            "decaid",
            "api_request",
            {
                "entry_id": entry.entry_id,
                "method": "GET",
                "path": "/api/v1/workflow",
            },
            blocking=True,
            return_response=True,
        )
        assert response["result"]["context"]["targetYield"] == 42
        result = await hass.config_entries.flow.async_init(
            "decaid", context={"source": "user"}, data={"url": url}
        )
        assert result["type"] == "abort"
        assert result["reason"] == "already_configured"
        coordinator = entry.runtime_data
        # A disconnected scale must lose its old reading, then reconnect.
        old_socket = by_channel["/ws/v1/scale/snapshot"]
        await old_socket.close()
        for _ in range(50):
            if hass.states.get("sensor.decaid_scale_weight").state == "unavailable":
                break
            await asyncio.sleep(0.01)
        assert hass.states.get("sensor.decaid_scale_weight").state == "unavailable"
        frames["/ws/v1/scale/snapshot"]["weight"] = 25
        for _ in range(200):
            if hass.states.get("sensor.decaid_scale_weight").state == "25":
                break
            await asyncio.sleep(0.01)
        assert hass.states.get("sensor.decaid_scale_weight").state == "25"
        await hass.services.async_call(
            "decaid",
            "subscribe",
            {
                "entry_id": entry.entry_id,
                "channel": "/ws/v1/sensors/test/snapshot",
            },
            blocking=True,
        )
        await hass.services.async_call(
            "decaid",
            "unsubscribe",
            {
                "entry_id": entry.entry_id,
                "channel": "/ws/v1/sensors/test/snapshot",
            },
            blocking=True,
        )
        assert "/ws/v1/sensors/test/snapshot" not in coordinator.tasks
        assert await hass.config_entries.async_unload(entry.entry_id)
        assert not coordinator.tasks
        assert not coordinator.sockets
    finally:
        await hass.async_stop(force=True)
        for socket in sockets:
            await socket.close()
        await runner.cleanup()
        await session.close()
