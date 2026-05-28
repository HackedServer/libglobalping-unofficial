# libglobalping-unofficial

Unofficial Python library for the [GlobalPing API](https://www.globalping.io/).

Async-first, built on `httpx` and `pydantic`.

## Installation

```
pip install git+https://github.com/HackedServer/libglobalping-unofficial.git
```

## Quick Start

```python
import asyncio
from libglobalping import GlobalpingClient

async def main():
    async with GlobalpingClient() as gp:
        result = await gp.ping("1.1.1.1")
        print(f"Avg: {result.results[0].result.stats.avg}ms")

asyncio.run(main())
```

## Authentication

Pass a token from the [Globalping Dashboard](https://dash.globalping.io/tokens) for higher rate limits:

```python
async with GlobalpingClient(token="your-token") as gp:
    ...
```

## Examples

### Ping

```python
async with GlobalpingClient() as gp:
    r = await gp.ping("1.1.1.1", packets=5, limit=3)
    for item in r.results:
        print(f"Avg from {item.probe.country}: {item.result.stats.avg}ms")
```

### HTTP

```python
async with GlobalpingClient() as gp:
    r = await gp.http("https://example.com/path")
    print(f"Status: {r.results[0].result.status_code}")
    print(f"TLS: {r.results[0].result.tls}")
```

### DNS

```python
async with GlobalpingClient() as gp:
    r = await gp.dns("globalping.io", query_type="NS")
    for item in r.results:
        for answer in item.result.answers:
            print(f"{answer.name} -> {answer.value}")
```

### DNS with trace

```python
async with GlobalpingClient() as gp:
    r = await gp.dns("example.com", trace=True)
    for item in r.results:
        for hop in item.result.hops:
            print(f"Resolver: {hop.resolver}, answers: {len(hop.answers)}")
```

### MTR

```python
async with GlobalpingClient() as gp:
    r = await gp.mtr("api.globalping.io", limit=2)
    for item in r.results:
        print(f"MTR from {item.probe.city}")
        item.pretty_print()
```

### Traceroute

```python
async with GlobalpingClient() as gp:
    r = await gp.traceroute("api.globalping.io")
    for item in r.results:
        for hop in item.result.hops:
            print(hop.resolved_hostname or hop.resolved_address or "*")
```

### Location filtering

Use `MeasurementLocation` or plain dicts to target specific probes:

```python
from libglobalping import GlobalpingClient
from libglobalping.models import MeasurementLocation

async with GlobalpingClient() as gp:
    r = await gp.ping(
        "1.1.1.1",
        locations=[
            MeasurementLocation(country="DE"),
            MeasurementLocation(country="US", state="CA"),
            MeasurementLocation(magic="AWS+Europe"),
        ],
    )
```

Or use a previous measurement ID to reuse the same probes:

```python
r2 = await gp.traceroute("1.1.1.1", locations=r.id)
```

### Probes

```python
async with GlobalpingClient() as gp:
    probes = await gp.get_probes()
    by_continent = {}
    for p in probes:
        c = p.location.continent
        by_continent[c] = by_continent.get(c, 0) + 1
    print(by_continent)
```

### Rate limits

```python
async with GlobalpingClient(token="your-token") as gp:
    limits = await gp.get_limits()
    print(f"Remaining: {limits.rate_limit.measurements.create.remaining}")
    if limits.credits:
        print(f"Credits: {limits.credits.remaining}")
```

## Error Handling

```python
from libglobalping.exceptions import (
    RateLimitExceededError,
    NoProbesFoundError,
    ValidationError,
    MeasurementTimeoutError,
)

try:
    r = await gp.ping("1.1.1.1")
except RateLimitExceededError as e:
    print(f"Rate limited. Resets in {e.reset}s")
except NoProbesFoundError:
    print("No probes available for that location")
except ValidationError as e:
    print(f"Bad request: {e}")
except MeasurementTimeoutError as e:
    print(f"Measurement {e.measurement_id} timed out")
```

## API Coverage

| Feature | Supported |
|---------|-----------|
| Ping (ICMP/TCP) | ✅ |
| Traceroute (ICMP/TCP/UDP) | ✅ |
| MTR (ICMP/TCP/UDP) | ✅ |
| DNS (A, AAAA, NS, MX, etc.) | ✅ |
| DNS trace mode | ✅ |
| HTTP (HEAD/GET/OPTIONS) | ✅ |
| Location filtering | ✅ |
| Magic location strings | ✅ |
| Probe reuse via measurement ID | ✅ |
| Authentication (Bearer token) | ✅ |
| Rate limit checking | ✅ |
| IPv6 (experimental) | ✅ |
| In-progress updates | ✅ |
| Typed error handling | ✅ |
| List online probes | ✅ |
