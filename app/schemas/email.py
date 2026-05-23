from typing import Literal, Optional

from pydantic import BaseModel


class Email(BaseModel):
    sender: Optional[str] = None
    recipients: list[str] = []
    subject: Optional[str] = None
    date_sent: Optional[str] = None
    intent: Literal["inquiry", "complaint", "request", "follow_up", "confirmation", "spam", "other"]
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str
    key_entities: list[str] = []
    action_required: bool = False
    action_items: list[str] = []
    priority: Literal["low", "normal", "high"] = "normal"
