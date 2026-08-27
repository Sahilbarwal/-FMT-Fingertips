from pathlib import Path
import hashlib

import chromadb
from pypdf import PdfReader

import pytesseract
import fitz  # PyMuPDF
from PIL import Image


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOCUMENTS_DIR = BASE_DIR / "documents"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"

COLLECTION_NAME = "fmt_knowledge_base"


# ============================================================
# TESSERACT
# ============================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

OCR_DPI = 200
OCR_LANGUAGE = "eng"


# ============================================================
# CHUNK SETTINGS
# Must match your existing ingestion settings
# ============================================================

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 250
CHROMA_BATCH_SIZE = 500


# ============================================================
# NORMAL TEXT CHECK
# ============================================================

def has_normal_text(pdf_path):

    try:
        reader = PdfReader(str(pdf_path))

        extracted_text = ""

        for page in reader.pages:
            text = page.extract_text() or ""
            extracted_text += text.strip()

            # We only need enough text to know
            # that this is NOT a scanned PDF
            if len(extracted_text) > 100:
                return True

        return False

    except Exception as error:

        print(f"WARNING checking {pdf_path.name}: {error}")

        return False


# ============================================================
# OCR PDF
# ============================================================

def ocr_pdf(pdf_path):

    print()
    print("=" * 70)
    print(f"OCR PROCESSING: {pdf_path.name}")
    print("=" * 70)

    pdf_document = fitz.open(str(pdf_path))

    total_pages = len(pdf_document)

    print(f"Total pages: {total_pages}")

    page_texts = []

    try:

        for page_index in range(total_pages):

            print(
                f"OCR page {page_index + 1}/{total_pages}..."
            )

            page = pdf_document.load_page(page_index)

            zoom = OCR_DPI / 72

            matrix = fitz.Matrix(zoom, zoom)

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples
            )

            text = pytesseract.image_to_string(
                image,
                lang=OCR_LANGUAGE
            ).strip()

            if text:
                page_texts.append(text)

                print(
                    f"  Extracted {len(text):,} characters"
                )
            else:
                print("  WARNING: No OCR text found")

    finally:

        pdf_document.close()

    return "\n".join(page_texts)


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\r", "\n")

    # Normalize excessive whitespace
    text = " ".join(text.split())

    return text.strip()


# ============================================================
# CREATE CHUNKS
# ============================================================

def create_chunks(text):

    if not text:
        return []

    chunks = []

    step = CHUNK_SIZE - CHUNK_OVERLAP

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


# ============================================================
# SAFE UNIQUE ID
# ============================================================

def make_chunk_id(pdf_name, chunk_index):

    source_hash = hashlib.md5(
        pdf_name.encode("utf-8")
    ).hexdigest()[:12]

    return f"ocr_{source_hash}_{chunk_index}"


# ============================================================
# CHECK IF PDF ALREADY EXISTS
# ============================================================

def source_already_ingested(collection, pdf_name):

    try:

        results = collection.get(
            where={"source": pdf_name},
            limit=1
        )

        return len(results["ids"]) > 0

    except Exception as error:

        print(
            f"WARNING checking existing source: {error}"
        )

        return False


# ============================================================
# ADD CHUNKS
# ============================================================

def add_chunks(collection, pdf_name, chunks):

    documents = []
    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        documents.append(chunk)

        ids.append(
            make_chunk_id(pdf_name, index)
        )

        metadatas.append(
            {
                "source": pdf_name,
                "chunk": index,
                "extraction": "ocr"
            }
        )

    total_added = 0

    for start in range(
        0,
        len(documents),
        CHROMA_BATCH_SIZE
    ):

        end = min(
            start + CHROMA_BATCH_SIZE,
            len(documents)
        )

        collection.add(
            documents=documents[start:end],
            ids=ids[start:end],
            metadatas=metadatas[start:end]
        )

        batch_count = end - start

        total_added += batch_count

        print(
            f"  Added {total_added}/{len(documents)} chunks"
        )

    return total_added


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("FMT@FINGERTIPS - OCR ADDITION")
    print("=" * 70)

    # --------------------------------------------------------
    # CHECK TESSERACT
    # --------------------------------------------------------

    if not Path(TESSERACT_PATH).exists():

        print()
        print("ERROR: Tesseract not found:")
        print(TESSERACT_PATH)

        return

    print()
    print("Tesseract found.")

    # --------------------------------------------------------
    # CHECK DOCUMENTS
    # --------------------------------------------------------

    if not DOCUMENTS_DIR.exists():

        print("ERROR: Documents folder not found:")
        print(DOCUMENTS_DIR)

        return

    pdf_files = sorted(
        DOCUMENTS_DIR.glob("*.pdf")
    )

    print()
    print(f"PDF files found: {len(pdf_files)}")

    # --------------------------------------------------------
    # OPEN EXISTING CHROMADB
    # --------------------------------------------------------

    client = chromadb.PersistentClient(
        path=str(VECTORSTORE_DIR)
    )

    try:

        collection = client.get_collection(
            name=COLLECTION_NAME
        )

    except Exception as error:

        print()
        print("ERROR: Existing collection not found.")
        print(error)

        return

    before_count = collection.count()

    print()
    print(
        f"Existing ChromaDB chunks: {before_count:,}"
    )

    # --------------------------------------------------------
    # FIND SCANNED / SKIPPED PDFs
    # --------------------------------------------------------

    scanned_pdfs = []

    print()
    print("=" * 70)
    print("CHECKING FOR PDFs THAT NEED OCR")
    print("=" * 70)

    for pdf_path in pdf_files:

        print()
        print(f"Checking: {pdf_path.name}")

        # Skip if already added to ChromaDB
        if source_already_ingested(
            collection,
            pdf_path.name
        ):

            print("  Already in knowledge base -> skipping")
            continue

        # Check normal text
        if has_normal_text(pdf_path):

            print(
                "  Has normal extractable text -> skipping"
            )

            continue

        print(
            "  SCANNED / NO TEXT -> OCR REQUIRED"
        )

        scanned_pdfs.append(pdf_path)

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        f"PDFs requiring OCR: {len(scanned_pdfs)}"
    )
    print("=" * 70)

    if not scanned_pdfs:

        print()
        print("No PDFs require OCR.")

        return

    for pdf_path in scanned_pdfs:
        print(f"- {pdf_path.name}")

    # --------------------------------------------------------
    # OCR AND ADD
    # --------------------------------------------------------

    total_added = 0
    successful = 0
    failed = 0

    for number, pdf_path in enumerate(
        scanned_pdfs,
        start=1
    ):

        print()
        print("#" * 70)
        print(
            f"OCR PDF {number}/{len(scanned_pdfs)}"
        )
        print("#" * 70)

        try:

            raw_text = ocr_pdf(pdf_path)

            cleaned_text = clean_text(raw_text)

            print()
            print(
                f"Total OCR characters: "
                f"{len(cleaned_text):,}"
            )

            if not cleaned_text:

                print(
                    "WARNING: No usable OCR text."
                )

                failed += 1

                continue

            chunks = create_chunks(cleaned_text)

            print(
                f"Chunks created: {len(chunks):,}"
            )

            if not chunks:

                failed += 1

                continue

            added = add_chunks(
                collection,
                pdf_path.name,
                chunks
            )

            total_added += added
            successful += 1

            print()
            print(
                f"SUCCESS: Added {added:,} chunks"
            )

        except Exception as error:

            failed += 1

            print()
            print(
                f"FAILED: {pdf_path.name}"
            )

            print(error)

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    after_count = collection.count()

    print()
    print()
    print("=" * 70)
    print("OCR INGESTION COMPLETE")
    print("=" * 70)

    print(
        f"Chunks before OCR : {before_count:,}"
    )

    print(
        f"Chunks added      : {total_added:,}"
    )

    print(
        f"Chunks after OCR  : {after_count:,}"
    )

    print(
        f"PDFs successful   : {successful}"
    )

    print(
        f"PDFs failed       : {failed}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()