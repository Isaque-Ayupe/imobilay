"""
IMOBILAY — FastAPI Server

Exposição das APIs REST para consumo do Frontend React (Directive 07).
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
from datetime import datetime

from main import get_pipeline

app = FastAPI(title="IMOBILAY API", version="1.0.0")

# CORS config para Vite frontend dev server (default porta 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    🛡️ Sentinel: Adiciona cabeçalhos de segurança (Security Headers)
    para todas as respostas (Defense in Depth).
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    response_text: str
    context_data: dict[str, Any]


class SessionResponse(BaseModel):
    id: str
    title: str
    timestamp: datetime
    isToday: bool
    isYesterday: bool


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Recebe uma mensagem, executa o pipeline sincronamente (espera todos agentes)
    e retorna o texto e o estado dos dados (ContextStore dumped) pro frontend usar no card.
    """
    import uuid
    import logging
    logger = logging.getLogger(__name__)

    # Validate UUID formats if provided
    try:
        if req.user_id:
            uuid.UUID(req.user_id)
        if req.session_id:
            uuid.UUID(req.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id or session_id format. Must be a valid UUID string.")

    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        pipeline = await get_pipeline()
        resp_text, ctx = await pipeline.run(
            message=req.message,
            user_id=req.user_id,
            session_id=req.session_id
        )

        return ChatResponse(
            response_text=resp_text,
            context_data=ctx.model_dump(mode="json")
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = str(e).lower()

        # Determine if it's likely a 502/503 external dependency issue
        if "timeout" in error_msg or "connection" in error_msg or "supabase" in error_msg or "openai" in error_msg or "llm" in error_msg:
            logger.error(f"External dependency or connection error in chat endpoint: {str(e)}")
            raise HTTPException(status_code=502, detail="Failed to communicate with external dependencies (e.g., LLM or database).")
        else:
            logger.error(f"Error in chat endpoint: {str(e)}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="An internal server error occurred processing the chat message.")


@app.get("/api/sessions", response_model=list[SessionResponse])
async def list_sessions(user_id: str):
    """
    Retorna as sessões de chat do usuário.
    """
    try:
        from database.client import get_system_client
        from database.repositories.session_repository import SessionRepository
        import uuid

        try:
            # Validate user_id is a valid UUID
            uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user_id format. Must be a UUID.")
        
        supabase = await get_system_client()
        repo = SessionRepository(supabase)
        sessions = await repo.list_by_user(user_id)
        
        if not sessions:
            raise HTTPException(status_code=404, detail="No sessions found for this user.")

        from datetime import timedelta
        response_list = []
        for s in sessions:
            is_today = s.last_active.date() == datetime.now().date()
            is_yesterday = s.last_active.date() == (datetime.now().date() - timedelta(days=1))

            response_list.append(SessionResponse(
                id=str(s.id),
                title=s.title or "Nova conversa",
                timestamp=s.last_active,
                isToday=is_today,
                isYesterday=is_yesterday
            ))

        return response_list
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching sessions for user {user_id}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal server error occurred while fetching sessions.")


class DependencyStatus(BaseModel):
    supabase: str
    redis: str

class HealthResponse(BaseModel):
    status: str
    service: str
    dependencies: DependencyStatus

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Liveness probe with real connectivity checks."""
    import os
    import logging
    from database.client import get_system_client

    logger = logging.getLogger(__name__)
    deps_status = DependencyStatus(supabase="unknown", redis="unknown")
    overall_status = "ok"

    # Check Supabase
    try:
        supabase = await get_system_client()
        # Simple query to check connectivity
        await supabase.table("sessions").select("id").limit(1).execute()
        deps_status.supabase = "ok"
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        deps_status.supabase = "error"
        overall_status = "error"

    # Check Redis
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        try:
            import redis.asyncio as redis_async
            redis_client = redis_async.from_url(redis_url, decode_responses=True)
            await redis_client.ping()
            await redis_client.aclose()
            deps_status.redis = "ok"
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            deps_status.redis = "error"
            overall_status = "error"
    else:
        deps_status.redis = "not_configured"

    if overall_status == "error":
        raise HTTPException(
            status_code=503,
            detail=HealthResponse(
                status=overall_status,
                service="imobilay-api",
                dependencies=deps_status
            ).model_dump()
        )

    return HealthResponse(
        status=overall_status,
        service="imobilay-api",
        dependencies=deps_status
    )

# Outros endpoints definidos na especificação da Camada 3 e Frontend
# como POST /api/feedback, GET /api/sessions que delegariam ao Supabase (ou repositórios).
