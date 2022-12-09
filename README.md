# libglobalping-unofficial
Unofficial Python library for the GlobalPing API


Very much a work in progress. As is GlobalPing.

Use at your own risk.



## To execute an HTTP(S) check:

```
from libglobalping import client

gclient = client()
response = gclient.check_http("https://github.com/HackedServer/libglobalping-unofficial")
print(f"Status Code: {r.results[0].result.statusCode}")
```

Response:
> Status Code: 200

## To execute an IPv4 Ping check:

```
from libglobalping import client

with client() as globalping:
    r = globalping.check_ping4(ip="72.82.42.42")

for result in r.results:
    print(f"Average ping from {result.probe.country}: {result.result.stats.avg}ms")
```

Response:
> Average ping from AU: 237.405ms

## To get a list of all probes:

```
from libglobalping import client

gclient = client()
continent_counts = {}
for probe in gclient.get_all_probes():
    continent = probe.location.continent
    continent_counts[continent] = continent_counts.get(continent, 0) + 1

print(continent_counts)

```

Response:

> {'EU': 275, 'NA': 156, 'OC': 15, 'AS': 85, 'SA': 18, 'AF': 5}


