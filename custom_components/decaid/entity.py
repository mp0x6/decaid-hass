"""Common entity behaviour."""

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import DecaidError
from .const import DOMAIN


def value_at(data, path):
    for segment in path.split("."):
        if not isinstance(data, dict):
            return None
        data = data.get(segment)
    return data


class DecaidEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, key, name, resource=None):
        super().__init__(coordinator)
        self.resource = resource
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "Decaid",
            "manufacturer": "Decent Espresso",
            "model": "Decaid API",
            "configuration_url": coordinator.client.url,
        }

    @property
    def available(self):
        return super().available and (
            self.resource is None or self.resource in self.coordinator.data
        )

    async def command(self, method, path, body=None):
        try:
            result = await self.coordinator.client.request(method, path, body=body)
        except DecaidError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
        return result
