import os
if os.path.isfile("env.py"):
    import env 

import cloudinary
import cloudinary.uploader


# Configure Cloudinary
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET")
)

# Absolute path to media directory
MEDIA_DIR = os.path.join(os.getcwd(), 'media')

# Walk through all files in the media directory
for root, dirs, files in os.walk(MEDIA_DIR):
    for file in files:
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, MEDIA_DIR)
        cloudinary_path = relative_path.replace("\\", "/")  # Normalize for Cloudinary

        try:
            response = cloudinary.uploader.upload(
                file_path,
                public_id=cloudinary_path,
                resource_type="image",  # adjust if you’re uploading videos or other types
                overwrite=True
            )
            print(f"✅ Uploaded: {cloudinary_path} -> {response['secure_url']}")
        except Exception as e:
            print(f"❌ Failed to upload {file_path}: {e}")
