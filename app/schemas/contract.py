from typing import Optional

from pydantic import BaseModel


class Party(BaseModel):
    name: str
    role: str
    address: Optional[str] = None


class Clause(BaseModel):
    title: str
    summary: str


class Contract(BaseModel):
    contract_type: str
    parties: list[Party]
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    jurisdiction: Optional[str] = None
    governing_law: Optional[str] = None
    key_clauses: list[Clause] = []
    payment_terms: Optional[str] = None
    termination_conditions: Optional[str] = None
    confidentiality_clause: bool = False
    non_compete_clause: bool = False
    total_value: Optional[float] = None
    currency: str = "USD"
