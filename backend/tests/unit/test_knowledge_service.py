"""
Unit Tests — Knowledge Base Service & Embeddings
=================================================
Tests for app/knowledge/service.py and app/knowledge/embedding_service.py.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.knowledge.service import KnowledgeBaseService, RetrievalResult
from app.knowledge.text_processor import TextChunk


class TestEmbeddingService:
    @patch("app.knowledge.embedding_service._get_model")
    def test_generate_embedding(self, mock_get_model):
        mock_model = MagicMock()
        mock_array = MagicMock()
        mock_array.tolist.return_value = [0.1, 0.2, 0.3]
        mock_model.encode.return_value = mock_array
        mock_get_model.return_value = mock_model

        from app.knowledge.embedding_service import generate_embedding
        result = generate_embedding("test query")
        assert result == [0.1, 0.2, 0.3]
        mock_model.encode.assert_called_once()

    @patch("app.knowledge.embedding_service._get_model")
    def test_generate_embeddings_batch(self, mock_get_model):
        mock_model = MagicMock()
        mock_array = MagicMock()
        mock_array.tolist.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_model.encode.return_value = mock_array
        mock_get_model.return_value = mock_model

        from app.knowledge.embedding_service import generate_embeddings_batch
        result = generate_embeddings_batch(["text1", "text2"])
        assert len(result) == 2
        assert result == [[0.1, 0.2], [0.3, 0.4]]

    def test_empty_text_raises_value_error(self):
        from app.knowledge.embedding_service import generate_embedding, generate_embeddings_batch
        with pytest.raises(ValueError):
            generate_embedding("")
        with pytest.raises(ValueError):
            generate_embeddings_batch([])


class TestKnowledgeBaseService:

    @patch("app.knowledge.service.get_collection_count")
    @patch("app.knowledge.service.get_chroma_collection")
    @patch("app.knowledge.service.generate_embedding")
    def test_retrieve_success(self, mock_gen_embed, mock_get_coll, mock_count):
        mock_count.return_value = 10
        mock_gen_embed.return_value = [0.1, 0.2]
        
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["chunk-123"]],
            "documents": [["Legal text chunk"]],
            "metadatas": [[{"source_file": "act.txt", "source_type": "act", "chunk_index": 0}]],
            "distances": [[0.5]]
        }
        mock_get_coll.return_value = mock_collection

        svc = KnowledgeBaseService()
        results = svc.retrieve("test query", top_k=5)

        assert len(results) == 1
        res = results[0]
        assert res.chunk_id == "chunk-123"
        assert res.text == "Legal text chunk"
        assert res.source_type == "act"
        assert res.score == 0.75  # 1.0 - (0.5 / 2.0)

    @patch("app.knowledge.service.get_collection_count")
    def test_retrieve_empty_kb_raises(self, mock_count):
        mock_count.return_value = 0
        svc = KnowledgeBaseService()
        with pytest.raises(RuntimeError, match="Knowledge base is empty"):
            svc.retrieve("test query")

    def test_retrieve_empty_query_raises(self):
        svc = KnowledgeBaseService()
        with pytest.raises(ValueError, match="Query must not be empty"):
            svc.retrieve("")

    @patch("app.knowledge.service.get_collection_count")
    def test_get_status_ready(self, mock_count):
        mock_count.return_value = 42
        svc = KnowledgeBaseService()
        status = svc.get_status()
        assert status["status"] == "ready"
        assert status["total_chunks"] == 42
        assert "collection_name" in status
