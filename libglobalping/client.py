"""Async GlobalPing API client."""

import asyncio
from typing import Any
from urllib.parse import urlparse

import httpx

from .exceptions import (
    GlobalpingError,
    MeasurementTimeoutError,
    NoProbesFoundError,
    RateLimitExceededError,
    ValidationError,
)
from .models import (
    DNSResponse,
    HTTPResponse,
    Limits,
    MeasurementLocation,
    MTRResponse,
    PingResponse,
    Probe,
    TracerouteResponse,
)

BASE_URL = "https://api.globalping.io"
USER_AGENT = "libglobalping-unofficial/0.2.0 (https://github.com/HackedServer/libglobalping-unofficial)"


class GlobalpingClient:
    """Async client for the GlobalPing API.

    Usage:
        async with GlobalpingClient(token="...") as client:
            result = await client.ping("1.1.1.1")
    """

    def __init__(self, token: str | None = None):
        headers: dict[str, str] = {
            "User-Agent": USER_AGENT,
            "Accept-Encoding": "br, gzip",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers=headers,
            timeout=30.0,
        )

    async def __aenter__(self) -> "GlobalpingClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    # --- Internal helpers ---

    async def _handle_response(self, resp: httpx.Response) -> dict[str, Any]:
        if resp.status_code == 400:
            body = resp.json()
            err = body.get("error", {})
            raise ValidationError(
                message=err.get("message", "Bad request"),
                params=err.get("params"),
            )
        if resp.status_code == 422:
            body = resp.json()
            err = body.get("error", {})
            raise NoProbesFoundError(err.get("message", "No probes found"))
        if resp.status_code == 429:
            body = resp.json()
            err = body.get("error", {})
            limit_hdr = resp.headers.get("X-RateLimit-Limit")
            remaining_hdr = resp.headers.get("X-RateLimit-Remaining")
            reset_hdr = resp.headers.get("X-RateLimit-Reset")
            raise RateLimitExceededError(
                message=err.get("message", "Rate limit exceeded"),
                limit=int(limit_hdr) if limit_hdr is not None else None,
                remaining=int(remaining_hdr) if remaining_hdr is not None else None,
                reset=int(reset_hdr) if reset_hdr is not None else None,
            )
        if resp.status_code == 404:
            body = resp.json()
            err = body.get("error", {})
            raise GlobalpingError(err.get("message", "Not found"), error_type="not_found")
        resp.raise_for_status()
        return resp.json()

    async def _create_measurement(self, body: dict[str, Any]) -> str:
        resp = await self._client.post("/v1/measurements", json=body)
        data = await self._handle_response(resp)
        return data["id"]

    async def _await_measurement(
        self, measurement_id: str, max_retries: int = 30
    ) -> dict[str, Any]:
        url = f"/v1/measurements/{measurement_id}"
        for _ in range(max_retries):
            resp = await self._client.get(url)
            data = await self._handle_response(resp)
            if data["status"] != "in-progress":
                return data
            await asyncio.sleep(0.5)
        raise MeasurementTimeoutError(measurement_id)

    @staticmethod
    def _build_locations(
        locations: list[MeasurementLocation | dict[str, Any]] | str | None,
    ) -> list[dict[str, Any]] | str | None:
        if locations is None:
            return None
        if isinstance(locations, str):
            return locations  # measurement ID reuse
        result = []
        for loc in locations:
            if isinstance(loc, MeasurementLocation):
                result.append(loc.model_dump(exclude_none=True))
            else:
                result.append(loc)
        return result

    def _build_body(
        self,
        type_: str,
        target: str,
        *,
        locations: list[MeasurementLocation | dict[str, Any]] | str | None = None,
        limit: int | None = None,
        in_progress_updates: bool = False,
        measurement_options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"type": type_, "target": target}
        locs = self._build_locations(locations)
        if locs is not None:
            body["locations"] = locs
        if limit is not None:
            body["limit"] = limit
        if in_progress_updates:
            body["inProgressUpdates"] = True
        if measurement_options:
            body["measurementOptions"] = measurement_options
        return body

    # --- Public API ---

    async def ping(
        self,
        target: str,
        *,
        packets: int | None = None,
        protocol: str | None = None,
        port: int | None = None,
        ip_version: int | None = None,
        locations: list[MeasurementLocation | dict[str, Any]] | str | None = None,
        limit: int | None = None,
        in_progress_updates: bool = False,
    ) -> PingResponse:
        """Run a ping measurement."""
        opts: dict[str, Any] = {}
        if packets is not None:
            opts["packets"] = packets
        if protocol is not None:
            opts["protocol"] = protocol
        if port is not None:
            opts["port"] = port
        if ip_version is not None:
            opts["ipVersion"] = ip_version

        body = self._build_body(
            "ping", target,
            locations=locations, limit=limit,
            in_progress_updates=in_progress_updates,
            measurement_options=opts or None,
        )
        mid = await self._create_measurement(body)
        data = await self._await_measurement(mid)
        return PingResponse.model_validate(data)

    async def traceroute(
        self,
        target: str,
        *,
        protocol: str | None = None,
        port: int | None = None,
        ip_version: int | None = None,
        locations: list[MeasurementLocation | dict[str, Any]] | str | None = None,
        limit: int | None = None,
        in_progress_updates: bool = False,
    ) -> TracerouteResponse:
        """Run a traceroute measurement."""
        opts: dict[str, Any] = {}
        if protocol is not None:
            opts["protocol"] = protocol
        if port is not None:
            opts["port"] = port
        if ip_version is not None:
            opts["ipVersion"] = ip_version

        body = self._build_body(
            "traceroute", target,
            locations=locations, limit=limit,
            in_progress_updates=in_progress_updates,
            measurement_options=opts or None,
        )
        mid = await self._create_measurement(body)
        data = await self._await_measurement(mid)
        return TracerouteResponse.model_validate(data)

    async def dns(
        self,
        target: str,
        *,
        query_type: str | None = None,
        resolver: str | None = None,
        protocol: str | None = None,
        port: int | None = None,
        trace: bool = False,
        ip_version: int | None = None,
        locations: list[MeasurementLocation | dict[str, Any]] | str | None = None,
        limit: int | None = None,
        in_progress_updates: bool = False,
    ) -> DNSResponse:
        """Run a DNS measurement."""
        opts: dict[str, Any] = {}
        if query_type is not None:
            opts.setdefault("query", {})["type"] = query_type
        if resolver is not None:
            opts["resolver"] = resolver
        if protocol is not None:
            opts["protocol"] = protocol
        if port is not None:
            opts["port"] = port
        if trace:
            opts["trace"] = True
        if ip_version is not None:
            opts["ipVersion"] = ip_version

        body = self._build_body(
            "dns", target,
            locations=locations, limit=limit,
            in_progress_updates=in_progress_updates,
            measurement_options=opts or None,
        )
        mid = await self._create_measurement(body)
        data = await self._await_measurement(mid)
        return DNSResponse.model_validate(data)

    async def mtr(
        self,
        target: str,
        *,
        packets: int | None = None,
        protocol: str | None = None,
        port: int | None = None,
        ip_version: int | None = None,
        locations: list[MeasurementLocation | dict[str, Any]] | str | None = None,
        limit: int | None = None,
        in_progress_updates: bool = False,
    ) -> MTRResponse:
        """Run an MTR measurement."""
        opts: dict[str, Any] = {}
        if packets is not None:
            opts["packets"] = packets
        if protocol is not None:
            opts["protocol"] = protocol
        if port is not None:
            opts["port"] = port
        if ip_version is not None:
            opts["ipVersion"] = ip_version

        body = self._build_body(
            "mtr", target,
            locations=locations, limit=limit,
            in_progress_updates=in_progress_updates,
            measurement_options=opts or None,
        )
        mid = await self._create_measurement(body)
        data = await self._await_measurement(mid)
        return MTRResponse.model_validate(data)

    async def http(
        self,
        target: str,
        *,
        method: str | None = None,
        path: str | None = None,
        query: str | None = None,
        host: str | None = None,
        headers: dict[str, str] | None = None,
        resolver: str | None = None,
        protocol: str | None = None,
        port: int | None = None,
        ip_version: int | None = None,
        locations: list[MeasurementLocation | dict[str, Any]] | str | None = None,
        limit: int | None = None,
        in_progress_updates: bool = False,
    ) -> HTTPResponse:
        """Run an HTTP measurement.

        `target` can be a hostname or a full URL. If a full URL is provided,
        the protocol, host, path, query, and port are extracted automatically.
        """
        opts: dict[str, Any] = {}

        # Auto-parse full URLs
        parsed = urlparse(target)
        if parsed.scheme and parsed.hostname:
            target = parsed.hostname
            if protocol is None and parsed.scheme:
                protocol = parsed.scheme.upper()
            if path is None and parsed.path:
                path = parsed.path
            if query is None and parsed.query:
                query = "?" + parsed.query
            if port is None and parsed.port:
                port = parsed.port

        request_opts: dict[str, Any] = {}
        if method is not None:
            request_opts["method"] = method
        if path is not None:
            request_opts["path"] = path
        if query is not None:
            request_opts["query"] = query
        if host is not None:
            request_opts["host"] = host
        if headers is not None:
            request_opts["headers"] = headers
        if request_opts:
            opts["request"] = request_opts

        if resolver is not None:
            opts["resolver"] = resolver
        if protocol is not None:
            opts["protocol"] = protocol
        if port is not None:
            opts["port"] = port
        if ip_version is not None:
            opts["ipVersion"] = ip_version

        body = self._build_body(
            "http", target,
            locations=locations, limit=limit,
            in_progress_updates=in_progress_updates,
            measurement_options=opts or None,
        )
        mid = await self._create_measurement(body)
        data = await self._await_measurement(mid)
        return HTTPResponse.model_validate(data)

    async def get_probes(self) -> list[Probe]:
        """List all probes currently online."""
        resp = await self._client.get("/v1/probes")
        data = await self._handle_response(resp)
        return [Probe.model_validate(p) for p in data]

    async def get_limits(self) -> Limits:
        """Get current rate limits."""
        resp = await self._client.get("/v1/limits")
        data = await self._handle_response(resp)
        return Limits.model_validate(data)
