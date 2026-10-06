"""Minimal MCP (stdio, JSON-RPC 2.0) server that lets Claude drive a running MusicSync backend.

Only use it with content you are entitled to download. Stdlib only on purpose: no extra
dependency to audit. Run with: python -m musicsync.mcp_server
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Any

API = os.environ.get("MUSICSYNC_API", "http://127.0.0.1:8000").rstrip("/") + "/api/v1"
PROTOCOL_VERSION = "2025-06-18"


def call_api(method: str, path: str, body: Any = None, timeout: int = 300) -> Any:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        API + path, data=data, method=method, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode(errors='replace')}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"MusicSync backend is not reachable at {API} ({exc.reason}). "
            "Start it with: cd backend; uv run uvicorn musicsync.main:app --port 8000"
        ) from exc


def _device(device_id: str | None) -> str:
    devices = call_api("GET", "/storage/devices")
    if device_id:
        return device_id
    if len(devices) == 1:
        return str(devices[0]["id"])
    raise RuntimeError(
        "device_id is required; available devices: "
        + json.dumps([{k: d[k] for k in ("id", "volume_label", "mount_point")} for d in devices])
    )


def search_music(query: str, source: str = "youtube", limit: int = 5) -> Any:
    params = urllib.parse.urlencode({"q": query, "source": source, "limit": limit})
    return call_api("GET", f"/search?{params}")


def analyze_url(url: str) -> Any:
    return call_api("POST", "/downloads/analyze", {"url": url})


def list_devices() -> Any:
    return call_api("GET", "/storage/devices")


def start_sync(url: str, device_id: str | None = None, track_ids: list[str] | None = None) -> Any:
    body = {"url": url, "destination_device_id": _device(device_id), "track_ids": track_ids}
    return call_api("POST", "/downloads", body)


def queue_songs(queries: list[str], source: str = "youtube", device_id: str | None = None) -> Any:
    """Search each 'Artist - Title' query, take the top hit and start its sync."""
    device = _device(device_id)
    results: list[dict[str, Any]] = []
    for query in queries:
        try:
            hits = search_music(query, source, 1)
            if not hits:
                results.append({"query": query, "error": "no results"})
                continue
            job = call_api(
                "POST",
                "/downloads",
                {"url": hits[0]["url"], "destination_device_id": device, "track_ids": None},
            )
            results.append(
                {"query": query, "match": hits[0], "job_id": job["id"], "status": job["status"]}
            )
        except RuntimeError as exc:
            results.append({"query": query, "error": str(exc)})
    return results


def job_status(job_id: str) -> Any:
    return call_api("GET", f"/downloads/{urllib.parse.quote(job_id)}")


def list_jobs() -> Any:
    return call_api("GET", "/downloads/history")


def cancel_job(job_id: str) -> Any:
    return call_api("POST", f"/downloads/{urllib.parse.quote(job_id)}/cancel")


def _schema(properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": required}


_STR = {"type": "string"}
_SOURCE = {"type": "string", "enum": ["youtube", "spotify"], "default": "youtube"}
_DEVICE = {"type": "string", "description": "Optional when exactly one device is connected."}

TOOLS: dict[str, tuple[str, dict[str, Any], Callable[..., Any]]] = {
    "search_music": (
        "Find song URLs from free text ('Artist - Title') on YouTube or Spotify.",
        _schema(
            {"query": _STR, "source": _SOURCE, "limit": {"type": "integer", "default": 5}},
            ["query"],
        ),
        search_music,
    ),
    "analyze_url": (
        "List the tracks behind a YouTube/Spotify URL (video, playlist, album).",
        _schema({"url": _STR}, ["url"]),
        analyze_url,
    ),
    "list_devices": (
        "List connected destination drives (USB) with free space.",
        _schema({}, []),
        list_devices,
    ),
    "start_sync": (
        "Download a URL and place the MP3s on a device. Returns a job; poll job_status.",
        _schema(
            {"url": _STR, "device_id": _DEVICE, "track_ids": {"type": "array", "items": _STR}},
            ["url"],
        ),
        start_sync,
    ),
    "queue_songs": (
        "Batch: for each 'Artist - Title' query, search, take the top result and start its sync.",
        _schema(
            {
                "queries": {"type": "array", "items": _STR},
                "source": _SOURCE,
                "device_id": _DEVICE,
            },
            ["queries"],
        ),
        queue_songs,
    ),
    "job_status": (
        "Status and per-track progress of a sync job.",
        _schema({"job_id": _STR}, ["job_id"]),
        job_status,
    ),
    "list_jobs": ("All sync jobs, newest first.", _schema({}, []), list_jobs),
    "cancel_job": (
        "Cancel a queued or running sync job.",
        _schema({"job_id": _STR}, ["job_id"]),
        cancel_job,
    ),
}


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method, request_id = message.get("method"), message.get("id")
    if request_id is None:
        return None  # notifications (e.g. notifications/initialized) get no reply
    try:
        if method == "initialize":
            requested = (message.get("params") or {}).get("protocolVersion")
            result: dict[str, Any] = {
                "protocolVersion": requested or PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "musicsync", "version": "0.1.0"},
            }
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {
                "tools": [
                    {"name": name, "description": description, "inputSchema": schema}
                    for name, (description, schema, _) in TOOLS.items()
                ]
            }
        elif method == "tools/call":
            result = _call_tool(message.get("params") or {})
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
    except Exception as exc:  # protocol errors must never kill the stdio loop
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(exc)}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _call_tool(params: dict[str, Any]) -> dict[str, Any]:
    entry = TOOLS.get(str(params.get("name")))
    if entry is None:
        return {"content": [{"type": "text", "text": "Unknown tool"}], "isError": True}
    try:
        output = entry[2](**(params.get("arguments") or {}))
        return {"content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}]}
    except (RuntimeError, TypeError, ValueError) as exc:
        return {"content": [{"type": "text", "text": str(exc)}], "isError": True}


def main() -> None:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            reply = handle(json.loads(line))
        except json.JSONDecodeError:
            reply = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
        if reply is not None:
            sys.stdout.write(json.dumps(reply) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
