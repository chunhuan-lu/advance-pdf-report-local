import os
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import pytz
import requests
from PIL import Image as PILImage
from reportlab.platypus import Image

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def _resolve_local_media(source: str):
    """把前端的 /media/xxx 相对链接解析成本地文件路径，其余原样返回。"""
    if isinstance(source, str) and source.startswith("/media/"):
        try:
            from django.conf import settings
            return str(Path(settings.MEDIA_ROOT) / source[len("/media/"):].lstrip("/"))
        except Exception:
            pass
    return source


def get_image_component(image_path, max_width=200, max_height=170, dpi=72):
    try:
        with PILImage.open(image_path) as im:
            orig_width, orig_height = im.size
        orig_width_pt = orig_width * 72 / dpi
        orig_height_pt = orig_height * 72 / dpi
        scale = min(max_width / orig_width_pt, max_height / orig_height_pt)
        return Image(image_path, width=orig_width_pt * scale, height=orig_height_pt * scale)
    except Exception as e:
        print(f"[Image Error] {image_path}: {e}")
        return None


def smart_image_import(source, max_width=200, max_height=170, dpi=72):
    """加载照片（http(s) 链接 / /media/ 相对链接 / 本地路径），等比缩放为 PDF 组件。"""
    if not source:
        return None
    try:
        source = _resolve_local_media(source)
        if isinstance(source, str) and (source.startswith("http://") or source.startswith("https://")):
            response = requests.get(source, stream=True, timeout=8)
            response.raise_for_status()
            if int(response.headers.get("Content-Length", 0)) > 5 * 1024 * 1024:
                raise ValueError("Image too large")
            img_data = BytesIO(response.content)
        else:
            if isinstance(source, str) and not os.path.exists(source):
                raise FileNotFoundError(source)
            img_data = source

        with PILImage.open(img_data) as im:
            im = im.convert("RGB")
            original_width, original_height = im.size
            max_pixel_width = int(max_width * dpi / 72)
            max_pixel_height = int(max_height * dpi / 72)
            ratio = min(max_pixel_width / original_width, max_pixel_height / original_height, 1)
            new_width = max(1, int(original_width * ratio))
            new_height = max(1, int(original_height * ratio))
            im = im.resize((new_width, new_height), PILImage.LANCZOS)
            buffer = BytesIO()
            im.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)
            return Image(buffer, width=new_width * 72 / dpi, height=new_height * 72 / dpi)
    except Exception as e:
        print(f"[Image Import Error] {e}")
        return None


def get_time_str(input_time):
    """兼容 ISO 字符串（带/不带毫秒）、纯日期 YYYY-MM-DD、epoch 时间戳，输出 d/m/Y。"""
    if not input_time:
        return ""
    melbourne_tz = pytz.timezone('Australia/Melbourne')

    if isinstance(input_time, (int, float)):
        ts = int(input_time)
        if ts > 1e12:
            ts //= 1000
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.astimezone(melbourne_tz).strftime("%d/%m/%Y")

    if isinstance(input_time, str):
        s = input_time.strip()
        # 纯日期直接按字面输出，避免时区偏移一天
        try:
            return datetime.strptime(s, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            pass
        for fmt in ('%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S%z'):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.astimezone(melbourne_tz).strftime("%d/%m/%Y")
            except ValueError:
                continue
        if s.endswith('Z'):
            try:
                dt = datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                return dt.astimezone(melbourne_tz).strftime("%d/%m/%Y")
            except ValueError:
                pass
        raise ValueError(f"Unsupported time string format: {input_time}")

    raise ValueError("Unsupported input type: must be int or str")
