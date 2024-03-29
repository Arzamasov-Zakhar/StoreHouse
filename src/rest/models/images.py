# """Модуль обработки и загрузки файлов."""
# import base64
# import tempfile
# from datetime import datetime
# from io import BytesIO
# from mimetypes import guess_extension, guess_type
# from typing import Union
#
# import boto3
# import requests
# from botocore.exceptions import ClientError
# from fastapi import HTTPException, Request
# from loguru import logger
# from nudenet import NudeClassifier
# from PIL import Image
# from pydantic import BaseModel
# from starlette import status
# from starlette.datastructures import UploadFile
#
# from goldstream.config import settings
# from goldstream.integrations.aws import AWS  # noqa N811
# from goldstream.middlewares import request_var
# from goldstream.rest.models.types import UploadFileOrLink
#
# from core.config import settings
# from src.rest.models.types import UploadFileOrLink
# from starlette.datastructures import UploadFile
#
#
# class UploadCloudModel(BaseModel):
#     """Базовая модель пидантик с возможностью загружать файлы в aws."""
#
#     @staticmethod
#     def get_type() -> type:
#         """Получаем тип."""
#         return UploadFileOrLink(validator=UploadCloudModel.validate_picture)
#
#     @staticmethod
#     def validate_picture(
#             value: Union[str, UploadFile], compress: bool = True
#     ) -> Union[UploadFile, str]:
#         """Валидация картинки."""
#         UploadCloudModel.validate_content_type(value)
#         UploadCloudModel.check_mature_content(value)
#
#         funcs = {
#             UploadFile: lambda: UploadCloudModel.upload_file(
#                 UploadCloudModel.compress_file(
#                     value, settings.FILE_SIZE if compress else float("inf")
#                 )
#             ),
#             str: lambda: value,
#         }
#         if func := funcs.get(type(value)):
#             return func()
#         raise ValueError(f"The {type(value)} type is not supported")
#
#     @staticmethod
#     def validate_content_type(file: Union[str, UploadFile]) -> None:
#         """Валидация content_type изображения."""
#         if (content_type := getattr(file, "content_type", None)) is None:
#             content_type = guess_type(file)[0]
#
#         if content_type is None:
#             try:
#                 content_type = requests.head(
#                     file, timeout=settings.TIMEOUT_TO_DEFINE_CONTENT_TYPE
#                 ).headers["Content-Type"]
#             except Exception as exc:
#                 logger.error(exc)
#
#         if content_type not in settings.ACCEPTABLE_CONTENT_TYPES:
#             raise HTTPException(
#                 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
#
#         @staticmethod
#         def compress_file(file: UploadFile, x_size: int) -> UploadFile:
#             """Сжать файл изображения."""
#             image = Image.open(file.file).convert("RGB")
#             if image.size[0] > x_size:
#                 y_size = int(image.size[1] / (image.size[0] / x_size))
#                 image = image.resize((x_size, y_size))
#             image_io = BytesIO()
#             image.save(image_io, "JPEG", optimize=True)
#             file.file = image_io
#             image_io.seek(0)
#             return file
#
#         @staticmethod
#         def upload(
#                 s3_client: boto3, file: UploadFile, aws: AWS, new_filename: str
#         ) -> str:
#             """Переопределение метода загрузки файла в облако."""
#             try:
#                 s3_client.upload_fileobj(
#                     file.file,
#                     aws.bucket,
#                     new_filename,
#                     ExtraArgs={
#                         "ContentType": (
#                                 guess_type(file.filename)[0] or file.content_type
#                         ),
#                         "Metadata": {
#                             "Cache-Control": f"public, max-age={settings.S3_IMAGE_CACHE_TIME}"
#                         },
#                     },
#                 )
#             except ClientError:
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
#             return (
#                 f"https://{aws.bucket}.{settings.AWS_DEFAULT_REGION}"
#                 f".{settings.AWS_DOMAIN}/{new_filename}"
#             )
#
#         @staticmethod
#         def upload_file(file: UploadFile) -> str:
#             """Загрузить файл в облако."""
#
#             def get_unique_name() -> str:
#                 """Получить уникальное имя."""
#                 user_id = -1
#                 if user := getattr(request, "user", None):
#                     user_id = user.id
#                 filename = bytes(
#                     f"{file.filename}_{datetime.now().timestamp()}_{user_id}",
#                     "utf-8",
#                 )
#                 filename = base64.b64encode(filename).decode("ascii")
#                 extension = (
#                     ".jpeg"
#                     if file.content_type == "image/jpeg"
#                     else guess_extension(file.content_type)
#                 )  # для корректной загрузки и открытия файлов .jpeg
#                 return f"{filename}==sep=={extension}"
#
#             def check_file_existence(filename: str) -> bool:
#                 """Проверить существование файла в облаке."""
#                 try:
#                     s3_client.head_object(Bucket=aws.bucket, Key=filename)
#                 except ClientError:
#                     return False
#                 return True
#
#             request: Request = request_var.get()
#             if int(request.headers["content-length"]) > settings.MAX_FILE_SIZE:
#                 raise HTTPException(
#                     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                     detail="Превышен максимальный размер файла",
#                 )
#             aws: AWS = request.app.state.aws
#             s3_client = aws.client_factory("s3")
#
#             new_filename = get_unique_name()
#
#             if check_file_existence(new_filename):
#                 raise HTTPException(status_code=status.HTTP_409_CONFLICT)
#             return UploadCloudModel.upload(s3_client, file, aws, new_filename)
#
