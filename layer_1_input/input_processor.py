"""
IMOBILAY — InputProcessor (Camada 1)

Ponto de entrada do pipeline: recebe a mensagem do usuário,
normaliza, gera trace_id e cria o ProcessedInput.
"""

from __future__ import annotations

import re
from uuid import uuid4

from models.context import ProcessedInput, UserProfile


class InputProcessor:
    """
    Responsável por:
    1. Gerar trace_id (UUID) — propagado por todo o sistema
    2. Normalizar a mensagem (strip, remoção de espaços duplos)
    3. Criar perfil default se user_profile é None
    4. Retornar ProcessedInput pronto para o SemanticRouter
    """

    def process(
        self,
        raw_message: str,
        session_id: str,
        user_profile: UserProfile | None = None,
    ) -> ProcessedInput:
        """
        Processa a mensagem bruta e retorna ProcessedInput.

        Args:
            raw_message: mensagem do usuário (pode conter espaços extras, etc.)
            session_id: ID da sessão de conversa
            user_profile: perfil do usuário (criado default se None)

        Returns:
            ProcessedInput pronto para o SemanticRouter

        Raises:
            ValueError: se a mensagem for vazia ou muito curta
        """
        # Normalizar a mensagem
        message = self._normalize(raw_message)

        # Validar
        if not message:
            raise ValueError("Mensagem vazia. Por favor, descreva o que você procura.")

        word_count = len(message.split())
        if word_count < 2:
            raise ValueError(
                "Mensagem muito curta. Pode dar mais detalhes sobre o que procura? "
                "Ex: 'quero um apartamento de 2 quartos em Pinheiros'"
            )

        # Perfil default se não fornecido
        if user_profile is None:
            user_profile = UserProfile()

        return ProcessedInput(
            message=message,
            session_id=session_id,
            user_profile=user_profile,
            trace_id=str(uuid4()),
        )

    def _normalize(self, raw: str) -> str:
        """Normaliza a mensagem: strip, espaços duplos, preserva case original."""
        text = raw.strip()
        text = re.sub(r"\s+", " ", text)     # espaços consecutivos → um só
        return text

    def normalize_for_embedding(self, message: str) -> str:
        """Versão lowercase para comparação de embeddings."""
        return message.lower().strip()
