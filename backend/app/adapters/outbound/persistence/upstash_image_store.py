"""Project images kept in Upstash Redis (base64), for hosts with a read-only
filesystem. Images are small once optimized (WebP, 1600 px max, around
100 KB), and their URLs never change, so the CDN caches them for good and
Upstash is rarely read. Images shipped with the code are served from disk."""

import base64
from pathlib import Path
from typing import Optional

from app.adapters.outbound.persistence.filesystem_image_store import (
    DEFAULT_UPLOAD_DIR,
    IMAGE_NAME,
    MAX_BYTES,
    URL_PREFIX,
    new_image_name,
    prepare_image,
    read_image_file,
)
from app.adapters.outbound.upstash import UpstashClient

PREFIX = "pf:img:"


class UpstashImageStore:
    def __init__(self, client: UpstashClient, seed_dir: Path = DEFAULT_UPLOAD_DIR, max_bytes: int = MAX_BYTES) -> None:
        self._client = client
        self._seed_dir = seed_dir
        self._max_bytes = max_bytes

    def save(self, content: bytes) -> str:
        optimized = prepare_image(content, self._max_bytes)
        name = new_image_name()
        self._client.set(PREFIX + name, base64.b64encode(optimized).decode("ascii"))
        return f"{URL_PREFIX}/{name}"

    def load(self, name: str) -> Optional[bytes]:
        if not IMAGE_NAME.match(name):
            return None
        shipped = read_image_file(self._seed_dir, name)
        if shipped is not None:
            return shipped
        encoded = self._client.get(PREFIX + name)
        return base64.b64decode(encoded) if encoded else None
