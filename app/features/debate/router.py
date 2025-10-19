from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging
import json
from pydantic import BaseModel, Field

from .service import generate_debate


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/debate", tags=["debate"])


class DebateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)


async def debate_event_generator(topic: str):
    """
    Generator that yields Server-Sent Events (SSE) for each debate message.
    
    Format: data: {json}\n\n
    """
    try:
        async for message_data in generate_debate(topic):
            # Format as SSE
            json_data = json.dumps(message_data)
            yield f"data: {json_data}\n\n"
        
        # Send a final event to indicate completion
        yield f"data: {json.dumps({'done': True})}\n\n"
        
    except ValueError as exc:
        # Configuration errors (e.g., missing API key)
        logger.exception("Configuration error while generating debate")
        error_data = {"error": "Server configuration error"}
        yield f"data: {json.dumps(error_data)}\n\n"
    except Exception as exc:
        # Generic errors
        logger.exception("Unhandled error while generating debate")
        error_data = {"error": "Failed to generate debate"}
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/generate")
async def create_debate(body: DebateRequest):
    """
    Generate a debate between two AI agents on a given topic.
    
    Returns a stream of messages using Server-Sent Events (SSE).
    Each event contains: speaker, message, and position.
    """
    try:
        return StreamingResponse(
            debate_event_generator(body.topic.strip()),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable buffering in nginx
            }
        )
    except Exception as exc:
        logger.exception("Error setting up debate stream")
        raise HTTPException(status_code=500, detail="Failed to initiate debate") from exc

