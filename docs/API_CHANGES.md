# Decaid API review — 2026-10-04

Compared the integration's previous source `a6e2a0594c8a3cd96c58a75279d2b8a2f29a1651`
with Decaid main `a45961b323831d2170b3e7f3fef7c72fdd341642` (2026-10-01).
Checked both OpenAPI/AsyncAPI specifications and the new `GrinderHandler` routes.

| Source | REST operations | WS channel types | New relative to old catalogue |
|---|---:|---:|---|
| v0.8.7 (stable, 2026-09-29) | 153 | 14 | None |
| v0.8.8-beta.2 (2026-10-01) | 153 | 14 | None |
| main at the pinned commit | 159 | 15 | Six runtime grinder operations, one stream |

No previous operation or channel was removed. Stable/beta release changes also
include reconnect, import, device lifecycle and feedback fixes, without new routes.

## Added to integration 0.1.1

- `GET /api/v1/grinder/info`: runtime `deviceId` and `capabilities`.
- `GET /api/v1/grinder/state`: `timestamp`, `state` (`idle`, `grinding`, `error`,
  `unknown`), optional string `setting` and integer `rpm`.
- `PUT /api/v1/grinder/state/grinding`: start, requiring `startStop` capability.
- `PUT /api/v1/grinder/state/idle`: stop, requiring `startStop` capability.
- `PUT /api/v1/grinder/setting`: JSON `{"setting":"2.5"}`, requires `grindSetting`.
- `PUT /api/v1/grinder/rpm`: JSON `{"rpm":800}`, requires `rpmControl`.
- `/ws/v1/grinder/snapshot`: receive-only validated grinder snapshots.

All are exposed through existing API/subscription actions. There are no new native
HA entities in this update. These routes require an upstream build containing the
new runtime grinder API, not merely the latest stable/beta release listed above.

The REST handler returns 503 with no connected grinder (or no state snapshot),
400 for malformed setting/RPM data, and 500 for failed/unsupported commands.
The integration reports these failures and does not retry mutations. The stream
stays open and silent while disconnected; it does not emit connection events.
It must not be used alone as a reliable connection or last-known-state indicator.

## Existing endpoints: changed parameters and semantics

- App settings add nullable `preferredGrinderDeviceId`. Use the runtime device ID,
  not a persisted `grinderId`. Existing `POST /api/v1/settings` body forwarding
  already handles this; no endpoint rename is needed.
- Device inventory and plugin driver declarations add type `grinder` and grinder
  capabilities. Existing raw responses/events preserve these fields.
- Scans during protected post-wake scale recovery can be deferred/coalesced or
  dropped. Normal scans can additionally reconnect a preferred runtime grinder.
  REST `quick=true` is not a guarantee of an immediate response during deferral.
  The integration retains its 45-second request timeout and never retries the scan.
- Feedback now requires a verified Decent account. This is separate from the
  optional caller token configured in HA. The generic action reports an HTTP 400
  if account verification fails. No feedback was submitted during this review.
- Shot `enjoyment` is explicitly 0–10; the update endpoint rejects out-of-range
  values. Existing pass-through accepts the correct body; server validation applies.
- Classic DE1 `mixTemperature` during `hotWater` is not a reliable measured outlet
  temperature; `targetMixTemperature` is a requested target, not an outlet reading.
- Import error responses can include `reason: too_many_entries`. The current client
  continues to surface HTTP status only on errors; structured error bodies are not
  exposed by this update.

## Reproduction

Run `python tools/sync_api_catalog.py /path/to/decaid --ref
 a45961b323831d2170b3e7f3fef7c72fdd341642 --check` (on one line).
The generator reads git objects without modifying the upstream checkout.

Sources:
- https://github.com/decentespresso/decaid/releases
- https://github.com/decentespresso/decaid/blob/a45961b323831d2170b3e7f3fef7c72fdd341642/assets/api/rest_v1.yml
- https://github.com/decentespresso/decaid/blob/a45961b323831d2170b3e7f3fef7c72fdd341642/assets/api/websocket_v1.yml
- https://github.com/decentespresso/decaid/blob/a45961b323831d2170b3e7f3fef7c72fdd341642/lib/src/services/webserver/grinder_handler.dart
