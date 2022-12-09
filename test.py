from libglobalping import client

"""
gclient = client()
r = gclient.check_http("https://github.com/HackedServer/libglobalping-unofficial")
print(f"Status Code: {r.results[0].result.statusCode}")

continent_counts = {}
for probe in gclient.get_all_probes():
    continent = probe.location.continent
    continent_counts[continent] = continent_counts.get(continent, 0) + 1
print(continent_counts)

with client() as gclient2:
    r = gclient2.check_http("https://github.com/HackedServer/libglobalping-unofficial")
    print(f"Status Code: {r.results[0].result.statusCode}")
"""

with client() as globalping:
    r = globalping.check_ping4(ip="72.82.42.42")

for result in r.results:
    print(f"Average ping from {result.probe.country}: {result.result.stats.avg}ms")
