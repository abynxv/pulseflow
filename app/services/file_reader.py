from io import BytesIO

from fastapi import HTTPException, UploadFile

from app.config import settings

SUPPORTED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}


async def read_file_text(file: UploadFile) -> tuple[str, int]:
    """Return (extracted_text, file_size_bytes). Raises HTTPException on bad input."""
    content = await file.read()
    size = len(content)

    if size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size is {settings.max_file_size_mb}MB.",
        )

    content_type = file.content_type or ""
    filename = file.filename or ""

    if content_type == "application/pdf" or filename.endswith(".pdf"):
        text = _read_pdf(content)
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or filename.endswith(".docx"):
        text = _read_docx(content)
    elif content_type.startswith("text/") or filename.endswith(".txt"):
        text = content.decode("utf-8", errors="replace")
    else:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{content_type}'. Supported: PDF, DOCX, TXT.",
        )

    text = text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Could not extract any text from the file.")

    if len(text) > settings.max_text_length:
        text = text[: settings.max_text_length]

    return text, size


def _read_pdf(content: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _read_docx(content: bytes) -> str:
    from docx import Document

    doc = Document(BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
