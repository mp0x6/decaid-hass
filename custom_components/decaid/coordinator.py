"""Independent stream lifecycles with reconnect and REST reconciliation."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta

import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DecaidError, validate_path
from .const import DEFAULT_CHANNELS, POLL_PATHS

_LOGGER = logging.getLogger(__name__)


class DecaidCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, client):
        super().__init__(
            hass,
            _LOGGER,
            name="Decaid",
            config_entry=entry,
            update_interval=timedelta(seconds=entry.options.get("poll_interval", 30)),
        )
        self.entry = entry
        self.client = client
        self.cache = {}
        self.tasks = {}
        self.sockets = {}
        self.online = set()
        self.stopping = False

    async def _async_update_data(self):
        try:
            self.cache["devices"] = await self.client.request("GET", "/api/v1/devices")
        except DecaidError as err:
            raise UpdateFailed(str(err)) from err
        # Each optional resource can fail independently (e.g. no machine/Bengle).
        for key, path in POLL_PATHS.items():
            try:
                self.cache[key] = await self.client.request("GET", path)
            except DecaidError:
                if key not in DEFAULT_CHANNELS or DEFAULT_CHANNELS[key] not in self.online:
                    self.cache.pop(key, None)
        if DEFAULT_CHANNELS["machine"] not in self.online:
            try:
                self.cache["machine"] = await self.client.request("GET", "/api/v1/machine/state")
            except DecaidError:
                self.cache.pop("machine", None)
        return dict(self.cache)

    def start(self):
        for path in DEFAULT_CHANNELS.values():
            self.subscribe(path)

    def subscribe(self, path):
        validate_path(path, self.client.catalog["channels"])
        if path not in self.tasks:
            self.tasks[path] = self.entry.async_create_background_task(
                self.hass, self._listen(path), f"Decaid {path}"
            )

    async def unsubscribe(self, path):
        if path in DEFAULT_CHANNELS.values():
            raise DecaidError("Core entity streams cannot be unsubscribed")
        task = self.tasks.pop(path, None)
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def send(self, path, message):
        socket = self.sockets.get(path)
        if socket is None or socket.closed:
            raise DecaidError("Subscribe first and wait for the stream to connect")
        try:
            await socket.send_json(message)
        except (aiohttp.ClientError, ConnectionError) as err:
            raise DecaidError("WebSocket send failed; command was not retried") from err

    async def _listen(self, path):
        key = next((k for k, v in DEFAULT_CHANNELS.items() if v == path), None)
        delay = 1
        while not self.stopping:
            try:
                async with asyncio.timeout(15):
                    socket = await self.client.websocket(path)
                self.sockets[path] = socket
                async with socket:
                    async for message in socket:
                        if message.type == aiohttp.WSMsgType.TEXT:
                            try:
                                payload = json.loads(message.data)
                            except ValueError:
                                continue
                            if not isinstance(payload, (dict, list)):
                                continue
                            if isinstance(payload, dict) and "error" in payload:
                                continue
                            delay = 1
                            self.online.add(path)
                            if key:
                                self.cache[key] = payload
                                self.async_set_updated_data(dict(self.cache))
                            if (
                                path == DEFAULT_CHANNELS["shot"]
                                and isinstance(payload, dict)
                                and payload.get("event") in ("decision", "terminal")
                            ):
                                self.hass.bus.async_fire(
                                    "decaid_shot", {**payload, "entry_id": self.entry.entry_id}
                                )
                            # Raw/high-volume frames are opt-in to avoid recorder/event load.
                            if key is None or self.entry.options.get("emit_events", False):
                                self.hass.bus.async_fire(
                                    "decaid_message",
                                    {
                                        "entry_id": self.entry.entry_id,
                                        "channel": path,
                                        "data": payload,
                                    },
                                )
                        elif message.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSE):
                            break
            except (TimeoutError, aiohttp.ClientError, DecaidError, OSError):
                _LOGGER.debug("Decaid stream disconnected: %s", path)
            finally:
                self.sockets.pop(path, None)
                self.online.discard(path)
                if key:
                    self.cache.pop(key, None)
                    if not self.stopping:
                        self.async_set_updated_data(dict(self.cache))
            await asyncio.sleep(delay)
            delay = min(delay * 2, 60)

    async def stop(self):
        self.stopping = True
        for task in self.tasks.values():
            task.cancel()
        await asyncio.gather(*self.tasks.values(), return_exceptions=True)
        self.tasks.clear()
