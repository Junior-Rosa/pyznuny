from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


def _clean_dict(data: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


def _require_non_empty(value: str, field: str) -> None:
    if not value or not str(value).strip():
        raise ValueError(f"{field} is required.")




@dataclass(slots=True)
class TicketCreateTicket:
    Title: str
    Queue: str
    State: str
    Priority: str
    CustomerUser: str | None = None
    Type: str | None = None
    Service: str | None = None
    SLA: str | None = None
    Owner: str | None = None
    Responsible: str | None = None

    def validate(self) -> None:
        _require_non_empty(self.Title, "Ticket.Title")
        _require_non_empty(self.Queue, "Ticket.Queue")
        _require_non_empty(self.State, "Ticket.State")
        _require_non_empty(self.Priority, "Ticket.Priority")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return _clean_dict(
            {
                "Title": self.Title,
                "Queue": self.Queue,
                "State": self.State,
                "Priority": self.Priority,
                "CustomerUser": self.CustomerUser,
                "Type": self.Type,
                "Service": self.Service,
                "SLA": self.SLA,
                "Owner": self.Owner,
                "Responsible": self.Responsible,
            }
        )


@dataclass(slots=True)
class TicketCreateArticle:
    Subject: str
    Body: str
    ContentType: str
    Charset: str | None = None
    MimeType: str | None = None
    SenderType: str | None = None
    From_: str | None = None

    def validate(self) -> None:
        _require_non_empty(self.Subject, "Article.Subject")
        _require_non_empty(self.Body, "Article.Body")
        _require_non_empty(self.ContentType, "Article.ContentType")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return _clean_dict(
            {
                "Subject": self.Subject,
                "Body": self.Body,
                "ContentType": self.ContentType,
                "Charset": self.Charset,
                "MimeType": self.MimeType,
                "SenderType": self.SenderType,
                "From": self.From_,
            }
        )


@dataclass(slots=True)
class TicketCreatePayload:
    Ticket: TicketCreateTicket
    Article: TicketCreateArticle
    DynamicField: Mapping[str, Any] | None = None
    Attachment: list[Mapping[str, Any]] | None = None
    TimeUnit: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return _clean_dict(
            {
                "Ticket": self.Ticket.to_dict(),
                "Article": self.Article.to_dict(),
                "DynamicField": self.DynamicField,
                "Attachment": self.Attachment,
                "TimeUnit": self.TimeUnit,
            }
        )



class TicketUpdateTicket(TicketCreateTicket):
    def validate(self):
        pass