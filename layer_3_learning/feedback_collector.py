"""
IMOBILAY — FeedbackCollector

Captura e registra sinais de qualidade do usuário.
Pode ser:
- Explícito (rating 1-5, comentário)
- Implícito (inferido a partir das ações do usuário: salvar imóvel, follow-up)

Todos os feedbacks são persistidos via FeedbackRepository.
"""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import uuid4

from models.feedback import FeedbackRecord, ImplicitSignal
from database.client import get_system_client
from database.repositories.feedback_repository import FeedbackRepository, FeedbackRecordRow

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """Coleta e armazena feedbacks dos usuários."""

    def __init__(self, repository: FeedbackRepository | None = None):
        self._repo = repository

    async def _get_repo(self) -> FeedbackRepository:
        if self._repo is None:
            self._repo = FeedbackRepository(await get_system_client())
        return self._repo

    async def collect_explicit(
        self,
        trace_id: str,
        user_id: str,
        rating: int,
        session_id: str | None = None,
        intent_original: str | None = None,
    ) -> FeedbackRecordRow | None:
        """Coleta feedback direto do usuário (estrelas, like/dislike)."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating deve ser entre 1 e 5")

        try:
            repo = await self._get_repo()
            return await repo.save(
                trace_id=trace_id,
                user_id=user_id,
                session_id=session_id,
                explicit_rating=rating,
                implicit_signal=ImplicitSignal.GOOD.value if rating >= 4 else (
                    ImplicitSignal.NEEDS_IMPROVEMENT.value if rating <= 2 else ImplicitSignal.UNCERTAIN.value
                ),
                intent_original=intent_original,
            )
        except Exception as e:
            logger.error(f"Erro ao salvar feedback explícito: {e}")

        return None

    async def infer_implicit(
        self,
        trace_id: str,
        user_id: str,
        action: str,
        session_id: str | None = None,
        intent_original: str | None = None,
    ) -> FeedbackRecordRow | None:
        """
        Infere feedback a partir das ações do usuário.
        
        Ações conhecidas:
        - "saved_property" -> GOOD
        - "clicked_link" -> GOOD
        - "requested_adjustment" -> NEEDS_IMPROVEMENT
        - "abandoned_session" -> UNCERTAIN
        """
        signal_map = {
            "saved_property": ImplicitSignal.GOOD,
            "clicked_link": ImplicitSignal.GOOD,
            "requested_adjustment": ImplicitSignal.NEEDS_IMPROVEMENT,
            "abandoned_session": ImplicitSignal.UNCERTAIN,
        }

        signal = signal_map.get(action)
        if not signal:
            logger.warning(f"Ação desconhecida para inferência de feedback: {action}")
            return None

        try:
            repo = await self._get_repo()
            return await repo.save(
                trace_id=trace_id,
                user_id=user_id,
                session_id=session_id,
                implicit_signal=signal.value,
                intent_original=intent_original,
            )
        except Exception as e:
            logger.error(f"Erro ao salvar feedback implícito: {e}")

        return None
