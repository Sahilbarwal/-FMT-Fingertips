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
    Check whether the ChromaDB vectorstore already exists.

    chroma.sqlite3 is used as the primary indicator that
    the ChromaDB database has been restored.
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

    boto3 downloads the object directly to disk, so the
    entire ~400 MB ZIP is NOT loaded into RAM.
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

    file_size_mb = ZIP_PATH.stat().st_size / (1024 * 1024)

    print(
        f"Download completed successfully: "
        f"{file_size_mb:.2f} MB"
    )


# =========================================================
# Validate ZIP
# =========================================================

def validate_zip():
    """
    Make sure the downloaded ZIP is valid before extracting it.
    """

    print("Validating vectorstore ZIP...")

    if not ZIP_PATH.exists():
        raise RuntimeError(
            "vectorstore.zip does not exist."
        )

    if ZIP_PATH.stat().st_size == 0:
        raise RuntimeError(
            "vectorstore.zip is empty."
        )

    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            bad_file = zip_ref.testzip()

            if bad_file is not None:
                raise RuntimeError(
                    f"Corrupted file inside ZIP: {bad_file}"
                )

    except zipfile.BadZipFile as exc:
        raise RuntimeError(
            "Downloaded vectorstore.zip is not a valid ZIP file."
        ) from exc

    print("ZIP validation successful.")


# =========================================================
# Safe ZIP Extraction
# =========================================================

def restore_vectorstore():
    """
    Extract the ChromaDB vectorstore.

    The ZIP created from:

        Compress-Archive -Path .\\vectorstore

    contains the top-level 'vectorstore' directory.

    Therefore extracting into RAG_DIR restores:

        backend/rag/vectorstore/
    """

    print("=" * 60)
    print("Restoring ChromaDB vectorstore")
    print("=" * 60)

    # Remove any incomplete/old vectorstore.
    if VECTORSTORE_DIR.exists():
        print("Removing existing vectorstore...")
        shutil.rmtree(VECTORSTORE_DIR)

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(RAG_DIR)

    print("Extraction completed.")

    # Verify the important ChromaDB file exists.
    chroma_db = VECTORSTORE_DIR / "chroma.sqlite3"

    if not chroma_db.exists():
        raise RuntimeError(
            "Vectorstore extraction completed, but "
            "chroma.sqlite3 was not found."
        )

    if chroma_db.stat().st_size == 0:
        raise RuntimeError(
            "chroma.sqlite3 exists but is empty."
        )

    print(
        f"ChromaDB database found: {chroma_db}"
    )


# =========================================================
# Cleanup Temporary ZIP
# =========================================================

def cleanup():
    """
    Remove the downloaded ZIP after successful extraction.
    """

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
        print("Temporary vectorstore.zip removed.")


# =========================================================
# Main Restore Process
# =========================================================

def main():

    print()
    print("=" * 60)
    print("FMT@Fingertips - R2 Knowledge Base Restore")
    print("=" * 60)
    print()

    # -----------------------------------------------------
    # If vectorstore already exists, don't download again.
    # -----------------------------------------------------

    if vectorstore_exists():

        print(
            "Existing ChromaDB vectorstore found."
        )

        print(
            "Skipping R2 download."
        )

        print(
            f"Vectorstore location: {VECTORSTORE_DIR}"
        )

        print()
        print("=" * 60)
        print("Knowledge base is already available.")
        print("=" * 60)

        return

    # -----------------------------------------------------
    # Validate R2 configuration
    # -----------------------------------------------------

    check_configuration()

    # -----------------------------------------------------
    # Download
    # -----------------------------------------------------

    download_from_r2()

    # -----------------------------------------------------
    # Validate downloaded ZIP
    # -----------------------------------------------------

    validate_zip()

    # -----------------------------------------------------
    # Extract
    # -----------------------------------------------------

    restore_vectorstore()

    # -----------------------------------------------------
    # Final verification
    # -----------------------------------------------------

    if not vectorstore_exists():
        raise RuntimeError(
            "Knowledge base restoration failed. "
            "chroma.sqlite3 was not found."
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
        f"ChromaDB location: {VECTORSTORE_DIR}"
    )
    print("=" * 60)
    print()


# =========================================================
# Run
# =========================================================

if __name__ == "__main__":
    main()