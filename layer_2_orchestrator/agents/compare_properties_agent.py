"""
IMOBILAY — ComparePropertiesAgent

Gera ranking final dos imóveis com score ponderado:
  preço (30%) + localização (25%) + investimento (25%) + oportunidade (20%)

Identifica melhor_opcao e gera justificativa estruturada.
"""

from __future__ import annotations

from models.context import ContextPatch, ContextStore
from models.property import RankingJustificativa, RankingResult
from layer_2_orchestrator.agents.base_agent import BaseAgent


class ComparePropertiesAgent(BaseAgent):
    agent_id = "compare_properties"
    fallback_value = None
    _output_field = "analysis.ranking"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """Gera ranking final comparando todos os imóveis."""
        justificativas = []

        # Mapear dados por property_id
        valuation_map = {v.property_id: v for v in context.analysis.valuation}
        investment_map = {inv.property_id: inv for inv in context.analysis.investment}
        opportunity_map = {o.property_id: o for o in context.analysis.opportunities}

        for prop in context.properties:
            val = valuation_map.get(prop.id)
            inv = investment_map.get(prop.id)
            opp = opportunity_map.get(prop.id)

            # Score de preço (0-10): baseado no desvio percentual
            score_preco = 5.0
            if val:
                desvio = val.desvio_percentual
                # Mais negativo (barato) = melhor score
                score_preco = max(0, min(10, 5 - desvio / 10))

            # Score de localização (0-10)
            score_loc = 5.0
            if prop.location_insights:
                score_loc = prop.location_insights.bairro_score

            # Score de investimento (0-10): baseado no ROI anual
            score_invest = 5.0
            if inv:
                # ROI anual de 5% = score 10, 0% = score 0
                score_invest = max(0, min(10, inv.roi_anual * 2))

            # Score de oportunidade (0-10)
            score_opp = 0.0
            if opp:
                score_opp = opp.score_composto

            # Score total ponderado
            score_total = (
                0.30 * score_preco
                + 0.25 * score_loc
                + 0.25 * score_invest
                + 0.20 * score_opp
            )

            resumo = self._build_resumo(prop, val, inv, opp, score_total)

            justificativas.append(RankingJustificativa(
                property_id=prop.id,
                score_total=round(score_total, 2),
                score_preco=round(score_preco, 2),
                score_localizacao=round(score_loc, 2),
                score_investimento=round(score_invest, 2),
                score_oportunidade=round(score_opp, 2),
                resumo=resumo,
            ))

        # Ordenar por score total descendente
        justificativas.sort(key=lambda j: j.score_total, reverse=True)

        melhor = justificativas[0].property_id if justificativas else None

        ranking = RankingResult(
            ranking=justificativas,
            melhor_opcao=melhor,
            total_avaliados=len(justificativas),
        )

        return ContextPatch(
            agent_id=self.agent_id,
            field="analysis.ranking",
            value=ranking.model_dump(),
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.properties) > 0

    def _build_resumo(self, prop, val, inv, opp, score) -> str:
        """Constrói resumo estruturado para a justificativa."""
        parts = [f"{prop.address}, {prop.neighborhood}"]

        if val:
            parts.append(f"preço {val.classificacao.value}")
        if inv:
            parts.append(f"ROI {inv.roi_anual:.1f}%/ano")
        if opp:
            parts.append(f"oportunidade (score {opp.score_composto:.1f})")

        parts.append(f"score final {score:.1f}/10")

        return " | ".join(parts)
