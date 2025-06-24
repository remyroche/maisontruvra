import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from ..models import db, Asset
from .exceptions import ServiceError, NotFoundException

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class AssetService:
    @staticmethod
    def get_upload_folder():
        # Using instance folder is a good practice for user-uploaded content
        # as it's not part of the version-controlled application code.
        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.instance_path, 'uploads'))
        os.makedirs(upload_folder, exist_ok=True)
        return upload_folder

    @staticmethod
    def upload_asset(file_storage, usage_tag=None):
        if not file_storage or file_storage.filename == '':
            raise ServiceError("No file selected.", 400)

        if not allowed_file(file_storage.filename):
            raise ServiceError("File type not allowed.", 400)

        original_filename = secure_filename(file_storage.filename)
        # Create a unique filename to prevent overwrites and conflicts
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        upload_folder = AssetService.get_upload_folder()
        file_path = os.path.join(upload_folder, unique_filename)
        
        try:
            file_storage.save(file_path)

            # Create the database record
            # The URL path assumes the upload folder is served under '/uploads'
            file_url = f"/uploads/{unique_filename}"
            
            new_asset = Asset(
                filename=unique_filename,
                url=file_url,
                mime_type=file_storage.mimetype,
                usage_tag=usage_tag
            )
            db.session.add(new_asset)
            db.session.commit()

            current_app.logger.info(f"Uploaded new asset: {unique_filename}")
            return new_asset
        except Exception as e:
            db.session.rollback()
            # Clean up the saved file if DB operation fails
            if os.path.exists(file_path):
                os.remove(file_path)
            current_app.logger.error(f"Failed to upload asset {original_filename}: {e}", exc_info=True)
            raise ServiceError("Could not save asset.")

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
            current_app.logger.info(f"Deleted asset: {asset.filename}")
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to delete asset {asset.filename}: {e}", exc_info=True)
            raise ServiceError("Could not delete asset.")
            
    @staticmethod
    def get_all_assets():
        return Asset.query.order_by(Asset.created_at.desc()).all()
