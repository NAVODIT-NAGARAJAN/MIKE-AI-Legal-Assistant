"""
Image Parser tool for the Document Intelligence Agent.

Responsibilities:
- Accept an image file path or raw bytes as input.
- Validate the file format, integrity, and dimensions.
- Extract image metadata:
    - width, height
    - color mode
    - detected format
    - DPI (when available in EXIF/header data)
    - file name
- Return a structured ParsedImage result.

Supported formats: PNG, JPG, JPEG, TIFF, BMP, WEBP.

This module does NOT perform:
- OCR or text extraction (delegated to tools/ocr.py)
- Legal analysis
- Entity extraction
- Clause detection
- Risk detection
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple, Union

from PIL import Image, UnidentifiedImageError

from app.utils.logger import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Supported image extensions (lowercase, dot-prefixed).
# ---------------------------------------------------------------------------
_SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}
)

# ---------------------------------------------------------------------------
# Supported Pillow format identifiers (returned by Image.format).
# ---------------------------------------------------------------------------
_SUPPORTED_PILLOW_FORMATS: frozenset[str] = frozenset(
    {"PNG", "JPEG", "TIFF", "BMP", "WEBP"}
)


# =============================================================================
# Result dataclass
# =============================================================================


@dataclass
class ParsedImage:
    """
    Structured result returned by the image parser.

    Fields:
        file_name   : Original file name, if available.
        format      : Detected image format (e.g., 'JPEG', 'PNG').
        mode        : Color mode (e.g., 'RGB', 'L', 'RGBA').
        width       : Image width in pixels.
        height      : Image height in pixels.
        dpi         : Dots-per-inch as (x_dpi, y_dpi). None if unavailable.
        file_size   : File size in bytes. None when source is bytes input.
    """

    file_name: Optional[str]
    format: str
    mode: str
    width: int
    height: int
    dpi: Optional[Tuple[float, float]]
    file_size: Optional[int]


# =============================================================================
# Exceptions
# =============================================================================


class ImageParserError(Exception):
    """
    Base exception for all image parser errors.
    """


class InvalidImageError(ImageParserError):
    """
    Raised when the provided source cannot be decoded as a valid image.
    """


class UnsupportedImageFormatError(ImageParserError):
    """
    Raised when the image format is not supported by this parser.
    """


# =============================================================================
# Internal helpers
# =============================================================================


def _validate_extension(file_path: Path) -> None:
    """
    Raise UnsupportedImageFormatError if the file extension is not supported.
    """
    suffix = file_path.suffix.lower()
    if suffix not in _SUPPORTED_EXTENSIONS:
        raise UnsupportedImageFormatError(
            f"Unsupported file extension '{file_path.suffix}'. "
            f"Supported formats: {', '.join(sorted(_SUPPORTED_EXTENSIONS))}."
        )


def _validate_pillow_format(detected_format: Optional[str], label: str) -> str:
    """
    Validate that Pillow's detected format is in the supported set.

    Args:
        detected_format : The format string returned by Pillow (e.g. 'JPEG').
        label           : A human-readable description of the source (for error messages).

    Returns:
        The validated format string.

    Raises:
        UnsupportedImageFormatError: If the format is unsupported or undetected.
    """
    if not detected_format:
        raise UnsupportedImageFormatError(
            f"Could not detect the image format for '{label}'. "
            "The file may be corrupt or in an unsupported format."
        )
    if detected_format.upper() not in _SUPPORTED_PILLOW_FORMATS:
        raise UnsupportedImageFormatError(
            f"Image format '{detected_format}' is not supported. "
            f"Supported formats: {', '.join(sorted(_SUPPORTED_PILLOW_FORMATS))}."
        )
    return detected_format.upper()


def _extract_dpi(image: Image.Image) -> Optional[Tuple[float, float]]:
    """
    Attempt to read DPI information from the image metadata.

    Returns a (x_dpi, y_dpi) tuple, or None if DPI data is unavailable.
    """
    try:
        info = image.info or {}

        # Pillow stores DPI under 'dpi' for JPEG/PNG and 'resolution' for TIFF.
        dpi_value = info.get("dpi") or info.get("resolution")

        if dpi_value and isinstance(dpi_value, (tuple, list)) and len(dpi_value) == 2:
            x_dpi, y_dpi = float(dpi_value[0]), float(dpi_value[1])
            if x_dpi > 0 and y_dpi > 0:
                return x_dpi, y_dpi

    except Exception:
        pass

    return None


def _open_image_from_path(file_path: Path) -> tuple[Image.Image, int]:
    """
    Open an image from a file path after validating its existence and extension.

    Returns:
        (Image, file_size_bytes)

    Raises:
        ImageParserError           : For missing or empty files.
        UnsupportedImageFormatError: For unsupported extensions or Pillow formats.
        InvalidImageError          : For corrupt or unreadable image data.
    """
    if not file_path.exists():
        raise ImageParserError(f"Image file not found: {file_path}")

    if not file_path.is_file():
        raise ImageParserError(f"Path is not a file: {file_path}")

    file_size = file_path.stat().st_size
    if file_size == 0:
        raise ImageParserError(f"Image file is empty: {file_path}")

    _validate_extension(file_path)

    try:
        image = Image.open(str(file_path))
        image.verify()
        # Re-open after verify() — verify() consumes the file handle.
        image = Image.open(str(file_path))
        return image, file_size
    except UnidentifiedImageError as exc:
        raise InvalidImageError(
            f"Cannot decode '{file_path.name}' as an image: {exc}"
        ) from exc
    except Exception as exc:
        raise InvalidImageError(
            f"Unexpected error opening image '{file_path.name}': {exc}"
        ) from exc


def _open_image_from_bytes(data: bytes) -> Image.Image:
    """
    Open an image from raw bytes.

    Raises:
        ImageParserError           : For empty input.
        UnsupportedImageFormatError: For unsupported Pillow formats.
        InvalidImageError          : For corrupt or unreadable image data.
    """
    if len(data) == 0:
        raise ImageParserError("Image bytes are empty.")

    try:
        image = Image.open(io.BytesIO(data))
        image.verify()
        # Re-open after verify().
        image = Image.open(io.BytesIO(data))
        return image
    except UnidentifiedImageError as exc:
        raise InvalidImageError(
            f"Cannot decode image bytes: {exc}"
        ) from exc
    except Exception as exc:
        raise InvalidImageError(
            f"Unexpected error opening image from bytes: {exc}"
        ) from exc


# =============================================================================
# Public API
# =============================================================================


def parse_image(source: Union[str, Path, bytes]) -> ParsedImage:
    """
    Load and validate an image, returning its metadata as a ParsedImage.

    This function does NOT extract text. Text extraction (OCR) is handled
    separately by tools/ocr.py.

    Args:
        source: Absolute file path (str or Path) or raw image bytes.

    Returns:
        ParsedImage containing format, dimensions, color mode, DPI,
        file name, and file size.

    Raises:
        ImageParserError           : For missing, empty, or unreadable files.
        InvalidImageError          : For corrupt or non-image data.
        UnsupportedImageFormatError: For unsupported image formats.
    """

    log.info("=" * 60)
    log.info("ImageParser: starting validation and metadata extraction.")

    file_name: Optional[str] = None
    file_size: Optional[int] = None

    if isinstance(source, bytes):
        image = _open_image_from_bytes(source)
        label = "<bytes>"

    else:
        file_path = Path(source)
        image, file_size = _open_image_from_path(file_path)
        file_name = file_path.name
        label = file_name

    log.info("ImageParser: opened '%s'.", label)

    # ------------------------------------------------------------------
    # Validate and extract format
    # ------------------------------------------------------------------
    detected_format = _validate_pillow_format(image.format, label)

    # ------------------------------------------------------------------
    # Extract metadata
    # ------------------------------------------------------------------
    width, height = image.size
    mode = image.mode
    dpi = _extract_dpi(image)

    log.info(
        "ImageParser: '%s' — format=%s | mode=%s | size=%dx%d | dpi=%s.",
        label,
        detected_format,
        mode,
        width,
        height,
        f"{dpi[0]:.0f}x{dpi[1]:.0f}" if dpi else "unavailable",
    )
    log.info("=" * 60)

    return ParsedImage(
        file_name=file_name,
        format=detected_format,
        mode=mode,
        width=width,
        height=height,
        dpi=dpi,
        file_size=file_size,
    )
