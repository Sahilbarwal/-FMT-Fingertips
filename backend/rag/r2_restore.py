import os
import shutil
import zipfile
from pathlib import Path, PurePosixPath

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
    Check whether the expected ChromaDB database exists.
    """

    chroma_db = VECTORSTORE_DIR / "chroma.sqlite3"

    return (
        chroma_db.exists()
        and chroma_db.is_file()
        and chroma_db.stat().st_size > 0
    )


# =========================================================
# Create R2 Client
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
# Download From R2
# =========================================================

def download_from_r2():
    """
    Download vectorstore.zip directly to disk.

    The ZIP is approximately 400 MB.
    It is not loaded entirely into RAM.
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

    size_mb = (
        ZIP_PATH.stat().st_size / (1024 * 1024)
    )

    print(
        f"Download completed successfully: "
        f"{size_mb:.2f} MB"
    )


# =========================================================
# Find Chroma Database Inside ZIP
# =========================================================

def find_chroma_file(zip_ref):
    """
    Find chroma.sqlite3 inside the ZIP.

    We do not depend on one exact ZIP path string.

    Accepted examples:

        vectorstore/chroma.sqlite3
        ./vectorstore/chroma.sqlite3
        vectorstore\\chroma.sqlite3

    This makes the restore process more tolerant of
    ZIP path formatting differences.
    """

    matches = []

    for name in zip_ref.namelist():

        normalized = name.replace("\\", "/").lstrip("./")

        path = PurePosixPath(normalized)

        if path.name.lower() == "chroma.sqlite3":
            matches.append(name)

    if not matches:
        return None

    # Prefer the expected vectorstore location if available.
    for name in matches:

        normalized = name.replace("\\", "/").lstrip("./")

        if normalized.lower() == "vectorstore/chroma.sqlite3":
            return name

    return matches[0]


# =========================================================
# Validate ZIP Structure
# =========================================================

def validate_zip():
    """
    Quickly verify that the ZIP can be opened and contains
    the ChromaDB database.

    We intentionally do NOT use testzip(), because that caused
    very long validation times on Render Free.
    """

    print("=" * 60)
    print("Checking vectorstore ZIP")
    print("=" * 60)

    if not ZIP_PATH.exists():
        raise RuntimeError(
            "vectorstore.zip does not exist."
        )

    if ZIP_PATH.stat().st_size == 0:
        raise RuntimeError(
            "vectorstore.zip is empty."
        )

    try:

        with zipfile.ZipFile(
            ZIP_PATH,
            "r",
        ) as zip_ref:

            # Make sure the ZIP can be read.
            bad_file = zip_ref.testzip()

            if bad_file:
                raise RuntimeError(
                    f"ZIP contains a corrupted file: {bad_file}"
                )

            chroma_file = find_chroma_file(
                zip_ref
            )

            if chroma_file is None:

                print(
                    "ZIP contents containing 'chroma':"
                )

                for name in zip_ref.namelist():

                    if "chroma" in name.lower():

                        print(
                            f"  - {name}"
                        )

                raise RuntimeError(
                    "vectorstore.zip contains no "
                    "chroma.sqlite3 file."
                )

            print(
                f"Found ChromaDB file inside ZIP: "
                f"{chroma_file}"
            )

            info = zip_ref.getinfo(
                chroma_file
            )

            print(
                f"ChromaDB compressed size: "
                f"{info.compress_size / (1024 * 1024):.2f} MB"
            )

            print(
                f"ChromaDB uncompressed size: "
                f"{info.file_size / (1024 * 1024):.2f} MB"
            )

    except zipfile.BadZipFile as exc:

        raise RuntimeError(
            "Downloaded vectorstore.zip is not "
            "a valid ZIP file."
        ) from exc

    print(
        "ZIP check successful."
    )


# =========================================================
# Safe ZIP Extraction
# =========================================================

def safe_extract(zip_ref, destination):
    """
    Safely extract ZIP contents.

    Prevents files inside the archive from escaping
    the destination directory.
    """

    destination = Path(destination).resolve()

    for member in zip_ref.infolist():

        member_path = (
            destination
            / member.filename
        ).resolve()

        if not str(member_path).startswith(
            str(destination) + os.sep
        ):
            raise RuntimeError(
                f"Unsafe ZIP path detected: "
                f"{member.filename}"
            )

    zip_ref.extractall(destination)


# =========================================================
# Restore Vectorstore
# =========================================================

def restore_vectorstore():
    """
    Extract the ZIP directly into RAG_DIR.

    Expected ZIP structure:

        vectorstore/
            chroma.sqlite3
            UUID directories...
    """

    print("=" * 60)
    print("Restoring ChromaDB vectorstore")
    print("=" * 60)

    # -----------------------------------------------------
    # Remove old/incomplete vectorstore
    # -----------------------------------------------------

    if VECTORSTORE_DIR.exists():

        print(
            "Removing existing vectorstore..."
        )

        shutil.rmtree(
            VECTORSTORE_DIR
        )

    # -----------------------------------------------------
    # Extract directly into RAG_DIR
    # -----------------------------------------------------

    print(
        "Extracting vectorstore..."
    )

    try:

        with zipfile.ZipFile(
            ZIP_PATH,
            "r",
        ) as zip_ref:

            safe_extract(
                zip_ref,
                RAG_DIR,
            )

    except zipfile.BadZipFile as exc:

        raise RuntimeError(
            "Could not extract vectorstore.zip "
            "because the ZIP file is invalid."
        ) from exc

    print(
        "Extraction completed."
    )

    # -----------------------------------------------------
    # Verify expected directory
    # -----------------------------------------------------

    if not VECTORSTORE_DIR.exists():

        raise RuntimeError(
            "Extraction completed, but the "
            "vectorstore directory was not created."
        )

    # -----------------------------------------------------
    # Verify ChromaDB
    # -----------------------------------------------------

    chroma_db = (
        VECTORSTORE_DIR
        / "chroma.sqlite3"
    )

    if not chroma_db.exists():

        print(
            "Vectorstore directory contents:"
        )

        for item in VECTORSTORE_DIR.iterdir():

            print(
                f"  - {item.name}"
            )

        raise RuntimeError(
            "Extraction completed, but "
            "chroma.sqlite3 could not be found."
        )

    if not chroma_db.is_file():

        raise RuntimeError(
            "chroma.sqlite3 exists but is not a file."
        )

    if chroma_db.stat().st_size == 0:

        raise RuntimeError(
            "chroma.sqlite3 exists but is empty."
        )

    database_size_mb = (
        chroma_db.stat().st_size
        / (1024 * 1024)
    )

    print(
        "ChromaDB database restored successfully."
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
# Cleanup
# =========================================================

def cleanup():
    """
    Remove the temporary ZIP after successful restoration.
    """

    if ZIP_PATH.exists():

        ZIP_PATH.unlink()

        print(
            "Temporary vectorstore.zip removed."
        )


# =========================================================
# Main
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
    # Check configuration
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
    # Restore
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
    # Cleanup
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