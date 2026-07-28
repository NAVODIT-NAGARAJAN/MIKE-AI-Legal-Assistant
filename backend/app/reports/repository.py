"""
LegalEase AI - Report Repository
=================================
Database operations for Reports, Roadmaps, and EvidenceChecklists.
"""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.application_models import EvidenceChecklist, Report, Roadmap
from app.utils.logger import get_logger

log = get_logger(__name__)


class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_report_bundle(
        self,
        user_id: uuid.UUID,
        case_id: uuid.UUID,
        report_data: dict,
    ) -> Report:
        """Create a Report, Roadmap, and EvidenceChecklist in a single transaction."""
        
        # 1. Create Roadmap
        roadmap = Roadmap(
            case_id=case_id,
            user_id=user_id,
            steps=[s for s in report_data["roadmap_steps"]]
        )
        self.db.add(roadmap)

        # 2. Create EvidenceChecklist
        required_docs = [e for e in report_data["evidence_items"] if e["is_required"]]
        optional_docs = [e for e in report_data["evidence_items"] if not e["is_required"]]
        evidence = EvidenceChecklist(
            case_id=case_id,
            user_id=user_id,
            required_documents=required_docs,
            optional_documents=optional_docs
        )
        self.db.add(evidence)

        # 3. Create Report
        report = Report(
            case_id=case_id,
            user_id=user_id,
            case_summary=report_data["case_summary"],
            consumer_rights=report_data["consumer_rights"],
            roadmap_steps=report_data["roadmap_steps"],
            evidence_items=report_data["evidence_items"],
            next_steps=report_data["next_steps"],
            recommended_authority=report_data["recommended_authority"],
        )
        self.db.add(report)

        await self.db.commit()
        await self.db.refresh(report)
        log.info(f"Created report bundle for case {case_id}")
        return report

    async def get_report_by_case(self, case_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Report]:
        stmt = select(Report).where(Report.case_id == case_id, Report.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
