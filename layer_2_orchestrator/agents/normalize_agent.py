"""
IMOBILAY — NormalizeAgent

Padroniza dados brutos do WebScraperAgent:
  - Converter preço/área de string para float
  - Extrair quartos de texto
  - Calcular preço/m²
  - Remover duplicatas por (endereço + preço + área)
"""

from __future__ import annotations

import re
from models.context import ContextPatch, ContextStore
from models.property import Property, PropertyType, PropertySource
from layer_2_orchestrator.agents.base_agent import BaseAgent


class NormalizeAgent(BaseAgent):
    agent_id = "normalize"
    fallback_value = []   # manter raw se falhar
    _output_field = "properties"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """Normaliza properties raw → Property com campos tipados."""
        normalized = []
        seen = set()

        for raw in context.properties:
            try:
                prop = self._normalize_one(raw)
                # Deduplicação por (endereço + preço + área)
                key = (prop.address.lower(), prop.price, prop.area)
                if key not in seen:
                    seen.add(key)
                    normalized.append(prop)
            except Exception:
                continue  # pular imóveis com dados ruins

        return ContextPatch(
            agent_id=self.agent_id,
            field="properties",
            value=[p.model_dump() for p in normalized],
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.properties) > 0

    def _normalize_one(self, raw) -> Property:
        """Converte um registro raw/dict em Property normalizado."""
        # Suportar tanto Property quanto dict (do apply_patch)
        if isinstance(raw, dict):
            data = raw
        else:
            data = raw.model_dump() if hasattr(raw, "model_dump") else dict(raw)

        address = data.get("address") or data.get("raw_address", "")
        neighborhood = data.get("neighborhood") or data.get("raw_neighborhood", "")
        city = data.get("city") or data.get("raw_city", "São Paulo")

        price = self._parse_price(data.get("price") or data.get("raw_price", "0"))
        area = self._parse_area(data.get("area") or data.get("raw_area", "0"))
        rooms = self._parse_rooms(data.get("rooms") or data.get("raw_rooms", "0"))

        price_per_sqm = price / area if area > 0 else 0
        prop_type = self._detect_type(data.get("raw_title", "") or data.get("property_type", ""))

        return Property(
            id=data.get("id", ""),
            address=address,
            neighborhood=neighborhood,
            city=city,
            rooms=rooms,
            area=area,
            parking=data.get("parking", 0),
            floor=data.get("floor"),
            price=price,
            price_per_sqm=price_per_sqm,
            property_type=prop_type,
            source=data.get("source", PropertySource.OTHER),
            url=data.get("url"),
        )

    def _parse_price(self, raw: str | float | int) -> float:
        if isinstance(raw, (int, float)):
            return float(raw)
        # "R$ 749.000" → 749000.0
        cleaned = re.sub(r"[^\d,.]", "", str(raw))
        cleaned = cleaned.replace(".", "").replace(",", ".")
        return float(cleaned) if cleaned else 0.0

    def _parse_area(self, raw: str | float | int) -> float:
        if isinstance(raw, (int, float)):
            return float(raw)
        # "68m²" → 68.0
        match = re.search(r"(\d+[,.]?\d*)", str(raw))
        return float(match.group(1).replace(",", ".")) if match else 1.0

    def _parse_rooms(self, raw: str | int) -> int:
        if isinstance(raw, int):
            return raw
        match = re.search(r"(\d+)", str(raw))
        return int(match.group(1)) if match else 0

    def _detect_type(self, text: str) -> PropertyType:
        text_lower = str(text).lower()
        if "studio" in text_lower:
            return PropertyType.STUDIO
        if "cobertura" in text_lower:
            return PropertyType.COBERTURA
        if "kitnet" in text_lower:
            return PropertyType.KITNET
        if "casa" in text_lower:
            return PropertyType.CASA
        return PropertyType.APARTAMENTO
