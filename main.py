from fastapi import FastAPI, File, Request, Form, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from parser import extract_tickets, parse_ticket
from config import QUERY_MAPPING
import pandas as pd
from io import BytesIO
import io
from wo_validator import process_pdf
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "query_options": list(QUERY_MAPPING.keys())
    })

@app.get("/validator", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("validator.html", {"request": request})


@app.get("/extractor", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("extractorPage.html", {"request": request})


@app.post("/processTickets")
def process(ticket_text: str = Form(...)):

    file = extract_tickets(ticket_text)

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=tickets.xlsx"}
    )


@app.post("/process")
async def process_tickets(request: Request):
    form = await request.form()
    tickets = form.getlist("tickets")  # multiple ticket texts

    assigned_by_global = form.get("assigned_by")

    processed_tickets = []

    for i, ticket_text in enumerate(tickets, start=1):
        
        ticket_specific_field = f"assigned_by_ticket_{i}"
        assigned_by_ticket = form.get(ticket_specific_field)
        ticket_data = parse_ticket(ticket_text, assigned_by_global,assigned_by_ticket)


        # user-selected query
        query_field_name = f"query_related_{i}"
        user_query = form.get(query_field_name)

        if user_query:
            ticket_data["Query related to"] = user_query
            ticket_data["Ticket Bucket Group"] = QUERY_MAPPING.get(
                user_query, {}
            ).get("group", ticket_data["Ticket Bucket Group"])

        processed_tickets.append(ticket_data)

    # Convert to Excel
    df = pd.DataFrame(processed_tickets)
    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=tickets.xlsx"}
    )


@app.post("/processWO")
async def process_workorder(wo_file: UploadFile = File(...)):

    pdf_bytes = await wo_file.read()

    excel_file = process_pdf(io.BytesIO(pdf_bytes))

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=workorders.xlsx"
        }
    )