"""Profile selection preserving duplicate titles by stable content ID."""

from homeassistant.components.select import SelectEntity
from homeassistant.exceptions import HomeAssistantError

from .entity import DecaidEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([DecaidProfile(entry.runtime_data)])


class DecaidProfile(DecaidEntity, SelectEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator, "profile_select", "Brewing profile", "profiles")

    def _profiles(self):
        records = self.coordinator.data.get("profiles", [])
        if not isinstance(records, list):
            return {}
        return {
            f"{record['profile'].get('title', 'Profile')} [{record['id']}]": record["profile"]
            for record in records
            if isinstance(record, dict)
            and isinstance(record.get("profile"), dict)
            and "id" in record
            and record.get("visibility", "visible") == "visible"
        }

    @property
    def options(self):
        return list(self._profiles())

    @property
    def current_option(self):
        current = self.coordinator.data.get("workflow", {}).get("profile")
        return next(
            (label for label, profile in self._profiles().items() if profile == current), None
        )

    async def async_select_option(self, option):
        profile = self._profiles().get(option)
        if profile is None:
            raise HomeAssistantError("Profile is no longer available; refresh and select again")
        await self.command("PUT", "/api/v1/workflow", {"profile": profile})
