"""
IMOBILAY — WebScraperAgent

Busca imóveis em múltiplas fontes (ZAP, VivaReal, OLX).
Executa requests em paralelo com aiohttp.
Timeout por fonte: 5s.
Fallback: lista vazia com AgentError descritivo.
"""

from __future__ import annotations

import re
from models.context import ContextPatch, ContextStore
from models.property import RawProperty, PropertySource
from layer_2_orchestrator.agents.base_agent import BaseAgent


class WebScraperAgent(BaseAgent):
    agent_id = "web_scraper"
    fallback_value = []
    _output_field = "properties"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """
        Busca imóveis baseado na mensagem do usuário.

        TODO: Implementar scraping real com aiohttp quando as APIs
        estiverem configuradas. Por enquanto, retorna dados simulados
        para validar o pipeline.
        """
        message = context.input.message if context.input else ""
        properties = self._generate_mock_properties(message)

        return ContextPatch(
            agent_id=self.agent_id,
            field="properties",
            value=[p.model_dump() for p in properties],
        )

    def validate_input(self, context: ContextStore) -> bool:
        return context.input is not None and bool(context.input.message)

    def _generate_mock_properties(self, message: str) -> list[RawProperty]:
        """Gera dados mock para validação do pipeline."""
        # Extrair filtros básicos da mensagem
        city = "São Paulo"
        neighborhood = "Pinheiros"

        if "goiânia" in message.lower() or "goiania" in message.lower():
            city = "Goiânia"
            neighborhood = "Setor Bueno"
        elif "brooklin" in message.lower():
            neighborhood = "Brooklin"
        elif "vila madalena" in message.lower():
            neighborhood = "Vila Madalena"

        # Dados mock realistas
        mock_data = [
            RawProperty(
                raw_title=f"Apartamento 2 quartos - {neighborhood}",
                raw_price="R$ 749.000",
                raw_area="68m²",
                raw_rooms="2 quartos",
                raw_address=f"Rua dos Pinheiros, 1240",
                raw_neighborhood=neighborhood,
                raw_city=city,
                url="https://example.com/imovel/1",
                source=PropertySource.ZAP,
            ),
            RawProperty(
                raw_title=f"Studio moderno - {neighborhood}",
                raw_price="R$ 420.000",
                raw_area="35m²",
                raw_rooms="1 quarto",
                raw_address=f"Alameda Lorena, 890",
                raw_neighborhood=neighborhood,
                raw_city=city,
                url="https://example.com/imovel/2",
                source=PropertySource.VIVAREAL,
            ),
            RawProperty(
                raw_title=f"Cobertura ampla - {neighborhood}",
                raw_price="R$ 1.250.000",
                raw_area="120m²",
                raw_rooms="3 quartos",
                raw_address=f"Rua Oscar Freire, 500",
                raw_neighborhood=neighborhood,
                raw_city=city,
                url="https://example.com/imovel/3",
                source=PropertySource.OLX,
            ),
        ]
        return mock_data
