from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

if __name__ == "__main__" and __package__ is None:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from pyznuny.ticket.endpoints import Endpoint, EndpointsRegistry,EndpointSetter, _DEFAULT_ENDPOINT_IDENTIFIERS, _DEFAULT_ENDPOINTS
    from pyznuny.ticket.models import (
        TicketCreateArticle,
        TicketCreatePayload,
        TicketCreateTicket,
    )
    from pyznuny.ticket.exceptions import TicketClientError
    from pyznuny.ticket.routes import TicketRoutes, SessionRoutes
else:
    from .endpoints import Endpoint, EndpointsRegistry,EndpointSetter, _DEFAULT_ENDPOINT_IDENTIFIERS, _DEFAULT_ENDPOINTS
    from .models import (
        TicketCreateArticle,
        TicketCreatePayload,
        TicketCreateTicket,
    )
    from .routes import TicketRoutes, SessionRoutes
    from .exceptions import TicketClientError




class TicketClient:
    """
    Represents a client for interacting with the Ticket API

    :param base_url: Base URL for the Ticket API which the client will connect to
    :type base_url: str | None
    :param username: Username for authentication
    :type username: str | None
    :param password: Password for authentication
    :type password: str | None
    :param endpoints: Custom endpoints registry
    :type endpoints: EndpointsRegistry | None
    :param timeout: Request timeout
    :type timeout: float | None
    :param headers: Custom headers
    :type headers: Mapping[str, str] | None
    """
    def __init__(
        self,
        base_url: str | None = None,
        *,
        username: str | None = None,
        password: str | None = None,
        endpoints: EndpointsRegistry | None = None,
        timeout: float | None = None,
        headers: Mapping[str, str] | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self._endpoints = endpoints or EndpointsRegistry()
        self._endpoint_identifiers = dict(_DEFAULT_ENDPOINT_IDENTIFIERS)
        if client is not None:
            self._client = client
        else:
            client_kwargs: dict[str, Any] = {"timeout": timeout, "headers": headers}
            if base_url is not None:
                client_kwargs["base_url"] = base_url
            self._client = httpx.Client(**client_kwargs)

        self._register_default_endpoints()
        self.ticket = TicketRoutes(self)
        self.session = SessionRoutes(self)
        self.set_endpoint = EndpointSetter(self)
        self.session_id: str | None = None

        if username is not None and password is not None:
            self.login(username, password)

    @property
    def endpoints(self) -> EndpointsRegistry:
        return self._endpoints

    def register_endpoint(self, name: str, method: str, path: str) -> Endpoint:
        """
        Registers a custom endpoint for the Ticket API

        :param name: Name of the endpoint
        :type name: str
        :param method: HTTP method for the endpoint
        :type method: str
        :param path: Endpoint path
        :type path: str
        :return: Registered endpoint
        :rtype: Endpoint
        """
        return self._endpoints.register(Endpoint(name=name, method=method, path=path))

    def set_endpoint_identifier(self, name: str, identifier: str) -> None:
        """
        Sets a custom identifier for an endpoint

        :param name: Name of the endpoint
        :type name: str
        :param identifier: Custom identifier for the endpoint
        :type identifier: str
        """
        self._endpoint_identifiers[name] = identifier

    def endpoint_identifier(self, name: str) -> str:
        """
        Returns the custom identifier for an endpoint

        :param name: Name of the endpoint
        :type name: str
        :return: Custom identifier for the endpoint
        :rtype: str
        """
        try:
            return self._endpoint_identifiers[name]
        except KeyError as exc:
            raise KeyError(f"Endpoint identifier not registered: {name}") from exc

    def login(self, username: str, password: str) -> httpx.Response:
        """
        Creates a new session with the given username and password.

        :param username: Username for authentication
        :type username: str
        :param password: Password for authentication
        :type password: str
        :return: Response object containing session details
        :rtype: Response
        """
        response = self.session.create(username, password)
        self.session_id = response.json().get("SessionID")


    def request(
        self,
        endpoint_name: str,
        *,
        method: str | None = None,
        path: str | None = None,
        path_params: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Sends a request to the Ticket API

        :param endpoint_name: Name of the endpoint
        :type endpoint_name: str
        :param method: HTTP method for the request, defaults to None
        :type method: str | None
        :param path: Custom endpoint path, defaults to None
        :type path: str | None
        :param path_params: Parameters for the endpoint path, defaults to None
        :type path_params: Mapping[str, Any] | None
        :param kwargs: Additional keyword arguments for the request
        :type kwargs: Any
        :return: Response object
        :rtype: httpx.Response
        """
        endpoint_method = method or self._endpoints.method_for(endpoint_name)
        endpoint_path = path or self._endpoints.path_for(endpoint_name)
        
        
        
        if path_params:
            endpoint_path = endpoint_path.format(**path_params)
        response = self._client.request(endpoint_method, endpoint_path, **kwargs)
        
        response.raise_for_status()
        if error := response.json().get("Error"):
            self._raise_error(error)
            
        return response

    def _raise_error(self, error: Mapping[str, Any]) -> None:
        raise TicketClientError(error)

    def close(self) -> None:
        """
        Closes the client connection
        """
        self._client.close()

    def __enter__(self) -> "TicketClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def _register_default_endpoints(self) -> None:
        for name, (method, path) in _DEFAULT_ENDPOINTS.items():
            if not self._endpoints.has(name):
                self._endpoints.register(
                    Endpoint(name=name, method=method, path=path)
                )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    import os
    
    class_payload_create = TicketCreatePayload(
    Ticket=TicketCreateTicket(
        Title="Erro no login",
        Queue="ITS::Ops-TechOps::Sentinelops::Cops React - N1",
        State="new",
        Priority="3 normal",
        CustomerUser="joel.junior@eitisolucoes.com.br",
        Type="Monitoramento",
    ),
    Article=TicketCreateArticle(
        Subject="Não consigo acessar",
        Body="Detalhes do problema...",
        ContentType="text/plain; charset=utf-8",
        Charset="utf-8",
        MimeType="text/plain",
        SenderType="customer",
        From_="joel.junior@eitisolucoes.com.br",
    ),
)

    payload_create = {
        "Ticket": {
            "Title": "Erro no login",
            "Queue": "ITS::Ops-TechOps::Sentinelops::Cops React - N1",
            "State": "new",
            "Priority": "3 normal",
            "CustomerUser": "joel.junior@eitisolucoes.com.br",
            "Type": "Monitoramento",
        },
        "Article": {
            "Subject": "Não consigo acessar",
            "Body": "Detalhes do problema...",
            "ContentType": "text/plain; charset=utf-8",
            "Charset": "utf-8",
            "MimeType": "text/plain",
            "SenderType": "customer",
            "From": "joel.junior@eitisolucoes.com.br",
        },
    }
    
    payload_update = {
        "Ticket": {
            "State": "open",
        }
    }
    
    
    client = TicketClient(base_url=os.getenv("HOST"), 
                          username=os.getenv("USER_LOGIN"), password=os.getenv("PASS"))
    
    client.set_endpoint.ticket_get(endpoint="Tickets/{ticket_id}", 
                                   identifier="ticket_id")
    response = client.ticket.get(ticket_id=5853276)
    print("GET Ticket Response:", response.json())
