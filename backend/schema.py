COREP_SCHEMA = {
    "template": "COREP Own Funds (Prototype)",
    "fields": [
        {"id": "OF.CET1", "name": "CET1_capital", "type": "number | null"},
        {"id": "OF.T1", "name": "Tier1_capital", "type": "number | null"},
        {"id": "OF.T2", "name": "Tier2_capital", "type": "number | null"},
        {"id": "OF.TOTAL", "name": "Total_own_funds", "type": "number | null"},
    ],
    "metadata": {
        "answer": "short natural-language explanation for conceptual questions",
        "source_rules": "object mapping field name -> list of rule paragraph references",
        "audit_log": "list of {field, rule, excerpt} entries for populated fields",
        "warnings": "list of strings"
    }
}
