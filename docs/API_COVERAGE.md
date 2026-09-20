# API coverage

Source: decentespresso/decaid at `a6e2a0594c8a3cd96c58a75279d2b8a2f29a1651`.

152 of the 153 listed REST operations are reachable through `decaid.api_request`; `POST /api/v1/derek/answers/stream` is explicitly unsupported (SSE). Bodies are passed through; server validation applies. Binary bodies and responses use base64. Streaming HTTP responses are intentionally unsupported.

| Method | Path | Operation | Request types |
|---|---|---|---|
| GET | `/api/v1/devices` | Get Available Devices |  |
| PUT | `/api/v1/devices/forget` | Forget a remembered device | application/json |
| GET | `/api/v1/devices/scan` | Scan for Devices |  |
| PUT | `/api/v1/devices/connect` | Connect to specified device | application/json |
| PUT | `/api/v1/devices/disconnect` | Disconnect a specified device | application/json |
| GET | `/api/v1/devices/wifi` | List manually-added WiFi scale endpoints |  |
| POST | `/api/v1/devices/wifi` | Add a manual WiFi scale endpoint | application/json |
| DELETE | `/api/v1/devices/wifi` | Remove a manual WiFi scale endpoint | application/json |
| GET | `/api/v1/machine/info` | Retrieves the current Machine information |  |
| GET | `/api/v1/machine/state` | Get Machine State |  |
| PUT | `/api/v1/machine/state/{newState}` | Request Machine State Change |  |
| POST | `/api/v1/machine/profile` | Set Machine Profile | application/json |
| POST | `/api/v1/machine/shotSettings` | Update Shot Settings | application/json |
| GET | `/api/v1/machine/capabilities` | List machine capabilities |  |
| GET | `/api/v1/machine/cupWarmer` | Get cup-warmer state |  |
| PUT | `/api/v1/machine/cupWarmer` | Set cup-warmer setpoint and/or manual enable | application/json |
| GET | `/api/v1/machine/cupWarmer/preheat` | Get scheduled pre-warm state |  |
| PUT | `/api/v1/machine/cupWarmer/preheat` | Set scheduled pre-warm configuration | application/json |
| GET | `/api/v1/machine/ledStrip` | Get LED strip configuration |  |
| PUT | `/api/v1/machine/ledStrip` | Set LED strip configuration | application/json |
| POST | `/api/v1/machine/ledStrip/commit` | Commit LED strip config to NVM (compatibility no-op) | application/json |
| POST | `/api/v1/machine/ledStrip/reset` | Reload LED strip config from the firmware | application/json |
| GET | `/api/v1/machine/scaleCalibration` | Get scale-calibration state |  |
| PUT | `/api/v1/machine/scaleCalibration` | Start a scale-calibration step | application/json |
| GET | `/api/v1/machine/settings` | Get machine settings |  |
| POST | `/api/v1/machine/settings` | Set machine settings | application/json |
| GET | `/api/v1/machine/settings/advanced` | Get advanced machine settings |  |
| POST | `/api/v1/machine/settings/advanced` | Set advanced machine settings | application/json |
| DELETE | `/api/v1/machine/settings/reset` | Reset machine settings to defaults |  |
| GET | `/api/v1/machine/calibration` | Get machine calibration settings |  |
| POST | `/api/v1/machine/calibration` | Set machine calibration settings | application/json |
| GET | `/api/v1/machine/calibration/{target}` | Read DE1 sensor calibration |  |
| PUT | `/api/v1/machine/calibration/{target}` | Write DE1 sensor calibration | application/json |
| POST | `/api/v1/machine/waterLevels` | Set water level refill threshold. Only the refillLevel field is used. | application/json |
| GET | `/api/v1/machine/firmware` | Get firmware catalog and update availability |  |
| POST | `/api/v1/machine/firmware` | Push raw firmware to the machine (developer/recovery) | application/octet-stream |
| DELETE | `/api/v1/machine/firmware` | Cancel an in-progress firmware update |  |
| POST | `/api/v1/machine/firmware/apply` | Apply a managed firmware artifact | application/json |
| GET | `/api/v1/scale/info` | Get connected scale information |  |
| PUT | `/api/v1/scale/tare` | Tare Scale |  |
| PUT | `/api/v1/scales/{id}/tare` | Tare a connected scale by device id |  |
| PUT | `/api/v1/scale/timer/start` | Start Scale Timer |  |
| PUT | `/api/v1/scale/timer/stop` | Stop Scale Timer |  |
| PUT | `/api/v1/scale/timer/reset` | Reset Scale Timer |  |
| GET | `/api/v1/sensors` | Get a list of sensor devices connected to Decent |  |
| GET | `/api/v1/sensors/{id}` | Get full manifest for a sensor |  |
| POST | `/api/v1/sensors/{id}/execute` | Execute a sensor command | application/json |
| GET | `/api/v1/settings` | Get Decent settings |  |
| POST | `/api/v1/settings` | Update Decent settings | application/json |
| GET | `/api/v1/workflow` | Get current workflow |  |
| PUT | `/api/v1/workflow` | Update current workflow | application/json |
| GET | `/api/v1/shots` | List shots (paginated and filtered) |  |
| GET | `/api/v1/shots/ids` | Get a list of identifiers of all the shots |  |
| GET | `/api/v1/shots/latest` | Get the latest shot metadata |  |
| GET | `/api/v1/shots/{id}` | Get a specific shot by ID |  |
| PUT | `/api/v1/shots/{id}` | Update a shot record | application/json |
| DELETE | `/api/v1/shots/{id}` | Delete a shot record |  |
| GET | `/api/v1/steams` | List all steam records |  |
| GET | `/api/v1/steams/ids` | List steam record IDs |  |
| GET | `/api/v1/steams/latest` | Get the most recent steam record (metadata only) |  |
| GET | `/api/v1/steams/{id}` | Get a specific steam record by ID |  |
| PUT | `/api/v1/steams/{id}` | Update a steam record's annotations | application/json |
| DELETE | `/api/v1/steams/{id}` | Delete a steam record |  |
| GET | `/api/v1/beans` | List all beans |  |
| POST | `/api/v1/beans` | Create a new bean | application/json |
| GET | `/api/v1/beans/{id}` | Get bean by ID |  |
| PUT | `/api/v1/beans/{id}` | Update a bean | application/json |
| DELETE | `/api/v1/beans/{id}` | Delete a bean |  |
| GET | `/api/v1/beans/{beanId}/batches` | List batches for a bean |  |
| POST | `/api/v1/beans/{beanId}/batches` | Create a new batch for a bean | application/json |
| GET | `/api/v1/bean-batches` | List all bean batches |  |
| GET | `/api/v1/bean-batches/{id}` | Get a batch by ID |  |
| PUT | `/api/v1/bean-batches/{id}` | Update a batch | application/json |
| DELETE | `/api/v1/bean-batches/{id}` | Delete a batch |  |
| GET | `/api/v1/grinders` | List all grinders |  |
| POST | `/api/v1/grinders` | Create a new grinder | application/json |
| GET | `/api/v1/grinders/{id}` | Get grinder by ID |  |
| PUT | `/api/v1/grinders/{id}` | Update a grinder | application/json |
| DELETE | `/api/v1/grinders/{id}` | Delete a grinder |  |
| GET | `/api/v1/store/{namespace}` | List keys in a namespace, or read the whole namespace with `?full=1` |  |
| GET | `/api/v1/store/{namespace}/{key}` | Get value for a key |  |
| POST | `/api/v1/store/{namespace}/{key}` | Set value for a key | application/json |
| DELETE | `/api/v1/store/{namespace}/{key}` | Delete key |  |
| GET | `/api/v1/plugins` | List all plugins |  |
| GET | `/api/v1/plugins/{id}/settings` | Fetch settings for specific plugin |  |
| POST | `/api/v1/plugins/{id}/settings` | Save settings for specific plugin | application/json |
| POST | `/api/v1/plugins/{id}/enable` | Enable a plugin |  |
| POST | `/api/v1/plugins/{id}/disable` | Disable a plugin |  |
| PUT | `/api/v1/plugins/{id}/source` | Create or overwrite a plugin's manifest and source | application/json |
| DELETE | `/api/v1/plugins/{id}` | Delete a plugin |  |
| GET | `/api/v1/plugins/{id}/{endpoint}` | Call a plugin HTTP endpoint |  |
| POST | `/api/v1/plugins/install` | Install a plugin from URL (not supported) | application/json |
| POST | `/api/v1/plugins/install/github-release` | Install a plugin from a GitHub release | application/json |
| POST | `/api/v1/plugins/install/github-branch` | Install a plugin from a GitHub branch | application/json |
| POST | `/api/v1/plugins/update` | Check every GitHub-backed plugin for updates |  |
| POST | `/api/v1/plugins/{id}/update/approve` | Approve and install a permission-escalating update |  |
| GET | `/api/v1/profiles` | Get all profiles |  |
| POST | `/api/v1/profiles` | Create new profile | application/json |
| GET | `/api/v1/profiles/{id}` | Get profile by ID |  |
| PUT | `/api/v1/profiles/{id}` | Update profile | application/json |
| DELETE | `/api/v1/profiles/{id}` | Delete profile |  |
| PUT | `/api/v1/profiles/{id}/visibility` | Change profile visibility | application/json |
| GET | `/api/v1/profiles/{id}/lineage` | Get profile lineage |  |
| DELETE | `/api/v1/profiles/{id}/purge` | Permanently delete profile |  |
| POST | `/api/v1/profiles/import` | Import profiles | application/json |
| GET | `/api/v1/profiles/export` | Export profiles |  |
| POST | `/api/v1/profiles/restore/{filename}` | Restore default profile |  |
| GET | `/api/v1/profiles/defaults` | List bundled default profiles |  |
| GET | `/api/v1/webui/skins` | List all installed WebUI skins |  |
| GET | `/api/v1/webui/skins/{id}` | Get specific WebUI skin details |  |
| DELETE | `/api/v1/webui/skins/{id}` | Remove/uninstall a WebUI skin |  |
| GET | `/api/v1/webui/skins/default` | Get the default WebUI skin |  |
| PUT | `/api/v1/webui/skins/default` | Set the default WebUI skin | application/json |
| POST | `/api/v1/webui/skins/install/github-release` | Install skin from GitHub Release | application/json |
| POST | `/api/v1/webui/skins/install/github-branch` | Install skin from GitHub branch | application/json |
| POST | `/api/v1/webui/skins/install/url` | Install skin from URL | application/json |
| POST | `/api/v1/webui/skins/update` | Check for skin updates |  |
| GET | `/api/v1/webui/server/status` | Get WebUI server status |  |
| POST | `/api/v1/webui/server/start` | Start the WebUI server |  |
| POST | `/api/v1/webui/server/stop` | Stop the WebUI server |  |
| GET | `/api/v1/webui/skin-assets/{id}/{filepath}` | Fetch an asset from an installed skin |  |
| POST | `/api/v1/machine/heartbeat` | Signal user presence |  |
| GET | `/api/v1/presence/settings` | Get presence and wake schedule settings |  |
| POST | `/api/v1/presence/settings` | Update presence settings | application/json |
| GET | `/api/v1/presence/schedules` | Get all wake schedules |  |
| POST | `/api/v1/presence/schedules` | Add a new wake schedule | application/json |
| PUT | `/api/v1/presence/schedules/{id}` | Update a wake schedule | application/json |
| DELETE | `/api/v1/presence/schedules/{id}` | Delete a wake schedule |  |
| GET | `/api/v1/display` | Get current display state |  |
| PUT | `/api/v1/display/brightness` | Set screen brightness | application/json |
| POST | `/api/v1/display/wakelock` | Request wake-lock override |  |
| DELETE | `/api/v1/display/wakelock` | Release wake-lock override |  |
| GET | `/api/v1/data/export` | Export all app data |  |
| POST | `/api/v1/data/import` | Import app data from archive | application/zip |
| POST | `/api/v1/data/sync` | Sync data between Decaid instances | application/json |
| GET | `/api/v1/info` | Get build information |  |
| GET | `/api/v1/diagnostics/ble` | Read-only BLE reconnect diagnostics |  |
| GET | `/api/v1/update` | Get app update state |  |
| GET | `/api/v1/logs` | Get recent log entries |  |
| GET | `/api/v1/webview/logs` | Get WebView console logs |  |
| GET | `/api/v1/debug/flow-smoothing` | Get runtime display-flow smoothing (debug builds only) |  |
| POST | `/api/v1/debug/flow-smoothing` | Set runtime display-flow smoothing (debug builds only) | application/json |
| POST | `/api/v1/debug/scale/{command}` | Control mock scale (simulate mode only) |  |
| POST | `/api/v1/debug/machine/{command}` | Control mock machine (simulate mode only) |  |
| GET | `/api/v1/debug/replay/shots` | List replay recordings and current selection (simulate=replay only) |  |
| POST | `/api/v1/debug/replay/shot/{id}` | Force a replay recording for subsequent pulls (simulate=replay only) |  |
| DELETE | `/api/v1/debug/replay/shot` | Clear the forced replay recording (simulate=replay only) |  |
| POST | `/api/v1/feedback` | Submit feedback | application/json |
| GET | `/api/v1/account/decent` | Decent account auth status |  |
| GET | `/api/v1/account/proxy/support/api/{endpoint}` | Auth-enriching proxy to the Decent backend |  |
| POST | `/api/v1/account/proxy/support/api/{endpoint}` | Auth-enriching write proxy to the Decent backend | application/octet-stream |
| PUT | `/api/v1/account/proxy/support/api/{endpoint}` | Auth-enriching write proxy to the Decent backend | application/octet-stream |
| POST | `/api/v1/derek/answers/stream` | Relay to the Derek RAG assistant (streaming) | application/json |

## WebSockets

Every channel can be subscribed to with `decaid.subscribe`; incoming frames produce `decaid_message` events. Bidirectional commands use `decaid.websocket_send`. Parameterized paths must be resolved by the caller.

- `/ws/v1/machine/snapshot`
- `/ws/v1/machine/shotSettings`
- `/ws/v1/machine/waterLevels`
- `/ws/v1/scale/snapshot`
- `/ws/v1/scales/{id}/snapshot`
- `/ws/v1/machine/raw`
- `/ws/v1/machine/shotState`
- `/ws/v1/sensors/{id}/snapshot`
- `/ws/v1/plugins/{id}/{endpoint}`
- `/ws/v1/logs`
- `/ws/v1/webview/logs`
- `/ws/v1/devices`
- `/ws/v1/display`
- `/ws/v1/update`
