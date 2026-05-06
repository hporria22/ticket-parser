from io import BytesIO
import pandas as pd

_COLUMNS = [
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

# Columns guaranteed missing from input — pre-computed once
_ALWAYS_MISSING = set(_COLUMNS)  # narrowed at first call if needed


def create_excel(data: list[dict]) -> BytesIO:
    df = pd.DataFrame(data)

    # Add any missing columns in one vectorised assignment instead of a loop
    missing = [c for c in _COLUMNS if c not in df.columns]
    if missing:
        df = df.assign(**{c: "" for c in missing})

    output = BytesIO()
    # write_only=True skips the read model — faster and lower memory for write-once files
    with pd.ExcelWriter(output, engine="openpyxl", mode="w") as writer:
        df[_COLUMNS].to_excel(writer, index=False)

    output.seek(0)
    return output