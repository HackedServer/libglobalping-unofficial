from libglobalping import client, Probes

gclient = client()
r = gclient.check_http("https://github.com/HackedServer/libglobalping-unofficial")
print(r.results[0].result.statusCode)

continent_counts = {}
for probe in Probes.generate().all:
    continent = probe.location.continent
    continent_counts[continent] = continent_counts.get(continent, 0) + 1

print(continent_counts)
