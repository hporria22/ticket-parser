from io import BytesIO

import pandas as pd
from fastapi.responses import StreamingResponse

from config import QUERY_MAPPING

_EXCEL_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def excel_response(buffer: BytesIO, filename: str) -> StreamingResponse:
    """Wrap a BytesIO Excel buffer in a StreamingResponse."""
    return StreamingResponse(
        buffer,
        media_type=_EXCEL_MEDIA_TYPE,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def apply_user_query(ticket_data: dict, user_query: str | None) -> dict:
    """Overlay a user-selected query onto a parsed ticket dict."""
    if user_query:
        ticket_data["Query related to"] = user_query
        ticket_data["Ticket Bucket Group"] = (
            QUERY_MAPPING.get(user_query, {}).get("group", ticket_data.get("Ticket Bucket Group", ""))
        )
    return ticket_data


def tickets_to_excel(tickets: list[dict]) -> BytesIO:
    """Serialize a list of ticket dicts to an in-memory Excel file."""
    output = BytesIO()
    pd.DataFrame(tickets).to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output