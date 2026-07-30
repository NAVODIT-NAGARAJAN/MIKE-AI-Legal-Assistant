"""
PDF Parser tool for the Document Intelligence Agent.

Responsibilities:
- Accept a PDF file path or raw bytes as input.
- Extract full text from text-based PDFs using PyPDF2.
- Detect scanned PDFs (pages with no extractable text) and
  delegate those pages to the OCR module.
- Return a structured ParsedDocument result containing:
    - Extracted text (joined across all pages)
    - Per-page text breakdown
    - Page count
    - Whether OCR was applied
    - Source file name

This module does NOT perform:
- Legal analysis
- Entity extraction
- Clause detection
- Risk detection
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

import PyPDF2
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from app.utils.logger import get_logger

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Threshold: a page with fewer characters than this is considered scanned.
# ---------------------------------------------------------------------------
_SCANNED_PAGE_CHAR_THRESHOLD = 20


# =============================================================================
# Result dataclass
# =============================================================================


@dataclass
class ParsedDocument:
    """
    Structured result returned by the PDF parser.

    Fields:
        file_name       : Original file name, if available.
        page_count      : Total number of pages in the PDF.
        pages           : Per-page extracted text. Index 0 = page 1.
        full_text       : All page text joined with double newlines.
        character_count : Total character count of full_text.
        ocr_applied     : True if at least one page was processed via OCR.
        scanned_pages   : 1-based list of page numbers that required OCR.
    """

    file_name: Optional[str]
    page_count: int
    pages: List[str] = field(default_factory=list)
    full_text: str = ""
    character_count: int = 0
    ocr_applied: bool = False
    scanned_pages: List[int] = field(default_factory=list)


# =============================================================================
# Exceptions
# =============================================================================


class PDFParserError(Exception):
    """
    Raised when the PDF parser cannot process the provided document.
    """


class EmptyDocumentError(PDFParserError):
    """
    Raised when the PDF yields no extractable text on any page,
    even after OCR delegation.
    """


# =============================================================================
# Internal helpers
# =============================================================================


def _is_scanned_page(text: str) -> bool:
    """
    Return True if the extracted page text is too short to be a real
    text-based page and should be sent to OCR.
    """
    return len(text.strip()) < _SCANNED_PAGE_CHAR_THRESHOLD


def _open_reader(source: Union[str, Path, bytes]) -> tuple[PdfReader, Optional[str]]:
    """
    Open a PdfReader from a file path or raw bytes.

    Returns:
        (PdfReader, file_name) — file_name is None when source is bytes.

    Raises:
        PDFParserError: If the source cannot be read as a PDF.
    """
    if isinstance(source, bytes):
        try:
            reader = PdfReader(io.BytesIO(source))
            return reader, None
        except PdfReadError as exc:
            raise PDFParserError(f"Invalid PDF bytes: {exc}") from exc

    file_path = Path(source)

    if not file_path.exists():
        raise PDFParserError(f"PDF file not found: {file_path}")

    if not file_path.is_file():
        raise PDFParserError(f"Path is not a file: {file_path}")

    if file_path.stat().st_size == 0:
        raise PDFParserError(f"PDF file is empty: {file_path}")

    try:
        reader = PdfReader(str(file_path))
        return reader, file_path.name
    except PdfReadError as exc:
        raise PDFParserError(f"Cannot read PDF file '{file_path.name}': {exc}") from exc


def _extract_page_text(page: PyPDF2.PageObject) -> str:
    """
    Extract text from a single PdfReader page object.
    Returns an empty string if extraction fails.
    """
    try:
        text = page.extract_text()
        return text if text else ""
    except Exception:
        return ""


# =============================================================================
# Public API
# =============================================================================


def parse_pdf(
    source: Union[str, Path, bytes],
    *,
    ocr_fallback: bool = True,
) -> ParsedDocument:
    """
    Extract text and metadata from a PDF document.

    Args:
        source       : Absolute file path (str or Path) or raw PDF bytes.
        ocr_fallback : When True, pages that yield no extractable text are
                       sent to the OCR module. Defaults to True.

    Returns:
        ParsedDocument with full_text, page breakdown, and metadata.

    Raises:
        PDFParserError    : On unreadable, encrypted, or non-PDF input.
        EmptyDocumentError: When all pages are blank after OCR.
    """

    log.info("=" * 60)
    log.info("PDFParser: starting extraction.")

    reader, file_name = _open_reader(source)

    # ------------------------------------------------------------------
    # Encryption check
    # ------------------------------------------------------------------
    if reader.is_encrypted:
        raise PDFParserError(
            "The PDF is password-protected and cannot be processed. "
            "Please provide an unencrypted copy."
        )

    page_count = len(reader.pages)
    log.info("PDFParser: opened '%s' — %d page(s).", file_name or "<bytes>", page_count)

    if page_count == 0:
        raise PDFParserError("The PDF contains no pages.")

    # ------------------------------------------------------------------
    # Per-page extraction
    # ------------------------------------------------------------------
    pages: List[str] = []
    scanned_pages: List[int] = []
    ocr_applied = False

    for page_index, page in enumerate(reader.pages):
        page_number = page_index + 1
        raw_text = _extract_page_text(page)

        if _is_scanned_page(raw_text):
            # Delegate to OCR if enabled
            if ocr_fallback:
                log.info(
                    "PDFParser: page %d appears scanned — delegating to OCR.",
                    page_number,
                )
                ocr_text = _ocr_page(page, page_number)
                pages.append(ocr_text)
                scanned_pages.append(page_number)
                ocr_applied = True
            else:
                log.warning(
                    "PDFParser: page %d is scanned and OCR fallback is disabled. "
                    "Page will be empty.",
                    page_number,
                )
                pages.append("")
        else:
            pages.append(raw_text.strip())
            log.debug(
                "PDFParser: page %d extracted %d characters.",
                page_number,
                len(raw_text.strip()),
            )

    # ------------------------------------------------------------------
    # Assemble full text
    # ------------------------------------------------------------------
    full_text = "\n\n".join(p for p in pages if p.strip())
    character_count = len(full_text)

    if character_count == 0:
        raise EmptyDocumentError(
            "The PDF yielded no extractable text on any page, "
            "even after OCR processing."
        )

    log.info(
        "PDFParser: extraction complete. "
        "Pages: %d | Characters: %d | OCR applied: %s | Scanned pages: %s",
        page_count,
        character_count,
        ocr_applied,
        scanned_pages if scanned_pages else "none",
    )
    log.info("=" * 60)

    return ParsedDocument(
        file_name=file_name,
        page_count=page_count,
        pages=pages,
        full_text=full_text,
        character_count=character_count,
        ocr_applied=ocr_applied,
        scanned_pages=scanned_pages,
    )


# =============================================================================
# OCR delegation (thin adapter — OCR logic lives in tools/ocr.py)
# =============================================================================


def _ocr_page(page: PyPDF2.PageObject, page_number: int) -> str:
    """
    Delegate a scanned PDF page to the OCR module.

    Imports ocr.py lazily to avoid a hard dependency at module load time.
    Falls back to an empty string if the OCR module is unavailable.
    """
    try:
        from .ocr import run_ocr_on_pdf_page  # type: ignore[import]

        return run_ocr_on_pdf_page(page, page_number)

    except ImportError:
        log.warning(
            "PDFParser: OCR module (tools/ocr.py) is not available. "
            "Page %d will be empty.",
            page_number,
        )
        return ""

    except Exception as exc:
        log.warning(
            "PDFParser: OCR failed for page %d — %s. Page will be empty.",
            page_number,
            exc,
        )
        return ""
