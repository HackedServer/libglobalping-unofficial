from dataclasses import dataclass
from typing import Any, Union

from libglobalping.common import GlobalpingBaseResponse, ResultProbe


@dataclass
class MTRStats:
    min: float
    max: float
    avg: float
    total: int
    rcv: int
    drop: int
    stDev: float
    jMin: float
    jMax: float
    jAvg: float
    loss: int

    @classmethod
    def from_api_response(cls, data: dict[str, Union[float, int]]) -> "MTRStats":
        obj: MTRStats = cls(
            min=data.pop("min"),
            max=data.pop("max"),
            avg=data.pop("avg"),
            total=data.pop("total"),
            rcv=data.pop("rcv"),
            drop=data.pop("drop"),
            stDev=data.pop("stDev"),
            jMin=data.pop("jMin"),
            jMax=data.pop("jMax"),
            jAvg=data.pop("jAvg"),
            loss=data.pop("loss"),
        )

        return obj


@dataclass
class MTRTimings:
    rtt: float


@dataclass
class MTRHops:
    stats: MTRStats
    timings: list[MTRTimings]
    duplicate: bool
    asn: list[int]
    resolvedAddress: str
    resolvedHostname: str

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "MTRHops":
        return cls(
            stats=MTRStats.from_api_response(data["stats"]),
            timings=[MTRTimings(rtt=timing["rtt"]) for timing in data["timings"]],
            duplicate=data.get("duplicate", False),
            asn=data["asn"],
            resolvedAddress=data["resolvedHostname"],
            resolvedHostname=data["resolvedHostname"],
        )


@dataclass
class MTRResult:
    hops: list[MTRHops]
    rawOutput: str

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "MTRResult":
        return cls(
            hops=[MTRHops.from_api_response(hop) for hop in data["hops"]],
            rawOutput=data["rawOutput"],
        )


@dataclass
class MTRResults:
    probe: ResultProbe
    result: MTRResult

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "MTRResults":
        return cls(
            probe=ResultProbe.from_api_response(data["probe"]),
            result=MTRResult.from_api_response(data["result"]),
        )

    def pretty_print(self, line_length: int = 100, print_text: bool = True):
        output: list[str] = []
        for hop in self.result.hops:

            if hop.resolvedHostname:
                hostname = hop.resolvedHostname
            elif hop.resolvedAddress:
                hostname = hop.resolvedAddress
            else:
                hostname = "UNKNOWN"

            timings = [
                f"{timing.rtt}ms".ljust(10) if timing.rtt else "*".center(10)
                for timing in hop.timings
            ]

            line = "{}{}".format(
                hostname[: line_length - 34 - 2].ljust(line_length - 34),
                "- ".join(timings),
            )

            output.append(line)
        if print_text:
            for line in output:
                print(line)
        else:
            return line


@dataclass
class MTRResponse(GlobalpingBaseResponse):
    results: list[MTRResults]

    @classmethod
    def from_api_response(cls, data: dict[Any, Any]) -> "MTRResponse":
        return cls(
            id=data["id"],
            type=data["type"],
            status=data["status"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            probesCount=data["probesCount"],
            results=[MTRResults.from_api_response(r) for r in data["results"]],
        )
