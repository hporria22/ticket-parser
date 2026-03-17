from datetime import datetime
import re
from zoneinfo import ZoneInfo

import pandas as pd
import io
from config import TEAM_MAPPING, SUBCATEGORY_MAPPING


def extract(pattern, text):

    match = re.search(pattern, text, re.MULTILINE)

    if match:
        return match.group(1).strip()

    return ""


def normalize_name(name):
    if not name:
        return ""
    name_lower = name.lower()   
    for team in TEAM_MAPPING:
        for member in TEAM_MAPPING[team]:
            if member.lower() in name_lower:
                return member
    return name.strip()

def get_assigned_by(ticket_text):
    """
    Captures the person who did the action immediately before 'Assigned to',
    but only if the person is in Dot1 or MDM team.
    """
    # Pattern: person line before Field changes + Assigned to
    pattern = r"([A-Za-z .]+)\s*\nField changes.*?\nAssigned to"
    matches = re.findall(pattern, ticket_text, flags=re.DOTALL)
    print("DEBUG -> get_assigned_by matches:", matches)  # Debug print
    if matches:
        candidate = matches[-1].strip()  # take the last occurrence
        # Check if candidate is in Dot1 or MDM
        for team in ["Dot1", "MDM"]:
            for member in TEAM_MAPPING.get(team, []):
                if member.lower() == candidate.lower():
                    return member  # return normalized member name
    return ""  # not in allowed teams


def detect_team(assigned_to):

    for name in TEAM_MAPPING["Dot1"]:
        if name.lower() in assigned_to.lower():
            return "Dot1"

    for name in TEAM_MAPPING["MDM"]:
        if name.lower() in assigned_to.lower():
            return "MDM"

    return ""


def detect_category(ticket_text):

    for category in SUBCATEGORY_MAPPING:

        if category.lower() in ticket_text.lower():

            query = SUBCATEGORY_MAPPING[category]["query"]
            group = SUBCATEGORY_MAPPING[category]["group"]

            return category, query, group

    return "", "", ""


def parse_ticket(ticket_text, assigned_by_global,assigned_by_ticket):

    ticket_number = extract(r"(RITM\d+|INC\d+)", ticket_text)

    opened = extract(r"Opened\s+([0-9/]+\s+[0-9:]+\s+[APM]+)", ticket_text)

    ticket_date = ""
    ticket_time = ""

    if opened:
       parts = opened.split()
       if len(parts) >= 3:
        dt = datetime.strptime(f"{parts[0]} {parts[1]} {parts[2]}", "%d/%m/%Y %H:%M:%S %p")
        ticket_date = dt.strftime("%m-%d-%Y")
        ticket_time = dt.strftime("%I:%M:%S %p")

    action = extract(r"([0-9/]+\s+[0-9:]+\s+[APM]+)\s+Assigned", ticket_text)

    processed_date = ""
    action_time = ""

    if action:
        parts = action.split()
        if len(parts) >= 3:
         dt = datetime.strptime(f"{parts[0]} {parts[1]} {parts[2]}", "%d/%m/%Y %H:%M:%S %p")
         processed_date = dt.strftime("%m-%d-%Y")
         action_time = dt.strftime("%I:%M:%S %p")

# If still empty
    if not processed_date or not action_time: 
         now = datetime.now(ZoneInfo("Asia/Kolkata"))
         processed_date = now.strftime("%m-%d-%Y")
         action_time = now.strftime("%I:%M:%S %p")

    state = extract(r"State\s+([^\n]+)", ticket_text)

    if state.lower() == "new":
        state = "In Progress"
    elif state.lower() == "resolved":
        state = "Resolved"
    else:
        state = "Closed Incomplete"


    assigned_to_raw = extract(r"Assigned to\s+([A-Za-z .]+)", ticket_text)
    assigned_to = normalize_name(assigned_to_raw)

    if assigned_by_ticket:
        assigned_by = assigned_by_ticket
    elif assigned_by_global:
        assigned_by = assigned_by_global
    else:
        assigned_by = get_assigned_by(ticket_text)

    assigned_by = normalize_name(assigned_by)

    business = extract(r"Business Unit\s+([^\n]+)", ticket_text)

    category, query, group = detect_category(ticket_text)
    team = detect_team(assigned_to)

    resolvedDate = ""
    tat = ""
    tat_to = "" 
    resolvedField = ""

    justNow = datetime.now(ZoneInfo("Asia/Kolkata"))

    if state == "Resolved":
        resolvedField = "Resolved"
        resolvedDate = justNow.strftime("%m-%d-%Y")
        tat = (datetime.strptime(resolvedDate, "%m-%d-%Y") -datetime.strptime(ticket_date, "%m-%d-%Y")).days
        if team == "Dot1" :
           tat_to = '0'
        elif team == 'MDM':
            tat_to = '-'
    elif state == "Closed Incomplete":
        resolvedField = "Closed Incomplete"
        resolvedDate = justNow.strftime("%m-%d-%Y")
        tat = (datetime.strptime(resolvedDate, "%m-%d-%Y") - datetime.strptime(ticket_date, "%m-%d-%Y")).days
        if team == "Dot1" :
           tat_to = '0'
        elif team == 'MDM':
            tat_to = '-'
    else : 
        resolvedField = ""

    return {

        "Ticket Date": ticket_date,
        "Ticket Time": ticket_time,
        "Ticket Number": ticket_number,
        "Business Type": business,
        "Sub Category": category,
        "Ticket processed date": processed_date,
        "Action time": action_time,
        "Status": state,
        "Forwarded to Dot1 or MDM": team,
        "Assigned to": assigned_to,
        "Assigned by": assigned_by,
        "Query related to": query,
        "Ticket Bucket Group": group,
        "Remarks": "",
        "Resolved": resolvedField or "",
        "Resolved date":resolvedDate or "",
        "TAT": tat,
        "TAT to Dot1/MDM":tat_to or ""
    }


def extract_tickets(text):

    rows = []
    lines = text.splitlines()

    order = 0

    for i in range(len(lines)):

        ticket_match = re.search(r'(RITM\d+|INC\d+)', lines[i])

        if ticket_match:

            order += 1
            ticket = ticket_match.group()

            time = ""
            if i + 1 < len(lines):

                time_match = re.search(r'\d{2}:\d{2}:\d{2}\s?(AM|PM)', lines[i+1])

                if time_match:
                    time = time_match.group()

            business = ""
            if i + 2 < len(lines):

                parts = lines[i+2].split("\t")

                if len(parts) > 0:
                    business = parts[-1]

            rows.append({
                "Order": order,
                "Time": time,
                "Ticket Number": ticket,
                "Business": business,
                "Blank1": "",
                "Blank2": "",
                "Blank3": "",
                "Status": "In Progress"
            })

    df = pd.DataFrame(rows)

    df = df.sort_values("Order").drop(columns=["Order"])

    output = io.BytesIO()

    df.to_excel(output, index=False)

    output.seek(0)

    return output