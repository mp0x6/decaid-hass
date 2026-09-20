# Validation

Validated in Python 3.13.15 with Home Assistant 2025.12.5.

- 22 pytest cases passed.
- Ruff check passed.
- Actual HA integration loader, config entry setup, six entity platforms,
  service registration, workflow mutation, response data, duplicate configuration,
  stream disconnect/unavailability/reconnection, additional subscribe/unsubscribe,
  and config entry unload exercised against an in-process HTTP/WebSocket server.
- HA's shared HTTP-session factory is replaced in the integration test by a standard
  aiohttp ClientSession to avoid requiring host network discovery. The actual
  integration modules and HA entity/service machinery are used.
- Transport tests cover catalogue route matching, URL normalization, path restrictions,
  JSON/query/text/binary/empty bodies and responses, HTTP/authentication errors,
  no automatic mutation retries, redirects, response size limit, malformed JSON,
  unreachable host, WebSocket bidirectional transport and ambiguous body rejection.

One upstream aiohttp subclass deprecation warning occurs during HA import.
No real espresso machine, Decaid executable, cloud account or firmware update was
used in validation. Route-count tests verify catalogue accessibility, not the
functional semantics of all 152 supported server operations. Current releases newer
than the tested HA version have not been independently validated.
