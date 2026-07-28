"""
LegalEase AI - Text Processor
================================
Handles extraction, cleaning, normalization, and chunking of legal documents.

Supported formats: .txt, .pdf
Output: List of TextChunk objects ready for embedding and ingestion.
"""

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.config.settings import settings
from app.utils.logger import get_logger

log = get_logger(__name__)


@dataclass
class TextChunk:
    """
    A single text chunk ready for embedding and ChromaDB ingestion.

    Fields:
        chunk_id    — Unique identifier for this chunk (UUID string).
        text        — Cleaned chunk text content.
        source_file — Filename of the source document.
        source_type — 'act', 'rules', or 'guidance'.
        chunk_index — Sequential index within the source document.
        metadata    — Additional metadata dict stored in ChromaDB.
    """

    chunk_id: str
    text: str
    source_file: str
    source_type: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Source type mapping
# ---------------------------------------------------------------------------

_SOURCE_TYPE_MAP = {
    "consumer_protection_act_2019": "act",
    "consumer_protection_ecommerce_rules_2020": "rules",
    "consumer_protection_rules_2020": "rules",
}


def _detect_source_type(filename: str) -> str:
    stem = Path(filename).stem.lower()
    for key, value in _SOURCE_TYPE_MAP.items():
        if key in stem:
            return value
    return "guidance"


# ---------------------------------------------------------------------------
# Text Extraction
# ---------------------------------------------------------------------------

def extract_text_from_file(file_path: Path) -> str:
    """
    Extract raw text from a .txt or .pdf file.

    Args:
        file_path: Absolute path to the source document.

    Returns:
        Raw text content as a string.

    Raises:
        ValueError: If the file format is not supported.
        FileNotFoundError: If the file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        log.info(f"Extracting text from TXT: {file_path.name}")
        return file_path.read_text(encoding="utf-8", errors="replace")

    elif suffix == ".pdf":
        log.info(f"Extracting text from PDF: {file_path.name}")
        return _extract_pdf_text(file_path)

    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported: .txt, .pdf")


def _extract_pdf_text(file_path: Path) -> str:
    """Extract text from all pages of a PDF file."""
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF processing. Install it with: pip install PyPDF2")

    pages = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        total_pages = len(reader.pages)
        log.info(f"PDF has {total_pages} pages.")
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text)

    return "\n\n".join(pages)


# ---------------------------------------------------------------------------
# Text Cleaning
# ---------------------------------------------------------------------------

def clean_text(raw_text: str) -> str:
    """
    Normalize and clean extracted text for embedding.

    Operations:
        1. Normalize unicode whitespace.
        2. Remove excessive blank lines (max 2 consecutive).
        3. Remove page numbers and headers/footers.
        4. Strip leading/trailing whitespace per line.
        5. Remove null bytes and control characters.

    Args:
        raw_text: Raw extracted text.

    Returns:
        Cleaned, normalized text.
    """
    if not raw_text:
        return ""

    # Remove null bytes and non-printable control characters (keep newlines and tabs)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", raw_text)

    # Normalize unicode whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strip each line of leading/trailing whitespace
    lines = [line.strip() for line in text.split("\n")]

    # Remove isolated page number lines (e.g., "Page 1 of 10", "- 1 -", "1")
    lines = [
        line for line in lines
        if not re.match(r"^(Page\s+\d+(\s+of\s+\d+)?|[-–]\s*\d+\s*[-–]|\d+)$", line, re.IGNORECASE)
    ]

    # Collapse more than 2 consecutive blank lines into 2
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------------------------
# Text Chunking
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> list[str]:
    """
    Split text into overlapping chunks for embedding.

    Strategy:
        - Split on paragraph boundaries first (double newline).
        - If a paragraph exceeds chunk_size, split by sentence.
        - Merge small adjacent chunks to fill chunk_size.
        - Apply overlap between consecutive chunks.

    Args:
        text: Cleaned input text.
        chunk_size: Max characters per chunk (default from settings).
        chunk_overlap: Overlap characters between chunks (default from settings).

    Returns:
        List of text chunks. Each chunk is a non-empty string.
    """
    size = chunk_size or settings.chunk_size
    overlap = chunk_overlap or settings.chunk_overlap

    if not text.strip():
        return []

    # Split into paragraphs
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]

    raw_chunks: list[str] = []

    for para in paragraphs:
        if len(para) <= size:
            raw_chunks.append(para)
        else:
            # Split long paragraphs by sentence
            sentences = re.split(r"(?<=[.!?])\s+", para)
            current = ""
            for sentence in sentences:
                if len(current) + len(sentence) + 1 <= size:
                    current = (current + " " + sentence).strip() if current else sentence
                else:
                    if current:
                        raw_chunks.append(current)
                    current = sentence
            if current:
                raw_chunks.append(current)

    # Merge very small chunks (< 100 chars) with the next chunk
    merged: list[str] = []
    i = 0
    while i < len(raw_chunks):
        chunk = raw_chunks[i]
        while len(chunk) < 100 and i + 1 < len(raw_chunks):
            i += 1
            chunk = chunk + "\n\n" + raw_chunks[i]
        merged.append(chunk)
        i += 1

    # Apply overlap: prepend last `overlap` chars of previous chunk
    final_chunks: list[str] = []
    for i, chunk in enumerate(merged):
        if i > 0 and overlap > 0:
            prev = merged[i - 1]
            tail = prev[-overlap:].strip() if len(prev) > overlap else prev
            chunk = tail + "\n" + chunk
        final_chunks.append(chunk)

    # Final filter: remove empty or trivially short chunks
    return [c for c in final_chunks if len(c.strip()) >= 50]


# ---------------------------------------------------------------------------
# Full Pipeline: file → TextChunks
# ---------------------------------------------------------------------------

def process_document(file_path: Path) -> list[TextChunk]:
    """
    Full pipeline: extract → clean → chunk a single document.

    Args:
        file_path: Path to a .txt or .pdf legal document.

    Returns:
        List of TextChunk objects ready for embedding.
    """
    source_type = _detect_source_type(file_path.name)
    raw_text = extract_text_from_file(file_path)
    clean = clean_text(raw_text)
    chunks = chunk_text(clean)

    result: list[TextChunk] = []
    for idx, chunk_text_content in enumerate(chunks):
        chunk = TextChunk(
            chunk_id=str(uuid.uuid4()),
            text=chunk_text_content,
            source_file=file_path.name,
            source_type=source_type,
            chunk_index=idx,
            metadata={
                "source_file": file_path.name,
                "source_type": source_type,
                "chunk_index": idx,
                "char_count": len(chunk_text_content),
            },
        )
        result.append(chunk)

    log.info(
        f"Processed '{file_path.name}': "
        f"{len(result)} chunks from {len(clean)} chars."
    )
    return result


def process_all_documents(legal_data_path: Optional[str] = None) -> list[TextChunk]:
    """
    Process all .txt and .pdf files in the legal_data directory.

    Args:
        legal_data_path: Override path (default from settings).

    Returns:
        All TextChunks from all documents, combined.
    """
    data_dir = Path(legal_data_path or settings.legal_data_path)
    if not data_dir.exists():
        log.warning(f"Legal data directory not found: {data_dir}")
        return []

    all_chunks: list[TextChunk] = []
    supported = {".txt", ".pdf"}
    files = sorted([f for f in data_dir.iterdir() if f.suffix.lower() in supported])

    if not files:
        log.warning(f"No .txt or .pdf files found in {data_dir}")
        return []

    log.info(f"Found {len(files)} legal document(s) to process.")
    for file_path in files:
        try:
            chunks = process_document(file_path)
            all_chunks.extend(chunks)
        except Exception as exc:
            log.error(f"Failed to process {file_path.name}: {exc}")

    log.info(f"Total chunks generated: {len(all_chunks)}")
    return all_chunks
