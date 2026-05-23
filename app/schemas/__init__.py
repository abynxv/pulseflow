from app.schemas.contract import Contract
from app.schemas.email import Email
from app.schemas.invoice import Invoice
from app.schemas.ticket import SupportTicket

SCHEMA_MAP: dict[str, type] = {
    "invoice": Invoice,
    "contract": Contract,
    "ticket": SupportTicket,
    "email": Email,
}

__all__ = ["Invoice", "Contract", "SupportTicket", "Email", "SCHEMA_MAP"]
