from __future__ import annotations


from .models import Endpoint
from typing import Iterable, Mapping, MutableMapping, TYPE_CHECKING

if TYPE_CHECKING:
    from pyznuny.ticket.client import TicketClient

_DEFAULT_ENDPOINTS = {
    "ticket_create": ("POST", "/Ticket"),
    "ticket_update": ("PATCH", "/Ticket/{ticket_id}"),
    "ticket_get": ("GET", "/Ticket/{ticket_id}"),
    "session_create": ("POST", "/Session"),
}

_DEFAULT_ENDPOINT_IDENTIFIERS = {
    "ticket_update": "ticket_id",
    "ticket_get": "ticket_id",
}



class EndpointSetter:
    """
    Custom endpoint setter for the Ticket API

    :arg client: Ticket client instance
    :type client: TicketClient
    """
    def __init__(self, client: "TicketClient") -> None:
        self._client = client

    
    def ticket_create(self, *, endpoint: str, method: str = "POST") -> Endpoint:
        """
        Sets a custom endpoint for creating tickets

        :param endpoint: Custom endpoint for creating tickets
        :type endpoint: str
        :param method: HTTP method for creating tickets, defaults to POST
        :type method: str
        :return: Endpoint object
        :rtype: Endpoint
        """
        return self._client.register_endpoint("ticket_create", method, endpoint)

    def ticket_get(
        self,
        *,
        endpoint: str,
        identifier: str = "ticket_id",
        method: str = "GET",
    ) -> Endpoint:
        """
        Sets a custom endpoint for retrieving a ticket.

        :param endpoint: Custom endpoint path
        :type endpoint: str
        :param identifier: Identifier for the ticket ID in the endpoint path
        :type identifier: str
        :param method: HTTP method for the endpoint, defaults to GET
        :type method: str
        :return: Registered endpoint
        :rtype: Endpoint
        """
        endpoint_obj = self._client.register_endpoint(
            "ticket_get",
            method,
            endpoint,
        )
        self._client.set_endpoint_identifier("ticket_get", identifier)
        return endpoint_obj
    
    def ticket_update(
        self,
        *,
        endpoint: str,
        identifier: str = "ticket_id",
        method: str = "POST",
    ) -> Endpoint:
        """
        Sets a custom endpoint for updating a ticket.

        :param endpoint: Custom endpoint path
        :type endpoint: str
        :param identifier: Identifier for the ticket ID in the endpoint path
        :type identifier: str
        :param method: HTTP method for the endpoint, defaults to POST
        :type method: str
        :return: Registered endpoint
        :rtype: Endpoint
        """
        endpoint_obj = self._client.register_endpoint(
            "ticket_update",
            method,
            endpoint,
        )
        self._client.set_endpoint_identifier("ticket_update", identifier)
        return endpoint_obj




class EndpointsRegistry:
    """
    Object representing the registry of API endpoints for the Ticket API

    :arg base_path: Base path for the endpoints, defaults to an empty string
    :type base_path: str
    """
    def __init__(
        self,
        *,
        base_path: str = "",
        endpoints: Iterable[Endpoint] | None = None,
    ) -> None:
        self._base_path = base_path
        self._endpoints: MutableMapping[str, Endpoint] = {}
        if endpoints:
            for endpoint in endpoints:
                self.register(endpoint)

    @property
    def base_path(self) -> str:
        return self._base_path

    @base_path.setter
    def base_path(self, value: str) -> None:
        self._base_path = value

    def register(self, endpoint: Endpoint) -> Endpoint:
        self._endpoints[endpoint.name] = endpoint
        return endpoint

    def configure(self, mapping: Mapping[str, tuple[str, str]]) -> None:
        for name, (method, path) in mapping.items():
            self.register(Endpoint(name=name, method=method, path=path))

    def get(self, name: str) -> Endpoint:
        try:
            return self._endpoints[name]
        except KeyError as exc:
            raise KeyError(f"Endpoint not registered: {name}") from exc

    def has(self, name: str) -> bool:
        return name in self._endpoints

    def path_for(self, name: str) -> str:
        endpoint = self.get(name)
        return endpoint.full_path(self._base_path)

    def method_for(self, name: str) -> str:
        return self.get(name).method
