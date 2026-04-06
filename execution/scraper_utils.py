"""
IMOBILAY — Scraper Utilities

Parser de filtros da mensagem do usuário e helpers para requests paralelos.
Usado pelo WebScraperAgent para extrair parâmetros de busca.
"""

from __future__ import annotations

import re
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


# ── Constantes ───────────────────────────────────────────────

SCRAPER_TIMEOUT_S = 5

# Mapeamento de bairros conhecidos por cidade
KNOWN_NEIGHBORHOODS: dict[str, list[str]] = {
    "são paulo": [
        "pinheiros", "vila madalena", "brooklin", "moema", "itaim bibi",
        "jardins", "vila olímpia", "perdizes", "lapa", "butantã",
        "morumbi", "campo belo", "ibirapuera", "consolação", "bela vista",
        "liberdade", "aclimação", "ipiranga", "tatuapé", "santana",
        "casa verde", "tucuruvi", "mandaqui", "centro", "república",
        "higienópolis", "pacaembu", "sumaré", "pompéia", "água branca",
        "barra funda", "santa cecília", "cambuci", "saúde", "jabaquara",
        "santo amaro", "granja julieta", "chácara klabin", "paraíso",
        "vila mariana", "sacomã", "penha", "vila carrão", "anália franco",
        "jardim são paulo", "tremembé", "vila guilherme", "brás",
        "berrini", "chácara santo antônio", "vila andrade",
    ],
    "goiânia": [
        "setor bueno", "setor marista", "setor oeste", "setor central",
        "jardim goiás", "setor pedro ludovico", "setor coimbra",
        "setor aeroporto", "setor sul", "setor universitário",
        "parque amazônia", "alphaville flamboyant",
    ],
    "rio de janeiro": [
        "copacabana", "ipanema", "leblon", "botafogo", "flamengo",
        "laranjeiras", "tijuca", "barra da tijuca", "recreio",
        "centro", "lapa", "glória", "catete", "humaitá", "gávea",
        "jardim botânico", "urca", "são conrado", "méier",
    ],
}

# Palavras-chave de tipo de imóvel
PROPERTY_TYPE_KEYWORDS = {
    "apartamento": ["apartamento", "apto", "ap"],
    "studio": ["studio", "estúdio", "flat"],
    "cobertura": ["cobertura"],
    "kitnet": ["kitnet", "kit", "quitinete"],
    "casa": ["casa", "sobrado"],
    "terreno": ["terreno", "lote"],
    "comercial": ["comercial", "sala", "loja", "escritório"],
}


@dataclass
class SearchFilters:
    """Filtros extraídos da mensagem do usuário."""
    city: str = "São Paulo"
    neighborhood: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    rooms_min: int | None = None
    rooms_max: int | None = None
    area_min: float | None = None
    area_max: float | None = None
    property_type: str | None = None
    keywords: list[str] = field(default_factory=list)


def parse_filters(message: str) -> SearchFilters:
    """
    Extrai filtros de busca da mensagem em linguagem natural.

    Exemplos:
        "quero um apartamento de 2 quartos em Pinheiros até 800 mil"
        → city="São Paulo", neighborhood="Pinheiros", rooms_min=2, price_max=800000

        "flat perto do Ibirapuera para investir até 850 mil"
        → city="São Paulo", neighborhood="Ibirapuera", price_max=850000, property_type="studio"
    """
    filters = SearchFilters()
    msg = message.lower().strip()

    # ── Detectar cidade ──
    for city_name in KNOWN_NEIGHBORHOODS:
        # Buscar menção direta à cidade
        city_variants = [city_name]
        if city_name == "são paulo":
            city_variants.extend(["sp", "sampa", "sao paulo"])
        elif city_name == "goiânia":
            city_variants.extend(["goiania", "gyn"])
        elif city_name == "rio de janeiro":
            city_variants.extend(["rio", "rj"])

        for variant in city_variants:
            if variant in msg:
                filters.city = city_name.title()
                break

    # ── Detectar bairro ──
    city_key = filters.city.lower()
    neighborhoods = KNOWN_NEIGHBORHOODS.get(city_key, [])
    # Também buscar em todas as cidades se o bairro for único
    all_neighborhoods = []
    for c, ns in KNOWN_NEIGHBORHOODS.items():
        for n in ns:
            all_neighborhoods.append((n, c))

    for bairro, cidade in sorted(all_neighborhoods, key=lambda x: len(x[0]), reverse=True):
        if bairro in msg:
            filters.neighborhood = bairro.title()
            filters.city = cidade.title()
            break

    # ── Detectar preço ──
    # "até 800 mil" → price_max=800000
    # "entre 500 e 800 mil" → price_min=500000, price_max=800000
    # "até R$ 1.200.000" → price_max=1200000
    # "até uns 850 mil" → price_max=850000

    # Padrão: "até [uns/R$] X [mil/milhão/milhões]"
    price_max_match = re.search(
        r'at[eé]\s+(?:uns?\s+)?(?:r\$\s*)?(\d[\d.,]*)\s*(milh[oõ]es|milh[aã]o|mil)?\b',
        msg
    )
    if price_max_match:
        val = _parse_number(price_max_match.group(1))
        multiplier = price_max_match.group(2) or ""
        if multiplier and multiplier != "mil":
            # milhão/milhões
            val *= 1_000_000
        elif multiplier == "mil":
            val *= 1_000
        elif val < 10_000:
            val *= 1_000  # assume "mil" se valor pequeno
        filters.price_max = val

    # Padrão: "entre X e Y [mil]"
    price_range_match = re.search(
        r'entre\s+(?:r\$\s*)?(\d[\d.,]*)\s*(?:e|a)\s*(?:r\$\s*)?(\d[\d.,]*)\s*(mil(?:hão|hões)?)?',
        msg
    )
    if price_range_match:
        val_min = _parse_number(price_range_match.group(1))
        val_max = _parse_number(price_range_match.group(2))
        multiplier = price_range_match.group(3) or ""
        if multiplier and multiplier != "mil":
            val_min *= 1_000_000
            val_max *= 1_000_000
        elif multiplier == "mil":
            val_min *= 1_000
            val_max *= 1_000
        elif val_max < 10_000:
            val_min *= 1_000
            val_max *= 1_000
        filters.price_min = val_min
        filters.price_max = val_max

    # ── Detectar quartos ──
    rooms_match = re.search(r'(\d+)\s*(?:quartos?|q(?:tos?)?|dormit[oó]rios?|dorms?)', msg)
    if rooms_match:
        filters.rooms_min = int(rooms_match.group(1))

    # ── Detectar área ──
    area_match = re.search(r'(\d+)\s*(?:m²|m2|metros?\s*quadrados?)', msg)
    if area_match:
        filters.area_min = float(area_match.group(1))

    # ── Detectar tipo de imóvel ──
    for prop_type, keywords in PROPERTY_TYPE_KEYWORDS.items():
        for kw in keywords:
            # Usar word boundary para evitar match de "ap" dentro de "ibirapuera"
            if re.search(rf'\b{re.escape(kw)}\b', msg):
                filters.property_type = prop_type
                break
        if filters.property_type:
            break

    return filters


def _parse_number(s: str) -> float:
    """Parse '749.000' ou '749,000' ou '749000' → 749000.0"""
    cleaned = s.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def build_zap_search_url(filters: SearchFilters) -> str:
    """Constrói URL de busca para a API do ZAP Imóveis."""
    base = "https://glue-api.zapimoveis.com.br/v2/listings"

    # Normalizar cidade para slug
    city_slugs = {
        "São Paulo": "sao-paulo",
        "Goiânia": "goiania",
        "Rio De Janeiro": "rio-de-janeiro",
    }
    city_slug = city_slugs.get(filters.city, filters.city.lower().replace(" ", "-"))

    # Estado por cidade
    state_map = {
        "São Paulo": "sp",
        "Goiânia": "go",
        "Rio De Janeiro": "rj",
    }
    state = state_map.get(filters.city, "sp")

    params = {
        "business": "SALE",
        "listingType": "USED",
        "addressCity": filters.city,
        "addressState": state.upper(),
        "addressLocationId": f"BR>{state.upper()}>{city_slug}",
        "page": "1",
        "size": "24",
        "categoryPage": "RESULT",
        "includeFields": (
            "search(result(listings(listing(address,bathrooms,bedrooms,"
            "description,id,parkingSpaces,pricingInfos,suites,title,"
            "totalAreas,usableAreas,unitTypes,updatedAt),"
            "link,medias)))"
        ),
    }

    if filters.neighborhood:
        neighborhood_slug = filters.neighborhood.lower().replace(" ", "-")
        params["addressNeighborhood"] = filters.neighborhood
        params["addressLocationId"] += f">{neighborhood_slug}"

    if filters.price_max:
        params["priceMax"] = str(int(filters.price_max))
    if filters.price_min:
        params["priceMin"] = str(int(filters.price_min))
    if filters.rooms_min:
        params["bedrooms"] = str(filters.rooms_min)
    if filters.area_min:
        params["usableAreasMin"] = str(int(filters.area_min))

    # Tipo de imóvel para unitTypes do ZAP
    unit_type_map = {
        "apartamento": "APARTMENT",
        "studio": "APARTMENT",
        "cobertura": "PENTHOUSE",
        "kitnet": "KITNET",
        "casa": "HOME",
        "terreno": "ALLOTMENT_LAND",
        "comercial": "COMMERCIAL_PROPERTY",
    }
    if filters.property_type:
        params["unitTypes"] = unit_type_map.get(filters.property_type, "APARTMENT")

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{base}?{query_string}"


def build_vivareal_search_url(filters: SearchFilters) -> str:
    """Constrói URL de busca para a API do VivaReal."""
    base = "https://glue-api.vivareal.com/v2/listings"

    state_map = {
        "São Paulo": "SP",
        "Goiânia": "GO",
        "Rio De Janeiro": "RJ",
    }
    state = state_map.get(filters.city, "SP")
    city_slug = filters.city.lower().replace(" ", "-")

    params = {
        "business": "SALE",
        "listingType": "USED",
        "addressCity": filters.city,
        "addressState": state,
        "addressLocationId": f"BR>{state}>{city_slug}",
        "page": "1",
        "size": "24",
        "categoryPage": "RESULT",
        "includeFields": (
            "search(result(listings(listing(address,bathrooms,bedrooms,"
            "description,id,parkingSpaces,pricingInfos,suites,title,"
            "totalAreas,usableAreas,unitTypes,updatedAt),"
            "link,medias)))"
        ),
    }

    if filters.neighborhood:
        params["addressNeighborhood"] = filters.neighborhood
    if filters.price_max:
        params["priceMax"] = str(int(filters.price_max))
    if filters.price_min:
        params["priceMin"] = str(int(filters.price_min))
    if filters.rooms_min:
        params["bedrooms"] = str(filters.rooms_min)

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{base}?{query_string}"


# Headers para as APIs dos portais
_BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
}

BROWSER_HEADERS = {
    **_BASE_HEADERS,
    "Referer": "https://www.zapimoveis.com.br/",
    "Origin": "https://www.zapimoveis.com.br",
    "x-domain": "zap",
}

VIVAREAL_HEADERS = {
    **_BASE_HEADERS,
    "Referer": "https://www.vivareal.com.br/",
    "Origin": "https://www.vivareal.com.br",
    "x-domain": "vivareal",
}


async def fetch_url(
    url: str,
    headers: dict[str, str] | None = None,
    timeout_s: int = SCRAPER_TIMEOUT_S,
) -> dict[str, Any] | None:
    """
    Faz GET em uma URL e retorna o JSON parseado.
    Retorna None em caso de erro (timeout, HTTP error, etc).
    """
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_s)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json(content_type=None)
                else:
                    logger.warning(
                        f"HTTP {resp.status} ao buscar {url[:80]}..."
                    )
                    return None
    except asyncio.TimeoutError:
        logger.warning(f"Timeout ({timeout_s}s) ao buscar {url[:80]}...")
        return None
    except Exception as e:
        logger.warning(f"Erro ao buscar {url[:80]}...: {e}")
        return None


async def fetch_multiple(
    urls_with_headers: list[tuple[str, dict[str, str]]],
    timeout_s: int = SCRAPER_TIMEOUT_S,
) -> list[dict[str, Any] | None]:
    """
    Faz GET em paralelo para múltiplas URLs.
    Retorna lista de respostas JSON (None para falhas).
    """
    tasks = [fetch_url(url, headers, timeout_s) for url, headers in urls_with_headers]
    return await asyncio.gather(*tasks, return_exceptions=False)
