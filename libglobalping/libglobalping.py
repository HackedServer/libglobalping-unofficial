from functools import cache
from typing import Optional

import requests

from .common import DOMAIN_NAME, ApiPath, Probe, Probes, Schemas, await_completion
from .responses import (
    DNSResponse,
    HTTPResponse,
    MTRResponse,
    PINGResponse,
    TracerouteResponse,
)


class GlobalpingClient:
    def __init__(self, token: Optional[str] = None):
        super().__init__()
        self.token = token

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    @cache
    def get_probes(self) -> Probes:
        return Probes.generate()

    def get_all_probes(self) -> list[Probe]:
        return self.get_probes().all

    def has_country(self, country: str) -> bool:
        return self.get_probes().has_country(country)

    def check_ping4(
        self, ip: str, packets: Optional[int] = 3, limit: Optional[int] = None
    ):
        """Execute a ping check against an IPv4 address and returns the result output once it finishes.
        Blocks while waiting for the request to complete.

        Args:
            ip (str): IPv4 Address
            packets (Optional[int], optional): Number of packets to send. Defaults to 3.
            limit (Optional[int], optional): Number of probes to check from. Defaults to 1.

        Returns:
            PINGResponse: Response output from GlobalPing.
        """
        body = Schemas.PING(ip=ip, packets=packets, limit=limit)
        query_url = DOMAIN_NAME._replace(path=ApiPath.MEASUREMENTS.value).geturl()
        response = requests.post(query_url, json=body).json()
        request_id = response["id"]
        result = await_completion(request_id=request_id)
        return PINGResponse.from_api_response(result)

    def check_http(
        self, url: str, method: str = "GET", limit: Optional[int] = None
    ) -> HTTPResponse:
        """Execute an HTTP check against a URL and return the result output once it finishes.
        Blocks while waiting for the request to complete.

        Args:
            url (str): Full valid URL
            method (str, optional): HTTP Request Method. "HEAD" or "GET". Defaults to "GET".
            limit (Optional[int], optional): Number of probes to check from. Defaults to 1.

        Returns:
            HTTPResponse: Response output from GlobalPing
        """
        body = Schemas.HTTP(
            url=url, head=True if method == "HEAD" else False, limit=limit
        )
        query_url = DOMAIN_NAME._replace(path=ApiPath.MEASUREMENTS.value).geturl()
        response = requests.post(query_url, json=body).json()
        request_id = response["id"]
        result = await_completion(request_id=request_id)

        return HTTPResponse.from_api_response(result)

    def check_mtr(
        self,
        target: str,
        packets: Optional[int] = None,
        port: Optional[int] = None,
        protocol: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> MTRResponse:
        """Execute an MTR check against a taget and return the result output once it finishes.
        Blocks while waiting for the request to complete.

        Args:
            target (str): An IPv4 address or a domain.
            packets (Optional[int], optional): How many packets to send. Defaults to None.
            port (Optional[int], optional): What port to execute the traceroute on. Defaults to None.
            protocol (Optional[str], optional): What protocol to use for the traceroute. Defaults to None.
            limit (Optional[int], optional): Number of probes to check from. Defaults to 1.

        Returns:
            MTRResponse: Response output from GlobalPing
        """
        body = Schemas.MTR(
            target=target, protocol=protocol, packets=packets, port=port, limit=limit
        )
        query_url = DOMAIN_NAME._replace(path=ApiPath.MEASUREMENTS.value).geturl()
        response = requests.post(query_url, json=body).json()
        request_id = response["id"]
        result = await_completion(request_id=request_id)

        return MTRResponse.from_api_response(result)

    def check_dns(
        self, target: str, query_type: str = "A", resolver: Optional[str] = None
    ) -> DNSResponse:
        """Execute a DNS query against a target domain name and return the result output once it finishes.
        Blocks while waiting for the request to complete.

        Args:
            target (str): A publically resolvable domain name
            query_type (str, optional): The type of DNS record to query for. Defaults to "A".
            resolver (Optional[str], optional): The resolver to use for the query. Defaults to None.

        Returns:
            DNSResponse: Response output from GlobalPing
        """
        body = Schemas.DNS(target=target, query_type=query_type, resolver=resolver)
        query_url = DOMAIN_NAME._replace(path=ApiPath.MEASUREMENTS.value).geturl()
        response = requests.post(query_url, json=body).json()
        request_id = response["id"]
        result = await_completion(request_id=request_id)

        return DNSResponse.from_api_response(result)

    def check_traceroute(self, target: str) -> TracerouteResponse:
        body = Schemas.TRACEROUTE(target=target)
        query_url = DOMAIN_NAME._replace(path=ApiPath.MEASUREMENTS.value).geturl()
        response = requests.post(query_url, json=body).json()
        request_id = response["id"]
        result = await_completion(request_id=request_id)

        return TracerouteResponse.from_api_response(result)
