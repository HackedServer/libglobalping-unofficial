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

## To execute an MTR check and pretty print the results:

```
from libglobalping import client

target = "api.globalping.io"
with client() as globalping:
    r = globalping.check_mtr(target=target)
    
for result in r.results:
    print(f"MTR Results to {target} from {result.probe.region}")
    result.pretty_print(print_text=True)
```

Response:

```
MTR Results to api.globalping.io from Northern Europe
50.7.112.1                                                        1.132ms   - 1.662ms   - 0.954ms   
be4660.ccr42.lon13.atlas.cogentco.com                             0.992ms   - 0.991ms   - 0.929ms   
be12488.ccr42.ams03.atlas.cogentco.com                            8.147ms   - 8.317ms   - 8.08ms    
be2814.ccr42.fra03.atlas.cogentco.com                             127.72ms  - 14.799ms  - 14.709ms  
be2960.ccr22.muc03.atlas.cogentco.com                             20.178ms  - 20.19ms   - 20.111ms  
be2996.rcr21.nue01.atlas.cogentco.com                             22.008ms  - 21.705ms  - 21.995ms  
be3161.nr71.b040138-0.nue01.atlas.cogentco.com                    22.718ms  - 22.545ms  - 22.444ms  
149.6.158.186                                                     21.843ms  - 21.826ms  - 21.825ms  
core24.fsn1.hetzner.com                                           24.058ms  - 24.261ms  - 24.108ms  
spine3.cloud2.fsn1.hetzner.com                                    24.736ms  - 24.659ms  - 24.774ms  
UNKNOWN                                                               *     -     *     -     *     
static.25.98.69.159.clients.your-server.de                        24.15ms   - 24.139ms  - 24.193ms  
api.globalping.io                                                 24.011ms  - 24.054ms  - 24.22ms   
api.globalping.io                                                 24.124ms  
```

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


