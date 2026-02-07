from schema import COREP_SCHEMA


def format_to_table(data: dict) -> list:
    table = []

    fields = [
        ("CET1 Capital", data.get("CET1_capital")),
        ("Tier 1 Capital", data.get("Tier1_capital")),
        ("Tier 2 Capital", data.get("Tier2_capital")),
        ("Total Own Funds", data.get("Total_own_funds")),
    ]

    for field_name, value in fields:
        table.append({
            "Field": field_name,
            "Value": value if value is not None else "Not provided"
        })

    return table


def format_warnings(data: dict) -> list:
    return data.get("warnings", [])


def format_sources(data: dict) -> dict:
    """
    Extract source rules for display.
    """
    return data.get("source_rules", {})


def format_template_extract(data: dict) -> list:
    rows = []

    field_map = {
        "CET1_capital": data.get("CET1_capital"),
        "Tier1_capital": data.get("Tier1_capital"),
        "Tier2_capital": data.get("Tier2_capital"),
        "Total_own_funds": data.get("Total_own_funds"),
    }

    id_map = {f["name"]: f["id"] for f in COREP_SCHEMA["fields"]}
    source_rules = data.get("source_rules", {})

    for field_name, value in field_map.items():
        rows.append({
            "Template": COREP_SCHEMA["template"],
            "Field_ID": id_map.get(field_name, "UNKNOWN"),
            "Field_Name": field_name,
            "Value": value if value is not None else "Not provided",
            "Sources": source_rules.get(field_name, [])
        })

    return rows


def format_summary(data: dict) -> str:
    parts = []
    parts.append("COREP Own Funds Summary")

    if data.get("answer"):
        parts.append("Explanation:")
        parts.append(data["answer"])
        return "\n".join(parts)

    def safe_value(v):
        return v if v is not None else "Not provided"

    parts.append(f"- CET1 capital: {safe_value(data.get('CET1_capital'))}")
    parts.append(f"- Tier 1 capital: {safe_value(data.get('Tier1_capital'))}")
    parts.append(f"- Tier 2 capital: {safe_value(data.get('Tier2_capital'))}")
    parts.append(f"- Total own funds: {safe_value(data.get('Total_own_funds'))}")

    warnings = data.get("warnings", [])
    if warnings:
        parts.append("Warnings:")
        for w in warnings:
            parts.append(f"- {w}")

    return "\n".join(parts)
