
# LLM-Assisted COREP Reporting Assistant (Prototype)

This project is a prototype of an **LLM-assisted regulatory reporting assistant** designed to help interpret regulatory guidance and map reporting scenarios into a simplified **COREP Own Funds reporting template**.

The system demonstrates how Retrieval-Augmented Generation (RAG) can assist analysts by retrieving regulatory text, structuring extracted information, validating outputs, and presenting results in a human-readable reporting format with an audit trail.

This is a prototype and is not intended for production regulatory reporting.

---

# Problem Context

Banks subject to the PRA Rulebook and EBA regulations must submit COREP regulatory returns that accurately reflect:

- Capital structure
- Own funds
- Risk exposures

Preparing these reports requires:
- Interpreting complex regulatory documents
- Mapping rules to reporting templates
- Ensuring consistency and accuracy

This prototype demonstrates how an LLM-assisted system can support this process.

---

# Regulatory Document Used

The system uses the following regulatory document as its knowledge source:

**COREP Annex – Own Funds Instructions**

This document defines:
- CET1 capital
- Tier 1 capital
- Tier 2 capital
- Total own funds
- COREP CA1 template logic

The document is stored locally in:

backend/data/Annex_2.pdf

Only this document is ingested into the vector database to keep the prototype focused and retrieval precise.

---

# System Architecture

User Question
      |
      v
FastAPI Backend
      |
      v
RAG Pipeline
  - Document Retrieval
  - LLM Processing
  - Structured Output
  - Validation
  - Formatting
      |
      v
Template Extract + Summary + Audit Log

---

# End-to-End Processing Pipeline

### 1. Document Ingestion
The PDF document is loaded using PyPDFLoader (LangChain).

### 2. Text Chunking
The document is split into chunks using RecursiveCharacterTextSplitter.

Parameters:
- chunk_size = 1200
- chunk_overlap = 200

Each chunk is assigned metadata:
- source_file
- chunk_id
- page_number

This metadata is used for traceability and audit logs.

### 3. Embeddings
Each chunk is converted into embeddings using:
sentence-transformers/all-MiniLM-L6-v2

This enables semantic search over regulatory text.

### 4. Vector Storage
Embeddings are stored in ChromaDB (local persistent storage).

### 5. Retrieval
When a user asks a question:
1. The question is converted into an embedding.
2. The retriever searches ChromaDB.
3. The most relevant chunks are returned.

Each retrieved chunk is tagged with:
RuleID = <filename>-p<page>-c<chunk>

Example:
Annex_2.pdf-p7-c21

These RuleIDs are used for audit trails.

### 6. Prompt Construction
The retrieved context and user question are inserted into a structured prompt that instructs the LLM to:
- Extract structured values
- Provide explanations when needed
- Cite RuleIDs
- Avoid hallucinating values

### 7. LLM Processing
The system uses Groq API (LLM) to generate structured JSON output aligned to a predefined schema.

### 8. Structured Output Schema

{
  "answer": string or null,
  "CET1_capital": number or null,
  "Tier1_capital": number or null,
  "Tier2_capital": number or null,
  "Total_own_funds": number or null,
  "source_rules": {
    field_name: [RuleIDs]
  },
  "audit_log": [
    {field, rule, excerpt}
  ],
  "warnings": []
}

This schema is defined in schema.py.

### 9. Validation Layer
After the LLM produces output, the system validates:
- Missing values
- Negative values
- Logical consistency
- Invalid citations

### 10. Formatting Layer
The validated output is formatted into:
1. A table view
2. A COREP template extract
3. A summary explanation
4. Warning messages
5. Source references

---

# Example Flow

Example Question:
Our bank has CET1 capital of 50 million and Tier2 capital of 20 million. What are total own funds?

System performs:
1. Retrieve relevant COREP rules
2. Extract numeric values
3. Validate output
4. Map to template fields
5. Return structured result and audit log

---

# Project Structure

backend/
├── main.py
├── rag_pipeline.py
├── vectorstore.py
├── prompt_template.py
├── validator.py
├── formatter.py
├── schema.py
├── config.py
└── data/
    └── Annex_2.pdf

---

# Tech Stack

Backend:
- Python
- FastAPI
- LangChain
- Groq API
- HuggingFace Embeddings
- ChromaDB

Frontend (optional):
- Streamlit

---

# Running the Project

Install dependencies:
pip install -r requirements.txt

Run backend:
uvicorn main:app --reload

Open:
http://127.0.0.1:8000/docs

---

# Limitations

- Simplified COREP schema
- Limited regulatory coverage
- Prototype validation rules
- No production-grade data pipelines

---

# Future Improvements

- Support additional COREP templates
- Multi-document retrieval
- Improved validation rules
- Web UI enhancements
- Deployment automation

---

# Purpose

This project demonstrates:
- Retrieval-Augmented Generation
- Structured extraction
- Validation layers
- Audit trail generation
- Template mapping

It is intended as a learning and demonstration prototype.
