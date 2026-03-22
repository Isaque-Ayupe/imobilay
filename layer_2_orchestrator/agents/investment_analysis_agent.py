"""
IMOBILAY — InvestmentAnalysisAgent

Calcula métricas de investimento:
  - aluguel_estimado: % do valor de mercado por tipo/bairro
  - roi_mensal: aluguel / preço × 100
  - payback_anos: preço / (aluguel × 12)
  - potencial_valorizacao: baseado em liquidez + infraestrutura
"""

from __future__ import annotations

from models.context import ContextPatch, ContextStore
from models.property import InvestmentResult, AppreciationPotential
from layer_2_orchestrator.agents.base_agent import BaseAgent


# Taxa de aluguel mensal como % do valor do imóvel (mock por tipo)
RENTAL_YIELD = {
    "apartamento": 0.004,  # 0.4% ao mês
    "studio":      0.005,  # 0.5% (studios têm yield maior)
    "cobertura":   0.003,  # 0.3%
    "kitnet":      0.006,  # 0.6%
    "casa":        0.003,
}

DEFAULT_YIELD = 0.004


class InvestmentAnalysisAgent(BaseAgent):
    agent_id = "investment_analysis"
    fallback_value = []
    _output_field = "analysis.investment"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """Calcula ROI, payback e potencial para cada imóvel."""
        investments = []

        for prop in context.properties:
            yield_rate = RENTAL_YIELD.get(prop.property_type.value, DEFAULT_YIELD)

            aluguel_estimado = prop.price * yield_rate
            roi_mensal = (aluguel_estimado / prop.price) * 100 if prop.price > 0 else 0
            roi_anual = roi_mensal * 12
            payback = prop.price / (aluguel_estimado * 12) if aluguel_estimado > 0 else 999

            # Potencial de valorização baseado em location_insights
            potencial = self._calculate_potential(prop)

            investments.append(InvestmentResult(
                property_id=prop.id,
                aluguel_estimado=round(aluguel_estimado, 2),
                roi_mensal=round(roi_mensal, 4),
                roi_anual=round(roi_anual, 2),
                payback_anos=round(payback, 1),
                potencial_valorizacao=potencial,
            ))

        return ContextPatch(
            agent_id=self.agent_id,
            field="analysis.investment",
            value=[inv.model_dump() for inv in investments],
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.properties) > 0 and len(context.analysis.valuation) > 0

    def _calculate_potential(self, prop) -> AppreciationPotential:
        """Calcula potencial de valorização baseado em dados de localização."""
        if not prop.location_insights:
            return AppreciationPotential.MEDIO

        score = prop.location_insights.bairro_score
        liquidez = prop.location_insights.liquidez_estimada

        if score >= 8.0 and liquidez == "alta":
            return AppreciationPotential.ALTO
        elif score >= 6.0 and liquidez in ("media", "alta"):
            return AppreciationPotential.MEDIO
        return AppreciationPotential.BAIXO
