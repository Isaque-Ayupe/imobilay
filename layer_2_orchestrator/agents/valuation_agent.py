"""
IMOBILAY — ValuationAgent

Calcula preço justo por m² baseado em comparáveis do mesmo bairro.
Classifica: "barato" (<-10%), "justo" (-10% a +10%), "caro" (>+10%).
"""

from __future__ import annotations

from models.context import ContextPatch, ContextStore
from models.property import ValuationResult, ValuationTag
from layer_2_orchestrator.agents.base_agent import BaseAgent


# Preço médio por m² por bairro (mock — substituir por dados reais via Supabase ou API)
PRECO_MEDIO_M2 = {
    "pinheiros":       12500,
    "vila madalena":   11800,
    "brooklin":        13500,
    "moema":           13000,
    "itaim bibi":      15000,
    "setor bueno":     7500,
    "setor marista":   8500,
    "centro":          6000,
}

DEFAULT_PRECO_M2 = 9000


class ValuationAgent(BaseAgent):
    agent_id = "valuation"
    fallback_value = []
    _output_field = "analysis.valuation"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """Calcula preço justo para cada imóvel."""
        valuations = []

        for prop in context.properties:
            bairro = (prop.neighborhood or "").lower().strip()
            preco_m2_mercado = PRECO_MEDIO_M2.get(bairro, DEFAULT_PRECO_M2)

            preco_justo = preco_m2_mercado * prop.area
            preco_justo_m2 = preco_m2_mercado

            desvio = ((prop.price - preco_justo) / preco_justo) * 100 if preco_justo > 0 else 0

            if desvio < -10:
                classificacao = ValuationTag.BARATO
            elif desvio > 10:
                classificacao = ValuationTag.CARO
            else:
                classificacao = ValuationTag.JUSTO

            valuations.append(ValuationResult(
                property_id=prop.id,
                preco_justo=preco_justo,
                preco_justo_por_sqm=preco_justo_m2,
                desvio_percentual=round(desvio, 2),
                classificacao=classificacao,
                comparaveis_usados=5,  # mock
            ))

        return ContextPatch(
            agent_id=self.agent_id,
            field="analysis.valuation",
            value=[v.model_dump() for v in valuations],
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.properties) > 0
