import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from config import CHROMA_PATH, DATA_PATH


# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"


def resolve_pdf_path() -> str:
    """
    Resolve which PDF to load.
    Priority:
    1. Path provided in config
    2. Default file name
    3. First PDF in data directory
    """
    if DATA_PATH:
        print(f"[VectorStore] Using PDF from config: {DATA_PATH}")
        return DATA_PATH

    default_path = DATA_DIR / "Annex_2.pdf"
    if default_path.exists():
        print(f"[VectorStore] Using default PDF: {default_path}")
        return str(default_path)

    pdfs = sorted(DATA_DIR.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError("No PDF files found in backend/data")

    print(f"[VectorStore] Using first available PDF: {pdfs[0]}")
    return str(pdfs[0])


def load_and_split_documents():
    """
    Load the PDF and split into chunks suitable for retrieval.
    """
    pdf_path = resolve_pdf_path()

    print(f"[VectorStore] Loading PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    print(f"[VectorStore] Pages loaded: {len(documents)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " "]
    )

    chunks = text_splitter.split_documents(documents)

    print(f"[VectorStore] Chunks created: {len(chunks)}")

    # Attach metadata for audit trail
    source_file = Path(pdf_path).name
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["source_file"] = source_file

        # Preserve page number if available
        if "page" in chunk.metadata:
            chunk.metadata["page_number"] = chunk.metadata["page"]

    return chunks


def get_embeddings():
    """
    Load embedding model (MiniLM).
    """
    print("[VectorStore] Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings


def create_vector_store():
    """
    Create or load Chroma vector store.
    """
    embeddings = get_embeddings()

    # Ensure directory exists
    os.makedirs(CHROMA_PATH, exist_ok=True)

    # If DB already exists, load it
    if os.listdir(CHROMA_PATH):
        print("[VectorStore] Loading existing Chroma DB...")
        vectordb = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
        return vectordb

    # Otherwise create it
    print("[VectorStore] Creating new vector database...")
    chunks = load_and_split_documents()

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    vectordb.persist()
    print("[VectorStore] Vector DB created and persisted.")
    return vectordb


def get_retriever():
    """
    Return a retriever object.
    """
    vectordb = create_vector_store()
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
    return retriever


if __name__ == "__main__":
    # Quick test
    retriever = get_retriever()
    results = retriever.invoke("What are own funds?")

    for i, doc in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Page: {doc.metadata.get('page_number')}")
        print(doc.page_content[:300])
