"""Workflow controls send small deep-merge patches, never stale full recipes."""

from homeassistant.components.number import NumberEntity, NumberMode

from .entity import DecaidEntity, value_at

NUMBERS = [
    ("context.targetDoseWeight", "Dose", 0, 100, 0.1, "g"),
    ("context.targetYield", "Target yield", 0, 1000, 0.1, "g"),
    ("steamSettings.targetTemperature", "Steam target temperature", 135, 160, 1, "°C"),
    ("steamSettings.duration", "Steam duration", 0, 255, 1, "s"),
    ("steamSettings.flow", "Steam flow", 0, 3, 0.01, None),
    ("hotWaterData.targetTemperature", "Hot water temperature", 0, 100, 1, "°C"),
    ("hotWaterData.duration", "Hot water duration", 0, 255, 1, "s"),
    ("hotWaterData.volume", "Hot water volume", 0, 255, 1, "mL"),
    ("hotWaterData.flow", "Hot water flow", 0, 10, 0.1, None),
    ("rinseData.targetTemperature", "Rinse temperature", 0, 100, 1, "°C"),
    ("rinseData.duration", "Rinse duration", 0, 255, 1, "s"),
    ("rinseData.flow", "Rinse flow", 0, 10, 0.1, None),
]


async def async_setup_entry(hass, entry, async_add_entities):
    entities = [DecaidNumber(entry.runtime_data, "workflow", *item) for item in NUMBERS]
    entities.append(
        DecaidNumber(
            entry.runtime_data, "display", "brightness", "Display brightness", 0, 100, 1, "%"
        )
    )
    entities.append(
        DecaidNumber(
            entry.runtime_data, "cup_warmer", "temperature", "Cup warmer target", 0, 80, 1, "°C"
        )
    )
    async_add_entities(entities)


class DecaidNumber(DecaidEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, resource, path, name, low, high, step, unit):
        super().__init__(coordinator, "number_" + resource + "_" + path, name, resource)
        self.path = path
        self._attr_native_min_value = low
        self._attr_native_max_value = high
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_entity_registry_enabled_default = resource != "cup_warmer"

    @property
    def native_value(self):
        return value_at(self.coordinator.data.get(self.resource), self.path)

    async def async_set_native_value(self, value):
        value = int(value) if self.native_step == 1 else value
        if self.resource == "workflow":
            section, key = self.path.split(".")
            await self.command("PUT", "/api/v1/workflow", {section: {key: value}})
        elif self.resource == "display":
            await self.command("PUT", "/api/v1/display/brightness", {"brightness": value})
        else:
            # Preserve enable state: a bare temperature write enables the warmer upstream.
            await self.command(
                "PUT",
                "/api/v1/machine/cupWarmer",
                {
                    "temperature": value,
                    "enabled": self.coordinator.data["cup_warmer"]["enabled"],
                },
            )
