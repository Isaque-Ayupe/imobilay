"""
IMOBILAY — InvestmentAnalysisAgent

Calcula métricas de investimento com dados dinâmicos:
  - aluguel_estimado: yield por tipo/bairro com referência FipeZAP Aluguel
  - roi_mensal: aluguel / preço × 100
  - roi_anual: roi_mensal × 12
  - payback_anos: preço / (aluguel × 12)
  - potencial_valorizacao: baseado em liquidez + infraestrutura real
"""

from __future__ import annotations

import logging

from models.context import ContextPatch, ContextStore
from models.property import InvestmentResult, AppreciationPotential
from layer_2_orchestrator.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


# Yield médio mensal por tipo de imóvel (% do valor)
# Fonte: FipeZAP Índice de Aluguel (médias nacionais + ajustes por tipo)
# Atualizado periodicamente — valores representam tendência de mercado
RENTAL_YIELD_BY_TYPE = {
    "apartamento": 0.0042,   # ~0.42% ao mês (~5.0% a.a.)
    "studio":      0.0055,   # ~0.55% (studios e flats têm yield maior)
    "cobertura":   0.0030,   # ~0.30% (coberturas tendem a ter yield menor)
    "kitnet":      0.0060,   # ~0.60% (kitnet/quitinete = maior yield relativo)
    "casa":        0.0032,   # ~0.32%
    "sobrado":     0.0032,
    "terreno":     0.0000,   # terreno não gera aluguel
    "comercial":   0.0050,   # ~0.50%
}

# Ajuste de yield por bairro (premium = yield menor, popular = yield maior)
# Fonte: dados de mercado e tendências regionais
BAIRRO_YIELD_ADJUSTMENT: dict[str, float] = {
    # SP - Bairros premium (investidores pagam mais, yield relativo menor)
    "itaim bibi":      -0.0008,
    "jardins":         -0.0010,
    "vila olímpia":    -0.0005,
    "pinheiros":       -0.0003,
    "vila madalena":   -0.0002,
    "brooklin":        -0.0005,
    "moema":           -0.0005,
    # SP - Bairros com bom yield
    "tatuapé":          0.0005,
    "santana":          0.0004,
    "lapa":             0.0003,
    "butantã":          0.0006,
    "centro":           0.0008,
    # RJ
    "ipanema":         -0.0012,
    "leblon":          -0.0015,
    "copacabana":      -0.0003,
    "botafogo":        -0.0002,
    "barra da tijuca": -0.0003,
    # GO
    "setor bueno":      0.0003,
    "setor marista":    0.0002,
}

DEFAULT_YIELD = 0.0042  # fallback geral


class InvestmentAnalysisAgent(BaseAgent):
    agent_id = "investment_analysis"
    fallback_value = []
    _output_field = "analysis.investment"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """
        Calcula ROI, payback e potencial para cada imóvel.

        Usa yields ajustados por tipo + bairro para estimar aluguel.
        Potencial de valorização calculado com dados reais de location_insights.
        """
        investments = []

        for prop in context.properties:
            # Determinar yield ajustado
            base_yield = RENTAL_YIELD_BY_TYPE.get(
                prop.property_type.value, DEFAULT_YIELD
            )
            bairro = (prop.neighborhood or "").lower().strip()
            adjustment = BAIRRO_YIELD_ADJUSTMENT.get(bairro, 0.0)
            effective_yield = max(0.001, base_yield + adjustment)

            aluguel_estimado = prop.price * effective_yield
            roi_mensal = (aluguel_estimado / prop.price) * 100 if prop.price > 0 else 0
            roi_anual = roi_mensal * 12
            payback = prop.price / (aluguel_estimado * 12) if aluguel_estimado > 0 else 999

            # Potencial de valorização baseado em location_insights reais
            potencial = self._calculate_potential(prop)

            investments.append(InvestmentResult(
                property_id=prop.id,
                aluguel_estimado=round(aluguel_estimado, 2),
                roi_mensal=round(roi_mensal, 4),
                roi_anual=round(roi_anual, 2),
                payback_anos=round(payback, 1),
                potencial_valorizacao=potencial,
            ))

            logger.debug(
                f"Investment [{prop.address}, {bairro}]: "
                f"yield={effective_yield:.4f} (base={base_yield:.4f} adj={adjustment:+.4f}), "
                f"aluguel=R$ {aluguel_estimado:,.0f}/mês, "
                f"ROI={roi_anual:.1f}%/ano, "
                f"payback={payback:.1f} anos, "
                f"potencial={potencial.value}"
            )

        return ContextPatch(
            agent_id=self.agent_id,
            field="analysis.investment",
            value=[inv.model_dump() for inv in investments],
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.properties) > 0 and len(context.analysis.valuation) > 0

    def _calculate_potential(self, prop) -> AppreciationPotential:
        """
        Calcula potencial de valorização baseado em dados REAIS de localização.

        Critérios:
        - ALTO: score >= 7.5, liquidez alta, tem metrô ou shopping
        - MÉDIO: score >= 5.5, liquidez >= média
        - BAIXO: restante
        """
        if not prop.location_insights:
            return AppreciationPotential.MEDIO

        score = prop.location_insights.bairro_score
        liquidez = prop.location_insights.liquidez_estimada
        infra = prop.location_insights.infraestrutura_proxima

        # Verificar presença de infraestrutura-chave
        has_transport = any(
            i in infra for i in ["metrô", "estação"]
        )
        has_commerce = any(
            i in infra for i in ["shopping", "supermercado"]
        )

        if score >= 7.5 and liquidez == "alta":
            return AppreciationPotential.ALTO
        elif score >= 7.0 and (has_transport or has_commerce):
            return AppreciationPotential.ALTO
        elif score >= 5.5 and liquidez in ("media", "alta"):
            return AppreciationPotential.MEDIO
        return AppreciationPotential.BAIXO
