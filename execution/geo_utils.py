"""
IMOBILAY — Geo Utilities

Clients para Nominatim (geocodificação) e Overpass API (POIs).
Usado pelo LocationInsightsAgent para enriquecimento geográfico real.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


# ── Constantes ───────────────────────────────────────────────

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
OVERPASS_BASE = "https://overpass-api.de/api/interpreter"
GEO_TIMEOUT_S = 8

# Headers obrigatórios para Nominatim (política de uso justo)
NOMINATIM_HEADERS = {
    "User-Agent": "IMOBILAY/1.0 (contato@imobilay.com.br)",
    "Accept": "application/json",
}

# Tipos de POI e seus pesos para o cálculo de score
POI_WEIGHTS = {
    "metrô":       {"tag": "station", "query": "subway", "weight": 2.0},
    "hospital":    {"tag": "hospital", "query": "hospital", "weight": 1.5},
    "shopping":    {"tag": "mall", "query": "mall", "weight": 1.0},
    "parque":      {"tag": "park", "query": "park", "weight": 1.2},
    "escola":      {"tag": "school", "query": "school", "weight": 0.8},
    "universidade": {"tag": "university", "query": "university", "weight": 0.7},
    "supermercado": {"tag": "supermarket", "query": "supermarket", "weight": 0.6},
    "restaurantes": {"tag": "restaurant", "query": "restaurant", "weight": 0.3},
    "delegacia":   {"tag": "police", "query": "police", "weight": 1.0},
    "farmácia":    {"tag": "pharmacy", "query": "pharmacy", "weight": 0.4},
}

# Score base por bairro (estimado pela presença relativa de infraestrutura)
SEGURANCA_BOOST = {
    "delegacia": 0.5,
    "hospital": 0.3,
}


@dataclass
class GeoLocation:
    """Coordenadas e dados de localização."""
    lat: float
    lon: float
    display_name: str = ""
    bairro: str = ""
    city: str = ""
    state: str = ""


@dataclass
class NearbyInfra:
    """Infraestrutura próxima encontrada."""
    category: str              # ex: "metrô", "hospital"
    name: str                  # nome do POI
    distance_m: float = 0.0    # distância em metros (aproximada)


@dataclass
class LocationData:
    """Dados completos de localização para um endereço."""
    location: GeoLocation | None = None
    nearby: list[NearbyInfra] = field(default_factory=list)
    bairro_score: float = 6.0
    seguranca_index: float = 5.0
    liquidez_estimada: str = "media"
    infraestrutura_proxima: list[str] = field(default_factory=list)


async def geocode(address: str, city: str = "São Paulo") -> GeoLocation | None:
    """
    Geocodifica um endereço usando Nominatim.

    Args:
        address: endereço completo ou parcial
        city: cidade para refinar a busca

    Returns:
        GeoLocation com lat/lon ou None se não encontrado
    """
    query = f"{address}, {city}, Brasil"
    url = f"{NOMINATIM_BASE}/search"
    params = {
        "q": query,
        "format": "json",
        "addressdetails": "1",
        "limit": "1",
        "countrycodes": "br",
    }

    try:
        timeout = aiohttp.ClientTimeout(total=GEO_TIMEOUT_S)
        async with aiohttp.ClientSession(
            timeout=timeout, headers=NOMINATIM_HEADERS
        ) as session:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    logger.warning(f"Nominatim HTTP {resp.status} para '{query}'")
                    return None
                data = await resp.json(content_type=None)

        if not data:
            logger.debug(f"Nominatim: sem resultados para '{query}'")
            return None

        result = data[0]
        addr = result.get("address", {})

        return GeoLocation(
            lat=float(result["lat"]),
            lon=float(result["lon"]),
            display_name=result.get("display_name", ""),
            bairro=addr.get("suburb") or addr.get("neighbourhood") or "",
            city=addr.get("city") or addr.get("town") or city,
            state=addr.get("state", ""),
        )
    except asyncio.TimeoutError:
        logger.warning(f"Timeout geocodificando '{query}'")
        return None
    except Exception as e:
        logger.warning(f"Erro geocodificando '{query}': {e}")
        return None


async def find_nearby_pois(
    lat: float, lon: float, radius_m: int = 1500
) -> list[NearbyInfra]:
    """
    Busca POIs próximos usando a Overpass API.

    Args:
        lat, lon: coordenadas centrais
        radius_m: raio de busca em metros (default 1.5km)

    Returns:
        Lista de NearbyInfra encontrados
    """
    # Construir query Overpass para múltiplos tipos de POI
    poi_filters = [
        'node["railway"="station"](around:{radius},{lat},{lon});',
        'node["railway"="subway_entrance"](around:{radius},{lat},{lon});',
        'node["amenity"="hospital"](around:{radius},{lat},{lon});',
        'way["amenity"="hospital"](around:{radius},{lat},{lon});',
        'node["shop"="mall"](around:{radius},{lat},{lon});',
        'way["shop"="mall"](around:{radius},{lat},{lon});',
        'node["leisure"="park"](around:{radius},{lat},{lon});',
        'way["leisure"="park"](around:{radius},{lat},{lon});',
        'node["amenity"="school"](around:{radius},{lat},{lon});',
        'node["amenity"="university"](around:{radius},{lat},{lon});',
        'node["shop"="supermarket"](around:{radius},{lat},{lon});',
        'node["amenity"="police"](around:{radius},{lat},{lon});',
        'node["amenity"="pharmacy"](around:{radius},{lat},{lon});',
    ]

    overpass_query = "[out:json][timeout:10];\n(\n"
    for f in poi_filters:
        overpass_query += "  " + f.format(radius=radius_m, lat=lat, lon=lon) + "\n"
    overpass_query += ");\nout center body;\n"

    try:
        timeout = aiohttp.ClientTimeout(total=GEO_TIMEOUT_S)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                OVERPASS_BASE,
                data={"data": overpass_query},
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"Overpass HTTP {resp.status}")
                    return []
                data = await resp.json(content_type=None)

        elements = data.get("elements", [])
        nearby = []

        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name", "")

            # Classificar o POI
            category = _classify_poi(tags)
            if category and name:
                el_lat = el.get("lat") or el.get("center", {}).get("lat", lat)
                el_lon = el.get("lon") or el.get("center", {}).get("lon", lon)
                dist = _haversine_approx(lat, lon, el_lat, el_lon)

                nearby.append(NearbyInfra(
                    category=category,
                    name=name,
                    distance_m=dist,
                ))

        # Deduplicar por nome
        seen = set()
        unique = []
        for n in nearby:
            key = (n.category, n.name)
            if key not in seen:
                seen.add(key)
                unique.append(n)

        return sorted(unique, key=lambda x: x.distance_m)

    except asyncio.TimeoutError:
        logger.warning("Timeout na Overpass API")
        return []
    except Exception as e:
        logger.warning(f"Erro na Overpass API: {e}")
        return []


def calculate_location_scores(
    nearby: list[NearbyInfra],
) -> tuple[float, float, list[str]]:
    """
    Calcula scores de localização baseados nos POIs encontrados.

    Returns:
        (bairro_score, seguranca_index, infraestrutura_proxima)
    """
    if not nearby:
        return 6.0, 5.0, ["comércio"]

    # Contar categorias encontradas
    categories_found: dict[str, int] = {}
    for n in nearby:
        categories_found[n.category] = categories_found.get(n.category, 0) + 1

    # Calcular bairro_score (0-10) com pesos
    total_weight = 0.0
    max_possible = sum(info["weight"] for info in POI_WEIGHTS.values())

    for cat, count in categories_found.items():
        if cat in POI_WEIGHTS:
            # Peso base + bônus por quantidade (diminishing returns)
            weight = POI_WEIGHTS[cat]["weight"]
            quantity_bonus = min(count * 0.2, 1.0)  # max +1.0 por quantidade
            total_weight += weight + quantity_bonus

    # Normalizar para 0-10
    bairro_score = min(10.0, (total_weight / max_possible) * 10)
    bairro_score = max(3.0, bairro_score)  # mínimo 3.0 (se encontramos algo)

    # Calcular segurança (baseado em delegacia + hospital + iluminação geral)
    seg_score = 5.0  # base
    if "delegacia" in categories_found:
        seg_score += 1.5
    if "hospital" in categories_found:
        seg_score += 1.0
    if "metrô" in categories_found:
        seg_score += 0.5  # regiões com metrô tendem a ser mais movimentadas
    seg_score = min(10.0, seg_score)

    # Lista de infraestrutura para display
    infra_list = list(categories_found.keys())

    return round(bairro_score, 1), round(seg_score, 1), infra_list


def estimate_liquidity(
    bairro_score: float, categories_found: list[str]
) -> str:
    """
    Estima liquidez do bairro.

    Alta: score >= 7.5 e tem metrô
    Média: score >= 5.0
    Baixa: restante
    """
    has_metro = "metrô" in categories_found
    has_shopping = "shopping" in categories_found

    if bairro_score >= 7.5 and (has_metro or has_shopping):
        return "alta"
    elif bairro_score >= 5.0:
        return "media"
    return "baixa"


async def enrich_location(
    address: str, neighborhood: str, city: str
) -> LocationData:
    """
    Pipeline completo: geocodifica → busca POIs → calcula scores.

    Args:
        address: endereço do imóvel
        neighborhood: bairro
        city: cidade

    Returns:
        LocationData com todos os scores calculados
    """
    result = LocationData()

    # 1. Geocodificar
    search_address = f"{address}, {neighborhood}" if neighborhood else address
    location = await geocode(search_address, city)

    if not location:
        # Tentar só com bairro
        location = await geocode(neighborhood, city)

    if not location:
        logger.info(f"Não foi possível geocodificar: {search_address}, {city}")
        return result

    result.location = location

    # 2. Buscar POIs
    nearby = await find_nearby_pois(location.lat, location.lon)
    result.nearby = nearby

    # 3. Calcular scores
    bairro_score, seg_index, infra = calculate_location_scores(nearby)
    result.bairro_score = bairro_score
    result.seguranca_index = seg_index
    result.infraestrutura_proxima = infra
    result.liquidez_estimada = estimate_liquidity(bairro_score, infra)

    return result


def _classify_poi(tags: dict[str, str]) -> str | None:
    """Classifica um elemento OSM em uma categoria conhecida."""
    railway = tags.get("railway", "")
    if railway in ("station", "subway_entrance", "halt"):
        return "metrô"

    amenity = tags.get("amenity", "")
    if amenity == "hospital":
        return "hospital"
    if amenity == "school":
        return "escola"
    if amenity == "university":
        return "universidade"
    if amenity == "police":
        return "delegacia"
    if amenity == "pharmacy":
        return "farmácia"

    shop = tags.get("shop", "")
    if shop == "mall":
        return "shopping"
    if shop == "supermarket":
        return "supermercado"

    leisure = tags.get("leisure", "")
    if leisure == "park":
        return "parque"

    return None


def _haversine_approx(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Cálculo aproximado de distância em metros (fórmula simplificada para curtas distâncias)."""
    import math
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    avg_lat = math.radians((lat1 + lat2) / 2)

    # Aproximação para curtas distâncias
    x = d_lon * math.cos(avg_lat)
    y = d_lat
    return math.sqrt(x * x + y * y) * 6371000  # raio da Terra em metros
