"""Explicit machine and scale commands."""

from homeassistant.components.button import ButtonEntity

from .entity import DecaidEntity


async def async_setup_entry(hass, entry, async_add_entities):
    commands = [
        (state, title, "/api/v1/machine/state/" + state, disabled)
        for state, title, disabled in [
            ("idle", "Wake / stop", False),
            ("sleeping", "Sleep", False),
            ("espresso", "Start espresso", True),
            ("steam", "Start steam", True),
            ("hotWater", "Start hot water", True),
            ("flush", "Flush", True),
            ("steamRinse", "Steam rinse", True),
            ("skipStep", "Skip profile step", True),
        ]
    ]
    commands += [("tare", "Tare scale", "/api/v1/scale/tare", False)]
    commands += [
        ("timer_" + action, "Scale timer " + action, "/api/v1/scale/timer/" + action, False)
        for action in ("start", "stop", "reset")
    ]
    async_add_entities(DecaidButton(entry.runtime_data, *item) for item in commands)


class DecaidButton(DecaidEntity, ButtonEntity):
    def __init__(self, coordinator, key, name, path, disabled):
        super().__init__(coordinator, key, name)
        self.path = path
        self._attr_entity_registry_enabled_default = not disabled
        self._attr_icon = "mdi:coffee-maker"

    async def async_press(self):
        await self.command("PUT", self.path)
