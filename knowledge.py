import re
from pathlib import Path
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

SOP_PATH = Path(__file__).parent / "data" / "sops.txt"
RELEVANCE_THRESHOLD = 0.3


def load_sop_chunks():
    """Split the SOP file into one chunk per SOP (structure-aware chunking)."""
    text = SOP_PATH.read_text()
    sections = re.split(r"\n(?=SOP-\d+)", text)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section.startswith("SOP-"):
            continue  # skip the document title
        sop_id = section.split()[0]
        chunks.append(Document(
            page_content=section,
            metadata={"source": SOP_PATH.name, "sop_id": sop_id},
        ))
    return chunks


chunks = load_sop_chunks()

vectorstore = Chroma.from_documents(
    chunks,
    OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="sops",
    collection_metadata={"hnsw:space": "cosine"},
)


def search(query, k=3):
    results = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    return [doc for doc, score in results if score >= RELEVANCE_THRESHOLD]
