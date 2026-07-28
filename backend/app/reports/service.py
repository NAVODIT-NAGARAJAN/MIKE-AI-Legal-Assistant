"""
LegalEase AI - Report Service
=================================
Service layer for generating and retrieving reports.
"""

import uuid
from typing import Optional

from app.ai_agent.repository import ConversationRepository
from app.models.application_models import Report
from app.reports.ai_formatter import AIFormatter
from app.reports.pdf_generator import PDFGenerator
from app.reports.repository import ReportRepository
from app.utils.logger import get_logger

log = get_logger(__name__)


class ReportService:
    def __init__(self, report_repo: ReportRepository, conv_repo: ConversationRepository):
        self.report_repo = report_repo
        self.conv_repo = conv_repo

    async def generate_report_from_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Report:
        """
        1. Fetch conversation
        2. Verify it's complete and has a case_id
        3. Format via AI
        4. Save Report bundle to DB
        """
        conv = await self.conv_repo.get_by_id(conversation_id, user_id)
        if not conv:
            raise ValueError("Conversation not found or access denied.")
            
        if not conv.is_complete:
            raise ValueError("Cannot generate report for an incomplete conversation.")
            
        if not conv.case_id:
            raise ValueError("Conversation is not linked to a Case ID.")
            
        # Check if report already exists
        existing_report = await self.report_repo.get_report_by_case(conv.case_id, user_id)
        if existing_report:
            log.info(f"Report already exists for case {conv.case_id}")
            return existing_report
            
        # Format via AI
        report_data = await AIFormatter.format_conversation(conv.messages)
        
        # Save bundle
        report = await self.report_repo.create_report_bundle(
            user_id=user_id,
            case_id=conv.case_id,
            report_data=report_data
        )
        return report

    async def get_report(self, case_id: uuid.UUID, user_id: uuid.UUID) -> Report:
        """Fetch an existing report by case ID."""
        report = await self.report_repo.get_report_by_case(case_id, user_id)
        if not report:
            raise ValueError("Report not found for this case.")
        return report

    async def generate_pdf(self, case_id: uuid.UUID, user_id: uuid.UUID) -> bytes:
        """Fetch report and generate a PDF byte stream."""
        report = await self.get_report(case_id, user_id)
        return PDFGenerator.generate_report_pdf(report)
