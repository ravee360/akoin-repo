def validate_corep_output(data: dict, rule_ids: list | None = None) -> dict:
    """
    Validate COREP structured output and add warnings if needed.
    Returns updated data with warnings appended.
    """

    warnings = data.get("warnings", [])
    rule_id_set = set(rule_ids or [])

    required_fields = [
        "CET1_capital",
        "Tier1_capital",
        "Tier2_capital",
        "Total_own_funds"
    ]

    # Improved conceptual detection
    answer_val = data.get("answer")
    is_conceptual = isinstance(answer_val, str) and answer_val.strip() != ""

    # Check missing values (only for reporting scenarios)
    if not is_conceptual:
        for field in required_fields:
            if field not in data or data[field] is None:
                warnings.append(f"{field} is missing or not provided.")

    # Type and negative validation
    for field in required_fields:
        value = data.get(field)

        if value is not None and not isinstance(value, (int, float)):
            warnings.append(f"{field} must be numeric or null.")
            data[field] = None
            continue

        if isinstance(value, (int, float)) and value < 0:
            warnings.append(f"{field} cannot be negative.")

    # Logical consistency
    tier1 = data.get("Tier1_capital")
    tier2 = data.get("Tier2_capital")
    total = data.get("Total_own_funds")

    if isinstance(tier1, (int, float)) and isinstance(tier2, (int, float)) and isinstance(total, (int, float)):
        if total != tier1 + tier2:
            warnings.append(
                "Total_own_funds does not equal Tier1_capital + Tier2_capital."
            )

    # Ensure source_rules structure
    if not isinstance(data.get("source_rules"), dict):
        data["source_rules"] = {}
        warnings.append("source_rules missing or invalid; reset to empty.")

    for field in required_fields:
        if field not in data["source_rules"] or not isinstance(data["source_rules"][field], list):
            data["source_rules"][field] = []

    # Ensure audit_log structure
    if not isinstance(data.get("audit_log"), list):
        data["audit_log"] = []
        warnings.append("audit_log missing or invalid; reset to empty.")

    # Validate audit_log entries
    valid_entries = []
    for entry in data.get("audit_log", []):
        if not isinstance(entry, dict):
            warnings.append("audit_log contains non-object entry.")
            continue

        rule_id = entry.get("rule")
        if rule_id_set and rule_id and rule_id not in rule_id_set:
            warnings.append(f"audit_log cites unknown rule id: {rule_id}")

        valid_entries.append(entry)

    data["audit_log"] = valid_entries

    # Ensure answer field exists
    if "answer" not in data:
        data["answer"] = None
        warnings.append("answer missing; set to null.")

    # Validate cited rule IDs
    for field in required_fields:
        for rule_id in data["source_rules"].get(field, []):
            if rule_id_set and rule_id not in rule_id_set:
                warnings.append(f"{field} cites unknown rule id: {rule_id}")

    data["warnings"] = list(set(warnings))
    return data
