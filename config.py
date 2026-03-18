# config.py

TEAM_MAPPING = {
    "Dot1": [
        # Add Dot1 names here
        "Dilleswari",
        "Rahul",
        "Utkarsh",
        "Abhishek",
        "Pawan",
        "Ajay",
        "Ravindra"
    ],

    "MDM": [
        # Add MDM names here
        "Harsh",
        "Kashish",
        "Ashish",
        "Vipul",
        "Nikita",
        "Jaydeep",
        "Kishan",
        "Roocha",
    ]
}


SUBCATEGORY_MAPPING = {

"L1 - Access request - Power BI Reports": {
    "query": "Power BI Reports",
    "group": "L1"
},

"L1 - Dashboard - KPI Score": {
    "query": "KPI Score",
    "group": "L1"
},

"L1 - General - Password reset": {
    "query": "Password reset",
    "group": "L1"
},

"L1 - Master data - Contractor Master Renewal": {
    "query": "CM update",
    "group": "L1"
},

"L1 - Master data - Contractor onboarding": {
    "query": "Contractor onboarding",
    "group": "L1"
},

"L1 - Master data - Department and Area": {
    "query": "Department and Area",
    "group": "L1"
},

"L1 - Master data - Shift Schedule Pattern / Auto Shift": {
    "query": "Shift Schedule Pattern / Auto Shift",
    "group": "L1"
},

"L1 - Master data - Trade and Skill": {
    "query": "Trade and skill update",
    "group": "L1"
},

"L1 - Master data - Training records": {
    "query": "Training records",
    "group": "L1"
},

"L1 - Master data - User ID activation / deactivation": {
    "query": "User ID activation / deactivation",
    "group": "L1"
},

"L1 - Master data - User ID create / change": {
    "query": "User ID creation",
    "group": "L1"
},

"L1 - Master data - Work Order": {
    "query": "WO update",
    "group": "L1"
},

"L1 - Master data - Workmen wage master / State minimum wage": {
    "query": "Workmen wage master / State minimum wage",
    "group": "L1"
},

"L1 - Mobility - Add Users / Add Locations": {
    "query": "Add Users / Add Locations",
    "group": "L1"
},

"L1 - Paycode/Holiday update": {
    "query": "Paycode/Holiday update",
    "group": "L1"
},

"L1 - Person data cleansing": {
    "query": "Person data cleansing",
    "group": "L1"
},

"L1 - Shift Schedule assignment": {
    "query": "Shift Schedule assignment",
    "group": "L1"
},

"L1 - Transaction - Entry pass cancellation": {
    "query": "EP cancellation",
    "group": "L1"
},

"L1 - Transaction - Entry pass creation": {
    "query": "EP creation",
    "group": "L1"
},

"L1 - Transaction - Entry pass renewal": {
    "query": "EP bulk renewal",
    "group": "L1"
},

"L1 - Transaction - Intra Transfer": {
    "query": "Intra Transfer",
    "group": "L1"
},

"L3 - Change request Bulk import": {
    "query": "Bulk import",
    "group": "L3"
},

"L3 - Change request Enhancement": {
    "query": "Enhancement",
    "group": "L3"
},

"L3 - Pay rule create / update": {
    "query": "Pay rule create / update",
    "group": "L3"
},

"L4 - Change request - Mobility implementation": {
    "query": "Mobility implementation",
    "group": "L4"
},

"L4 - Change Request - New sites roll out": {
    "query": "New sites roll out",
    "group": "L4"
},

"L2 - Application Error - Others": {
    "query": "Application Error",
    "group": "L2"
},

"L2 - Reports - Incomplete/ Error": {
    "query": "Reports",
    "group": "L2"
},

"L2 - Transaction - Bill verification": {
    "query": "Bill verification",
    "group": "L2"
},

"L2 - Transaction data - Attendance": {
    "query": "Attendance",
    "group": "L2"
},

"L2 - Workflow - Error": {
    "query": "Workflow error",
    "group": "L2"
},

"L2 - Workflow / Approval Error": {
    "query": "Approval error",
    "group": "L2"
}


}
# Queries that user can select from frontend
QUERY_MAPPING = {
    "Application error": {"group": "L2"},
    "Attendance": {"group": "L2"},
    "Auto blocking": {"group": "L2"},
    "Auto shift": {"group": "L1"},
    "Bill verification": {"group": "L2"},
    "BRIBS": {"group": "L1"},
    "CM update": {"group": "L1"},
    "CM/EP bulk renewal": {"group": "L1"},
    "Contract Type": {"group": "L1"},
    "Contract Category": {"group": "L1"},
    "Contract Type Change": {"group": "L1"},
    "Contractor onboarding": {"group": "L1"},
    "Department & Area": {"group": "L1"},
    "Device mapping": {"group": "L2"},
    "EIC Update": {"group": "L1"},
    "Email ID Update": {"group": "L1"},
    "Email Notification": {"group": "L2"},
    "EP approval error": {"group": "L2"},
    "EP blocking error": {"group": "L2"},
    "EP bulk renewal": {"group": "L1"},
    "EP cancellation": {"group": "L1"},
    "EP cancellation error": {"group": "L2"},
    "EP creation error": {"group": "L2"},
    "EP renewal error": {"group": "L2"},
    "EP workflow error": {"group": "L2"},
    "EP error": {"group": "L2"},
    "Flexi paycode update": {"group": "L1"},
    "Genetec Issue": {"group": "L2"},
    "Holiday update": {"group": "L1"},
    "Intra transfer": {"group": "L1"},
    "KPI Score": {"group": "L2"},
    "Last Working day": {"group": "L1"},
    "Master data update": {"group": "L1"},
    "Mobility": {"group": "L1"},
    "New Site Roll Out": {"group": "L1"},
    "Not related to Kronos": {"group": "L1"},
    "Password reset": {"group": "L1"},
    "Paycode Update": {"group": "L1"},
    "Payrull Assignments": {"group": "L2"},
    "Person data cleansing": {"group": "L1"},
    "Power BI Access": {"group": "L2"},
    "Punch exception": {"group": "L2"},
    "Punch Report": {"group": "L1"},
    "Punching error": {"group": "L2"},
    "Report": {"group": "L2"},
    "Service Master": {"group": "L1"},
    "Shift Schedule": {"group": "L1"},
    "State minimum wage": {"group": "L1"},
    "Trade & skill update": {"group": "L1"},
    "Training records": {"group": "L1"},
    "Transaction error": {"group": "L2"},
    "User ID activation": {"group": "L1"},
    "User ID Activation/Deactivation": {"group": "L1"},
    "User ID creation": {"group": "L1"},
    "User Information": {"group": "L1"},
    "Wage Master Update": {"group": "L1"},
    "WO Update": {"group": "L1"},
    "WO/CM Update": {"group": "L1"},
    "WO/CM/EP bulk renewal": {"group": "L1"},
    "WO/EP bulk renewal": {"group": "L1"},
    "Workmen upload": {"group": "L3"}
}