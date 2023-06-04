from dataclasses import dataclass
from enum import Enum
from functools import cache
from time import sleep
from typing import Any, Optional
from urllib.parse import urlparse

import requests

DOMAIN_NAME = urlparse(url="https://api.globalping.io/")


class ApiPath(Enum):
    MEASUREMENTS = "/v1/measurements"
    PROBES = "/v1/probes"


@dataclass
class ResultProbe:
    continent: str
    region: str
    country: str
    state: Optional[str]
    city: str
    asn: int
    longitude: float
    latitude: float
    network: str
    resolvers: list[str]

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "ResultProbe":
        return cls(
            continent=data["continent"],
            region=data["region"],
            country=data["country"],
            state=data.get("state", None),
            city=data["city"],
            asn=data["asn"],
            longitude=data["longitude"],
            latitude=data["latitude"],
            network=data["network"],
            resolvers=data["resolvers"],
        )


@dataclass
class GlobalpingBaseResponse:
    id: str
    type: str
    status: str
    createdAt: str
    updatedAt: str
    probesCount: int


class Schemas:
    DEFAULT = {
        "limit": 1,
        "locations": [],
    }

    def PING(
        ip: str,
        packets: int = 3,
        limit: Optional[int] = None,
        locations: Optional[list] = None,
    ) -> dict[str, Any]:
        body = {
            "type": "ping",
            "target": ip,
            "measurementOptions": {"packets": packets},
        }

        return Schemas.DEFAULT | body | loc_limit_mod(limit, locations)

    def HTTP(
        url: str,
        head: bool = False,
        limit: Optional[int] = None,
        locations: Optional[list] = None,
    ) -> dict[str, Any]:
        parsed = urlparse(url)
        port = parsed.port if parsed.port else 443 if parsed.scheme.upper() == "HTTPS" else 80

        body = {
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
                    "headers": {"Referer": "https://github.com/HackedServer/libglobalping-unofficial"},
                },
            },
        }

        return Schemas.DEFAULT | body | loc_limit_mod(limit, locations)

    def MTR(
        target: str,
        protocol: Optional[str] = None,
        port: Optional[int] = None,
        packets: Optional[int] = None,
        limit: Optional[int] = None,
        locations: Optional[list] = None,
    ) -> dict[str, Any]:

        body = {"type": "mtr", "target": target, "measurementOptions": {}}
        if protocol:
            body["measurementOptions"]["protocol"] = protocol

        if packets:
            body["measurementOptions"]["packets"] = packets

        if port:
            body["measurementOptions"]["port"] = port

        return Schemas.DEFAULT | body | loc_limit_mod(limit, locations)

    def DNS(
        target: str,
        protocol: Optional[str] = None,
        port: Optional[int] = None,
        resolver: Optional[str] = None,
        query_type: str = "A",
        limit: Optional[int] = None,
        locations: Optional[list] = None,
    ) -> dict[str, Any]:
        body = {"type": "dns", "target": target, "measurementOptions": {}}

        body["measurementOptions"]["query"] = {"type": query_type}

        if protocol:
            body["measurementOptions"]["protocol"] = protocol

        if port:
            body["measurementOptions"]["port"] = port

        if resolver:
            body["measurementOptions"]["resolver"] = resolver

        return Schemas.DEFAULT | body | loc_limit_mod(limit, locations)

    def TRACEROUTE(
        target: str,
        protocol: Optional[str] = None,
        port: Optional[int] = None,
        limit: Optional[int] = None,
        locations: Optional[list] = None,
    ):
        body = {"type": "traceroute", "target": target, "measurementOptions": {}}

        if protocol:
            body["measurementOptions"]["protocol"] = protocol

        if port:
            body["measurementOptions"]["port"] = port

        return Schemas.DEFAULT | body | loc_limit_mod(limit, locations)


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
    location: ProbeLocation
    tags: list[str]
    resolvers: list[str]

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "Probe":
        return cls(location=(ProbeLocation(**data.pop("location"))), **data)


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
        probe_list = requests.get(url=DOMAIN_NAME._replace(path=ApiPath.PROBES.value).geturl()).json()
        for probe in probe_list:
            probes.append(Probe.from_api_response(probe))
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


def loc_limit_mod(
    limit: Optional[int] = None,
    locations: Optional[list] = None,
) -> dict[Any, Any]:
    body = {}
    if limit:
        body["limit"] = limit

    if locations:
        body["locations"] = locations

    return body
