"""Tests for the GlobalPing client using respx to mock HTTP."""

import pytest
import respx
from httpx import Response

from libglobalping import GlobalpingClient
from libglobalping.exceptions import (
    MeasurementTimeoutError,
    NoProbesFoundError,
    RateLimitExceededError,
    ValidationError,
)


@pytest.fixture
def mock_api():
    with respx.mock(base_url="https://api.globalping.io") as respx_mock:
        yield respx_mock


@pytest.fixture
async def client():
    async with GlobalpingClient() as c:
        yield c


@pytest.fixture
async def authed_client():
    async with GlobalpingClient(token="test-token-123") as c:
        yield c


# --- Ping ---


@pytest.mark.asyncio
async def test_ping(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(202, json={"id": "ping-123", "probesCount": 1})
    )
    mock_api.get("/v1/measurements/ping-123").mock(
        return_value=Response(200, json={
            "id": "ping-123",
            "type": "ping",
            "status": "finished",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:01Z",
            "target": "1.1.1.1",
            "probesCount": 1,
            "results": [{
                "probe": {
                    "continent": "EU",
                    "region": "Western Europe",
                    "country": "DE",
                    "state": None,
                    "city": "Berlin",
                    "asn": 12345,
                    "network": "Test Net",
                    "latitude": 52.52,
                    "longitude": 13.41,
                    "tags": [],
                    "resolvers": ["1.1.1.1"],
                },
                "result": {
                    "status": "finished",
                    "rawOutput": "PING 1.1.1.1...",
                    "resolvedAddress": "1.1.1.1",
                    "resolvedHostname": "one.one.one.one",
                    "timings": [{"rtt": 5.2, "ttl": 64}],
                    "stats": {
                        "min": 5.0, "max": 5.5, "avg": 5.2,
                        "total": 3, "rcv": 3, "drop": 0, "loss": 0.0,
                    },
                },
            }],
        })
    )

    result = await client.ping("1.1.1.1", packets=3)
    assert result.id == "ping-123"
    assert result.results[0].result.stats.avg == 5.2
    assert result.results[0].probe.country == "DE"


# --- DNS ---


@pytest.mark.asyncio
async def test_dns(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(202, json={"id": "dns-123", "probesCount": 1})
    )
    mock_api.get("/v1/measurements/dns-123").mock(
        return_value=Response(200, json={
            "id": "dns-123",
            "type": "dns",
            "status": "finished",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:01Z",
            "target": "example.com",
            "probesCount": 1,
            "results": [{
                "probe": {
                    "continent": "NA",
                    "region": "Northern America",
                    "country": "US",
                    "state": None,
                    "city": "New York",
                    "asn": 99999,
                    "network": "Test",
                    "latitude": 40.71,
                    "longitude": -74.01,
                    "tags": [],
                    "resolvers": ["8.8.8.8"],
                },
                "result": {
                    "status": "finished",
                    "rawOutput": ";; ANSWER SECTION...",
                    "statusCode": 0,
                    "statusCodeName": "NOERROR",
                    "resolver": "8.8.8.8",
                    "answers": [
                        {"name": "example.com.", "type": "A", "ttl": 300, "class": "IN", "value": "93.184.216.34"},
                    ],
                    "timings": {"total": 42.0},
                },
            }],
        })
    )

    result = await client.dns("example.com", query_type="A")
    assert result.results[0].result.answers[0].value == "93.184.216.34"
    assert result.results[0].result.timings.total == 42.0


# --- HTTP ---


@pytest.mark.asyncio
async def test_http(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(202, json={"id": "http-123", "probesCount": 1})
    )
    mock_api.get("/v1/measurements/http-123").mock(
        return_value=Response(200, json={
            "id": "http-123",
            "type": "http",
            "status": "finished",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:01Z",
            "target": "example.com",
            "probesCount": 1,
            "results": [{
                "probe": {
                    "continent": "EU",
                    "region": "Western Europe",
                    "country": "NL",
                    "state": None,
                    "city": "Amsterdam",
                    "asn": 11111,
                    "network": "Test",
                    "latitude": 52.37,
                    "longitude": 4.89,
                    "tags": [],
                    "resolvers": [],
                },
                "result": {
                    "status": "finished",
                    "rawOutput": "HTTP/1.1 200 OK...",
                    "resolvedAddress": "93.184.216.34",
                    "headers": {"content-type": "text/html"},
                    "rawHeaders": "Content-Type: text/html",
                    "rawBody": "<html>...</html>",
                    "truncated": False,
                    "statusCode": 200,
                    "statusCodeName": "OK",
                    "timings": {"total": 150, "download": 5, "firstByte": 100, "dns": 20, "tls": 15, "tcp": 10},
                    "tls": None,
                },
            }],
        })
    )

    result = await client.http("https://example.com/path?q=1")
    assert result.results[0].result.status_code == 200
    assert result.results[0].result.timings.total == 150


# --- MTR ---


@pytest.mark.asyncio
async def test_mtr(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(202, json={"id": "mtr-123", "probesCount": 1})
    )
    mock_api.get("/v1/measurements/mtr-123").mock(
        return_value=Response(200, json={
            "id": "mtr-123",
            "type": "mtr",
            "status": "finished",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:01Z",
            "target": "example.com",
            "probesCount": 1,
            "results": [{
                "probe": {
                    "continent": "EU",
                    "region": "Northern Europe",
                    "country": "SE",
                    "state": None,
                    "city": "Stockholm",
                    "asn": 22222,
                    "network": "Test",
                    "latitude": 59.33,
                    "longitude": 18.07,
                    "tags": [],
                    "resolvers": [],
                },
                "result": {
                    "status": "finished",
                    "rawOutput": "Host Loss%...",
                    "resolvedAddress": "93.184.216.34",
                    "resolvedHostname": "example.com",
                    "hops": [{
                        "resolvedAddress": "10.0.0.1",
                        "resolvedHostname": "gateway",
                        "asn": [12345],
                        "timings": [{"rtt": 1.5}, {"rtt": 1.6}],
                        "stats": {
                            "min": 1.5, "max": 1.6, "avg": 1.55,
                            "total": 2, "rcv": 2, "drop": 0, "loss": 0.0,
                            "stDev": 0.1, "jMin": 0.1, "jMax": 0.1, "jAvg": 0.1,
                        },
                    }],
                },
            }],
        })
    )

    result = await client.mtr("example.com")
    assert result.results[0].result.hops[0].resolved_hostname == "gateway"
    assert result.results[0].result.hops[0].stats.avg == 1.55


# --- Traceroute ---


@pytest.mark.asyncio
async def test_traceroute(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(202, json={"id": "tr-123", "probesCount": 1})
    )
    mock_api.get("/v1/measurements/tr-123").mock(
        return_value=Response(200, json={
            "id": "tr-123",
            "type": "traceroute",
            "status": "finished",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:01Z",
            "target": "example.com",
            "probesCount": 1,
            "results": [{
                "probe": {
                    "continent": "NA",
                    "region": "Northern America",
                    "country": "US",
                    "state": "CA",
                    "city": "Los Angeles",
                    "asn": 33333,
                    "network": "Test",
                    "latitude": 34.05,
                    "longitude": -118.24,
                    "tags": [],
                    "resolvers": [],
                },
                "result": {
                    "status": "finished",
                    "rawOutput": "traceroute to...",
                    "resolvedAddress": "93.184.216.34",
                    "resolvedHostname": "example.com",
                    "hops": [
                        {"resolvedAddress": "10.0.0.1", "resolvedHostname": "gw", "timings": [{"rtt": 1.0}]},
                        {"resolvedAddress": "93.184.216.34", "resolvedHostname": "example.com", "timings": [{"rtt": 25.0}]},
                    ],
                },
            }],
        })
    )

    result = await client.traceroute("example.com")
    assert len(result.results[0].result.hops) == 2
    assert result.results[0].result.hops[1].resolved_hostname == "example.com"


# --- Probes ---


@pytest.mark.asyncio
async def test_get_probes(mock_api, client):
    mock_api.get("/v1/probes").mock(
        return_value=Response(200, json=[{
            "version": "0.28.0",
            "location": {
                "continent": "EU",
                "region": "Western Europe",
                "country": "DE",
                "state": None,
                "city": "Frankfurt",
                "asn": 44444,
                "network": "AWS",
                "latitude": 50.11,
                "longitude": 8.68,
            },
            "tags": ["aws-eu-central-1", "datacenter-network"],
            "resolvers": ["1.1.1.1"],
        }])
    )

    probes = await client.get_probes()
    assert len(probes) == 1
    assert probes[0].location.country == "DE"
    assert "aws-eu-central-1" in probes[0].tags


# --- Limits ---


@pytest.mark.asyncio
async def test_get_limits(mock_api, client):
    mock_api.get("/v1/limits").mock(
        return_value=Response(200, json={
            "rateLimit": {
                "measurements": {
                    "create": {"type": "ip", "limit": 250, "remaining": 245, "reset": 3500},
                },
            },
        })
    )

    limits = await client.get_limits()
    assert limits.rate_limit.measurements.create.remaining == 245


# --- Error handling ---


@pytest.mark.asyncio
async def test_validation_error(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(400, json={
            "error": {
                "type": "validation_error",
                "message": "Parameter validation failed.",
                "params": {"target": "invalid"},
            },
        })
    )

    with pytest.raises(ValidationError) as exc_info:
        await client.ping("not valid!!!")
    assert "validation" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_no_probes_error(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(422, json={
            "error": {"type": "no_probes_found", "message": "No matching probes."},
        })
    )

    with pytest.raises(NoProbesFoundError):
        await client.ping("1.1.1.1", locations=[{"country": "XX"}])


@pytest.mark.asyncio
async def test_rate_limit_error(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(
            429,
            json={"error": {"type": "rate_limit_exceeded", "message": "Too many requests."}},
            headers={"X-RateLimit-Limit": "250", "X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "3600"},
        )
    )

    with pytest.raises(RateLimitExceededError) as exc_info:
        await client.ping("1.1.1.1")
    assert exc_info.value.remaining == 0


@pytest.mark.asyncio
async def test_timeout_error(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(202, json={"id": "stuck-123", "probesCount": 1})
    )
    mock_api.get("/v1/measurements/stuck-123").mock(
        return_value=Response(200, json={
            "id": "stuck-123",
            "type": "ping",
            "status": "in-progress",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
            "target": "1.1.1.1",
            "probesCount": 1,
            "results": [],
        })
    )

    with pytest.raises(MeasurementTimeoutError):
        await client.ping.__wrapped__(client, "1.1.1.1") if hasattr(client.ping, '__wrapped__') else None
        # Use low max_retries via internal method
        mid = await client._create_measurement({"type": "ping", "target": "1.1.1.1"})
        await client._await_measurement(mid, max_retries=2)


# --- Auth header ---


@pytest.mark.asyncio
async def test_auth_header(mock_api, authed_client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(202, json={"id": "auth-123", "probesCount": 1})
    )
    mock_api.get("/v1/measurements/auth-123").mock(
        return_value=Response(200, json={
            "id": "auth-123",
            "type": "ping",
            "status": "finished",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:01Z",
            "target": "1.1.1.1",
            "probesCount": 1,
            "results": [],
        })
    )

    await authed_client.ping("1.1.1.1")
    req = mock_api.calls[0].request
    assert req.headers["authorization"] == "Bearer test-token-123"


# --- Locations ---


@pytest.mark.asyncio
async def test_locations(mock_api, client):
    mock_api.post("/v1/measurements").mock(
        return_value=Response(202, json={"id": "loc-123", "probesCount": 2})
    )
    mock_api.get("/v1/measurements/loc-123").mock(
        return_value=Response(200, json={
            "id": "loc-123",
            "type": "ping",
            "status": "finished",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:01Z",
            "target": "1.1.1.1",
            "probesCount": 2,
            "results": [],
        })
    )

    from libglobalping.models import MeasurementLocation
    await client.ping(
        "1.1.1.1",
        locations=[
            MeasurementLocation(country="DE"),
            MeasurementLocation(magic="AWS+US"),
        ],
    )
    import json
    body = json.loads(mock_api.calls[0].request.content)
    assert body["locations"] == [{"country": "DE"}, {"magic": "AWS+US"}]
