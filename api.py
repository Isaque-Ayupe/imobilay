"""
IMOBILAY — FastAPI Server

Exposição das APIs REST para consumo do Frontend React (Directive 07).
"""

import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

from main import get_pipeline

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

app = FastAPI(title="IMOBILAY API", version="1.0.0")

# Rate Limiter setup
REDIS_URL = os.environ.get("REDIS_URL")
redis_client = redis.from_url(REDIS_URL, decode_responses=True) if redis and REDIS_URL else None
_local_rate_limit = {}

async def check_rate_limit(request: Request, user_id: str | None = None):
    """
    Limita a 10 requisições por minuto por IP ou user_id.
    Retorna 429 se excedido.
    """
    identifier = user_id or request.client.host if request.client else "unknown"
    key = f"rate_limit:{identifier}:{int(time.time() / 60)}"
    limit = 10

    if redis_client:
        try:
            current = await redis_client.incr(key)
            if current == 1:
                await redis_client.expire(key, 60)
            if current > limit:
                raise HTTPException(status_code=429, detail="Too Many Requests. Please try again later.")
            return
        except HTTPException:
            raise
        except Exception:
            pass # Fallback to local if Redis fails

    # Fallback in-memory
    current_time = time.time()
    # Cleanup expired
    expired = [k for k, v in _local_rate_limit.items() if v["expires"] <= current_time]
    for k in expired:
        del _local_rate_limit[k]

    entry = _local_rate_limit.get(key)
    if not entry:
        _local_rate_limit[key] = {"count": 1, "expires": current_time + 60}
    else:
        entry["count"] += 1
        if entry["count"] > limit:
            raise HTTPException(status_code=429, detail="Too Many Requests. Please try again later.")

# CORS config para Vite frontend dev server (default porta 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    response_text: str
    context_data: dict[str, Any]


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request, req: ChatRequest):
    """
    Recebe uma mensagem, executa o pipeline sincronamente (espera todos agentes)
    e retorna o texto e o estado dos dados (ContextStore dumped) pro frontend usar no card.
    """
    try:
        await check_rate_limit(request, req.user_id)

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
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in chat endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


@app.get("/api/health")
async def health_check():
    """Liveness probe."""
    return {"status": "ok", "service": "imobilay-api"}

# Outros endpoints definidos na especificação da Camada 3 e Frontend
# como POST /api/feedback, GET /api/sessions que delegariam ao Supabase (ou repositórios).
