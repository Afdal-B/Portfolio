"""Filesystem-backed ImageStore.

Every upload is decoded, downscaled and re-encoded to WebP before being
written to backend/storage/uploads/ (served read-only at /api/uploads/).
That does three things at once: it keeps a 4 MB phone photo from being
served as-is, it strips EXIF (including GPS coordinates), and it proves the
bytes really are an image — a declared Content-Type is not trusted.

Filenames are always generated server-side from a uuid; the client's
filename is never used, so it can't drive a path traversal or smuggle an
executable extension."""

import io
import uuid
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from app.domain.errors import ImageRejected

DEFAULT_UPLOAD_DIR = Path(__file__).resolve().parents[4] / "storage" / "uploads"
URL_PREFIX = "/api/uploads"

MAX_BYTES = 5 * 1024 * 1024
# Largest the design ever displays an image is the ~720px modal, so 1600px
# still covers high-DPI screens with room to spare.
MAX_DIMENSION = 1600
WEBP_QUALITY = 85

# Decompression-bomb guard: a small file can decode to an enormous bitmap.
Image.MAX_IMAGE_PIXELS = 50_000_000

# Pillow format names, not MIME types — this is what the decoded bytes
# actually are. SVG is absent by design (scriptable, served from our origin)
# and isn't a raster format Pillow decodes anyway.
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class FilesystemImageStore:
    def __init__(self, upload_dir: Path = DEFAULT_UPLOAD_DIR, max_bytes: int = MAX_BYTES) -> None:
        self._upload_dir = upload_dir
        self._max_bytes = max_bytes

    def save(self, content: bytes) -> str:
        if not content:
            raise ImageRejected("Fichier vide.")
        if len(content) > self._max_bytes:
            raise ImageRejected(
                f"Image trop lourde ({len(content) // 1024} Ko). "
                f"Maximum : {self._max_bytes // 1024 // 1024} Mo."
            )

        optimized = _to_webp(content)

        self._upload_dir.mkdir(parents=True, exist_ok=True)
        name = f"{uuid.uuid4().hex}.webp"
        (self._upload_dir / name).write_bytes(optimized)
        return f"{URL_PREFIX}/{name}"


def _to_webp(content: bytes) -> bytes:
    try:
        with Image.open(io.BytesIO(content)) as opened:
            if opened.format not in ALLOWED_FORMATS:
                allowed = ", ".join(sorted(ALLOWED_FORMATS))
                raise ImageRejected(f"Format non supporté ({opened.format}). Formats acceptés : {allowed}.")
            # Honour the EXIF orientation flag before dropping the metadata,
            # otherwise phone photos come out rotated.
            image = ImageOps.exif_transpose(opened)
    except UnidentifiedImageError as exc:
        raise ImageRejected("Fichier illisible : ce n'est pas une image valide.") from exc
    except Image.DecompressionBombError as exc:
        raise ImageRejected("Image trop grande en pixels.") from exc

    image = image.convert("RGBA") if image.mode in ("RGBA", "LA", "P") else image.convert("RGB")
    # thumbnail() only ever shrinks, so small images are left at their size.
    image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))

    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=WEBP_QUALITY, method=6)
    return buffer.getvalue()
