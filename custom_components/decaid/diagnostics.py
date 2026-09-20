"""Minimal diagnostics: no tokens, hostnames, coffee metadata or raw frames."""


async def async_get_config_entry_diagnostics(hass, entry):
    coordinator = entry.runtime_data
    return {
        "source_commit": coordinator.client.catalog["source_commit"],
        "rest_operation_count": len(coordinator.client.catalog["operations"]),
        "last_update_success": coordinator.last_update_success,
        "resources": sorted(coordinator.cache),
        "connected_stream_count": len(coordinator.online),
        "options": dict(entry.options),
    }
