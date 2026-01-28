

from typing import Any, Mapping


class TicketClientError(Exception):
    """
    Docstring for TicketClientError
    Represents an error returned by the TicketClient API.
    """
    def __init__(self, error: Mapping[str, Any] | str) -> None:
        
        self.error = error
        code = error.get("ErrorCode") if isinstance(error, dict) else error
        message = error.get("ErrorMessage") or "Unknown error" \
            if isinstance(error, dict) else str(error)
            
        super().__init__(f"{code}: {message}" if code else str(message))