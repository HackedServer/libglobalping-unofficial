from libglobalping import client

gclient = client()
r = gclient.check_http("https://github.com/HackedServer/libglobalping-unofficial")
print(f"Status Code: {r.results[0].result.statusCode}")

continent_counts = {}
for probe in gclient.get_all_probes():
    continent = probe.location.continent
    continent_counts[continent] = continent_counts.get(continent, 0) + 1

print(continent_counts)
