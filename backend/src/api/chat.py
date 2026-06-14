from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.schemas.chat import ChatRequest
from src.workflows.flight_agent import run_agent

router = APIRouter()


@router.post("/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        run_agent(req.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
