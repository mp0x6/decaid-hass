"""Live machine, scale and recipe sensors."""

from homeassistant.components.sensor import SensorEntity, SensorStateClass

from .entity import DecaidEntity, value_at

# resource, JSON path, display name, unit, device class
SENSORS = [
    ("machine", "state.state", "Machine state", None, None),
    ("machine", "state.substate", "Machine substate", None, None),
    ("machine", "pressure", "Pressure", "bar", "pressure"),
    ("machine", "targetPressure", "Target pressure", "bar", "pressure"),
    ("machine", "flow", "Flow", "mL/s", None),
    ("machine", "targetFlow", "Target flow", "mL/s", None),
    ("machine", "mixTemperature", "Mix temperature", "°C", "temperature"),
    ("machine", "groupTemperature", "Group temperature", "°C", "temperature"),
    ("machine", "targetMixTemperature", "Target mix temperature", "°C", "temperature"),
    ("machine", "targetGroupTemperature", "Target group temperature", "°C", "temperature"),
    ("machine", "steamTemperature", "Steam temperature", "°C", "temperature"),
    ("machine", "profileFrame", "Profile frame", None, None),
    ("scale", "weight", "Scale weight", "g", "weight"),
    ("scale", "weightFlow", "Scale flow", "g/s", None),
    ("scale", "battery", "Scale battery", "%", "battery"),
    ("scale", "timerValue", "Scale timer", "ms", "duration"),
    ("water", "currentLevel", "Tank water level", "mm", "distance"),
    ("water", "refillLevel", "Refill threshold", "mm", "distance"),
    ("shot", "state", "Shot phase", None, None),
    ("shot", "decision.reason", "Shot stop reason", None, None),
    ("workflow", "profile.title", "Profile", None, None),
    ("workflow", "context.coffeeName", "Coffee", None, None),
    ("workflow", "context.grinderModel", "Grinder", None, None),
    ("display", "brightness", "Display brightness", "%", None),
    ("cup_warmer", "currentTemperature", "Cup warmer temperature", "°C", "temperature"),
]


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities(DecaidSensor(entry.runtime_data, *item) for item in SENSORS)


class DecaidSensor(DecaidEntity, SensorEntity):
    def __init__(self, coordinator, resource, path, name, unit, device_class):
        super().__init__(coordinator, resource + "_" + path, name, resource)
        self.path = path
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        if unit:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_registry_enabled_default = resource != "cup_warmer"

    @property
    def native_value(self):
        value = value_at(self.coordinator.data.get(self.resource), self.path)
        return (
            value if isinstance(value, (str, int, float)) and not isinstance(value, bool) else None
        )
