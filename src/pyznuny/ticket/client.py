from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

if __name__ == "__main__" and __package__ is None:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from pyznuny.ticket.endpoints import Endpoint, EndpointsRegistry
    from pyznuny.ticket.models import TicketCreatePayload, TicketCreateTicket, TicketCreateArticle, TicketUpdateTicket
else:
    from .endpoints import Endpoint, EndpointsRegistry
    from .models import TicketCreatePayload, TicketCreateTicket, TicketCreateArticle, TicketUpdateTicket


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

class TicketClientError(Exception):
    def __init__(self, error: Mapping[str, Any]) -> None:
        self.error = error
        code = error.get("ErrorCode")
        message = error.get("ErrorMessage") or "Unknown error"
        super().__init__(f"{code}: {message}" if code else str(message)) #TODO: make logging
        

class SessionRoutes:
    def __init__(self, client: "TicketClient") -> None:
        self._client = client

    def create(self, username: str, password: str) -> httpx.Response:
        return self._client.request(
            "session_create",
            json={"UserLogin": username, "Password": password},
        )


class TicketRoutes:
    def __init__(self, client: "TicketClient") -> None:
        self._client = client

    def create(
        self,
        payload: TicketCreatePayload | Mapping[str, Any] | None = None,
        **payload_kwargs: Any,
    ) -> httpx.Response:
        
        if payload is None:
            payload_dict = dict(payload_kwargs)
            
        elif isinstance(payload, TicketCreatePayload):
            payload_dict = payload.to_dict()
            payload_dict.update(payload_kwargs)
        else:
            payload_dict = dict(payload)
            payload_dict.update(payload_kwargs)

        payload_dict.update({"SessionID": self._client.session_id})
        return self._client.request("ticket_create", json=payload_dict)
    

    def update(self, ticket_id: str | int , **payload: dict) -> httpx.Response:
        identifier = self._client.endpoint_identifier("ticket_update")
        
        payload.update({"SessionID": self._client.session_id})
        return self._client.request(
            "ticket_update",
            path_params={identifier: ticket_id},
            json=payload,
        )
        
    def get(self, ticket_id: str | int, 
            dynamic_fields:int=0,
            all_articles:int=0) -> httpx.Response:
        identifier = self._client.endpoint_identifier("ticket_get")
        return self._client.request(
            "ticket_get",
            path_params={identifier: ticket_id},
            params={"SessionID": self._client.session_id,
                    "DynamicFields": dynamic_fields,
                    "AllArticles": all_articles},
        )


class EndpointSetter:
    def __init__(self, client: "TicketClient") -> None:
        self._client = client

    def clean_endpoint(self, endpoint: str) -> str:
        endpoint = endpoint.rstrip('/')
        return endpoint.strip()
    
    def ticket_create(self, *, endpoint: str, method: str = "POST") -> Endpoint:
        endpoint = self.clean_endpoint(endpoint)
        return self._client.register_endpoint("ticket_create", method, endpoint)

    def ticket_get(
        self,
        *,
        endpoint: str,
        identifier: str = "ticket_id",
        method: str = "GET",
    ) -> Endpoint:
        endpoint = self.clean_endpoint(endpoint)
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
        endpoint = self.clean_endpoint(endpoint)
        endpoint_obj = self._client.register_endpoint(
            "ticket_update",
            method,
            endpoint,
        )
        self._client.set_endpoint_identifier("ticket_update", identifier)
        return endpoint_obj


class TicketClient:
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
        return self._endpoints.register(Endpoint(name=name, method=method, path=path))

    def set_endpoint_identifier(self, name: str, identifier: str) -> None:
        self._endpoint_identifiers[name] = identifier

    def endpoint_identifier(self, name: str) -> str:
        try:
            return self._endpoint_identifiers[name]
        except KeyError as exc:
            raise KeyError(f"Endpoint identifier not registered: {name}") from exc

    def login(self, username: str, password: str) -> httpx.Response:
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
    
    client.set_endpoint.ticket_get(endpoint="Tickets/{ticket_id}", identifier="ticket_id")
    response = client.ticket.get(ticket_id=5853276)
    print("GET Ticket Response:", response.json())
