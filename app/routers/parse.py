import uuid
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.db_models import ParseResult
from app.schemas import SCHEMA_MAP
from app.services.extractor import extract
from app.services.file_reader import read_file_text

router = APIRouter(prefix="/api/v1", tags=["parse"])

DocumentType = Literal["invoice", "contract", "ticket", "email", "auto"]


class ParseResponse(BaseModel):
    id: uuid.UUID
    document_type: str
    file_name: str
    file_size: int
    extracted_data: Optional[dict[str, Any]]
    success: bool
    error_message: Optional[str]
    retry_count: int
    created_at: str

    model_config = {"from_attributes": True}


class ResultListResponse(BaseModel):
    total: int
    items: list[ParseResponse]


@router.post("/parse", response_model=ParseResponse, summary="Parse a document")
async def parse_document(
    file: UploadFile,
    document_type: DocumentType = Query(
        default="auto",
        description="Document type. Use 'auto' to let the AI detect it.",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF, DOCX, or TXT file and receive structured JSON.

    - **invoice** — extracts vendor, line items, totals, dates
    - **contract** — extracts parties, clauses, dates, jurisdiction
    - **ticket** — extracts category, priority, sentiment, action items
    - **email** — extracts intent, sentiment, action items, entities
    - **auto** — AI classifies the document type first, then extracts
    """
    if document_type != "auto" and document_type not in SCHEMA_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown document_type '{document_type}'.")

    text, file_size = await read_file_text(file)

    record = ParseResult(
        document_type=document_type,
        file_name=file.filename or "unknown",
        file_size=file_size,
        raw_text=text,
    )

    try:
        result = await extract(text, document_type)
        record.document_type = result.document_type
        record.extracted_data = result.data
        record.retry_count = result.retry_count
        record.success = True
    except Exception as exc:
        record.success = False
        record.error_message = str(exc)

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return _to_response(record)


@router.get("/results", response_model=ResultListResponse, summary="List all parse results")
async def list_results(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    document_type: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Paginated list of all parsed documents, newest first."""
    query = select(ParseResult).order_by(ParseResult.created_at.desc()).offset(skip).limit(limit)
    if document_type:
        query = query.where(ParseResult.document_type == document_type)

    result = await db.execute(query)
    rows = result.scalars().all()

    count_query = select(ParseResult)
    if document_type:
        count_query = count_query.where(ParseResult.document_type == document_type)
    total = len((await db.execute(count_query)).scalars().all())

    return ResultListResponse(total=total, items=[_to_response(r) for r in rows])


@router.get("/results/{result_id}", response_model=ParseResponse, summary="Get a specific result")
async def get_result(result_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    row = await db.get(ParseResult, result_id)
    if not row:
        raise HTTPException(status_code=404, detail="Result not found.")
    return _to_response(row)


@router.delete("/results/{result_id}", status_code=204, summary="Delete a result")
async def delete_result(result_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    row = await db.get(ParseResult, result_id)
    if not row:
        raise HTTPException(status_code=404, detail="Result not found.")
    await db.delete(row)
    await db.commit()


def _to_response(row: ParseResult) -> ParseResponse:
    return ParseResponse(
        id=row.id,
        document_type=row.document_type,
        file_name=row.file_name,
        file_size=row.file_size,
        extracted_data=row.extracted_data,
        success=row.success,
        error_message=row.error_message,
        retry_count=row.retry_count,
        created_at=row.created_at.isoformat(),
    )
