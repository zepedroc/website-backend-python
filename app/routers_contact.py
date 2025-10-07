from fastapi import APIRouter, HTTPException
import logging
from pydantic import BaseModel, EmailStr, Field

from .services_contact import draft_contact_message, improve_contact_draft


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/contact", tags=["contact"])


class DraftRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=200)


class DraftResponse(BaseModel):
    draft: str


@router.post("/draft", response_model=DraftResponse)
async def create_draft(body: DraftRequest) -> DraftResponse:
    try:
        draft = await draft_contact_message(body.name.strip(), body.email, body.subject.strip())
        if not draft:
            raise HTTPException(status_code=502, detail="Empty draft returned by the model")
        return DraftResponse(draft=draft)
    except HTTPException:
        raise
    except ValueError as exc:
        # Configuration errors (e.g., missing API key)
        logger.exception("Configuration error while generating draft")
        raise HTTPException(status_code=500, detail="Server configuration error") from exc
    except Exception as exc:  # pragma: no cover - generic safety net
        logger.exception("Unhandled error while generating draft")
        raise HTTPException(status_code=502, detail="Failed to generate draft") from exc



class ImproveDraftRequest(BaseModel):
    draft: str = Field(..., min_length=1)
    comment: str = Field(..., min_length=1)


@router.post("/draft/improve", response_model=DraftResponse)
async def improve_draft(body: ImproveDraftRequest) -> DraftResponse:
    try:
        improved = await improve_contact_draft(body.draft.strip(), body.comment.strip())
        if not improved:
            raise HTTPException(status_code=502, detail="Empty improved draft returned by the model")
        return DraftResponse(draft=improved)
    except HTTPException:
        raise
    except ValueError as exc:
        # Configuration errors (e.g., missing API key)
        logger.exception("Configuration error while improving draft")
        raise HTTPException(status_code=500, detail="Server configuration error") from exc
    except Exception as exc:  # pragma: no cover - generic safety net
        logger.exception("Unhandled error while improving draft")
        raise HTTPException(status_code=502, detail="Failed to improve draft") from exc


