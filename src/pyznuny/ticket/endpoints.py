from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping

_VALID_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
}


def _normalize_method(method: str) -> str:
    normalized = method.strip().upper()
    if normalized not in _VALID_METHODS:
        valid = ", ".join(sorted(_VALID_METHODS))
        raise ValueError(f"Unsupported HTTP method: {method!r}. Use one of: {valid}")
    return normalized


def _normalize_path(path: str) -> str:
    normalized = "/" + path.lstrip("/")
    if normalized == "/":
        raise ValueError("Endpoint path cannot be empty.")
    return normalized


def _join_base_path(base_path: str, endpoint_path: str) -> str:
    base = base_path.strip("/")
    tail = endpoint_path.lstrip("/")
    if not base:
        return "/" + tail
    return f"/{base}/{tail}"


@dataclass(frozen=True, slots=True)
class Endpoint:
    name: str
    method: str
    path: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "method", _normalize_method(self.method))
        object.__setattr__(self, "path", _normalize_path(self.path))

    def full_path(self, base_path: str = "") -> str:
        return _join_base_path(base_path, self.path)


class EndpointsRegistry:
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

if __name__ == "__main__":
    registry = EndpointsRegistry(base_path="http://localhost:8000")
    registry.register(Endpoint(name="get_user", method="GET", path="/users/{id}"))
    endpoint = registry.get("get_user")
    print(endpoint.method)  # Output: GET
    print(endpoint.full_path(registry.base_path))  
