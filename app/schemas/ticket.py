from typing import Literal, Optional

from pydantic import BaseModel


class SupportTicket(BaseModel):
    subject: str
    category: Literal["billing", "technical", "account", "general", "refund", "other"]
    priority: Literal["low", "medium", "high", "critical"]
    sentiment: Literal["positive", "neutral", "negative", "frustrated", "angry"]
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    product: Optional[str] = None
    issue_description: str
    summary: str
    action_items: list[str] = []
    suggested_response: Optional[str] = None
