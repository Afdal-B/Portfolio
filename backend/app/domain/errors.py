"""Domain errors. Raised by adapters implementing the ports, handled by the
inbound adapters — so neither side needs to know about the other."""


class ImageRejected(Exception):
    """An uploaded image was refused (not an image, or too large)."""
