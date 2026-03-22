"""
IMOBILAY — OpportunityDetectionAgent

Detecta oportunidades de investimento:
  - desvio_percentual < -8% (preço abaixo do justo)
  - liquidez >= "media"
  - location_score >= 6.5
Score composto: 0.4*desvio + 0.3*liquidez + 0.3*location
"""

from __future__ import annotations

from models.context import ContextPatch, ContextStore
from models.property import Opportunity
from layer_2_orchestrator.agents.base_agent import BaseAgent


LIQUIDEZ_SCORES = {"baixa": 3.0, "media": 6.0, "alta": 9.0}


class OpportunityDetectionAgent(BaseAgent):
    agent_id = "opportunity_detection"
    fallback_value = []
    _output_field = "analysis.opportunities"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """Detecta oportunidades entre os imóveis analisados."""
        opportunities = []

        # Mapear valuations por property_id
        valuation_map = {v.property_id: v for v in context.analysis.valuation}

        for prop in context.properties:
            val = valuation_map.get(prop.id)
            if not val:
                continue

            desvio = val.desvio_percentual
            liquidez = "media"
            location_score = 6.0

            if prop.location_insights:
                liquidez = prop.location_insights.liquidez_estimada
                location_score = prop.location_insights.bairro_score

            # Critérios de oportunidade
            is_opportunity = (
                desvio < -8
                and liquidez in ("media", "alta")
                and location_score >= 6.5
            )

            if is_opportunity:
                liq_score = LIQUIDEZ_SCORES.get(liquidez, 5.0)
                # Score composto: maior desvio negativo = melhor oportunidade
                score = (
                    0.4 * min(abs(desvio) / 20 * 10, 10)   # normalizar desvio para 0-10
                    + 0.3 * liq_score
                    + 0.3 * location_score
                )

                opportunities.append(Opportunity(
                    property_id=prop.id,
                    score_composto=round(min(score, 10), 2),
                    desvio_percentual=desvio,
                    liquidez=liquidez,
                    location_score=location_score,
                    motivo=(
                        f"Preço {abs(desvio):.0f}% abaixo do justo, "
                        f"liquidez {liquidez}, "
                        f"score bairro {location_score:.1f}/10"
                    ),
                ))

        # Ordernar por score composto (melhor primeiro)
        opportunities.sort(key=lambda o: o.score_composto, reverse=True)

        return ContextPatch(
            agent_id=self.agent_id,
            field="analysis.opportunities",
            value=[o.model_dump() for o in opportunities],
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.analysis.valuation) > 0
