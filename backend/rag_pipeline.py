import json
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from vectorstore import get_retriever
from config import MODEL_NAME
from prompt_template import PROMPT_TEMPLATE
from validator import validate_corep_output   # <-- added


# Initialize prompt once
PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)


def get_llm():
    return ChatGroq(
        model_name=MODEL_NAME,
        temperature=0.1
    )


def build_rule_id(metadata: dict) -> str:
    source = metadata.get("source_file", "unknown")
    page = metadata.get("page_number", "na")
    chunk_id = metadata.get("chunk_id", "na")
    return f"{source}-p{page}-c{chunk_id}"


def has_numeric_values(text: str) -> bool:
    return bool(re.search(r"\d", text))


def run_rag_pipeline(question: str):

    retriever = get_retriever()
    llm = get_llm()

    docs = retriever.invoke(question)

    rule_lookup = {}
    context_blocks = []

    for doc in docs:
        rule_id = build_rule_id(doc.metadata)
        rule_lookup[rule_id] = doc.page_content

        context_blocks.append(
            f"[RuleID: {rule_id}]\n{doc.page_content}"
        )

    context = "\n\n".join(context_blocks)

    formatted_prompt = PROMPT.format(
        context=context,
        question=question
    )

    response = llm.invoke(formatted_prompt).content.strip()

    # ---- Parse JSON safely ----
    try:
        structured_output = json.loads(response)
    except json.JSONDecodeError:
        structured_output = {
            "answer": response[:400],
            "CET1_capital": None,
            "Tier1_capital": None,
            "Tier2_capital": None,
            "Total_own_funds": None,
            "source_rules": {},
            "audit_log": [],
            "warnings": ["LLM returned invalid JSON; raw answer provided"]
        }

    # ---- Mode adjustment ----
    if not has_numeric_values(question):
        structured_output["CET1_capital"] = None
        structured_output["Tier1_capital"] = None
        structured_output["Tier2_capital"] = None
        structured_output["Total_own_funds"] = None

    # ---- Enrich audit log ----
    audit_log = structured_output.get("audit_log", [])
    if isinstance(audit_log, list):
        for entry in audit_log:
            if isinstance(entry, dict):
                rule_id = entry.get("rule")
                if rule_id and rule_id in rule_lookup:
                    excerpt = rule_lookup[rule_id].strip().replace("\n", " ")
                    entry["excerpt"] = excerpt[:240]

    # ---- Validate output ----
    structured_output = validate_corep_output(
        structured_output,
        rule_ids=list(rule_lookup.keys())
    )

    return {
        "structured_output": structured_output,
        "retrieved_rule_ids": list(rule_lookup.keys()),
        "retrieved_context": context   # add this
    }



# ---------- Local Test ----------
if __name__ == "__main__":
    test_question = "How are own funds determined?"

    result = run_rag_pipeline(test_question)

    print("\nStructured Output:")
    print(json.dumps(result["structured_output"], indent=2))
