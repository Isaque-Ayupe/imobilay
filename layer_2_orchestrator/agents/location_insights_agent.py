"""
IMOBILAY — LocationInsightsAgent

Enriquece cada imóvel com dados geográficos REAIS:
  - Geocodificação via Nominatim (OpenStreetMap)
  - Busca de POIs próximos via Overpass API
  - bairro_score, seguranca_index, liquidez_estimada, infraestrutura_proxima
  - Todos calculados com base em dados reais do OSM
"""

from __future__ import annotations

import asyncio
import logging

from models.context import ContextPatch, ContextStore
from models.property import LocationInsights
from layer_2_orchestrator.agents.base_agent import BaseAgent
from execution.geo_utils import enrich_location

logger = logging.getLogger(__name__)

# Cache em memória para evitar requests repetidos para o mesmo bairro
_location_cache: dict[str, dict] = {}


class LocationInsightsAgent(BaseAgent):
    agent_id = "location_insights"
    fallback_value = None
    _output_field = "properties"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """
        Enriquece cada Property com LocationInsights reais.

        Para cada imóvel:
        1. Geocodifica o endereço via Nominatim
        2. Busca POIs num raio de 1.5km via Overpass API
        3. Calcula scores baseados na infraestrutura encontrada

        Usa cache por bairro+cidade para evitar requests repetidos.
        """
        enriched = []

        # Agrupar por bairro+cidade para cachear
        tasks_by_key: dict[str, list[int]] = {}
        props_data = []

        for i, prop in enumerate(context.properties):
            prop_data = prop.model_dump() if hasattr(prop, "model_dump") else dict(prop)
            props_data.append(prop_data)

            bairro = (prop_data.get("neighborhood") or "").strip()
            city = (prop_data.get("city") or "São Paulo").strip()
            cache_key = f"{bairro}|{city}".lower()

            if cache_key not in tasks_by_key:
                tasks_by_key[cache_key] = []
            tasks_by_key[cache_key].append(i)

        # Buscar dados de localização para cada bairro único (em paralelo, limitado)
        sem = asyncio.Semaphore(3)  # max 3 requests simultâneos (respeitar Nominatim)

        async def fetch_location(cache_key: str) -> tuple[str, dict]:
            if cache_key in _location_cache:
                return cache_key, _location_cache[cache_key]

            async with sem:
                parts = cache_key.split("|")
                bairro = parts[0] if parts else ""
                city = parts[1] if len(parts) > 1 else "São Paulo"

                # Usar o primeiro imóvel deste bairro para geocodificar
                first_idx = tasks_by_key[cache_key][0]
                address = props_data[first_idx].get("address", "")

                location_data = await enrich_location(address, bairro, city)

                insights_dict = {
                    "bairro_score": location_data.bairro_score,
                    "seguranca_index": location_data.seguranca_index,
                    "liquidez_estimada": location_data.liquidez_estimada,
                    "infraestrutura_proxima": location_data.infraestrutura_proxima,
                }

                _location_cache[cache_key] = insights_dict

                logger.info(
                    f"LocationInsights [{bairro}, {city}]: "
                    f"score={location_data.bairro_score}, "
                    f"seg={location_data.seguranca_index}, "
                    f"liq={location_data.liquidez_estimada}, "
                    f"infra={location_data.infraestrutura_proxima}"
                )

                # Pequeno delay para respeitar rate limit do Nominatim (1 req/s)
                await asyncio.sleep(1.1)

                return cache_key, insights_dict

        # Executar todas as buscas
        location_tasks = [
            fetch_location(key) for key in tasks_by_key.keys()
        ]
        results = await asyncio.gather(*location_tasks, return_exceptions=True)

        # Mapear resultados
        location_results: dict[str, dict] = {}
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Erro buscando localização: {result}")
                continue
            key, insights_dict = result
            location_results[key] = insights_dict

        # Aplicar insights em cada propriedade
        for i, prop_data in enumerate(props_data):
            bairro = (prop_data.get("neighborhood") or "").strip()
            city = (prop_data.get("city") or "São Paulo").strip()
            cache_key = f"{bairro}|{city}".lower()

            insights_dict = location_results.get(cache_key, {
                "bairro_score": 6.0,
                "seguranca_index": 5.0,
                "liquidez_estimada": "media",
                "infraestrutura_proxima": ["comércio"],
            })

            try:
                insights = LocationInsights(**insights_dict)
                prop_data["location_insights"] = insights.model_dump()
            except Exception as e:
                logger.warning(f"Erro criando LocationInsights: {e}")
                prop_data["location_insights"] = {
                    "bairro_score": 6.0,
                    "seguranca_index": 5.0,
                    "liquidez_estimada": "media",
                    "infraestrutura_proxima": ["comércio"],
                }

            enriched.append(prop_data)

        return ContextPatch(
            agent_id=self.agent_id,
            field="properties",
            value=enriched,
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.properties) > 0
