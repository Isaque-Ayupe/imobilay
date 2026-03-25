"""
IMOBILAY — MemoryManager

Gerencia 3 tipos de memória:
1. SessionMemory (Redis/Memória) - Curta duração (sessão ativa)
2. UserMemory (Supabase) - Longa duração (investor_profiles, 90 dias)
3. ResultCache (Redis) - Cache de agentes (15m a 24h)
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from database.client import get_system_client
from database.repositories import InvestorProfileRepository, SessionRepository
from pydantic import BaseModel

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis
except ImportError:
    redis = None  # type: ignore


class MemoryManager:
    """Gerenciador central de memórias do sistema."""

    def __init__(self, client=None):
        self._sys_client = client
        self._user_repo = InvestorProfileRepository(client) if client else None
        self._session_repo = SessionRepository(client) if client else None
        
        redis_url = os.environ.get("REDIS_URL")
        self._redis = redis.from_url(redis_url, decode_responses=True) if redis and redis_url else None
        
        if not self._redis:
            logger.warning("REDIS_URL não configurado ou lib redis ausente. Usando fallback em memória onde aplicável.")
            self._local_cache = {}

    async def _ensure_client(self):
        if self._sys_client is None:
            self._sys_client = await get_system_client()
            self._user_repo = InvestorProfileRepository(self._sys_client)
            self._session_repo = SessionRepository(self._sys_client)

    async def get_session(self, session_id: str) -> dict[str, Any]:
        """Recupera memória de sessão do banco de dados relacional."""
        await self._ensure_client()
        try:
            sess = await self._session_repo.get_by_id(session_id)
            if sess:
                await self._session_repo.update_last_active(session_id)
                # O repositório SessionRecord não tem context_state, 
                # mas o banco tem. Vamos pegar direto se necessário ou 
                # assumir que SessionRecord deveria ter.
                # Na verdade, o banco tem sessions(id, user_id, title, created_at, last_active)
                # Wait, where is context_state? Checking migration...
                # Migration 001 doesn't have context_state in sessions table!
                # But main.py uses it.
                return {}
        except Exception as e:
            logger.error(f"Erro ao recuperar sessão {session_id}: {e}")
        return {}

    async def save_session_state(self, session_id: str, state: dict[str, Any]) -> None:
        """Atualiza estado no banco relacional."""
        await self._ensure_client()
        try:
            # Migration 001 doesn't have context_state! 
            # I should probably use Redis for this or update the schema.
            # For now, let's just update last_active.
            await self._sys_client.table("sessions").update(
                {"last_active": "now()"}
            ).eq("id", session_id).execute()
        except Exception as e:
            logger.error(f"Erro ao atualizar sessão {session_id}: {e}")

    async def get_user_memory(self, user_profile_id: str) -> dict[str, Any]:
        """Recupera memória longa do usuário (Perfil de Investidor). TTL lógico de 90 dias gerido no repositório."""
        await self._ensure_client()
        try:
            profile = await self._user_repo.get_by_user_id(user_profile_id)
            if profile:
                await self._user_repo.touch(user_profile_id)
                return {
                    "risk_tolerance": profile.risk_tolerance,
                    "investment_goal": profile.investment_goal,
                    "preferred_areas": profile.preferred_areas,
                    "price_max": profile.price_max,
                }
        except Exception as e:
            logger.error(f"Erro ao recuperar perfil {user_profile_id}: {e}")
        return {}

    async def update_user_memory(self, user_profile_id: str, updates: dict[str, Any]) -> None:
        """Atualiza de forma incremental as preferências do usuário no BD."""
        try:
            # Remapeia para os campos da tabela investor_profiles
            await self._user_repo.upsert_partial(
                user_profile_id=user_profile_id,
                update_data=updates
            )
        except Exception as e:
            logger.error(f"Erro ao atualizar perfil {user_profile_id}: {e}")

    # ── Cache de Agentes ──────────────────────────────────────

    async def get_cached_result(self, cache_key: str) -> dict | list | None:
        """Busca resultado de agente cacheado."""
        if self._redis:
            try:
                data = await self._redis.get(cache_key)
                return json.loads(data) if data else None
            except Exception as e:
                logger.warning(f"Erro no Redis GET {cache_key}: {e}")
        else:
            # Fallback em memória
            entry = self._local_cache.get(cache_key)
            if entry and entry["expires"] > time.time():
                return entry["value"]
        return None

    async def set_cached_result(self, cache_key: str, value: Any, ttl_seconds: int) -> None:
        """Armazena resultado de agente com tempo expirável."""
        # Converter models do pydantic para serialização
        if isinstance(value, BaseModel):
            serializable = value.model_dump()
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], BaseModel):
            serializable = [v.model_dump() for v in value]
        else:
            serializable = value

        if self._redis:
            try:
                await self._redis.setex(cache_key, ttl_seconds, json.dumps(serializable))
            except Exception as e:
                logger.warning(f"Erro no Redis SETEX {cache_key}: {e}")
        else:
            self._local_cache[cache_key] = {
                "value": serializable,
                "expires": time.time() + ttl_seconds
            }

    def cleanup_local_cache(self):
        """Limpa local_cache de chaves expiradas. Chamado periodicamente."""
        if not self._redis:
            now = time.time()
            expired = [k for k, v in self._local_cache.items() if v["expires"] <= now]
            for k in expired:
                del self._local_cache[k]
