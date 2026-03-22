"""
IMOBILAY — LocationInsightsAgent

Enriquece cada imóvel com dados geográficos:
  - bairro_score, seguranca_index, liquidez_estimada, infraestrutura_proxima

TODO: integrar com Nominatim/OSM e dados IBGE reais.
Por enquanto usa dados mock baseados no bairro.
"""

from __future__ import annotations

from models.context import ContextPatch, ContextStore
from models.property import LocationInsights
from layer_2_orchestrator.agents.base_agent import BaseAgent


# Dados mock por bairro (substituir por API real depois)
BAIRRO_DATA = {
    "pinheiros":       {"score": 8.5, "seg": 7.0, "liq": "alta",  "infra": ["metrô", "parque", "hospital", "shopping"]},
    "vila madalena":   {"score": 8.0, "seg": 6.5, "liq": "alta",  "infra": ["metrô", "bares", "parque"]},
    "brooklin":        {"score": 8.8, "seg": 8.0, "liq": "alta",  "infra": ["metrô", "shopping", "parque", "escola"]},
    "moema":           {"score": 8.5, "seg": 7.5, "liq": "alta",  "infra": ["metrô", "parque", "shopping"]},
    "itaim bibi":      {"score": 9.0, "seg": 7.0, "liq": "alta",  "infra": ["metrô", "restaurantes", "shopping"]},
    "setor bueno":     {"score": 7.5, "seg": 7.0, "liq": "media", "infra": ["shopping", "parque", "escola"]},
    "setor marista":   {"score": 8.0, "seg": 7.5, "liq": "alta",  "infra": ["shopping", "hospital", "restaurantes"]},
    "centro":          {"score": 5.0, "seg": 4.0, "liq": "media", "infra": ["metrô", "comércio"]},
}

DEFAULT_DATA = {"score": 6.0, "seg": 5.0, "liq": "media", "infra": ["comércio"]}


class LocationInsightsAgent(BaseAgent):
    agent_id = "location_insights"
    fallback_value = None  # null por imóvel — mantém sem enriquecimento
    _output_field = "properties"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """Enriquece cada Property com LocationInsights."""
        enriched = []
        for prop in context.properties:
            prop_data = prop.model_dump() if hasattr(prop, "model_dump") else dict(prop)

            bairro = (prop_data.get("neighborhood") or "").lower().strip()
            data = BAIRRO_DATA.get(bairro, DEFAULT_DATA)

            insights = LocationInsights(
                bairro_score=data["score"],
                seguranca_index=data["seg"],
                liquidez_estimada=data["liq"],
                infraestrutura_proxima=data["infra"],
            )
            prop_data["location_insights"] = insights.model_dump()
            enriched.append(prop_data)

        return ContextPatch(
            agent_id=self.agent_id,
            field="properties",
            value=enriched,
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.properties) > 0
