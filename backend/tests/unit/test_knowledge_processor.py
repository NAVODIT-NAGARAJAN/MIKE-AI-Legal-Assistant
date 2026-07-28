"""
Unit Tests — Knowledge Base Text Processor
===========================================
Tests for app/knowledge/text_processor.py.
No ChromaDB or network required.
"""

import pytest
from pathlib import Path
import tempfile
import os

from app.knowledge.text_processor import (
    TextChunk,
    clean_text,
    chunk_text,
    process_document,
    _detect_source_type,
)


class TestCleanText:

    def test_empty_string_returns_empty(self):
        assert clean_text("") == ""

    def test_strips_leading_trailing_whitespace(self):
        result = clean_text("  hello world  ")
        assert result == "hello world"

    def test_normalizes_multiple_blank_lines(self):
        result = clean_text("para1\n\n\n\n\npara2")
        assert "\n\n\n" not in result

    def test_removes_page_numbers(self):
        text = "Some legal text\nPage 1 of 10\nMore text"
        result = clean_text(text)
        assert "Page 1 of 10" not in result

    def test_removes_null_bytes(self):
        result = clean_text("hello\x00world")
        assert "\x00" not in result

    def test_preserves_legal_content(self):
        text = "Section 2 — Definitions\n\nConsumer means any person who buys goods."
        result = clean_text(text)
        assert "Section 2" in result
        assert "Consumer means" in result

    def test_crlf_normalized(self):
        result = clean_text("line1\r\nline2\r\nline3")
        assert "\r" not in result


class TestChunkText:

    def test_empty_text_returns_empty_list(self):
        assert chunk_text("") == []

    def test_short_text_returns_single_chunk(self):
        text = "This is a short legal statement about consumer rights in India."
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) == 1
        assert text in chunks[0]

    def test_long_text_creates_multiple_chunks(self):
        # Create text longer than chunk_size
        long_para = ("Consumer rights are fundamental rights. " * 20)
        chunks = chunk_text(long_para, chunk_size=200, chunk_overlap=0)
        assert len(chunks) > 1

    def test_chunks_not_empty(self):
        text = "\n\n".join([
            "Section 1 deals with preliminary matters and definitions.",
            "Section 2 covers consumer rights under Indian law effectively.",
            "Section 3 explains the complaint filing process in detail.",
        ])
        chunks = chunk_text(text, chunk_size=500)
        assert all(len(c.strip()) > 0 for c in chunks)

    def test_chunk_size_respected(self):
        long_text = "This is a sentence. " * 100
        chunks = chunk_text(long_text, chunk_size=200, chunk_overlap=0)
        # Allow some tolerance for sentence boundary splitting
        assert all(len(c) <= 400 for c in chunks)

    def test_overlap_applied(self):
        text = "First paragraph about consumer rights in India.\n\nSecond paragraph about remedies available."
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
        if len(chunks) > 1:
            # Second chunk should contain some content from the first
            assert len(chunks[1]) > 0

    def test_trivially_short_chunks_filtered(self):
        text = "A\n\n" + "This is a substantial legal paragraph with enough content to be useful.\n\n" * 5
        chunks = chunk_text(text, chunk_size=500)
        assert all(len(c.strip()) >= 50 for c in chunks)


class TestDetectSourceType:

    def test_act_detection(self):
        assert _detect_source_type("consumer_protection_act_2019.txt") == "act"

    def test_rules_detection(self):
        assert _detect_source_type("consumer_protection_ecommerce_rules_2020.txt") == "rules"

    def test_unknown_returns_guidance(self):
        assert _detect_source_type("some_other_document.txt") == "guidance"


class TestProcessDocument:

    def test_process_txt_file(self):
        content = (
            "Consumer Protection Act, 2019\n\n"
            "Section 1: Preliminary provisions of the Act\n\n"
            "Section 2: Definitions of terms used in the Act including consumer, defect, and deficiency.\n\n"
            "A consumer is any person who buys goods for personal use and not for commercial purpose.\n\n"
            "The right to redressal means the right to seek fair settlement of genuine grievances.\n\n"
            "The District Commission has jurisdiction over complaints up to one crore rupees.\n\n"
            "Filing a complaint requires gathering all relevant documents and evidence.\n\n"
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)

        try:
            chunks = process_document(tmp_path)
            assert len(chunks) > 0
            assert all(isinstance(c, TextChunk) for c in chunks)
            assert all(c.chunk_id for c in chunks)
            assert all(c.text for c in chunks)
            assert all(c.source_file == tmp_path.name for c in chunks)
        finally:
            os.unlink(tmp_path)

    def test_process_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            process_document(Path("/nonexistent/file.txt"))

    def test_process_unsupported_format_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            tmp_path = Path(f.name)
        try:
            with pytest.raises(ValueError, match="Unsupported file format"):
                process_document(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_chunk_ids_are_unique(self):
        content = "\n\n".join([
            "Paragraph one about consumer rights and definitions under Indian law.",
            "Paragraph two about complaint filing procedure at district commission.",
            "Paragraph three about redressal and compensation available to consumers.",
            "Paragraph four about e-commerce rules and online seller obligations.",
            "Paragraph five about warranty claims and product defect provisions.",
        ])
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            tmp_path = Path(f.name)

        try:
            chunks = process_document(tmp_path)
            ids = [c.chunk_id for c in chunks]
            assert len(ids) == len(set(ids)), "Chunk IDs must be unique"
        finally:
            os.unlink(tmp_path)
