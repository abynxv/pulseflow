import json
from dataclasses import dataclass
from typing import Any, Type, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.schemas import SCHEMA_MAP

T = TypeVar("T", bound=BaseModel)

client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.api_base_url)

SYSTEM_PROMPT = """You are a precise document parser. Extract structured information from the document and return it as valid JSON.

The JSON must strictly match this schema:
{schema}

Rules:
- Return ONLY valid JSON, no markdown fences, no extra text.
- Use null for missing optional fields.
- Dates must be ISO 8601 strings (e.g. "2024-01-15").
- Numbers must be numeric types, never strings (e.g. 1500.00 not "1500.00").
- Booleans must be true/false, never "yes"/"no".
"""

AUTO_CLASSIFY_PROMPT = """Classify this document into exactly one of these types:
invoice, contract, ticket, email

Return ONLY the single word — nothing else."""


@dataclass
class ExtractionResult:
    data: dict[str, Any]
    document_type: str
    retry_count: int


async def extract(text: str, document_type: str) -> ExtractionResult:
    """
    Extract structured data from text using the given document type schema.
    Retries up to settings.max_retries times if Pydantic validation fails,
    feeding the validation errors back to the model each attempt.
    """
    if document_type == "auto":
        document_type = await _classify(text)

    schema_class: Type[BaseModel] = SCHEMA_MAP[document_type]
    schema_json = json.dumps(schema_class.model_json_schema(), indent=2)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(schema=schema_json)},
        {"role": "user", "content": f"Extract structured data from this document:\n\n{text}"},
    ]

    last_error: Exception | None = None

    for attempt in range(settings.max_retries):
        raw = await _call_llm(messages)

        try:
            parsed_json = json.loads(raw)
            validated = schema_class.model_validate(parsed_json)
            return ExtractionResult(
                data=validated.model_dump(),
                document_type=document_type,
                retry_count=attempt,
            )
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            # Feed the error back so the model can self-correct
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": (
                    f"Your response failed validation (attempt {attempt + 1}/{settings.max_retries}).\n"
                    f"Errors:\n{exc}\n\n"
                    "Fix the issues and return only valid JSON matching the schema."
                ),
            })

    raise ValueError(
        f"Extraction failed after {settings.max_retries} attempts. "
        f"Last error: {last_error}"
    )


async def _call_llm(messages: list[dict]) -> str:
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0,
    )
    return _strip_fences(response.choices[0].message.content or "")


def _strip_fences(text: str) -> str:
    """Remove markdown code fences that some models wrap JSON in."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # drop opening fence line and closing ```
        inner = lines[1:] if lines[0].startswith("```") else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()
    return text


async def _classify(text: str) -> str:
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": AUTO_CLASSIFY_PROMPT},
            {"role": "user", "content": text[:3000]},
        ],
        temperature=0,
        max_tokens=10,
    )
    label = (response.choices[0].message.content or "").strip().lower()
    if label not in SCHEMA_MAP:
        raise ValueError(
            f"Could not classify document. Model returned: '{label}'. "
            f"Expected one of: {list(SCHEMA_MAP.keys())}"
        )
    return label
