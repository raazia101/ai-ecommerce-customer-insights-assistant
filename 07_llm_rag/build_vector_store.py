from pathlib import Path
import hashlib
import json
import re

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "07_llm_rag" / "data"
ARTIFACT_DIR = PROJECT_ROOT / "07_llm_rag" / "artifacts"
VECTOR_STORE_DIR = ARTIFACT_DIR / "vector_store"

MODEL_NAME = "all-MiniLM-L6-v2"

COLLECTION_NAME = "ecommerce_support"

CHUNK_SIZE = 120
CHUNK_OVERLAP = 20

INDEX_VERSION = "week8-day2-v1"


# ============================================================
# Directory setup
# ============================================================

ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Utility functions
# ============================================================

def clean_text(text: str) -> str:
    """Normalize whitespace while preserving readable text."""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def split_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into word-based chunks with overlap.
    """

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def parse_markdown_sections(text: str) -> list[dict]:
    """
    Split a Markdown document into sections based on ## headings.

    Each section contains:
    - section title
    - section content
    """

    lines = text.splitlines()

    sections = []

    current_section = "Introduction"
    current_lines = []

    for line in lines:

        if line.startswith("## "):

            if current_lines:
                sections.append(
                    {
                        "section": current_section,
                        "content": "\n".join(current_lines).strip(),
                    }
                )

            current_section = line.replace("## ", "").strip()
            current_lines = []

        elif line.startswith("# "):
            # Ignore the document-level title.
            continue

        else:
            current_lines.append(line)

    if current_lines:
        sections.append(
            {
                "section": current_section,
                "content": "\n".join(current_lines).strip(),
            }
        )

    return sections


def make_chunk_id(source: str, section: str, chunk_index: int, text: str) -> str:
    """
    Generate a deterministic ID for each chunk.
    """

    raw = f"{source}|{section}|{chunk_index}|{text}"

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:16]

    return f"{source}_{chunk_index}_{digest}"


# ============================================================
# Load and process documents
# ============================================================

documents = []

markdown_files = sorted(DATA_DIR.glob("*.md"))

if not markdown_files:
    raise FileNotFoundError(
        f"No Markdown documents found in {DATA_DIR}"
    )


for file_path in markdown_files:

    source_name = file_path.stem

    text = file_path.read_text(
        encoding="utf-8"
    )

    sections = parse_markdown_sections(text)

    for section_data in sections:

        section_name = section_data["section"]

        cleaned_section = clean_text(
            section_data["content"]
        )

        chunks = split_into_chunks(
            cleaned_section
        )

        for chunk_index, chunk_text in enumerate(chunks):

            chunk_id = make_chunk_id(
                source_name,
                section_name,
                chunk_index,
                chunk_text,
            )

            documents.append(
                {
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        "source": f"{source_name}.md",
                        "section": section_name,
                        "page": "N/A",
                        "chunk_index": chunk_index,
                    },
                }
            )


# ============================================================
# Display chunk statistics
# ============================================================

print("=" * 60)
print("DOCUMENT PROCESSING")
print("=" * 60)

print(f"Documents found: {len(markdown_files)}")
print(f"Chunks created: {len(documents)}")

for file_path in markdown_files:
    print(f"  - {file_path.name}")

print()


# ============================================================
# Generate embeddings
# ============================================================

print("=" * 60)
print("EMBEDDING GENERATION")
print("=" * 60)

print(f"Loading model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)

texts = [
    document["text"]
    for document in documents
]

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    normalize_embeddings=True,
)

print(f"Embedding shape: {embeddings.shape}")
print(
    f"Embedding dimension: "
    f"{model.get_embedding_dimension()}"
)

print()


# ============================================================
# Create Chroma client
# ============================================================

print("=" * 60)
print("CHROMA VECTOR STORE")
print("=" * 60)

client = chromadb.PersistentClient(
    path=str(VECTOR_STORE_DIR)
)


# ============================================================
# Create / recreate collection
# ============================================================

try:
    client.delete_collection(
        name=COLLECTION_NAME
    )
    print(f"Existing collection deleted: {COLLECTION_NAME}")

except Exception:
    pass


collection = client.create_collection(
    name=COLLECTION_NAME,
    metadata={
        "description": "E-commerce customer support knowledge base",
        "embedding_model": MODEL_NAME,
        "index_version": INDEX_VERSION,
    },
)


# ============================================================
# Add documents to Chroma
# ============================================================

collection.add(
    ids=[
        document["id"]
        for document in documents
    ],
    documents=[
        document["text"]
        for document in documents
    ],
    metadatas=[
        document["metadata"]
        for document in documents
    ],
    embeddings=embeddings.tolist(),
)


print(f"Collection: {COLLECTION_NAME}")
print(f"Stored chunks: {collection.count()}")

print()


# ============================================================
# Save index metadata
# ============================================================

metadata_output = ARTIFACT_DIR / "index_metadata.json"

index_metadata = {
    "index_version": INDEX_VERSION,
    "collection_name": COLLECTION_NAME,
    "embedding_model": MODEL_NAME,
    "embedding_dimension": int(
        model.get_embedding_dimension()
    ),
    "chunk_size": CHUNK_SIZE,
    "chunk_overlap": CHUNK_OVERLAP,
    "documents": [
        file_path.name
        for file_path in markdown_files
    ],
    "document_count": len(markdown_files),
    "chunk_count": len(documents),
    "metadata_fields": [
        "source",
        "section",
        "page",
        "chunk_index",
    ],
}

metadata_output.write_text(
    json.dumps(
        index_metadata,
        indent=2,
    ),
    encoding="utf-8",
)


print(f"Index metadata saved to: {metadata_output}")

print()
print("=" * 60)
print("VECTOR STORE BUILD COMPLETE")
print("=" * 60)