"""
Unit Tests — Reports Service & Repository
===========================================
"""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.application_models import Conversation, Report
from app.reports.repository import ReportRepository
from app.reports.service import ReportService

MOCK_USER_ID = uuid.uuid4()
MOCK_CASE_ID = uuid.uuid4()
MOCK_CONV_ID = uuid.uuid4()

MOCK_REPORT_DATA = {
    "case_summary": "Summary",
    "consumer_rights": [{"right": "R1", "description": "D1", "legal_citation": "C1"}],
    "roadmap_steps": [{"step_number": 1, "title": "T1", "description": "D1", "is_done": False}],
    "evidence_items": [{"item": "E1", "is_required": True, "description": "D1"}],
    "next_steps": "N1",
    "recommended_authority": "A1"
}

class TestReportRepository:
    @pytest.mark.asyncio
    async def test_create_report_bundle(self):
        mock_db = AsyncMock()
        repo = ReportRepository(mock_db)
        
        report = await repo.create_report_bundle(MOCK_USER_ID, MOCK_CASE_ID, MOCK_REPORT_DATA)
        
        assert mock_db.add.call_count == 3  # Roadmap, Evidence, Report
        mock_db.commit.assert_called_once()
        assert report.case_summary == "Summary"
        assert report.user_id == MOCK_USER_ID

    @pytest.mark.asyncio
    async def test_get_report_by_case(self):
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars().first.return_value = Report(id=uuid.uuid4(), case_id=MOCK_CASE_ID)
        mock_db.execute.return_value = mock_result
        
        repo = ReportRepository(mock_db)
        report = await repo.get_report_by_case(MOCK_CASE_ID, MOCK_USER_ID)
        assert report is not None
        assert report.case_id == MOCK_CASE_ID

class TestReportService:
    @pytest.mark.asyncio
    @patch("app.reports.service.AIFormatter")
    async def test_generate_report_from_conversation(self, mock_formatter):
        mock_formatter.format_conversation = AsyncMock(return_value=MOCK_REPORT_DATA)
        
        mock_report_repo = AsyncMock()
        mock_report_repo.get_report_by_case.return_value = None
        mock_report_repo.create_report_bundle.return_value = Report(case_id=MOCK_CASE_ID)
        
        mock_conv_repo = AsyncMock()
        conv = Conversation(id=MOCK_CONV_ID, case_id=MOCK_CASE_ID, is_complete=True, messages=[])
        mock_conv_repo.get_by_id.return_value = conv
        
        service = ReportService(mock_report_repo, mock_conv_repo)
        report = await service.generate_report_from_conversation(MOCK_CONV_ID, MOCK_USER_ID)
        
        assert report is not None
        assert report.case_id == MOCK_CASE_ID
        mock_formatter.format_conversation.assert_called_once()
        mock_report_repo.create_report_bundle.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_report_incomplete_conversation_raises(self):
        mock_report_repo = AsyncMock()
        mock_conv_repo = AsyncMock()
        conv = Conversation(id=MOCK_CONV_ID, case_id=MOCK_CASE_ID, is_complete=False)
        mock_conv_repo.get_by_id.return_value = conv
        
        service = ReportService(mock_report_repo, mock_conv_repo)
        with pytest.raises(ValueError, match="Cannot generate report for an incomplete conversation"):
            await service.generate_report_from_conversation(MOCK_CONV_ID, MOCK_USER_ID)

    @pytest.mark.asyncio
    @patch("app.reports.service.PDFGenerator")
    async def test_generate_pdf(self, mock_pdf_gen):
        mock_pdf_gen.generate_report_pdf.return_value = b"pdf_data"
        mock_report_repo = AsyncMock()
        mock_report_repo.get_report_by_case.return_value = Report(case_id=MOCK_CASE_ID)
        mock_conv_repo = AsyncMock()
        
        service = ReportService(mock_report_repo, mock_conv_repo)
        pdf = await service.generate_pdf(MOCK_CASE_ID, MOCK_USER_ID)
        
        assert pdf == b"pdf_data"
