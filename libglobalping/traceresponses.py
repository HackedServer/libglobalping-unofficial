from dataclasses import dataclass
from typing import Any

from libglobalping.common import GlobalpingBaseResponse, ResultProbe


@dataclass
class TracerouteTiming:
    rtt: float


@dataclass
class TracerouteHop:
    resolvedAddress: str
    resolvedHostname: str
    timings: list[TracerouteTiming]

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "TracerouteHop":
        return cls(
            resolvedAddress=data["resolvedHostname"],
            resolvedHostname=data["resolvedHostname"],
            timings=[TracerouteTiming(rtt=timing["rtt"]) for timing in data["timings"]],
        )


@dataclass
class TracerouteResult:
    resolvedAddress: str
    resolvedHostname: str
    rawOutput: str
    hops: list[TracerouteHop]

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "TracerouteResult":
        return cls(
            rawOutput=data["rawOutput"],
            resolvedAddress=data["resolvedHostname"],
            resolvedHostname=data["resolvedHostname"],
            hops=[TracerouteHop.from_api_response(hop) for hop in data["hops"]],
        )


@dataclass
class TracerouteResults:
    probe: ResultProbe
    result: TracerouteResult

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "TracerouteResults":
        return cls(
            probe=ResultProbe.from_api_response(data["probe"]),
            result=TracerouteResult.from_api_response(data["result"]),
        )


@dataclass
class TracerouteResponse(GlobalpingBaseResponse):
    results: list[TracerouteResults]

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "TracerouteResponse":
        return cls(
            id=data["id"],
            type=data["type"],
            status=data["status"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            probesCount=data["probesCount"],
            results=[TracerouteResults.from_api_response(r) for r in data["results"]],
        )
