import uuid
from fastapi import UploadFile
from app.core.supabase_client import supabase
from app.exceptions.custom_exceptions import StockFlowException

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_DOCUMENT_TYPES = {
    "application/pdf",
    "application/zip",
    "application/x-zip-compressed",
    "image/jpeg",
    "image/png",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit


def upload_file_to_supabase(
    file: UploadFile, bucket: str, path_prefix: str, allowed_types: set[str]
) -> dict:
    if file.content_type not in allowed_types:
        raise StockFlowException(
            message=f"Unsupported file format '{file.content_type}'. Allowed types: {list(allowed_types)}",
            status_code=400,
        )

    file_bytes = file.file.read()
    file_size = len(file_bytes)

    if file_size > MAX_FILE_SIZE:
        raise StockFlowException(
            message=f"File exceeds maximum allowed size of 10 MB.",
            status_code=400,
        )

    extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    file_path = f"{path_prefix}/{uuid.uuid4()}.{extension}"

    try:
        supabase.storage.from_(bucket).upload(
            file_path,
            file_bytes,
            file_options={"content-type": file.content_type},
        )
    except Exception as e:
        raise StockFlowException(
            message=f"Supabase storage upload failed: {str(e)}",
            status_code=500,
        )

    public_url = supabase.storage.from_(bucket).get_public_url(file_path)

    return {
        "file_name": file.filename,
        "file_url": public_url,
        "file_size": file_size,
    }