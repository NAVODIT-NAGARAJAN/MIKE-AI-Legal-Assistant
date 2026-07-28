"""
LegalEase AI - Legal Data Ingestion Script
============================================
CLI script to process and ingest all official Indian consumer rights
documents into the ChromaDB vector database.

Usage:
    python scripts/ingest_legal_data.py              # Normal ingestion
    python scripts/ingest_legal_data.py --reset      # Reset + re-ingest
    python scripts/ingest_legal_data.py --status     # Check current status

Run from the backend/ directory:
    cd backend
    venv\\Scripts\\python scripts/ingest_legal_data.py
"""

import argparse
import sys
import time
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def _setup_logging():
    """Minimal logging setup for the ingestion script."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("ingest")


def cmd_status(log) -> None:
    """Print the current knowledge base status."""
    from app.knowledge.service import KnowledgeBaseService
    svc = KnowledgeBaseService()
    status = svc.get_status()
    log.info(f"Knowledge Base Status: {status['status']}")
    log.info(f"Collection: {status.get('collection_name', 'N/A')}")
    log.info(f"Total chunks: {status.get('total_chunks', 0)}")


def cmd_ingest(log, reset: bool = False) -> None:
    """Run the full ingestion pipeline."""
    from app.knowledge.service import KnowledgeBaseService
    from app.config.settings import settings

    log.info("=" * 60)
    log.info("LegalEase AI — Legal Knowledge Base Ingestion")
    log.info("=" * 60)
    log.info(f"Legal data path: {settings.legal_data_path}")
    log.info(f"ChromaDB path: {settings.chroma_db_path}")
    log.info(f"Embedding model: {settings.embedding_model}")
    log.info(f"Chunk size: {settings.chunk_size} chars | Overlap: {settings.chunk_overlap} chars")
    if reset:
        log.warning("RESET MODE: Existing collection will be cleared.")
    log.info("=" * 60)

    start = time.time()

    svc = KnowledgeBaseService()

    # Check if data files exist
    data_dir = Path(settings.legal_data_path)
    if not data_dir.exists():
        log.error(f"Legal data directory not found: {data_dir}")
        log.error("Create the directory and add .txt or .pdf legal documents.")
        sys.exit(1)

    files = list(data_dir.glob("*.txt")) + list(data_dir.glob("*.pdf"))
    if not files:
        log.error(f"No .txt or .pdf files found in {data_dir}")
        sys.exit(1)

    log.info(f"Found {len(files)} document(s): {[f.name for f in files]}")

    try:
        result = svc.ingest_all_documents(reset=reset)
    except Exception as exc:
        log.error(f"Ingestion failed: {exc}")
        sys.exit(1)

    elapsed = time.time() - start
    log.info("=" * 60)
    log.info(f"Ingestion complete in {elapsed:.1f}s")
    log.info(f"Documents processed: {result['documents_processed']}")
    log.info(f"Chunks ingested: {result['chunks_ingested']}")
    log.info(f"Status: {result['status']}")

    # Final status
    status = svc.get_status()
    log.info(f"Knowledge base now contains {status['total_chunks']} total chunks.")
    log.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="LegalEase AI — Legal Knowledge Base Ingestion Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Reset the ChromaDB collection before ingesting (re-builds from scratch).",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show current knowledge base status and exit.",
    )
    args = parser.parse_args()

    log = _setup_logging()

    if args.status:
        cmd_status(log)
    else:
        cmd_ingest(log, reset=args.reset)


if __name__ == "__main__":
    main()
