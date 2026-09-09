import os
import shutil
import zipfile
from pathlib import Path

import boto3
from botocore.config import Config


# =========================================================
# Paths
# =========================================================

RAG_DIR = Path(__file__).resolve().parent

VECTORSTORE_DIR = RAG_DIR / "vectorstore"
ZIP_PATH = RAG_DIR / "vectorstore.zip"

# Temporary extraction directory
EXTRACT_DIR = RAG_DIR / "_vectorstore_extract"


# =========================================================
# Cloudflare R2 Configuration
# =========================================================

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")

R2_BUCKET_NAME = os.getenv(
    "R2_BUCKET_NAME",
    "fmt-knowledge-base",
)

R2_OBJECT_KEY = os.getenv(
    "R2_OBJECT_KEY",
    "vectorstore.zip",
)


# =========================================================
# Configuration Validation
# =========================================================

def check_configuration():
    """
    Make sure all required R2 environment variables exist.
    """

    required = {
        "R2_ACCOUNT_ID": R2_ACCOUNT_ID,
        "R2_ACCESS_KEY_ID": R2_ACCESS_KEY_ID,
        "R2_SECRET_ACCESS_KEY": R2_SECRET_ACCESS_KEY,
        "R2_BUCKET_NAME": R2_BUCKET_NAME,
        "R2_OBJECT_KEY": R2_OBJECT_KEY,
    }

    missing = [
        name
        for name, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            "Missing R2 environment variables: "
            + ", ".join(missing)
        )


# =========================================================
# Check Existing Vectorstore
# =========================================================

def vectorstore_exists():
    """
    Check whether the expected ChromaDB vectorstore exists.
    """

    chroma_db = VECTORSTORE_DIR / "chroma.sqlite3"

    return (
        chroma_db.exists()
        and chroma_db.is_file()
        and chroma_db.stat().st_size > 0
    )


# =========================================================
# Create Cloudflare R2 Client
# =========================================================

def create_r2_client():
    """
    Create an S3-compatible Cloudflare R2 client.
    """

    endpoint = (
        f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    )

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(
            retries={
                "max_attempts": 5,
                "mode": "standard",
            }
        ),
    )


# =========================================================
# Download Vectorstore From R2
# =========================================================

def download_from_r2():
    """
    Download vectorstore.zip from Cloudflare R2.

    boto3 writes directly to disk instead of loading the
    entire ZIP into RAM.
    """

    print("=" * 60)
    print("Downloading FMT knowledge base from Cloudflare R2")
    print("=" * 60)

    print(f"Bucket : {R2_BUCKET_NAME}")
    print(f"Object : {R2_OBJECT_KEY}")
    print(f"Target : {ZIP_PATH}")

    client = create_r2_client()

    client.download_file(
        R2_BUCKET_NAME,
        R2_OBJECT_KEY,
        str(ZIP_PATH),
    )

    if not ZIP_PATH.exists():
        raise RuntimeError(
            "R2 download completed but vectorstore.zip "
            "was not found on disk."
        )

    file_size_mb = (
        ZIP_PATH.stat().st_size / (1024 * 1024)
    )

    print(
        f"Download completed successfully: "
        f"{file_size_mb:.2f} MB"
    )


# =========================================================
# Find ChromaDB Inside ZIP
# =========================================================

def find_chroma_sqlite_in_zip(zip_ref):
    """
    Find chroma.sqlite3 anywhere inside the ZIP.

    We do not assume a specific folder structure because
    PowerShell Compress-Archive can produce different
    archive layouts depending on how the source path
    was supplied.
    """

    candidates = []

    for name in zip_ref.namelist():

        normalized = name.replace("\\", "/").rstrip("/")

        if normalized.lower().endswith(
            "/chroma.sqlite3"
        ) or normalized.lower() == "chroma.sqlite3":

            candidates.append(name)

    if not candidates:
        raise RuntimeError(
            "Could not find chroma.sqlite3 anywhere "
            "inside vectorstore.zip."
        )

    if len(candidates) > 1:
        print(
            "Warning: multiple chroma.sqlite3 files found:"
        )

        for candidate in candidates:
            print(f"  - {candidate}")

    selected = candidates[0]

    print(
        f"Found ChromaDB database inside ZIP: {selected}"
    )

    return selected


# =========================================================
# Validate ZIP
# =========================================================

def validate_zip():
    """
    Quickly verify that the ZIP is readable and contains
    a ChromaDB database.

    We intentionally do NOT call testzip(), because the
    archive is large and full integrity testing caused
    Render Free to time out.
    """

    print("=" * 60)
    print("Checking vectorstore ZIP...")
    print("=" * 60)

    if not ZIP_PATH.exists():
        raise RuntimeError(
            "vectorstore.zip does not exist."
        )

    if not ZIP_PATH.is_file():
        raise RuntimeError(
            "vectorstore.zip is not a file."
        )

    if ZIP_PATH.stat().st_size == 0:
        raise RuntimeError(
            "vectorstore.zip is empty."
        )

    try:

        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:

            # Check that the archive can be opened.
            zip_ref.namelist()

            # Find the actual ChromaDB database path.
            chroma_path = find_chroma_sqlite_in_zip(
                zip_ref
            )

    except zipfile.BadZipFile as exc:

        raise RuntimeError(
            "Downloaded vectorstore.zip is not "
            "a valid ZIP file."
        ) from exc

    print("ZIP check successful.")
    print(f"ChromaDB path in ZIP: {chroma_path}")


# =========================================================
# Restore Vectorstore
# =========================================================

def restore_vectorstore():
    """
    Extract the ZIP into a temporary directory, locate
    chroma.sqlite3, identify its containing directory,
    and move that directory to:

        backend/rag/vectorstore/

    This makes the restore independent of the ZIP's
    internal folder structure.
    """

    print("=" * 60)
    print("Restoring ChromaDB vectorstore")
    print("=" * 60)

    # -----------------------------------------------------
    # Remove previous temporary extraction
    # -----------------------------------------------------

    if EXTRACT_DIR.exists():

        print(
            "Removing previous temporary extraction..."
        )

        shutil.rmtree(EXTRACT_DIR)

    EXTRACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # Remove old vectorstore
    # -----------------------------------------------------

    if VECTORSTORE_DIR.exists():

        print(
            "Removing existing vectorstore..."
        )

        shutil.rmtree(VECTORSTORE_DIR)

    # -----------------------------------------------------
    # Extract ZIP
    # -----------------------------------------------------

    print(
        "Extracting vectorstore..."
    )

    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:

        zip_ref.extractall(EXTRACT_DIR)

    print(
        "Extraction completed."
    )

    # -----------------------------------------------------
    # Find chroma.sqlite3 after extraction
    # -----------------------------------------------------

    chroma_files = list(
        EXTRACT_DIR.rglob("chroma.sqlite3")
    )

    if not chroma_files:

        raise RuntimeError(
            "Extraction completed, but "
            "chroma.sqlite3 could not be found."
        )

    chroma_db = chroma_files[0]

    print(
        f"Found extracted ChromaDB: {chroma_db}"
    )

    # -----------------------------------------------------
    # Find the directory containing chroma.sqlite3
    # -----------------------------------------------------

    source_vectorstore_dir = chroma_db.parent

    print(
        f"Source vectorstore directory: "
        f"{source_vectorstore_dir}"
    )

    # -----------------------------------------------------
    # Move the complete ChromaDB directory
    # -----------------------------------------------------

    shutil.move(
        str(source_vectorstore_dir),
        str(VECTORSTORE_DIR),
    )

    # -----------------------------------------------------
    # Remove temporary extraction directory
    # -----------------------------------------------------

    if EXTRACT_DIR.exists():

        shutil.rmtree(EXTRACT_DIR)

    # -----------------------------------------------------
    # Verify final database
    # -----------------------------------------------------

    final_chroma_db = (
        VECTORSTORE_DIR / "chroma.sqlite3"
    )

    if not final_chroma_db.exists():

        raise RuntimeError(
            "Vectorstore restoration failed: "
            "chroma.sqlite3 was not found in "
            "backend/rag/vectorstore."
        )

    if not final_chroma_db.is_file():

        raise RuntimeError(
            "chroma.sqlite3 exists but is not a file."
        )

    if final_chroma_db.stat().st_size == 0:

        raise RuntimeError(
            "chroma.sqlite3 exists but is empty."
        )

    database_size_mb = (
        final_chroma_db.stat().st_size
        / (1024 * 1024)
    )

    print(
        f"ChromaDB database restored successfully."
    )

    print(
        f"Database size: "
        f"{database_size_mb:.2f} MB"
    )

    print(
        f"Vectorstore location: "
        f"{VECTORSTORE_DIR}"
    )


# =========================================================
# Cleanup ZIP
# =========================================================

def cleanup():
    """
    Remove the temporary downloaded ZIP.
    """

    if ZIP_PATH.exists():

        ZIP_PATH.unlink()

        print(
            "Temporary vectorstore.zip removed."
        )


# =========================================================
# Main Restore Process
# =========================================================

def main():

    print()

    print("=" * 60)
    print(
        "FMT@Fingertips - R2 Knowledge Base Restore"
    )
    print("=" * 60)

    print()

    # -----------------------------------------------------
    # Check existing vectorstore
    # -----------------------------------------------------

    if vectorstore_exists():

        print(
            "Existing ChromaDB vectorstore found."
        )

        print(
            "Skipping R2 download."
        )

        print(
            f"Vectorstore location: "
            f"{VECTORSTORE_DIR}"
        )

        print()

        print("=" * 60)
        print(
            "Knowledge base is already available."
        )
        print("=" * 60)

        return

    # -----------------------------------------------------
    # Validate configuration
    # -----------------------------------------------------

    check_configuration()

    # -----------------------------------------------------
    # Download
    # -----------------------------------------------------

    download_from_r2()

    # -----------------------------------------------------
    # Quick ZIP validation
    # -----------------------------------------------------

    validate_zip()

    # -----------------------------------------------------
    # Restore vectorstore
    # -----------------------------------------------------

    restore_vectorstore()

    # -----------------------------------------------------
    # Final verification
    # -----------------------------------------------------

    if not vectorstore_exists():

        raise RuntimeError(
            "Knowledge base restoration failed."
        )

    # -----------------------------------------------------
    # Remove temporary ZIP
    # -----------------------------------------------------

    cleanup()

    # -----------------------------------------------------
    # Success
    # -----------------------------------------------------

    print()

    print("=" * 60)
    print("KNOWLEDGE BASE READY")
    print("=" * 60)

    print(
        f"ChromaDB location: "
        f"{VECTORSTORE_DIR}"
    )

    print("=" * 60)

    print()


# =========================================================
# Run
# =========================================================

if __name__ == "__main__":
    main()