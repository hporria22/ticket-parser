import pdfplumber
import re
import pandas as pd
from io import BytesIO
from datetime import datetime

COLUMNS = [
"Document_Number","Item","Line","Line_Number","Activity_Number",
"Short_Text","Delivery_Complition","Item_Changed_ON","Vendor",
"Vendor_Name","Address","Blocked_Vendor","Work_Order_Validity_From",
"Work_Order_Validity_To","Work_Order_Type","Plant_Code","Section_Code",
"Department_Code","GL_Code","Cost_Center","Job","Rate","Quantity",
"Base_Unit_of_Measure","Work_Order_Released","PM_Order_No","WBS_Element",
"Quantity_Completed","Work_Order_Release_Date","Service_Entry_Created_Date",
"Service_Entry_Updated_Date","Purchase_Org_Level","Company_code"
]


def clean_number(value):
    """Remove leading and trailing zeros"""
    if not value:
        return ""

    value = value.strip()

    if value.isdigit():
        value = value.lstrip("0")

    if "." in value:
        value = value.rstrip("0").rstrip(".")

    return value


def format_date(value):
    """Convert date to DD-MM-YYYY text"""
    if not value:
        return ""

    try:
        date_obj = datetime.strptime(value, "%d.%m.%Y")
        return date_obj.strftime("%d-%m-%Y")
    except:
        return value


def extract_field(text, field):

    pattern = rf"{field}\s*:\s*(.*)"
    match = re.search(pattern, text)

    if match:
        return match.group(1).strip()

    return ""


def create_empty_row():

    row = {col: "" for col in COLUMNS}

    # Static values
    row["Item"] = "10"
    row["Line"] = "1"
    row["Line_Number"] = "10"
    row["Short_Text"] = "Supply of Services"
    row["Work_Order_Type"] = "ZSER"
    row["Job"] = "Supply of services"
    row["Rate"] = "1"
    row["Quantity"] = "1"
    row["Base_Unit_of_Measure"] = "MON"
    row["Work_Order_Released"] = "R"
    row["Purchase_Org_Level"] = "1000"
    row["Company_code"] = "1000"

    return row

def extract_state(text):

    match = re.search(r"\b([A-Z]+),INDIA\b", text)

    if match:
        return match.group(1).upper()

    return ""

def extract_completion_date(text):

    match = re.search(r"Completion.*?(\d{2}\.\d{2}\.\d{4})", text, re.S)

    if match:
        date_obj = datetime.strptime(match.group(1), "%d.%m.%Y")
        return date_obj.strftime("%d-%m-%Y")

    return ""


def extract_vendor(text):

    match = re.search(r"Vendor Code\s*:\s*(\d+)", text)

    if match:
        return str(int(match.group(1)))  # removes leading zeros

    return ""

def extract_vendor_name(text):

    match = re.search(r"Contractor's details\s*\n\s*([A-Z\s]+)", text)

    if match:
        return match.group(1).strip()

    return ""

def process_pdf(pdf_bytes):

    text = ""

    with pdfplumber.open(pdf_bytes) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    row = create_empty_row()

    # Extract required fields
    row["Document_Number"] = clean_number(extract_field(text, "SO No"))
    row["Vendor"] = extract_vendor(text)
    row["Vendor_Name"] = extract_vendor_name(text)
    row["Address"] = extract_state(text)

    row["Work_Order_Validity_From"] = format_date(
        extract_field(text, "SO Release Date")
    )

    row["Work_Order_Validity_To"] = extract_completion_date(text)

    row["Plant_Code"] = extract_field(text, "Plant")

    row["Work_Order_Release_Date"] = row["Work_Order_Validity_From"]

    df = pd.DataFrame([row], columns=COLUMNS)

    # Force everything to text
    df = df.astype(str)

    output = BytesIO()
    df.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)

    return output