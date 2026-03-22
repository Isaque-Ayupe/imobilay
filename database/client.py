"""
IMOBILAY — Cliente Supabase

Dois clientes distintos por design:
  - system_client: usa service_role, bypassa RLS, usado pelos agentes do pipeline
  - user_client:   usa anon_key + JWT do usuário, respeita RLS, usado pelo frontend

O sistema é 100% async (asyncio) — usar SEMPRE AsyncClient.
"""

import os
from supabase._async.client import AsyncClient
from supabase._async.client import create_client as acreate_client
from dotenv import load_dotenv

load_dotenv()

# ── Singleton do cliente de sistema ──────────────────────────
_system_client: AsyncClient | None = None


async def get_system_client() -> AsyncClient:
    """
    Retorna o cliente com service_role key.
    Singleton — criado uma vez e reutilizado por todo o processo.

    Usar para: agentes do pipeline, ObservabilityLayer,
    FeedbackCollector, RouterFeedbackLoop.
    """
    global _system_client
    if _system_client is None:
        _system_client = await acreate_client(
            supabase_url=os.environ["SUPABASE_URL"],
            supabase_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
    return _system_client


async def get_user_client(user_jwt: str) -> AsyncClient:
    """
    Retorna cliente com contexto de usuário autenticado.
    NÃO é singleton — cada request recebe sua própria instância
    para evitar vazamento de sessão entre usuários diferentes.

    Usar para: leitura de histórico, perfil, imóveis salvos via frontend.
    """
    client = await acreate_client(
        supabase_url=os.environ["SUPABASE_URL"],
        supabase_key=os.environ["SUPABASE_ANON_KEY"],
    )
    await client.auth.set_session(
        access_token=user_jwt,
        refresh_token="",
    )
    return client
