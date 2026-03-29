"""
IMOBILAY — SemanticRouter (Camada 1)

Classifica a intenção do usuário via embedding similarity.
NUNCA usa LLM — apenas sentence-transformers + cosine similarity.

Estratégia:
1. Gera embedding da mensagem com all-MiniLM-L6-v2
2. Compara contra embeddings pré-computados por intent
3. Retorna RoutingResult com scores e flags de intent composto
"""

from __future__ import annotations

import numpy as np
from typing import Any

from models.routing import RoutingResult


# ── Constantes ───────────────────────────────────────────────

CONFIDENCE_THRESHOLD = 0.65   # mínimo para ativar um intent
LOW_CONFIDENCE = 0.40         # abaixo disso → pedir clarificação
MODEL_NAME = "all-MiniLM-L6-v2"

# Intents suportados e keywords de fallback (caso sentence-transformers não esteja disponível)
INTENT_KEYWORDS = {
    "buscar_imoveis": [
        "apartamento", "quarto", "quartos", "imóvel", "imovel", "procuro",
        "comprar", "alugar", "buscar", "busco", "kitnet", "studio", "cobertura",
        "vaga", "garagem", "bairro", "região", "disponível",
    ],
    "analisar_imovel": [
        "analisar", "análise", "analise", "analisa", "preço justo",
        "vale a pena", "caro", "barato", "metro quadrado", "m²",
        "mercado", "liquidez",
    ],
    "investimento": [
        "investir", "investimento", "roi", "retorno", "payback",
        "rentabilidade", "aluguel", "renda", "capital",
    ],
    "refinar_busca": [
        "agora", "filtrar", "filtra", "tirar", "remover", "ordenar",
        "só", "apenas", "mínimo", "máximo", "maior", "menor",
    ],
}

DEFAULT_INTENT_EXAMPLES = {
    "buscar_imoveis": [
        "quero um apartamento com 2 quartos",
        "procuro imóvel para comprar em pinheiros",
        "busco kitnet perto do metrô",
    ],
    "analisar_imovel": [
        "analisar se esse imóvel está caro",
        "quero saber o preço justo desse apartamento",
        "faça uma análise desse imóvel",
    ],
    "investimento": [
        "quero investir em um apartamento",
        "analise o roi desse imóvel",
        "busco rentabilidade com aluguel",
    ],
    "refinar_busca": [
        "agora filtre só os mais baratos",
        "remova os imóveis sem garagem",
        "ordene pelos melhores",
    ],
}


class SemanticRouter:
    """
    Classificador de intents via embedding similarity.
    Sem LLM — 100% determinístico após os embeddings serem computados.
    """

    def __init__(self):
        self._model = None
        self._intent_embeddings: dict[str, list[np.ndarray]] = {}
        self._embeddings_cache: dict[str, list[np.ndarray]] | None = None
        self._use_fallback = False

    async def initialize(self, intent_examples: dict[str, list[str]] | None = None):
        """
        Inicializa o modelo e computa embeddings dos intents.

        Args:
            intent_examples: dict de intent_name → lista de frases exemplo.
                             Se None, usa embeddings do banco via seed_intents.py.
        """
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(MODEL_NAME)
            self._use_fallback = False

            examples_by_intent = intent_examples or DEFAULT_INTENT_EXAMPLES
            for intent_name, examples in examples_by_intent.items():
                embeddings = self._model.encode(examples)
                self._intent_embeddings[intent_name] = [
                    emb / np.linalg.norm(emb) for emb in embeddings
                ]
            self._embeddings_cache = dict(self._intent_embeddings)

        except ImportError:
            self._use_fallback = True
            self._embeddings_cache = {
                intent_name: [np.array([1.0])]
                for intent_name in (intent_examples or DEFAULT_INTENT_EXAMPLES)
            }

    async def route(self, message: str) -> RoutingResult:
        """
        Classifica a intenção da mensagem.

        Returns:
            RoutingResult com primary_intent, confidence e raw_scores
        """
        if self._use_fallback or self._model is None:
            return self._keyword_fallback(message)

        return self._embedding_route(message)

    def _embedding_route(self, message: str) -> RoutingResult:
        """Classificação via embedding cosine similarity."""
        # Gerar embedding da mensagem
        msg_embedding = self._model.encode([message.lower()])[0]
        msg_embedding = msg_embedding / np.linalg.norm(msg_embedding)

        # Calcular scores por intent (média dos top-3 mais similares)
        raw_scores: dict[str, float] = {}

        for intent_name, embeddings in self._intent_embeddings.items():
            similarities = [
                float(np.dot(msg_embedding, emb))
                for emb in embeddings
            ]
            # Top-3 para robustez (menos sensível a outliers)
            top_k = sorted(similarities, reverse=True)[:3]
            raw_scores[intent_name] = sum(top_k) / len(top_k)

        return self._build_result(raw_scores)

    def _keyword_fallback(self, message: str) -> RoutingResult:
        """Fallback com keyword matching quando sentence-transformers não disponível."""
        msg_lower = message.lower()
        raw_scores: dict[str, float] = {}

        for intent_name, keywords in INTENT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in msg_lower)
            total = len(keywords)
            raw_scores[intent_name] = min(matches / max(total * 0.3, 1), 1.0)

        return self._build_result(raw_scores)

    def _build_result(self, raw_scores: dict[str, float]) -> RoutingResult:
        """Constrói RoutingResult a partir dos scores brutos."""
        if not raw_scores:
            return RoutingResult(
                primary_intent="buscar_imoveis",
                confidence=0.0,
                raw_scores={},
            )

        # Ordenar por score descrescente
        sorted_intents = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)

        primary_intent = sorted_intents[0][0]
        primary_score = sorted_intents[0][1]

        # Verificar intent composto (dois intents acima do threshold)
        secondary_intent = None
        is_compound = False

        if len(sorted_intents) > 1:
            second_intent = sorted_intents[1][0]
            second_score = sorted_intents[1][1]

            if second_score >= CONFIDENCE_THRESHOLD and primary_score >= CONFIDENCE_THRESHOLD:
                secondary_intent = second_intent
                is_compound = True

        return RoutingResult(
            primary_intent=primary_intent,
            secondary_intent=secondary_intent,
            confidence=primary_score,
            is_compound=is_compound,
            raw_scores=raw_scores,
        )

    @property
    def is_ready(self) -> bool:
        """Verifica se o router está inicializado e pronto para classificar."""
        return bool(self._intent_embeddings) or self._use_fallback
