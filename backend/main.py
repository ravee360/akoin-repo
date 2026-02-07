from fastapi import FastAPI
from pydantic import BaseModel

from rag_pipeline import run_rag_pipeline
from formatter import (
    format_to_table,
    format_warnings,
    format_sources,
    format_template_extract,
    format_summary
)

app = FastAPI(title="COREP Reporting Assistant")


# ---------- Request Schema ----------
class QueryRequest(BaseModel):
    question: str


# ---------- Health Check ----------
@app.get("/")
def read_root():
    return {"message": "COREP Reporting Assistant is running"}


# ---------- Query Endpoint ----------
@app.post("/query")
def query_corep(request: QueryRequest):

    # Run RAG pipeline
    result = run_rag_pipeline(request.question)

    structured_output = result["structured_output"]
    retrieved_context = result.get("retrieved_context", "")

    # Format for UI
    table_data = format_to_table(structured_output)
    template_extract = format_template_extract(structured_output)
    summary = format_summary(structured_output)
    warnings = format_warnings(structured_output)
    sources = format_sources(structured_output)

    return {
        "table": table_data,
        "structured_output": structured_output,
        "template_extract": template_extract,
        "summary": summary,
        "answer": structured_output.get("answer"),
        "warnings": warnings,
        "sources": sources,
        "retrieved_context": retrieved_context
    }
