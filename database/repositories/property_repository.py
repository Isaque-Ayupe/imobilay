"""
IMOBILAY — Property Repository

Busca de imóveis no Supabase (tabela properties_cache).
Usado pelo WebScraperAgent como fonte primária de dados reais.
"""

from __future__ import annotations

import logging
from typing import Any

from supabase._async.client import AsyncClient

logger = logging.getLogger(__name__)


class PropertyRepository:
    """Repositório para busca de imóveis na tabela properties_cache."""

    def __init__(self, client: AsyncClient):
        self._client = client

    async def search(
        self,
        city: str | None = None,
        neighborhood: str | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        rooms_min: int | None = None,
        property_type: str | None = None,
        limit: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Busca imóveis com filtros.

        Args:
            city: filtrar por cidade
            neighborhood: filtrar por bairro
            price_min: preço mínimo
            price_max: preço máximo
            rooms_min: mínimo de quartos
            property_type: tipo de imóvel
            limit: máximo de resultados

        Returns:
            Lista de dicts com dados dos imóveis
        """
        try:
            query = (
                self._client.table("properties_cache")
                .select("*")
                .eq("active", True)
            )

            if city:
                query = query.ilike("city", f"%{city}%")

            if neighborhood:
                query = query.ilike("neighborhood", f"%{neighborhood}%")

            if price_min is not None:
                query = query.gte("price", price_min)

            if price_max is not None:
                query = query.lte("price", price_max)

            if rooms_min is not None:
                query = query.gte("rooms", rooms_min)

            if property_type:
                query = query.eq("property_type", property_type)

            query = query.order("price", desc=False).limit(limit)

            result = await query.execute()
            return result.data or []

        except Exception as e:
            logger.error(f"Erro buscando imóveis no Supabase: {e}")
            return []

    async def count_by_neighborhood(
        self, city: str, neighborhood: str
    ) -> int:
        """Conta imóveis em um bairro (para estimar liquidez)."""
        try:
            result = await (
                self._client.table("properties_cache")
                .select("id", count="exact")
                .eq("active", True)
                .ilike("city", f"%{city}%")
                .ilike("neighborhood", f"%{neighborhood}%")
                .execute()
            )
            return result.count or 0
        except Exception as e:
            logger.debug(f"Erro contando imóveis: {e}")
            return 0

    async def get_avg_price_m2(
        self, city: str, neighborhood: str
    ) -> float | None:
        """
        Calcula preço médio por m² num bairro.
        Retorna None se não houver dados suficientes.
        """
        try:
            result = await (
                self._client.table("properties_cache")
                .select("price, area_m2")
                .eq("active", True)
                .ilike("city", f"%{city}%")
                .ilike("neighborhood", f"%{neighborhood}%")
                .gt("area_m2", 0)
                .gt("price", 0)
                .execute()
            )

            data = result.data or []
            if len(data) < 2:
                return None

            prices_m2 = [
                float(d["price"]) / float(d["area_m2"])
                for d in data
                if float(d["area_m2"]) > 0
            ]

            if not prices_m2:
                return None

            # Retornar mediana
            prices_m2.sort()
            n = len(prices_m2)
            if n % 2 == 0:
                return (prices_m2[n // 2 - 1] + prices_m2[n // 2]) / 2
            return prices_m2[n // 2]

        except Exception as e:
            logger.debug(f"Erro calculando preço/m²: {e}")
            return None
