from libglobalping import client, Probes

gclient = client()
r = gclient.check_http("https://ipinfo.io/json")
print(r.results[0].result)


print(Probes.generate().all[0])
