from functools import cache
from typing import Optional

import requests

from .common import DOMAIN_NAME, ApiPath, Probe, Probes, Schemas, await_completion
from .httpresponses import HTTPResponse
from .pingresponses import PINGResponse


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
            PINGResponse: Response output from GlobalPing
        """
        body = Schemas.PING(ip=ip, packets=packets)
        query_url = DOMAIN_NAME._replace(path=ApiPath.MEASUREMENTS.value).geturl()
        response = requests.post(query_url, json=body).json()
        request_id = response["id"]
        result = await_completion(request_id=request_id)
        return PINGResponse.from_api_response(result)

    def check_http(
        self, url: str, method: str = "GET", limit: Optional[int] = None
    ) -> HTTPResponse:
        """Execute a check against a URL and return the result output once it finishes.
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
