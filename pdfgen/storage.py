"""存储层：默认本地（local_store/media），可通过 STORAGE_MODE=s3 切到 S3。

本地模式的照片按调用方给的 key 存固定文件名，重复上传同一 key 即覆盖。
"""
import os
import re
import uuid
from io import BytesIO
from pathlib import Path

from django.conf import settings
from PIL import Image as PILImage


def _is_s3():
    return getattr(settings, 'STORAGE_MODE', 'local') == 's3'


def compress_image(file_obj, max_size=(1280, 1280), quality=85) -> BytesIO:
    image = PILImage.open(file_obj)
    image = image.convert("RGB")
    image.thumbnail(max_size)
    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)
    return buffer


def _safe_key(key: str) -> str:
    """key 形如 '<reportId>/<slotId>'，只保留安全字符，防目录穿越。"""
    parts = [re.sub(r'[^A-Za-z0-9_-]', '', p) for p in str(key).split('/')]
    parts = [p for p in parts if p]
    if not parts:
        parts = [uuid.uuid4().hex]
    return "/".join(parts[:4])


def _local_save(rel_path: str, data: bytes) -> str:
    target = Path(settings.MEDIA_ROOT) / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return f"{settings.MEDIA_URL}{rel_path}"


def save_photo(file_obj, key: str) -> str:
    """压缩并保存照片。同 key 重复上传直接覆盖，返回可访问 URL。"""
    compressed = compress_image(file_obj)
    if _is_s3():
        return _s3_upload_stream(compressed, 'photo.jpg')
    rel = f"photos/{_safe_key(key)}.jpg"
    return _local_save(rel, compressed.getvalue())


def save_photo_bytes(raw: bytes, subdir: str = "imported") -> str:
    """保存解析 PDF 时抽出的照片字节。"""
    if _is_s3():
        return _s3_upload_stream(BytesIO(raw), 'photo.jpg')
    rel = f"photos/{_safe_key(subdir)}/{uuid.uuid4().hex}.jpg"
    return _local_save(rel, raw)


def save_pdf_bytes(pdf_bytes: bytes, filename: str) -> str:
    filename = re.sub(r'[^A-Za-z0-9._ -]', '', filename) or f"report-{uuid.uuid4().hex[:8]}.pdf"
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    if _is_s3():
        return _s3_upload_pdf(pdf_bytes, filename)
    rel = f"reports/{filename}"
    return _local_save(rel, pdf_bytes)


def media_url_to_path(url: str):
    """把 /media/xxx 链接转换为本地绝对路径（非本地链接返回 None）。"""
    if isinstance(url, str) and url.startswith(settings.MEDIA_URL):
        return Path(settings.MEDIA_ROOT) / url[len(settings.MEDIA_URL):]
    return None


# ------------------------------------------------------------------ S3

S3_BUCKET = os.environ.get("S3_BUCKET", "advance-essentials")
S3_PREFIX = os.environ.get("S3_PREFIX", "photos")
S3_REGION = os.environ.get("S3_REGION", "ap-southeast-2")
S3_EXPIRE = int(os.environ.get("S3_EXPIRE_SECONDS", 86400 * 30))


def _s3_client():
    import boto3  # 懒加载：本地模式无需安装 boto3
    return boto3.client('s3', region_name=S3_REGION)


def _time_prefix():
    from datetime import datetime
    dt = datetime.now()
    return f"{dt.strftime('%m-%Y')}/{dt.strftime('%d-%m-%Y')}"


def _s3_upload_stream(stream, filename: str) -> str:
    s3 = _s3_client()
    key = f"{S3_PREFIX}/{_time_prefix()}/{uuid.uuid4().hex}-{filename.replace(' ', '_')}"
    s3.upload_fileobj(stream, S3_BUCKET, key)
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': S3_BUCKET, 'Key': key},
        ExpiresIn=S3_EXPIRE)


def _s3_upload_pdf(pdf_bytes: bytes, filename: str) -> str:
    s3 = _s3_client()
    key = f"{S3_PREFIX}/{_time_prefix()}/{uuid.uuid4().hex}-{filename.replace(' ', '_')}"
    s3.upload_fileobj(BytesIO(pdf_bytes), S3_BUCKET, key, ExtraArgs={
        'ContentType': 'application/pdf',
        'ContentDisposition': 'inline'})
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': S3_BUCKET, 'Key': key},
        ExpiresIn=S3_EXPIRE)
