"""Run this once to generate sample test PDFs in the tests/ folder."""
from fpdf import FPDF
from pathlib import Path

OUT = Path("tests/sample_docs")
OUT.mkdir(parents=True, exist_ok=True)


def make_invoice():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "INVOICE", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "From:  Acme Software Ltd.", ln=True)
    pdf.cell(0, 8, "       12 Tech Park, San Francisco, CA 94105", ln=True)
    pdf.cell(0, 8, "       billing@acmesoftware.com", ln=True)
    pdf.ln(4)
    pdf.cell(0, 8, "Bill To:  Nova Indus Pvt. Ltd.", ln=True)
    pdf.cell(0, 8, "          88 Innovation Drive, Bangalore, India 560001", ln=True)
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(60, 8, "Invoice Number:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "INV-2026-0042", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(60, 8, "Invoice Date:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "2026-05-20", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(60, 8, "Due Date:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "2026-06-20", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(60, 8, "Payment Terms:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Net 30", ln=True)
    pdf.ln(6)

    # Table header
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(80, 9, "Description", border=1, fill=True)
    pdf.cell(25, 9, "Qty", border=1, fill=True, align="C")
    pdf.cell(35, 9, "Unit Price", border=1, fill=True, align="C")
    pdf.cell(40, 9, "Total", border=1, fill=True, align="C")
    pdf.ln()

    # Line items
    pdf.set_font("Helvetica", "", 11)
    items = [
        ("API Integration Module", 1, 1200.00),
        ("Cloud Hosting (monthly)", 3, 299.00),
        ("Priority Support Package", 1, 450.00),
        ("Developer License x5", 5, 80.00),
    ]
    for desc, qty, price in items:
        total = qty * price
        pdf.cell(80, 8, desc, border=1)
        pdf.cell(25, 8, str(qty), border=1, align="C")
        pdf.cell(35, 8, f"${price:,.2f}", border=1, align="R")
        pdf.cell(40, 8, f"${total:,.2f}", border=1, align="R")
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(140, 8, "Subtotal:", align="R")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(40, 8, "$2,947.00", align="R", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(140, 8, "Tax (8%):", align="R")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(40, 8, "$235.76", align="R", ln=True)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(140, 10, "TOTAL DUE:", align="R")
    pdf.cell(40, 10, "$3,182.76 USD", align="R", ln=True)

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 8, "Payment via bank transfer to: Account 1234567890 | Routing 021000021", ln=True)
    pdf.cell(0, 8, "Late payments subject to 1.5% monthly interest.", ln=True)

    pdf.output(OUT / "invoice.pdf")
    print("Created invoice.pdf")


def make_contract():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "SOFTWARE SERVICES AGREEMENT", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    body = [
        ("Parties", (
            "This Software Services Agreement (the \"Agreement\") is entered into as of "
            "January 1, 2026 by and between:\n\n"
            "  Client:   Nova Indus Pvt. Ltd., a company incorporated under the laws of India,\n"
            "            having its principal office at 88 Innovation Drive, Bangalore 560001.\n\n"
            "  Vendor:   Acme Software Ltd., a corporation incorporated in the State of California,\n"
            "            having its principal office at 12 Tech Park, San Francisco, CA 94105."
        )),
        ("Term", (
            "This Agreement shall commence on January 1, 2026 and shall remain in full force "
            "and effect until December 31, 2026, unless earlier terminated in accordance with "
            "the provisions hereof."
        )),
        ("Services", (
            "Vendor agrees to provide the following services: API development, cloud "
            "infrastructure management, and tier-1 technical support. Detailed specifications "
            "are outlined in Schedule A attached hereto."
        )),
        ("Payment Terms", (
            "Client shall pay Vendor a monthly retainer of USD 3,182.76 due within 30 days "
            "of each invoice date. Late payments shall accrue interest at 1.5% per month."
        )),
        ("Confidentiality", (
            "Each party agrees to hold the other party's Confidential Information in strict "
            "confidence and not to disclose such information to any third parties without "
            "prior written consent. This obligation survives termination of the Agreement."
        )),
        ("Non-Compete", (
            "During the term and for 12 months thereafter, Vendor shall not directly solicit "
            "or engage Client's employees or clients without prior written approval."
        )),
        ("Governing Law", (
            "This Agreement shall be governed by and construed in accordance with the laws "
            "of the State of California, United States, without regard to conflict of law "
            "principles. Disputes shall be resolved by binding arbitration in San Francisco, CA."
        )),
        ("Termination", (
            "Either party may terminate this Agreement with 30 days written notice. Client may "
            "terminate immediately for cause if Vendor materially breaches this Agreement and "
            "fails to cure such breach within 15 days of notice."
        )),
    ]

    for title, text in body:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 9, title, ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, text)
        pdf.ln(3)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(95, 8, "For Nova Indus Pvt. Ltd.:", ln=False)
    pdf.cell(0, 8, "For Acme Software Ltd.:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(95, 8, "Signature: ___________________", ln=False)
    pdf.cell(0, 8, "Signature: ___________________", ln=True)
    pdf.cell(95, 8, "Name: Arjun Menon", ln=False)
    pdf.cell(0, 8, "Name: Sarah Mitchell", ln=True)
    pdf.cell(95, 8, "Title: CEO", ln=False)
    pdf.cell(0, 8, "Title: VP Sales", ln=True)

    pdf.output(OUT / "contract.pdf")
    print("Created contract.pdf")


def make_ticket():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "CUSTOMER SUPPORT TICKET", ln=True, align="C")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(50, 8, "Ticket ID:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "TKT-20260524-9981", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(50, 8, "Date Submitted:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "2026-05-24 09:15 UTC", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(50, 8, "Customer Name:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Riya Thomas", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(50, 8, "Customer Email:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "riya.thomas@noviindus.com", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(50, 8, "Product:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "ParseFlow API v1.0", ln=True)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(50, 8, "Subject:", border=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "API returning 500 error on large PDF uploads", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 9, "Issue Description:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, (
        "Hi team,\n\n"
        "I've been using ParseFlow for the past two weeks and it's been great for smaller files. "
        "However, I'm now trying to parse PDFs that are between 8-10 MB in size and I'm consistently "
        "getting a 500 Internal Server Error response with no useful error message in the body.\n\n"
        "This is blocking our production rollout scheduled for next week. We have over 200 documents "
        "queued and cannot proceed. I've tried reducing file size but our documents cannot be split.\n\n"
        "Steps to reproduce:\n"
        "1. Upload any PDF larger than 7 MB via POST /api/v1/parse\n"
        "2. Select document_type = invoice\n"
        "3. Receive 500 error after approximately 30 seconds\n\n"
        "Expected: Successful extraction or a clear error message with guidance.\n"
        "Actual: 500 Internal Server Error with empty response body.\n\n"
        "Please escalate this urgently. This is blocking a client delivery."
    ))

    pdf.output(OUT / "support_ticket.pdf")
    print("Created support_ticket.pdf")


def make_email():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", "B", 14)
    pdf.cell(0, 10, "EMAIL MESSAGE", ln=True, align="C")
    pdf.ln(2)

    pdf.set_font("Courier", "", 11)
    headers = [
        ("From", "arjun.menon@noviindus.com"),
        ("To", "sarah.mitchell@acmesoftware.com"),
        ("CC", "support@acmesoftware.com"),
        ("Date", "Mon, 24 May 2026 10:30:00 +0530"),
        ("Subject", "Request: Additional API rate limit increase for Q2"),
    ]
    for key, val in headers:
        pdf.set_font("Courier", "B", 11)
        pdf.cell(25, 7, f"{key}:", border=0)
        pdf.set_font("Courier", "", 11)
        pdf.cell(0, 7, val, ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, (
        "Hi Sarah,\n\n"
        "Hope you're doing well. Following our call last Thursday, I wanted to formally request "
        "an increase to our API rate limit from the current 100 requests/minute to 500 requests/minute "
        "for the period of June 1 to July 31, 2026.\n\n"
        "We have an upcoming product launch campaign and expect a significant spike in document "
        "processing volume. Our current limit is already being hit during peak hours, causing "
        "delays in our automated pipeline.\n\n"
        "Specifically we need:\n"
        "- Rate limit: 500 req/min (from current 100 req/min)\n"
        "- Duration: June 1 - July 31, 2026 (2 months)\n"
        "- Scope: Production API key only\n\n"
        "We understand there may be additional costs involved and are happy to discuss pricing. "
        "Could you please confirm if this is possible and share the next steps?\n\n"
        "This is time-sensitive as we need to configure our systems before June 1.\n\n"
        "Thanks,\nArjun Menon\nCEO, Nova Indus Pvt. Ltd.\n+91-98765-43210"
    ))

    pdf.output(OUT / "email.pdf")
    print("Created email.pdf")


if __name__ == "__main__":
    make_invoice()
    make_contract()
    make_ticket()
    make_email()
    print(f"\nAll PDFs saved to {OUT.resolve()}")
