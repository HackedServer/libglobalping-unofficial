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

## To execute a DNS query check:

```
target = "globalping.io"
query_type = "NS"
with client() as globalping:
    r = globalping.check_dns(target=target, query_type=query_type)

for result in r.results:
    print(
        "Answer for {} type {} in {}ms using resolver {}:".format(
            target, query_type, result.result.timings.total, result.result.resolver
        )
    )

    for answer in result.result.answers:
        print(f"Name: {answer.name}  Type: {answer.type}  TTL: {answer.ttl}  Value: {answer.value}")
```

Response:

```
Answer for globalping.io type NS in 452ms using resolver 1.1.1.1:
Name: globalping.io.  Type: NS  TTL: 3600  Value: hydrogen.ns.hetzner.com.
Name: globalping.io.  Type: NS  TTL: 3600  Value: oxygen.ns.hetzner.com.
Name: globalping.io.  Type: NS  TTL: 3600  Value: helium.ns.hetzner.de.
```

## To execute a traceroute:

```
target = "api.globalping.io"
hop_count = 0

with client() as globalping:
    r = globalping.check_traceroute(target=target)

for result in r.results:
    print(f"Traceroute to {target} from {result.probe.region}")
    for hop in result.result.hops:
        hostname = hop.resolvedHostname if hop.resolvedHostname else hop.resolvedAddress if hop.resolvedAddress else "UNKNOWN"
        print(f"{str(hop_count).ljust(2)} {hostname}")
        hop_count += 1
```

Response:

```
Traceroute to api.globalping.io from Southern Europe
0  vrrp.gcore.lu
1  10.255.32.225
2  10.255.32.161
3  hu0-1-0-3.rcr51.b050634-1.mad05.atlas.cogentco.com
4  be3618.ccr31.mad05.atlas.cogentco.com
5  be2324.ccr31.bio02.atlas.cogentco.com
6  be2315.ccr41.par01.atlas.cogentco.com
7  be2799.ccr41.fra03.atlas.cogentco.com
8  be2959.ccr21.muc03.atlas.cogentco.com
9  be2995.rcr21.nue01.atlas.cogentco.com
10 be3161.nr71.b040138-0.nue01.atlas.cogentco.com
11 149.6.158.186
12 core24.fsn1.hetzner.com
13 spine2.cloud2.fsn1.hetzner.com
14 UNKNOWN
15 static.25.98.69.159.clients.your-server.de
16 api.globalping.io
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


