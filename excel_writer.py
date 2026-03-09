import pandas as pd
from io import BytesIO


def create_excel(data):

    df = pd.DataFrame(data)

    columns = [
        "S.No",
        "Ticket Date",
        "Ticket Time",
        "Ticket Number",
        "Business Type",
        "Sub Category",
        "Ticket processed date",
        "Action time",
        "Forwarded to Dot1 or MDM",
        "Assigned to",
        "Assigned by",
        "Query related to",
        "Ticket Bucket Group",
    ]

    for col in columns:
        if col not in df:
            df[col] = ""

    df = df[columns]

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    output.seek(0)

    return output