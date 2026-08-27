from pathlib import Path
import shutil

import chromadb
from pypdf import PdfReader


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = BASE_DIR / "documents"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"


# ============================================================
# CHROMADB
# ============================================================

COLLECTION_NAME = "fmt_knowledge_base"


# ============================================================
# CHUNK SETTINGS
# ============================================================

# Number of characters in each chunk
CHUNK_SIZE = 1500

# Number of characters overlapping between chunks
CHUNK_OVERLAP = 250


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(pdf_path):
    """
    Extract text from every page of a PDF.
    """

    print()
    print("=" * 70)
    print(f"Reading PDF: {pdf_path.name}")
    print("=" * 70)

    try:

        reader = PdfReader(
            str(pdf_path)
        )

    except Exception as error:

        print(
            f"ERROR opening PDF: {error}"
        )

        return ""

    pages = []

    total_pages = len(
        reader.pages
    )

    print(
        f"Total pages: {total_pages}"
    )

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            text = page.extract_text()

            if text:

                pages.append(text)

            # Progress every 25 pages
            if (
                page_number % 25 == 0
                or page_number == total_pages
            ):

                print(
                    f"  Pages processed: "
                    f"{page_number}/{total_pages}"
                )

        except Exception as error:

            print(
                f"WARNING: Could not read "
                f"page {page_number}: {error}"
            )

    return "\n".join(
        pages
    )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    Clean extracted PDF text.
    """

    if not text:

        return ""

    # Remove null characters
    text = text.replace(
        "\x00",
        " "
    )

    # Normalize line breaks
    text = text.replace(
        "\r",
        "\n"
    )

    # Remove excessive whitespace
    text = " ".join(
        text.split()
    )

    return text.strip()


# ============================================================
# CHUNKING
# ============================================================

def create_chunks(text):
    """
    Split text into overlapping chunks.

    Example:

    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 250

    Chunk 1:
        characters 0-1500

    Chunk 2:
        characters 1250-2750

    Chunk 3:
        characters 2500-4000

    This overlap helps preserve context between chunks.
    """

    if not text:

        return []

    chunks = []

    text_length = len(
        text
    )

    step = (
        CHUNK_SIZE
        - CHUNK_OVERLAP
    )

    if step <= 0:

        raise ValueError(
            "CHUNK_OVERLAP must be "
            "smaller than CHUNK_SIZE."
        )

    start = 0

    while start < text_length:

        end = (
            start
            + CHUNK_SIZE
        )

        chunk = text[
            start:end
        ].strip()

        if chunk:

            chunks.append(
                chunk
            )

        start += step

    return chunks


# ============================================================
# CHROMADB CLIENT
# ============================================================

def create_chroma_client():
    """
    Create a persistent ChromaDB client.
    """

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print(
        "Opening ChromaDB..."
    )

    client = chromadb.PersistentClient(
        path=str(
            VECTORSTORE_DIR
        )
    )

    return client


# ============================================================
# COLLECTION
# ============================================================

def recreate_collection(client):
    """
    Delete the old collection and create a fresh one.

    WARNING:
    Running ingest.py rebuilds the entire knowledge base.
    """

    print()
    print(
        "Checking existing collection..."
    )

    try:

        client.delete_collection(
            name=COLLECTION_NAME
        )

        print(
            "Old collection deleted."
        )

    except Exception:

        print(
            "No previous collection found."
        )

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    print(
        f"Created collection: "
        f"{COLLECTION_NAME}"
    )

    return collection


# ============================================================
# PROCESS ONE PDF
# ============================================================

def process_pdf(
    pdf_path,
    collection
):
    """
    Extract, clean, chunk and store one PDF.
    """

    print()
    print(
        "-" * 70
    )

    print(
        f"Processing: {pdf_path.name}"
    )

    print(
        "-" * 70
    )

    # --------------------------------------------------------
    # Extract
    # --------------------------------------------------------

    raw_text = extract_text_from_pdf(
        pdf_path
    )

    if not raw_text.strip():

        print(
            "WARNING: No text extracted."
        )

        print(
            "This PDF may be scanned/image-based."
        )

        return 0

    print(
        f"Raw characters: "
        f"{len(raw_text):,}"
    )

    # --------------------------------------------------------
    # Clean
    # --------------------------------------------------------

    cleaned_text = clean_text(
        raw_text
    )

    print(
        f"Clean characters: "
        f"{len(cleaned_text):,}"
    )

    if not cleaned_text:

        print(
            "WARNING: PDF became empty after cleaning."
        )

        return 0

    # --------------------------------------------------------
    # Chunk
    # --------------------------------------------------------

    chunks = create_chunks(
        cleaned_text
    )

    print(
        f"Created chunks: "
        f"{len(chunks):,}"
    )

    if not chunks:

        return 0

    # --------------------------------------------------------
    # Prepare ChromaDB data
    # --------------------------------------------------------

    documents = []
    ids = []
    metadatas = []

    for index, chunk in enumerate(
        chunks
    ):

        # Make ID unique using PDF filename
        chunk_id = (
            f"{pdf_path.stem}_{index}"
        )

        documents.append(
            chunk
        )

        ids.append(
            chunk_id
        )

        metadatas.append(
            {
                "source":
                    pdf_path.name,

                "chunk":
                    index,
            }
        )

    # --------------------------------------------------------
    # Store
    # --------------------------------------------------------

    try:

        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
        )

    except Exception as error:

        print()
        print(
            f"ERROR adding chunks "
            f"from {pdf_path.name}:"
        )

        print(error)

        return 0

    print(
        f"Added {len(documents):,} "
        f"chunks to ChromaDB."
    )

    return len(
        documents
    )


# ============================================================
# MAIN INGESTION
# ============================================================

def main():

    print()
    print(
        "=" * 70
    )

    print(
        "FMT@Fingertips"
    )

    print(
        "RAG KNOWLEDGE BASE BUILDER"
    )

    print(
        "=" * 70
    )

    print()
    print(
        f"Documents folder:"
    )

    print(
        DOCUMENTS_DIR
    )

    print()
    print(
        f"Vectorstore folder:"
    )

    print(
        VECTORSTORE_DIR
    )

    # ========================================================
    # CHECK DOCUMENTS DIRECTORY
    # ========================================================

    if not DOCUMENTS_DIR.exists():

        print()
        print(
            "ERROR:"
        )

        print(
            "Documents folder does not exist."
        )

        print()
        print(
            "Create:"
        )

        print(
            DOCUMENTS_DIR
        )

        return

    # ========================================================
    # FIND PDFs
    # ========================================================

    pdf_files = sorted(
        DOCUMENTS_DIR.glob(
            "*.pdf"
        )
    )

    if not pdf_files:

        print()
        print(
            "ERROR:"
        )

        print(
            "No PDF files found."
        )

        print()
        print(
            "Put your FMT PDFs inside:"
        )

        print(
            DOCUMENTS_DIR
        )

        return

    print()
    print(
        f"Found {len(pdf_files)} PDF file(s)."
    )

    # ========================================================
    # WARNING
    # ========================================================

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "This process will recreate the "
        "ChromaDB collection."
    )

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    print()

    # ========================================================
    # CREATE CHROMADB
    # ========================================================

    try:

        client = create_chroma_client()

    except Exception as error:

        print()
        print(
            "ERROR creating ChromaDB:"
        )

        print(error)

        return

    # ========================================================
    # RECREATE COLLECTION
    # ========================================================

    try:

        collection = recreate_collection(
            client
        )

    except Exception as error:

        print()
        print(
            "ERROR creating collection:"
        )

        print(error)

        return

    # ========================================================
    # PROCESS PDFs
    # ========================================================

    total_chunks = 0

    successful_pdfs = 0

    failed_pdfs = 0

    skipped_pdfs = 0

    for pdf_number, pdf_path in enumerate(
        pdf_files,
        start=1
    ):

        print()
        print(
            "=" * 70
        )

        print(
            f"PDF {pdf_number}/{len(pdf_files)}"
        )

        print(
            "=" * 70
        )

        try:

            chunks_added = process_pdf(
                pdf_path,
                collection
            )

            if chunks_added > 0:

                successful_pdfs += 1

                total_chunks += (
                    chunks_added
                )

            else:

                skipped_pdfs += 1

        except Exception as error:

            failed_pdfs += 1

            print()
            print(
                f"FAILED: {pdf_path.name}"
            )

            print(
                error
            )

    # ========================================================
    # FINAL DATABASE COUNT
    # ========================================================

    try:

        final_count = (
            collection.count()
        )

    except Exception:

        final_count = total_chunks

    # ========================================================
    # FINAL REPORT
    # ========================================================

    print()
    print()
    print(
        "=" * 70
    )

    print(
        "RAG KNOWLEDGE BASE CREATED"
    )

    print(
        "=" * 70
    )

    print()
    print(
        f"PDF files found       : "
        f"{len(pdf_files)}"
    )

    print(
        f"PDFs processed        : "
        f"{successful_pdfs}"
    )

    print(
        f"PDFs skipped          : "
        f"{skipped_pdfs}"
    )

    print(
        f"PDFs failed           : "
        f"{failed_pdfs}"
    )

    print(
        f"Total chunks created  : "
        f"{total_chunks:,}"
    )

    print(
        f"ChromaDB count        : "
        f"{final_count:,}"
    )

    print()
    print(
        f"Vector database:"
    )

    print(
        VECTORSTORE_DIR
    )

    print()
    print(
        f"Collection:"
    )

    print(
        COLLECTION_NAME
    )

    print()
    print(
        "=" * 70
    )

    print(
        "INGESTION COMPLETE"
    )

    print(
        "=" * 70
    )

    print()
    print(
        "Next step:"
    )

    print(
        "Test the ChromaDB before starting Django."
    )

    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()