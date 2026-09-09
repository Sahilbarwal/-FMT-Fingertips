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
# Normalize ZIP Paths
# =========================================================

def normalize_zip_path(name):
    """
    Convert ZIP paths to Linux/POSIX format.

    This is important because the uploaded ZIP contains
    Windows-style paths such as:

        vectorstore\\chroma.sqlite3

    which must become:

        vectorstore/chroma.sqlite3
    """

    if not name:
        return ""

    # Convert Windows separators to POSIX separators
    normalized = name.replace("\\", "/")

    # Remove leading ./ components
    while normalized.startswith("./"):
        normalized = normalized[2:]

    # Remove leading slashes
    normalized = normalized.lstrip("/")

    return normalized


# =========================================================
# Find ChromaDB File
# =========================================================

def find_chroma_file(zip_ref):
    """
    Find chroma.sqlite3 anywhere inside the ZIP.

    The ZIP may contain either:

        vectorstore/chroma.sqlite3

    or:

        vectorstore\\chroma.sqlite3

    We normalize both forms.
    """

    exact_match = None
    candidates = []

    for info in zip_ref.infolist():

        normalized = normalize_zip_path(info.filename)

        if not normalized:
            continue

        if normalized.lower() == "vectorstore/chroma.sqlite3":
            exact_match = info
            break

        if PurePosixPath(normalized).name.lower() == "chroma.sqlite3":
            candidates.append(info)

    if exact_match is not None:
        return exact_match

    if candidates:
        return candidates[0]

    return None


# =========================================================
# Validate ZIP Structure
# =========================================================

def validate_zip():
    """
    Quickly verify that the ZIP can be opened and that
    chroma.sqlite3 exists inside it.

    IMPORTANT:
    We intentionally do NOT use zipfile.testzip().

    testzip() reads the entire 400 MB archive and previously
    caused Render Free to spend more than 18 minutes
    validating the archive.
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

        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:

            chroma_info = find_chroma_file(zip_ref)

            if chroma_info is None:
                raise RuntimeError(
                    "vectorstore.zip does not contain "
                    "chroma.sqlite3."
                )

            normalized_path = normalize_zip_path(
                chroma_info.filename
            )

            compressed_mb = (
                chroma_info.compress_size
                / (1024 * 1024)
            )

            uncompressed_mb = (
                chroma_info.file_size
                / (1024 * 1024)
            )

            print(
                f"Found ChromaDB file inside ZIP: "
                f"{normalized_path}"
            )

            print(
                f"ChromaDB compressed size: "
                f"{compressed_mb:.2f} MB"
            )

            print(
                f"ChromaDB uncompressed size: "
                f"{uncompressed_mb:.2f} MB"
            )

    except zipfile.BadZipFile as exc:

        raise RuntimeError(
            "Downloaded vectorstore.zip is not "
            "a valid ZIP file."
        ) from exc

    print("ZIP check successful.")


# =========================================================
# Safe ZIP Extraction
# =========================================================

def safe_extract_zip(zip_ref, destination):
    """
    Extract the ZIP manually.

    This handles both:

        vectorstore/chroma.sqlite3

    and:

        vectorstore\\chroma.sqlite3

    correctly on Linux.

    It also protects against ZIP path traversal.
    """

    destination = Path(destination).resolve()

    extracted_files = 0
    extracted_dirs = 0

    for info in zip_ref.infolist():

        raw_name = info.filename

        if not raw_name:
            continue

        normalized = normalize_zip_path(raw_name)

        if not normalized:
            continue

        # Build the destination path
        relative_path = Path(*PurePosixPath(normalized).parts)

        target_path = (
            destination / relative_path
        ).resolve()

        # ZIP-slip protection
        try:
            target_path.relative_to(destination)
        except ValueError:
            raise RuntimeError(
                f"Unsafe ZIP path detected: {raw_name}"
            )

        # Detect directories
        is_directory = (
            raw_name.endswith("/")
            or raw_name.endswith("\\")
            or info.is_dir()
        )

        if is_directory:

            target_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            extracted_dirs += 1

            continue

        # Create parent directory
        target_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Stream file extraction
        with zip_ref.open(info, "r") as source:
            with open(target_path, "wb") as target:

                while True:

                    chunk = source.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    target.write(chunk)

        extracted_files += 1

    return extracted_files, extracted_dirs


# =========================================================
# Restore Vectorstore
# =========================================================

def restore_vectorstore():
    """
    Restore the ChromaDB vectorstore from the ZIP.

    The ZIP contains Windows-style paths, so we manually
    normalize them while extracting.
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
    # Create clean vectorstore directory
    # -----------------------------------------------------

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Vectorstore target: "
        f"{VECTORSTORE_DIR}"
    )

    # -----------------------------------------------------
    # Extract ZIP
    # -----------------------------------------------------

    print(
        "Extracting vectorstore..."
    )

    try:

        with zipfile.ZipFile(
            ZIP_PATH,
            "r",
        ) as zip_ref:

            extracted_files, extracted_dirs = (
                safe_extract_zip(
                    zip_ref,
                    RAG_DIR,
                )
            )

    except zipfile.BadZipFile as exc:

        raise RuntimeError(
            "Could not extract vectorstore.zip "
            "because the ZIP file is invalid."
        ) from exc

    print(
        "Extraction completed."
    )

    print(
        f"Extracted files: {extracted_files}"
    )

    print(
        f"Extracted directories: {extracted_dirs}"
    )

    # -----------------------------------------------------
    # Verify vectorstore directory
    # -----------------------------------------------------

    if not VECTORSTORE_DIR.exists():

        raise RuntimeError(
            "Extraction completed, but the "
            "vectorstore directory was not created."
        )

    if not VECTORSTORE_DIR.is_dir():

        raise RuntimeError(
            "vectorstore exists but is not a directory."
        )

    # -----------------------------------------------------
    # Verify ChromaDB
    # -----------------------------------------------------

    chroma_db = (
        VECTORSTORE_DIR / "chroma.sqlite3"
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

        try:

            ZIP_PATH.unlink()

            print(
                "Temporary vectorstore.zip removed."
            )

        except Exception as exc:

            print(
                f"Warning: could not remove "
                f"temporary ZIP: {exc}"
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
    # Check R2 configuration
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

    print(
        "KNOWLEDGE BASE READY"
    )

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