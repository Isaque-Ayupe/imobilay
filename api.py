"""
IMOBILAY — FastAPI Server

Exposição das APIs REST para consumo do Frontend React (Directive 07).
"""

from fastapi import FastAPI, HTTPException
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


class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    response_text: str
    context_data: dict[str, Any]


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Recebe uma mensagem, executa o pipeline sincronamente (espera todos agentes)
    e retorna o texto e o estado dos dados (ContextStore dumped) pro frontend usar no card.
    """
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
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in chat endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


@app.get("/api/sessions")
async def list_sessions(user_id: str):
    """
    Retorna as sessões de chat do usuário.
    """
    try:
        from database.client import get_supabase
        from database.repositories.session_repository import SessionRepository
        
        supabase = await get_supabase()
        repo = SessionRepository(supabase)
        sessions = await repo.list_by_user(user_id)
        
        return [
            {
                "id": str(s.id),
                "title": s.title or "Nova conversa",
                "timestamp": s.last_active,
                "isToday": s.last_active.date() == datetime.now().date(),
                # Lógica simples para isYesterday/isToday para o frontend
            } for s in sessions
        ]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Liveness probe."""
    return {"status": "ok", "service": "imobilay-api"}

# Outros endpoints definidos na especificação da Camada 3 e Frontend
# como POST /api/feedback, GET /api/sessions que delegariam ao Supabase (ou repositórios).
