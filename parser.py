import io
import re
from datetime import datetime
from difflib import get_close_matches
from zoneinfo import ZoneInfo

import pandas as pd

from config import TEAM_MAPPING, SUBCATEGORY_MAPPING

# ---------------------------------------------------------------------------
# Pure helpers — defined first so they can be used in the lookup tables below
# ---------------------------------------------------------------------------

def _norm(text: str) -> str:
    """Lowercase + collapse whitespace."""
    return " ".join(text.strip().lower().split())


def _parse_dt(raw: str) -> datetime | None:
    try:
        return datetime.strptime(raw, "%d/%m/%Y %I:%M:%S %p")
    except (ValueError, TypeError):
        return None


def _now_ist() -> datetime:
    return datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)


def _fmt_date(dt: datetime) -> str:
    return dt.strftime("%m-%d-%Y")


def _fmt_time(dt: datetime) -> str:
    return dt.strftime("%I:%M:%S %p")


# ---------------------------------------------------------------------------
# Pre-built lookup tables  (built ONCE at import — O(1) access everywhere)
# ---------------------------------------------------------------------------

# { "dilleswari": ("Dilleswari", "Dot1"), "harsh": ("Harsh", "MDM"), ... }
_MEMBER_TO_TEAM: dict[str, tuple[str, str]] = {
    member.lower(): (member, team)
    for team, members in TEAM_MAPPING.items()
    for member in members
}

# Normalised subcategory key → raw mapping dict
_SUBCATEGORY_NORM: dict[str, dict] = {
    _norm(k): v for k, v in SUBCATEGORY_MAPPING.items()
}
# Normalised key → original-cased key (needed for the return value)
_SUBCATEGORY_ORIG: dict[str, str] = {
    _norm(k): k for k in SUBCATEGORY_MAPPING
}

# Fuzzy-match candidate list — built once, reused on every mismatch
_SUBCATEGORY_KEYS: list[str] = list(_SUBCATEGORY_NORM)

# ---------------------------------------------------------------------------
# Compiled regex patterns  (compiled ONCE at import)
# ---------------------------------------------------------------------------

_RE_TICKET_NUM  = re.compile(r"(RITM\d+|INC\d+)", re.MULTILINE)
_RE_OPENED      = re.compile(r"Opened\s+([0-9/]+\s+[0-9:]+\s+[AP]M+)", re.MULTILINE)
_RE_ACTION      = re.compile(r"([0-9/]+\s+[0-9:]+\s+[AP]M+)\s+Assigned", re.MULTILINE)
_RE_ASSIGNED_TO = re.compile(r"Assigned to\s+([A-Za-z .]+)", re.MULTILINE)
_RE_BUSINESS    = re.compile(r"Business Unit\s+([^\n]+)", re.MULTILINE)
_RE_STATE       = re.compile(r"State\s*\n\s*([^\n]+)", re.MULTILINE)
_RE_SUBCATEGORY = re.compile(r"Subcategory\s*[:\-]?\s*(.+)", re.MULTILINE)
_RE_ASSIGNED_BY = re.compile(
    r"([A-Za-z .]+)\s*\nField changes.*?\nAssigned to", re.DOTALL
)
_RE_RESOLVED_DT = re.compile(
    r"Field changes•([\d]{2}/[\d]{2}/[\d]{4}).*?State\s*Resolved\s*was\s*In Progress",
    re.DOTALL,
)
_RE_ERROR_BLOCK = re.compile(
    r"Error Message.*?Actual Subcategory\s*", re.IGNORECASE | re.DOTALL
)
_RE_TICKET_LINE = re.compile(r"(RITM\d+|INC\d+)")
_RE_TIME_LINE   = re.compile(r"\d{2}:\d{2}:\d{2}\s?(?:AM|PM)")

# State normalisation map
_STATE_MAP: dict[str, str] = {
    "new":         "In Progress",
    "in progress": "In Progress",
    "resolved":    "Resolved",
    "on hold":     "Hold",
}

# ---------------------------------------------------------------------------
# Small private extractor
# ---------------------------------------------------------------------------

def _extract(pattern: re.Pattern, text: str) -> str:
    m = pattern.search(text)
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def remove_error_before_subcategory(text: str) -> str:
    return _RE_ERROR_BLOCK.sub("", text).strip()


def normalize_name(name: str) -> str:
    if not name:
        return ""
    entry = _MEMBER_TO_TEAM.get(name.strip().lower())
    return entry[0] if entry else name.strip()


def get_assigned_by(ticket_text: str) -> str:
    matches = _RE_ASSIGNED_BY.findall(ticket_text)
    if not matches:
        return ""
    entry = _MEMBER_TO_TEAM.get(matches[-1].strip().lower())
    return entry[0] if entry else ""


def detect_team(assigned_to: str) -> str:
    entry = _MEMBER_TO_TEAM.get(assigned_to.strip().lower())
    return entry[1] if entry else ""


def detect_category(ticket_text: str) -> tuple[str, str, str]:
    raw = _extract(_RE_SUBCATEGORY, ticket_text)
    if not raw:
        return "", "", ""

    sub_norm = _norm(raw)

    # O(1) exact match
    data = _SUBCATEGORY_NORM.get(sub_norm)
    if data:
        return _SUBCATEGORY_ORIG[sub_norm], data["query"], data["group"]

    # Fuzzy fallback — only reached on a genuine mismatch
    close = get_close_matches(sub_norm, _SUBCATEGORY_KEYS, n=1, cutoff=0.6)
    if close:
        data = _SUBCATEGORY_NORM[close[0]]
        return _SUBCATEGORY_ORIG[close[0]], data["query"], data["group"]

    return "", "", ""


def extract_resolved_date(text: str) -> str:
    matches = _RE_RESOLVED_DT.findall(text)
    if matches:
        return datetime.strptime(matches[-1].strip(), "%d/%m/%Y").strftime("%m-%d-%Y")
    return _now_ist().strftime("%m-%d-%Y")


def parse_ticket(
    ticket_text: str,
    assigned_by_global: str | None,
    assigned_by_ticket: str | None,
) -> dict:

    # --- identifiers ---
    ticket_number = _extract(_RE_TICKET_NUM, ticket_text)

    # --- opened date/time ---
    opened_dt     = _parse_dt(_extract(_RE_OPENED, ticket_text))
    ticket_date   = _fmt_date(opened_dt) if opened_dt else ""
    ticket_time   = _fmt_time(opened_dt) if opened_dt else ""

    # --- action date/time (fallback: now) ---
    action_dt = _parse_dt(_extract(_RE_ACTION, ticket_text))
    if action_dt:
        processed_date = _fmt_date(action_dt)
        action_time    = _fmt_time(action_dt)
    else:
        now            = _now_ist()
        processed_date = _fmt_date(now)
        action_time    = _fmt_time(now)

    # --- state ---
    state = _STATE_MAP.get(_extract(_RE_STATE, ticket_text).lower(), "Closed Incomplete")

    # --- people ---
    assigned_to = normalize_name(_extract(_RE_ASSIGNED_TO, ticket_text))
    assigned_by = normalize_name(
        assigned_by_ticket or assigned_by_global or get_assigned_by(ticket_text)
    )

    # --- other fields ---
    business = _extract(_RE_BUSINESS, ticket_text)
    category, query, group = detect_category(ticket_text)
    team = detect_team(assigned_to)

    # --- resolved / TAT ---
    resolved_field = resolved_date = ""
    tat: int | None = None
    tat_to: str | None = None

    if state in ("Resolved", "Closed Incomplete"):
        resolved_field = state
        resolved_date  = (
            extract_resolved_date(ticket_text)
            if state == "Resolved"
            else _now_ist().strftime("%m-%d-%Y")
        )
        if ticket_date:
            tat = (
                datetime.strptime(resolved_date, "%m-%d-%Y")
                - datetime.strptime(ticket_date, "%m-%d-%Y")
            ).days
        tat_to = "0" if team == "Dot1" else ("-" if team == "MDM" else None)

    return {
        "Ticket Date":              ticket_date,
        "Ticket Time":              ticket_time,
        "Ticket Number":            ticket_number,
        "Business Type":            business,
        "Sub Category":             category,
        "Ticket processed date":    processed_date,
        "Action time":              action_time,
        "Status":                   state,
        "Forwarded to Dot1 or MDM": team,
        "Assigned to":              assigned_to,
        "Assigned by":              assigned_by,
        "Query related to":         query,
        "Ticket Bucket Group":      group,
        "Remarks":                  "",
        "Resolved":                 resolved_field or None,
        "Resolved date":            resolved_date  or None,
        "TAT":                      tat,
        "TAT to Dot1/MDM":          tat_to,
    }


def extract_tickets(text: str) -> io.BytesIO:
    rows = []
    lines = text.splitlines()

    for i, line in enumerate(lines):
        m = _RE_TICKET_LINE.search(line)
        if not m:
            continue

        time_val = ""
        if i + 1 < len(lines):
            tm = _RE_TIME_LINE.search(lines[i + 1])
            if tm:
                time_val = tm.group()

        business = ""
        if i + 2 < len(lines):
            parts = lines[i + 2].split("\t")
            business = parts[-1] if parts else ""

        rows.append({
            "Time":          time_val,
            "Ticket Number": m.group(),
            "Business":      business,
            "Blank1": "", "Blank2": "", "Blank3": "",
            "Status":        "In Progress",
        })

    output = io.BytesIO()
    pd.DataFrame(rows).to_excel(output, index=False)
    output.seek(0)
    return output