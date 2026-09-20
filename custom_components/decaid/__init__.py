"""Home Assistant integration for the Decaid local API."""

from __future__ import annotations

import json
from pathlib import Path

import voluptuous as vol
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DecaidClient, DecaidError
from .const import DOMAIN, PLATFORMS
from .coordinator import DecaidCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def load_catalog():
    return json.loads(Path(__file__).with_name("catalog.json").read_text())


async def async_setup(hass, config):
    async def service(call):
        entry = hass.config_entries.async_get_entry(call.data["entry_id"])
        if entry is None or entry.domain != DOMAIN or not getattr(entry, "runtime_data", None):
            raise HomeAssistantError("Decaid entry is not loaded")
        coordinator = entry.runtime_data
        try:
            result = None
            if call.service == "api_request":
                result = await coordinator.client.request(
                    call.data["method"],
                    call.data["path"],
                    body=call.data.get("body"),
                    params=call.data.get("query"),
                    body_base64=call.data.get("body_base64"),
                    content_type=call.data.get("content_type"),
                )
                if call.data["method"] != "GET":
                    await coordinator.async_request_refresh()
            elif call.service == "websocket_send":
                await coordinator.send(call.data["channel"], call.data["message"])
            elif call.service == "subscribe":
                coordinator.subscribe(call.data["channel"])
            elif call.service == "unsubscribe":
                await coordinator.unsubscribe(call.data["channel"])
            elif call.service == "set_state":
                await coordinator.client.request(
                    "PUT", "/api/v1/machine/state/" + call.data["state"]
                )
            elif call.service == "set_workflow":
                result = await coordinator.client.request(
                    "PUT", "/api/v1/workflow", body=call.data["workflow"]
                )
                await coordinator.async_request_refresh()
        except DecaidError as err:
            raise HomeAssistantError(str(err)) from err
        if call.return_response:
            return {"result": result}
        return None

    base = {vol.Required("entry_id"): str}
    schemas = {
        "api_request": {
            vol.Required("method"): vol.In(["GET", "POST", "PUT", "PATCH", "DELETE"]),
            vol.Required("path"): str,
            vol.Optional("body"): object,
            vol.Optional("query"): dict,
            vol.Optional("body_base64"): str,
            vol.Optional("content_type"): str,
        },
        "websocket_send": {vol.Required("channel"): str, vol.Required("message"): dict},
        "subscribe": {vol.Required("channel"): str},
        "unsubscribe": {vol.Required("channel"): str},
        "set_state": {
            vol.Required("state"): vol.In(
                [
                    "idle",
                    "sleeping",
                    "espresso",
                    "steam",
                    "hotWater",
                    "flush",
                    "steamRinse",
                    "skipStep",
                    "cleaning",
                    "descaling",
                    "airPurge",
                ]
            )
        },
        "set_workflow": {vol.Required("workflow"): dict},
    }
    for name, fields in schemas.items():
        hass.services.async_register(
            DOMAIN,
            name,
            service,
            schema=vol.Schema({**base, **fields}),
            supports_response=SupportsResponse.OPTIONAL,
        )
    return True


async def async_setup_entry(hass, entry):
    catalog = await hass.async_add_executor_job(load_catalog)
    client = DecaidClient(
        async_get_clientsession(hass), entry.data["url"], catalog, entry.data.get("token", "")
    )
    coordinator = DecaidCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    coordinator.start()
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_reload_entry(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.stop()
        entry.runtime_data = None
        return True
    return False
