"""UI setup, reconfiguration and options."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import load_catalog
from .api import DecaidAuthError, DecaidClient, DecaidError, normalize_url
from .const import DOMAIN


class DecaidConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def _validate(self, data):
        data = dict(data)
        data["url"] = normalize_url(data["url"])
        catalog = await self.hass.async_add_executor_job(load_catalog)
        client = DecaidClient(
            async_get_clientsession(self.hass), data["url"], catalog, data.get("token", "")
        )
        devices = await client.request("GET", "/api/v1/devices")
        if not isinstance(devices, list):
            raise DecaidError("Unexpected devices response")
        return data

    async def async_step_user(self, user_input=None):
        return await self._form("user", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._form("reconfigure", user_input)

    async def _form(self, step, user_input):
        errors = {}
        if user_input is not None:
            try:
                data = await self._validate(user_input)
                if step == "reconfigure":
                    entry = self._get_reconfigure_entry()
                    for other in self._async_current_entries():
                        if other.entry_id != entry.entry_id and other.data["url"] == data["url"]:
                            return self.async_abort(reason="already_configured")
                    return self.async_update_reload_and_abort(
                        entry, data_updates=data, unique_id=data["url"]
                    )
                await self.async_set_unique_id(data["url"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Decaid " + data["url"], data=data)
            except DecaidAuthError:
                errors["base"] = "invalid_auth"
            except DecaidError:
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_url"
        return self.async_show_form(
            step_id=step,
            data_schema=vol.Schema(
                {
                    vol.Required("url", default="http://192.168.1.42:8080"): str,
                    vol.Optional("token", default=""): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DecaidOptionsFlow()


class DecaidOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "poll_interval", default=self.config_entry.options.get("poll_interval", 30)
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
                    vol.Required(
                        "emit_events", default=self.config_entry.options.get("emit_events", False)
                    ): bool,
                }
            ),
        )
