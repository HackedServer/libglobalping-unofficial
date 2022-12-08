from dataclasses import dataclass
from enum import Enum
from functools import cache
from time import sleep
from typing import Any
from urllib.parse import urlparse

import requests

DOMAIN_NAME = urlparse(url="https://api.globalping.io/")


class Schemas:
    DEFAULT = {
        "limit": 1,
        "locations": [],
    }

    def HTTP(url: str, head: bool = False) -> dict[str, Any]:
        parsed = urlparse(url)
        port = (
            parsed.port
            if parsed.port
            else 443
            if parsed.scheme.upper() == "HTTPS"
            else 80
        )

        return Schemas.DEFAULT | {
            "type": "http",
            "target": parsed.hostname,
            "measurementOptions": {
                "protocol": parsed.scheme.upper(),
                "port": port,
                "request": {
                    "method": "HEAD" if head else "GET",
                    "path": parsed.path,
                    "query": "?" + parsed.query,
                    "host": parsed.hostname,
                    "headers": {
                        "Referer": "https://github.com/HackedServer/libglobalping-unofficial"
                    },
                },
            },
        }


class ApiPath(Enum):
    MEASUREMENTS = "/v1/measurements"
    PROBES = "/v1/probes"


class Status(Enum):
    FINISHED = "finished"
    IN_PROGRESS = "in-progress"


@dataclass
class ProbeLocation:
    continent: str
    region: str
    country: str
    city: str
    asn: int
    latitude: float
    longitude: float
    network: str
    state: str = None


@dataclass
class Probe:
    version: str
    ready: bool
    location: ProbeLocation


# Is there a way to not have the `all` variable and have it be the default?
# This dataclasss seems dumb.
@dataclass
class Probes:
    all: list[Probe]

    @cache
    def has_country(self, country: str) -> bool:
        return any(probe.location.country == country for probe in self.all)

    @classmethod
    def generate(cls) -> "Probes":
        probes: list[Probe] = []
        probe_list = requests.get(
            url=DOMAIN_NAME._replace(path=ApiPath.PROBES.value).geturl()
        ).json()
        for probe in probe_list:
            # Misspelling fix pending PR
            # https://github.com/jsdelivr/globalping/pull/249
            probes.append(
                Probe(
                    probe["version"],
                    probe["ready"],
                    ProbeLocation(
                        latitude=probe["location"].pop("latitute"), **probe["location"]
                    ),
                )
            )
        return cls(probes)


def await_completion(request_id: str):
    query_url = DOMAIN_NAME._replace(
        path=ApiPath.MEASUREMENTS.value + "/" + request_id,
    ).geturl()
    for _ in range(10):
        response = requests.get(query_url).json()
        if response["status"] == Status.FINISHED.value:
            return response
        sleep(1)
