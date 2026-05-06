import io
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import QUERY_MAPPING
from helpers import apply_user_query, excel_response, tickets_to_excel
from parser import extract_tickets, parse_ticket, remove_error_before_subcategory
from wo_validator import process_pdf

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

_BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(_BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(_BASE_DIR / "templates"))

_MAX_TICKETS = 200

# ---------------------------------------------------------------------------
# Routes — pages
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {
        "request": request,
        "query_options": list(QUERY_MAPPING.keys()),
    })


@app.get("/validator", response_class=HTMLResponse)
async def validator_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("validator.html", {"request": request})


@app.get("/extractor", response_class=HTMLResponse)
async def extractor_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("extractorPage.html", {"request": request})

# ---------------------------------------------------------------------------
# Routes — processing
# ---------------------------------------------------------------------------

@app.post("/processTickets")
async def process_tickets_bulk(ticket_text: str = Form(...)) -> StreamingResponse:
    """Extract tickets from raw queue text and return as Excel."""
    return excel_response(extract_tickets(ticket_text), "tickets.xlsx")


@app.post("/process")
async def process_tickets(request: Request) -> StreamingResponse:
    """Parse detailed ticket blocks with optional per-ticket query overrides."""
    form = await request.form()
    tickets: list[str] = form.getlist("tickets")

    if len(tickets) > _MAX_TICKETS:
        return {"error": f"Too many tickets. Max limit is {_MAX_TICKETS}."}

    assigned_by_global: str | None = form.get("assigned_by")

    processed = [
        apply_user_query(
            parse_ticket(
                remove_error_before_subcategory(text),
                assigned_by_global,
                form.get(f"assigned_by_ticket_{i}"),
            ),
            form.get(f"query_related_{i}"),
        )
        for i, text in enumerate(tickets, start=1)
    ]

    return excel_response(tickets_to_excel(processed), "tickets.xlsx")


@app.post("/processWO")
async def process_workorder(wo_file: UploadFile = File(...)) -> StreamingResponse:
    """Validate and extract work-order data from an uploaded PDF."""
    pdf_bytes = await wo_file.read()
    return excel_response(process_pdf(io.BytesIO(pdf_bytes)), "workorders.xlsx")