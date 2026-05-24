# ParseFlow

Convert messy documents into clean structured JSON using AI.

Upload an invoice, contract, support ticket, or email — ParseFlow extracts the fields that matter and returns validated, typed JSON ready for any downstream system.

---

## Why this project exists

80% of enterprise AI work is turning unstructured text into structured data so traditional software can use it. ParseFlow solves that problem end-to-end:

- A PDF invoice becomes a typed `Invoice` object with line items, totals, and dates.
- A scanned contract becomes a list of parties, clauses, and key terms.
- A support email becomes a categorized ticket with priority, sentiment, and action items.

---

## How it works

```
PDF / DOCX / TXT
      │
      ▼
  File Reader          extracts raw text from the document
      │
      ▼
  LLM Extractor        sends text + Pydantic schema to the AI model
      │
      ├── Pydantic validates the JSON response
      │
      ├── if validation fails → feeds the error back to the model → retries
      │
      └── on success → saves to PostgreSQL → returns clean JSON
```

The retry loop is the core learning in this project. Models sometimes return `"100 dollars"` when the schema asked for a `float`, or miss a required field. ParseFlow catches those `ValidationError`s, explains them to the model in plain text, and asks it to self-correct — up to 3 times before giving up.

---

## Tech stack and why each piece is here

| Technology | Role | Why |
|---|---|---|
| **FastAPI** | API framework | Auto-generates Swagger UI at `/docs`; async-native for non-blocking I/O |
| **Pydantic v2** | Schema + validation | Strict typed models for each document type; catches bad LLM output |
| **OpenRouter** | LLM provider | One API key, access to dozens of models (OpenAI-compatible format) |
| **PostgreSQL** | Storage | Persists every parse result — raw text, extracted JSON, retry count |
| **SQLAlchemy (async)** | ORM | Async DB access so the API stays non-blocking during DB writes |
| **pypdf / python-docx** | File parsing | Extracts plain text from PDF and Word files before sending to the LLM |
| **Docker** | Containerisation | One command to spin up the database — no local postgres setup needed |

---

## Project structure

```
ParseFlow/
├── app/
│   ├── config.py              # All settings via environment variables
│   ├── database.py            # SQLAlchemy async engine + session
│   ├── db_models.py           # ParseResult table (stores every parse)
│   ├── main.py                # FastAPI app, lifespan, health endpoint
│   ├── schemas/               # Pydantic extraction schemas
│   │   ├── invoice.py         # vendor, line items, totals, dates
│   │   ├── contract.py        # parties, clauses, jurisdiction, term
│   │   ├── ticket.py          # category, priority, sentiment, actions
│   │   └── email.py           # intent, sentiment, entities, actions
│   ├── services/
│   │   ├── extractor.py       # LLM call + retry loop (core logic)
│   │   └── file_reader.py     # PDF / DOCX / TXT text extraction
│   └── routers/
│       └── parse.py           # All API endpoints
├── tests/
│   └── sample_docs/           # Generated test PDFs (run generate_test_pdfs.py)
├── generate_test_pdfs.py      # Creates realistic sample documents for testing
├── docker-compose.yml         # PostgreSQL container
├── Dockerfile                 # Production container for the API
├── requirements.txt
└── .env.example
```

---

## Setup

### 1. Clone and create virtual environment

```bash
git clone <repo-url>
cd ParseFlow
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
OPENAI_API_KEY=sk-or-v1-...        # Your OpenRouter API key
API_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=meta-llama/llama-3.3-70b-instruct:free
DATABASE_URL=postgresql+asyncpg://parseflow:parseflow@localhost:5433/parseflow
```

Get a free OpenRouter key at [openrouter.ai/keys](https://openrouter.ai/keys). No credit card required for free models.

### 3. Start PostgreSQL via Docker

```bash
docker compose up -d db
```

This starts a PostgreSQL container on port `5433`. Tables are created automatically on first run.

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

---

## Testing

### Swagger UI (easiest)

Open `http://localhost:8000/docs` in your browser.

1. Click `POST /api/v1/parse`
2. Click **Try it out**
3. Upload a file from `tests/sample_docs/`
4. Set `document_type` to `auto` (or a specific type)
5. Click **Execute**

Generate the sample docs first if you haven't:

```bash
python generate_test_pdfs.py
```

### Postman

```
POST http://localhost:8000/api/v1/parse?document_type=auto
Body: form-data
  Key: file  (type: File)
  Value: [attach invoice.pdf]
```

### curl

```bash
curl -X POST "http://localhost:8000/api/v1/parse?document_type=invoice" \
  -F "file=@tests/sample_docs/invoice.pdf"
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/parse` | Upload a document, get structured JSON |
| `GET` | `/api/v1/results` | List all parsed results (paginated) |
| `GET` | `/api/v1/results/{id}` | Get a specific result by ID |
| `DELETE` | `/api/v1/results/{id}` | Delete a result |
| `GET` | `/health` | Health check |

**Query params for `/parse`:**

| Param | Values | Default |
|---|---|---|
| `document_type` | `invoice`, `contract`, `ticket`, `email`, `auto` | `auto` |

---

## Example response

```json
{
  "id": "bd456e3e-dd5a-4da8-ba3a-fef51552c5c4",
  "document_type": "invoice",
  "file_name": "invoice.pdf",
  "file_size": 4821,
  "extracted_data": {
    "vendor_name": "Acme Software Ltd.",
    "invoice_number": "INV-2026-0042",
    "invoice_date": "2026-05-20",
    "due_date": "2026-06-20",
    "bill_to": "Nova Indus Pvt. Ltd.",
    "line_items": [
      { "description": "API Integration Module", "quantity": 1, "unit_price": 1200.0, "total": 1200.0 },
      { "description": "Cloud Hosting (monthly)", "quantity": 3, "unit_price": 299.0, "total": 897.0 }
    ],
    "subtotal": 2947.0,
    "tax_rate": 0.08,
    "tax_amount": 235.76,
    "total_amount": 3182.76,
    "currency": "USD",
    "payment_terms": "Net 30"
  },
  "success": true,
  "error_message": null,
  "retry_count": 0,
  "created_at": "2026-05-24T12:00:00+00:00"
}
```

---

## Supported document types

| Type | Key fields extracted |
|---|---|
| **Invoice** | Vendor, invoice number, line items, subtotal, tax, total, currency, payment terms |
| **Contract** | Parties, effective/expiry dates, clauses, jurisdiction, confidentiality, non-compete |
| **Support Ticket** | Category, priority, sentiment, customer info, issue description, action items |
| **Email** | Sender, recipients, intent, sentiment, key entities, action items, priority |

---

## Changing the AI model

Any OpenRouter-compatible model works. Update `OPENAI_MODEL` in `.env`:

```env
# Free models (no credits needed)
OPENAI_MODEL=meta-llama/llama-3.3-70b-instruct:free
OPENAI_MODEL=qwen/qwen3-coder:free

# Paid models (better accuracy)
OPENAI_MODEL=openai/gpt-4o-mini
OPENAI_MODEL=anthropic/claude-3-haiku
```

List all available free models:

```bash
curl -s "https://openrouter.ai/api/v1/models" \
  -H "Authorization: Bearer $OPENAI_API_KEY" | \
  python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] if ':free' in m['id']]"
```

---

## Docker (full stack)

To run both the API and database in containers:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.
