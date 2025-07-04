import io
import os

import magic
from flask import current_app
from PIL import Image
from werkzeug.utils import secure_filename

from backend.database import db
from backend.models.asset_models import Asset

from .exceptions import NotFoundException, ServiceError, ValidationException
from .monitoring_service import MonitoringService

# Define constants for file validation
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
ALLOWED_MIMETYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
}


def _allowed_file(filename):
    """Helper function to check if the file extension is in the allowed list."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


class AssetService:
    @staticmethod
    def get_upload_folder():
        # Using instance folder is a good practice for user-uploaded content
        # as it's not part of the version-controlled application code.
        upload_folder = current_app.config.get(
            "UPLOAD_FOLDER", os.path.join(current_app.instance_path, "uploads")
        )
        os.makedirs(upload_folder, exist_ok=True)
        return upload_folder

    @staticmethod
    def _validate_and_sanitize_upload(file_storage):
        """
        Validates the file's true MIME type and size, and sanitizes images to remove potential threats.
        Returns a sanitized, in-memory buffer of the file.
        """
        # 1. Check if the file is empty
        file_storage.seek(0, os.SEEK_END)
        file_size = file_storage.tell()
        file_storage.seek(0)
        if file_size == 0:
            raise ValidationException("Submitted file is empty.")

        # 2. Check file size against the maximum allowed
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValidationException(
                f"File is too large. Max size is {MAX_FILE_SIZE_BYTES / 1024 / 1024}MB."
            )

        # 3. Securely determine the MIME type using the file's content (magic numbers)
        # This prevents attackers from bypassing checks by simply renaming a malicious file.
        mime_type = magic.from_buffer(file_storage.read(2048), mime=True)
        file_storage.seek(0)

        if mime_type not in ALLOWED_MIMETYPES:
            raise ValidationException(
                f"Invalid file type '{mime_type}'. Allowed types are: {', '.join(ALLOWED_MIMETYPES)}"
            )

        # 4. Sanitize image files using Pillow
        # This re-encodes the image, which effectively strips malicious scripts (e.g., in EXIF data) or malformations.
        try:
            with Image.open(file_storage) as img:
                # The 'verify()' method checks for basic integrity.
                img.verify()

            # Re-open the file to work with it after verification
            file_storage.seek(0)
            with Image.open(file_storage) as img:
                # Create a new, clean in-memory buffer
                sanitized_buffer = io.BytesIO()
                # Preserve the original format, or enforce a standard one like 'JPEG'
                img_format = img.format or "JPEG"
                img.save(sanitized_buffer, format=img_format)
                sanitized_buffer.seek(0)

            current_app.logger.info(
                f"Successfully sanitized image with MIME type {mime_type}."
            )
            return sanitized_buffer, mime_type

        except Exception as e:
            current_app.logger.error(f"Failed to process or sanitize image: {e}")
            raise ValidationException(
                "The uploaded image file appears to be corrupted or invalid."
            )

    @staticmethod
    def upload_asset(file_storage, folder="general"):
        """
        Uploads a validated and sanitized asset to the configured storage.
        """
        if not file_storage or not file_storage.filename:
            raise ValidationException("No file provided or file has no name.")

        # The core of the security enhancement is calling the validation method first.
        sanitized_file_buffer, mime_type = AssetService._validate_and_sanitize_upload(
            file_storage
        )

        # Use Werkzeug's utility to prevent directory traversal attacks from malicious filenames.
        filename = secure_filename(file_storage.filename)

        # The remainder of your upload logic (e.g., saving to a local path or uploading to a cloud provider like S3)
        # MUST use the 'sanitized_file_buffer' and not the original 'file_storage' object.

        # --- Placeholder for storage logic ---
        # For example, to save locally:
        # save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder, filename)
        # with open(save_path, 'wb') as f:
        #     f.write(sanitized_file_buffer.read())

        mock_url = f"https://cdn.maison-truvra.com/{folder}/{filename}"
        current_app.logger.info(
            f"Successfully processed and 'uploaded' file {filename} to {mock_url}"
        )

        return {"url": mock_url}

    @staticmethod
    def delete_asset(asset_id):
        asset = Asset.query.get(asset_id)
        if not asset:
            raise NotFoundException("Asset not found.")

        upload_folder = AssetService.get_upload_folder()
        file_path = os.path.join(upload_folder, asset.filename)

        try:
            # Delete file from filesystem
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete record from database
            db.session.delete(asset)
            db.session.commit()
            MonitoringService.log_info(
                f"Deleted asset: {asset.filename}", "AssetService"
            )
            return True
        except Exception as e:
            db.session.rollback()
            MonitoringService.log_error(
                f"Failed to delete asset {asset.filename}: {e}",
                "AssetService",
                exc_info=True,
            )
            raise ServiceError("Could not delete asset.")

    @staticmethod
    def get_all_assets():
        return Asset.query.order_by(Asset.created_at.desc()).all()
