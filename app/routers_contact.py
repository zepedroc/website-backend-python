from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from .services_contact import draft_contact_message


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
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - generic safety net
        raise HTTPException(status_code=502, detail=f"Failed to generate draft: {str(exc)}") from exc


