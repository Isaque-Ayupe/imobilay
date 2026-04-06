"""
IMOBILAY — WebScraperAgent

Busca imóveis em múltiplas fontes (ZAP, VivaReal) usando suas APIs de busca.
Executa requests em paralelo com aiohttp.
Timeout por fonte: 5s.
Fallback: lista vazia com AgentError descritivo.
"""

from __future__ import annotations

import logging
from models.context import ContextPatch, ContextStore
from models.property import RawProperty, PropertySource
from layer_2_orchestrator.agents.base_agent import BaseAgent
from execution.scraper_utils import (
    parse_filters,
    build_zap_search_url,
    build_vivareal_search_url,
    fetch_url,
    BROWSER_HEADERS,
    VIVAREAL_HEADERS,
    SearchFilters,
)

logger = logging.getLogger(__name__)


class WebScraperAgent(BaseAgent):
    agent_id = "web_scraper"
    fallback_value = []
    _output_field = "raw_properties"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """
        Busca imóveis reais nos portais imobiliários.

        1. Extrai filtros da mensagem do usuário
        2. Constrói URLs de busca para ZAP e VivaReal
        3. Faz requests paralelos
        4. Parseia resultados em RawProperty
        """
        message = context.input.message if context.input else ""
        filters = parse_filters(message)

        logger.info(
            f"WebScraper: buscando em {filters.city}"
            f"{f', {filters.neighborhood}' if filters.neighborhood else ''}"
            f"{f', até R${filters.price_max:,.0f}' if filters.price_max else ''}"
        )

        # Buscar em paralelo nas fontes
        all_properties: list[RawProperty] = []

        # ZAP Imóveis
        zap_props = await self._fetch_zap(filters)
        all_properties.extend(zap_props)

        # VivaReal
        vr_props = await self._fetch_vivareal(filters)
        all_properties.extend(vr_props)

        logger.info(
            f"WebScraper: encontrados {len(all_properties)} imóveis "
            f"(ZAP={len(zap_props)}, VivaReal={len(vr_props)})"
        )

        return ContextPatch(
            agent_id=self.agent_id,
            field="raw_properties",
            value=[p.model_dump() for p in all_properties],
        )

    def validate_input(self, context: ContextStore) -> bool:
        return context.input is not None and bool(context.input.message)

    async def _fetch_zap(self, filters: SearchFilters) -> list[RawProperty]:
        """Busca imóveis na API do ZAP Imóveis."""
        try:
            url = build_zap_search_url(filters)
            data = await fetch_url(url, BROWSER_HEADERS)

            if not data:
                logger.warning("ZAP: sem resposta ou erro na API")
                return []

            return self._parse_zap_response(data)
        except Exception as e:
            logger.warning(f"ZAP: erro ao buscar: {e}")
            return []

    async def _fetch_vivareal(self, filters: SearchFilters) -> list[RawProperty]:
        """Busca imóveis na API do VivaReal."""
        try:
            url = build_vivareal_search_url(filters)
            data = await fetch_url(url, VIVAREAL_HEADERS)

            if not data:
                logger.warning("VivaReal: sem resposta ou erro na API")
                return []

            return self._parse_vivareal_response(data)
        except Exception as e:
            logger.warning(f"VivaReal: erro ao buscar: {e}")
            return []

    def _parse_zap_response(self, data: dict) -> list[RawProperty]:
        """Parseia resposta JSON da API do ZAP para RawProperty."""
        properties = []

        try:
            listings = (
                data.get("search", {})
                .get("result", {})
                .get("listings", [])
            )
        except (AttributeError, TypeError):
            return []

        for item in listings:
            try:
                listing = item.get("listing", {})
                link = item.get("link", {})

                # Extrair dados do listing
                address_data = listing.get("address", {})
                pricing = listing.get("pricingInfos", [{}])
                price_info = pricing[0] if pricing else {}

                # Preço
                raw_price = price_info.get("price", "0")
                if not raw_price or raw_price == "0":
                    continue  # Pular imóveis sem preço

                # Área
                usable = listing.get("usableAreas", [])
                total = listing.get("totalAreas", [])
                raw_area = ""
                if usable:
                    raw_area = f"{usable[0]}m²"
                elif total:
                    raw_area = f"{total[0]}m²"

                # Quartos
                bedrooms = listing.get("bedrooms", [0])
                raw_rooms = f"{bedrooms[0]} quarto{'s' if bedrooms[0] != 1 else ''}" if bedrooms else ""

                # URL do anúncio
                url_path = link.get("href", "")
                full_url = f"https://www.zapimoveis.com.br{url_path}" if url_path else None

                # Endereço
                street = address_data.get("street", "")
                street_number = address_data.get("streetNumber", "")
                raw_address = f"{street}, {street_number}".strip(", ") if street else ""

                props = RawProperty(
                    raw_title=listing.get("title", "Imóvel ZAP"),
                    raw_price=f"R$ {raw_price}",
                    raw_area=raw_area or None,
                    raw_rooms=raw_rooms or None,
                    raw_address=raw_address or None,
                    raw_neighborhood=address_data.get("neighborhood", None),
                    raw_city=address_data.get("city", None),
                    url=full_url,
                    source=PropertySource.ZAP,
                    raw_data=listing,
                )
                properties.append(props)

            except Exception as e:
                logger.debug(f"ZAP: erro parseando listing: {e}")
                continue

        return properties

    def _parse_vivareal_response(self, data: dict) -> list[RawProperty]:
        """Parseia resposta JSON da API do VivaReal para RawProperty."""
        properties = []

        try:
            listings = (
                data.get("search", {})
                .get("result", {})
                .get("listings", [])
            )
        except (AttributeError, TypeError):
            return []

        for item in listings:
            try:
                listing = item.get("listing", {})
                link = item.get("link", {})

                address_data = listing.get("address", {})
                pricing = listing.get("pricingInfos", [{}])
                price_info = pricing[0] if pricing else {}

                raw_price = price_info.get("price", "0")
                if not raw_price or raw_price == "0":
                    continue

                usable = listing.get("usableAreas", [])
                total = listing.get("totalAreas", [])
                raw_area = ""
                if usable:
                    raw_area = f"{usable[0]}m²"
                elif total:
                    raw_area = f"{total[0]}m²"

                bedrooms = listing.get("bedrooms", [0])
                raw_rooms = f"{bedrooms[0]} quarto{'s' if bedrooms[0] != 1 else ''}" if bedrooms else ""

                url_path = link.get("href", "")
                full_url = f"https://www.vivareal.com.br{url_path}" if url_path else None

                street = address_data.get("street", "")
                street_number = address_data.get("streetNumber", "")
                raw_address = f"{street}, {street_number}".strip(", ") if street else ""

                props = RawProperty(
                    raw_title=listing.get("title", "Imóvel VivaReal"),
                    raw_price=f"R$ {raw_price}",
                    raw_area=raw_area or None,
                    raw_rooms=raw_rooms or None,
                    raw_address=raw_address or None,
                    raw_neighborhood=address_data.get("neighborhood", None),
                    raw_city=address_data.get("city", None),
                    url=full_url,
                    source=PropertySource.VIVAREAL,
                    raw_data=listing,
                )
                properties.append(props)

            except Exception as e:
                logger.debug(f"VivaReal: erro parseando listing: {e}")
                continue

        return properties
