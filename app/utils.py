from uuid import uuid4

import boto3
from fastapi import UploadFile

from app.core.config import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION
)


def upload_image_to_s3(file: UploadFile, bucket_name: str) -> str:
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{file_extension}"
    s3_client.upload_fileobj(file.file, bucket_name, filename)
    return f"https://{bucket_name}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{filename}"
