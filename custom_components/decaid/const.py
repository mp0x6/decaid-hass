"""Integration constants."""

DOMAIN = "decaid"
PLATFORMS = ["sensor", "binary_sensor", "button", "number", "switch", "select"]
DEFAULT_CHANNELS = {
    "machine": "/ws/v1/machine/snapshot",
    "scale": "/ws/v1/scale/snapshot",
    "water": "/ws/v1/machine/waterLevels",
    "shot_settings": "/ws/v1/machine/shotSettings",
    "shot": "/ws/v1/machine/shotState",
    "display": "/ws/v1/display",
    "devices_stream": "/ws/v1/devices",
}
POLL_PATHS = {
    "workflow": "/api/v1/workflow",
    "profiles": "/api/v1/profiles",
    "display": "/api/v1/display",
    "settings": "/api/v1/machine/settings",
    "cup_warmer": "/api/v1/machine/cupWarmer",
}
