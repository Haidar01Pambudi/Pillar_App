from dataclasses import dataclass

@dataclass(frozen=True)
class Field:
    name: str
    label: str
    kind: str
    group: str
    lookup: str | None = None
    required: bool = False
    in_list: bool = False
    excel: str | None = None

GROUPS = ["Identity", "Location", "Customer", "Configuration", 
          "Status", "Milestones", "Contact & Notes"]

FIELDS: list[Field] = [
    Field("serial_number", "Serial Number", "text", "Identity", required=True, in_list=True),
    Field("contract_name", "Contract Name", "text", "Idendity"),
    Field("brand_name", "Brand Name", "text", "Identity", in_list=True),
    Field("project_name", "Project Name", "text", "Identity", in_list=True),
    Field("project_year", "Project Year", "year", "Identity", in_list=True),
    Field("province_id", "Region", "province", "Location", in_list=True),
    Field("city_id", "City/Regency", "city", "Location"),
    Field("customer_id", "Customer", "lookup", "Customer", lookup="customer", in_list=True),
    Field("customer_division", "Customer Division", "text", "Customer"),
    Field("customer_detail", "Customer Detail", "text", "Customer", in_list=True),
    Field("system_type_id", "System Type", "lookup", "Configuration", lookup="system_type", in_list=True),
    Field("antenna_position_id", "Antenna Position", "lookup", "Configuration", lookup="antenna_position"),
    Field("sw_version_id", "SW Version", "version", "Configuration", in_list=True),
    Field("server_id", "Server", "lookup", "Configuration", lookup="server"),
    Field("interception_module", "Interception Module", "bool", "Configuration"),
    Field("bts_count", "Number of BTS", "int", "Configuration"),
    Field("status_id", "System Status", "lookup", "Status", lookup="system_status", in_list=True),
    Field("hardware_status", "Hardware Status", "text", "Status"),
    Field("date_arrive_jakarta", "Date Arrive in Jakarta", "date", "Milestones"),
    Field("material_check_date", "Date of Material Check", "date", "Milestones"),
    Field("inspection_start", "Inspection Start", "date", "Milestones"),
    Field("inspection_end", "Inspection End", "date", "Milestones"),
    Field("sat_start", "SAT Start", "date", "Milestones"),
    Field("sat_end", "SAT End", "date", "Milestones"),
    Field("training_start", "Training Start", "date", "Milestones"),
    Field("training_end", "Training End", "date", "Milestones"),
    Field("regional_training", "Regional Training", "date", "Milestones"),
    Field("delivery_date", "Date of Delivery", "date", "Milestones"),
    Field("contact_person", "Contact Person", "text", "Contact & Notes"),
    Field("remarks", "Remarks", "textarea", "Contact & Notes"),
    Field("needs_review", "Needs Review", "bool", "Contact & Notes"),
    Field("review_note", "Review Note", "textarea", "Contact & Notes"),
]

BY_NAME = {f.name: f for f in FIELDS}
LABELS = {f.name: f.label for f in FIELDS}
LIST_FIELDS = [f for f in FIELDS if f.in_list]

DATE_PAIRS = [
    ("inspection_start", "inspection_end"),
    ("sat_start", "sat_end"),
    ("training_start", "training_end"),
]