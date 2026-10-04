"""Regenerate the catalogue and coverage table from a pinned Decaid git ref.

Usage: python tools/sync_api_catalog.py /path/to/decaid --ref <commit-or-tag>
Requires PyYAML (provided by the test requirements). Does not modify the checkout.
"""

import argparse
import json
import subprocess
from pathlib import Path

import yaml


def generate(upstream: Path, ref: str):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(upstream), *args], text=True)

    commit = git("rev-parse", f"{ref}^{{commit}}").strip()
    rest = yaml.safe_load(git("show", f"{commit}:assets/api/rest_v1.yml"))
    ws = yaml.safe_load(git("show", f"{commit}:assets/api/websocket_v1.yml"))
    operations = [
        {
            "method": method.upper(),
            "path": path,
            "summary": op.get("summary", ""),
            "request_types": list(op.get("requestBody", {}).get("content", {})),
        }
        for path, item in rest["paths"].items()
        for method, op in item.items()
        if method in ("get", "post", "put", "patch", "delete")
    ]
    channels = [channel["address"] for channel in ws["channels"].values()]
    catalog = {"source_commit": commit, "operations": operations, "channels": channels}
    doc = (
        f"# API coverage\n\nSource: decentespresso/decaid at `{commit}`.\n\n"
        f"{len(operations) - 1} of {len(operations)} REST operations are addressable through "
        "`decaid.api_request`. `POST /api/v1/derek/answers/stream` is unsupported (SSE). "
        "This is transport coverage, not a separate HA entity for every parameter. "
        "Bodies pass through to server validation; binary bodies/responses use base64. "
        "The 45-second timeout and 8 MiB response limit still apply.\n\n"
        "Runtime grinder routes and its WebSocket require a Decaid build containing the "
        "grinder API; they are absent from v0.8.7 and v0.8.8-beta.2. "
        "See [API changes](API_CHANGES.md).\n\n"
        "| Method | Path | Operation | Request types |\n|---|---|---|---|\n"
    )
    for op in operations:
        doc += f"| {op['method']} | `{op['path']}` | {op['summary']} | {', '.join(op['request_types'])} |\n"
    doc += (
        "\n## WebSockets\n\nEvery channel can be subscribed to with `decaid.subscribe`; "
        "additional subscriptions emit `decaid_message`. Core-stream events are opt-in. "
        "Only bidirectional channels accept `decaid.websocket_send`. "
        "The grinder snapshot stream is receive-only. "
        "Resolve parameterized paths before calling.\n\n"
    )
    doc += "".join(f"- `/{channel}`\n" for channel in channels)
    return catalog, doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream", type=Path)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    catalog, doc = generate(args.upstream, args.ref)
    root = Path(__file__).resolve().parents[1]
    outputs = {
        root / "custom_components/decaid/catalog.json": json.dumps(catalog, indent=2) + "\n",
        root / "docs/API_COVERAGE.md": doc,
    }
    for path, content in outputs.items():
        if args.check:
            if path.read_text() != content:
                raise SystemExit(f"Out of date: {path.relative_to(root)}")
        else:
            path.write_text(content)
    print(
        f"{len(catalog['operations'])} REST operations, {len(catalog['channels'])} channels; "
        f"source {catalog['source_commit']}"
    )


if __name__ == "__main__":
    main()
