"""Connection and machine conditions."""

from homeassistant.components.binary_sensor import BinarySensorEntity

from .entity import DecaidEntity, value_at


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(
        DecaidBinary(entry.runtime_data, *spec)
        for spec in [
            ("machine", "ready", "Ready", None),
            ("water", "low", "Water low", "problem"),
            ("shot", "scaleConnected", "Scale connected", "connectivity"),
            ("shot", "scaleLost", "Scale lost during shot", "problem"),
            ("display", "lowBatteryBrightnessActive", "Display battery limit", None),
        ]
    )


class DecaidBinary(DecaidEntity, BinarySensorEntity):
    def __init__(self, coordinator, resource, path, name, device_class):
        super().__init__(coordinator, resource + "_" + path, name, resource)
        self.path = path
        self._attr_device_class = device_class

    @property
    def is_on(self):
        data = self.coordinator.data.get(self.resource, {})
        if self.path == "ready":
            state = value_at(data, "state.state")
            return None if state is None else state == "idle"
        if self.path == "low":
            current, refill = data.get("currentLevel"), data.get("refillLevel")
            return None if current is None or refill is None else current <= refill
        return value_at(data, self.path)
