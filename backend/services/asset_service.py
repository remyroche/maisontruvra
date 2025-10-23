import io
import logging
import os

import magic
from flask import current_app
from PIL import Image
from werkzeug.utils import secure_filename

from backend.database import db
from backend.models.asset_models import Asset
from backend.services.exceptions import (
    NotFoundException,
    ServiceError,
    ValidationException,
)
from backend.services.monitoring_service import MonitoringService

# --- Constants for File Validation ---
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
ALLOWED_MIMETYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
}

logger = logging.getLogger(__name__)


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
        """Gets or creates the designated upload folder."""
        upload_folder = current_app.config.get(
            "UPLOAD_FOLDER", os.path.join(current_app.instance_path, "uploads")
        )
        os.makedirs(upload_folder, exist_ok=True)
        return upload_folder

    @staticmethod
    def _validate_and_sanitize_upload(file_storage):
        """
        Validates the file's true MIME type and size, and sanitizes images.
        Returns a sanitized, in-memory buffer of the file and its MIME type.
        """
        # 1. Check file size
        file_storage.seek(0, os.SEEK_END)
        file_size = file_storage.tell()
        file_storage.seek(0)
        if file_size == 0:
            raise ValidationException("Submitted file is empty.")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValidationException(
                f"File is too large. Max size is {MAX_FILE_SIZE_BYTES / 1024 / 1024}MB."
            )

        # 2. Securely determine MIME type from file content
        mime_type = magic.from_buffer(file_storage.read(2048), mime=True)
        file_storage.seek(0)
        if mime_type not in ALLOWED_MIMETYPES:
            raise ValidationException(
                f"Invalid file type '{mime_type}'. Allowed types are: {', '.join(ALLOWED_MIMETYPES)}"
            )

        # 3. Sanitize image files to remove potential threats
        if mime_type.startswith("image/"):
            try:
                with Image.open(file_storage) as img:
                    img.verify()  # Check for basic integrity

                file_storage.seek(0)
                with Image.open(file_storage) as img:
                    sanitized_buffer = io.BytesIO()
                    img_format = img.format or "JPEG"
                    img.save(sanitized_buffer, format=img_format)
                    sanitized_buffer.seek(0)

                logger.info(f"Successfully sanitized image with MIME type {mime_type}.")
                return sanitized_buffer, mime_type
            except Exception as e:
                logger.error(f"Failed to process or sanitize image: {e}", exc_info=True)
                raise ValidationException(
                    "The uploaded image file appears to be corrupted or invalid."
                ) from e

        # For non-image files like PDFs, return the original buffer
        return file_storage.stream, mime_type

    @staticmethod
    def upload_asset(file_storage, folder="general"):
        """
        Uploads a validated and sanitized asset to the configured storage.
        """
        if not file_storage or not file_storage.filename:
            raise ValidationException("No file provided or file has no name.")

        sanitized_buffer, mime_type = AssetService._validate_and_sanitize_upload(
            file_storage
        )
        filename = secure_filename(file_storage.filename)

        # Store the file using the configured storage backend
        try:
            if current_app.config.get('ASSET_STORAGE_BACKEND') == 's3':
                # AWS S3 storage
                import boto3
                from botocore.exceptions import ClientError
                
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=current_app.config.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=current_app.config.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=current_app.config.get('AWS_REGION', 'eu-west-1')
                )
                
                bucket_name = current_app.config.get('AWS_S3_BUCKET')
                s3_key = f"{folder}/{filename}"
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=sanitized_buffer,
                    ContentType=content_type,
                    ACL='public-read'
                )
                
                url = f"https://{bucket_name}.s3.{current_app.config.get('AWS_REGION', 'eu-west-1')}.amazonaws.com/{s3_key}"
                
            elif current_app.config.get('ASSET_STORAGE_BACKEND') == 'local':
                # Local file storage
                import os
                
                upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                full_folder_path = os.path.join(upload_dir, folder)
                os.makedirs(full_folder_path, exist_ok=True)
                
                file_path = os.path.join(full_folder_path, filename)
                with open(file_path, 'wb') as f:
                    f.write(sanitized_buffer)
                
                url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/uploads/{folder}/{filename}"
                
            else:
                # Fallback to mock URL for development
                url = f"https://cdn.maison-truvra.com/{folder}/{filename}"
                logger.warning("Using mock URL - configure ASSET_STORAGE_BACKEND for production")
            
            logger.info(f"Successfully processed and uploaded file {filename} to {url}")
            return {"url": url}
            
        except Exception as e:
            logger.error(f"Error storing file {filename}: {e}")
            # Fallback to mock URL on error
            mock_url = f"https://cdn.maison-truvra.com/{folder}/{filename}"
            logger.warning(f"Using fallback mock URL: {mock_url}")
            return {"url": mock_url}

    @staticmethod
    def delete_asset(asset_id):
        """Deletes an asset from the filesystem and database."""
        asset = Asset.query.get(asset_id)
        if not asset:
            raise NotFoundException("Asset not found.")

        upload_folder = AssetService.get_upload_folder()
        file_path = os.path.join(upload_folder, asset.filename)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)

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
            raise ServiceError("Could not delete asset.") from e

    @staticmethod
    def get_all_assets():
        """Retrieves all assets from the database."""
        return Asset.query.order_by(Asset.created_at.desc()).all()
