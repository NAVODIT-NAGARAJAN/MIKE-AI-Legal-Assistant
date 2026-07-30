"""
Document Intelligence Router
"""

from fastapi import APIRouter, File, Form, UploadFile

router = APIRouter(prefix="/document-intelligence", tags=["Document Intelligence"])


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    message: str = Form("Analyze this document"),
):
    """
    Analyze uploaded documents.
    """

    return {
        "filename": file.filename,
        "message": message,
    }