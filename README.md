# libglobalping-unofficial
Unofficial library for the GlobalPing API


Very much a work in progress.



To execute an HTTP(S) check:

```
from libglobalping import client

gclient = client()
response = gclient.check_http("https://github.com/HackedServer/libglobalping-unofficial")
print(response.results[0].result.statusCode)
```

To get a list of all probes:

```
from libglobalping import Probes

continent_counts = {}
for probe in Probes.generate().all:
    continent = probe.location.continent
    continent_counts[continent] = continent_counts.get(continent, 0) + 1

print(continent_counts)
```