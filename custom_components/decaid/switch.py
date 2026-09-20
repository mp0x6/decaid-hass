"""Explicit power, display, charger and warmer controls."""

from homeassistant.components.switch import SwitchEntity

from .entity import DecaidEntity, value_at


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        DecaidSwitch(entry.runtime_data, *item)
        for item in [
            ("machine", "power", "Machine awake"),
            ("display", "wakeLockOverride", "Display wake lock"),
            ("settings", "usb", "USB charger"),
            ("cup_warmer", "enabled", "Cup warmer"),
        ]
    )


class DecaidSwitch(DecaidEntity, SwitchEntity):
    def __init__(self, coordinator, resource, key, name):
        super().__init__(coordinator, "switch_" + resource + "_" + key, name, resource)
        self.key = key
        self._attr_entity_registry_enabled_default = resource != "cup_warmer"

    @property
    def is_on(self):
        data = self.coordinator.data.get(self.resource, {})
        if self.key == "power":
            state = value_at(data, "state.state")
            return None if state is None else state not in ("sleeping", "booting")
        return data.get(self.key)

    async def _set(self, enabled):
        if self.key == "power":
            await self.command(
                "PUT", "/api/v1/machine/state/" + ("idle" if enabled else "sleeping")
            )
        elif self.resource == "display":
            await self.command("POST" if enabled else "DELETE", "/api/v1/display/wakelock")
        elif self.resource == "settings":
            await self.command(
                "POST", "/api/v1/machine/settings", {"usb": "enable" if enabled else "disable"}
            )
        else:
            await self.command("PUT", "/api/v1/machine/cupWarmer", {"enabled": enabled})

    async def async_turn_on(self, **kwargs):
        await self._set(True)

    async def async_turn_off(self, **kwargs):
        await self._set(False)
