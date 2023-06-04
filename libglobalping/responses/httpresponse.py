from dataclasses import dataclass
from typing import Any

from libglobalping.common import GlobalpingBaseResponse, ResultProbe


@dataclass
class HTTPTimings:
    total: int
    download: int
    firstByte: int
    dns: int
    tls: int
    tcp: int

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "HTTPTimings":
        return cls(**data)


@dataclass
class HTTPResult:
    resolvedAddress: str
    headers: dict[str, str]  # ugh
    rawHeaders: str
    rawBody: str
    statusCode: int
    timings: HTTPTimings
    tls: dict[Any, Any]  # ugh
    rawOutput: str

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "HTTPResult":
        return cls(
            resolvedAddress=data["resolvedAddress"],
            headers=data["headers"],
            rawHeaders=data["rawHeaders"],
            rawBody=data["rawBody"],
            statusCode=data["statusCode"],
            timings=HTTPTimings.from_api_response(data["timings"]),
            tls=data["tls"],
            rawOutput=data["rawOutput"],
        )


@dataclass
class HTTPResults:
    probe: ResultProbe
    result: HTTPResult

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "HTTPResults":
        return cls(
            probe=ResultProbe.from_api_response(data["probe"]),
            result=HTTPResult.from_api_response(data["result"]),
        )


@dataclass
class HTTPResponse(GlobalpingBaseResponse):
    results: list[HTTPResults]

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "HTTPResponse":
        return cls(
            id=data["id"],
            type=data["type"],
            status=data["status"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            probesCount=data["probesCount"],
            results=[HTTPResults.from_api_response(r) for r in data["results"]],
        )
