"""
IMOBILAY — ValuationAgent

Calcula preço justo por m² baseado em comparáveis REAIS do pipeline.
Usa mediana dos imóveis encontrados no mesmo bairro como referência.

Classificação:
  "barato" (< -10%), "justo" (-10% a +10%), "caro" (> +10%)
"""

from __future__ import annotations

import logging
import statistics

from models.context import ContextPatch, ContextStore
from models.property import ValuationResult, ValuationTag
from layer_2_orchestrator.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


# Dados de fallback por bairro — usados SOMENTE quando não há comparáveis
# suficientes no pipeline (< 3 imóveis no mesmo bairro).
# Fonte: FipeZAP (aproximações, atualizadas periodicamente)
FIPEZAP_FALLBACK_M2: dict[str, float] = {
    "pinheiros":       14200,
    "vila madalena":   12800,
    "brooklin":        14500,
    "moema":           14000,
    "itaim bibi":      17000,
    "jardins":         16500,
    "vila olímpia":    15000,
    "perdizes":        12000,
    "consolação":      11500,
    "bela vista":      10800,
    "higienópolis":    13500,
    "paraíso":         13000,
    "vila mariana":    11500,
    "campo belo":      12500,
    "santo amaro":     10000,
    "morumbi":         11000,
    "butantã":          9500,
    "lapa":            10500,
    "santana":          9000,
    "tatuapé":          9800,
    "anália franco":   10500,
    "setor bueno":      8500,
    "setor marista":    9500,
    "setor oeste":      7500,
    "centro":           7000,
    "copacabana":      13000,
    "ipanema":         22000,
    "leblon":          24000,
    "botafogo":        13500,
    "flamengo":        11500,
    "barra da tijuca": 10500,
    "ibirapuera":      15000,
    "berrini":         14000,
    "chácara santo antônio": 11000,
    "vila andrade":     9000,
    "granja julieta":  11500,
}

GLOBAL_DEFAULT_M2 = 10000


class ValuationAgent(BaseAgent):
    agent_id = "valuation"
    fallback_value = []
    _output_field = "analysis.valuation"

    async def execute(self, context: ContextStore) -> ContextPatch:
        """
        Calcula preço justo para cada imóvel usando comparáveis reais.

        Estratégia:
        1. Agrupar imóveis por bairro
        2. Calcular mediana do preço/m² por bairro (comparáveis reais)
        3. Se < 3 comparáveis no bairro, usar FipeZAP fallback
        4. Calcular desvio, classificar como barato/justo/caro
        """
        valuations = []

        # Agrupar preço/m² por bairro para ter comparáveis
        bairro_prices: dict[str, list[float]] = {}
        for prop in context.properties:
            bairro = (prop.neighborhood or "").lower().strip()
            if prop.price_per_sqm and prop.price_per_sqm > 0:
                if bairro not in bairro_prices:
                    bairro_prices[bairro] = []
                bairro_prices[bairro].append(prop.price_per_sqm)

        # Log dos comparáveis encontrados
        for bairro, prices in bairro_prices.items():
            logger.info(
                f"Valuation [{bairro}]: {len(prices)} comparáveis, "
                f"mediana R$ {statistics.median(prices):,.0f}/m²"
            )

        for prop in context.properties:
            bairro = (prop.neighborhood or "").lower().strip()

            # Determinar preço médio de referência
            comparaveis = bairro_prices.get(bairro, [])
            comparaveis_count = len(comparaveis)
            source = "comparáveis"

            if comparaveis_count >= 3:
                # Usar mediana dos comparáveis reais (excluindo o próprio imóvel)
                other_prices = [
                    p for p in comparaveis if abs(p - prop.price_per_sqm) > 0.01
                ]
                if len(other_prices) >= 2:
                    preco_m2_mercado = statistics.median(other_prices)
                else:
                    preco_m2_mercado = statistics.median(comparaveis)
            else:
                # Fallback: dados FipeZAP
                preco_m2_mercado = FIPEZAP_FALLBACK_M2.get(bairro, GLOBAL_DEFAULT_M2)
                source = "FipeZAP (fallback)"
                logger.debug(
                    f"Valuation [{bairro}]: poucos comparáveis ({comparaveis_count}), "
                    f"usando {source}: R$ {preco_m2_mercado:,.0f}/m²"
                )

            preco_justo = preco_m2_mercado * prop.area
            preco_justo_m2 = preco_m2_mercado

            desvio = (
                ((prop.price - preco_justo) / preco_justo) * 100
                if preco_justo > 0
                else 0
            )

            if desvio < -10:
                classificacao = ValuationTag.BARATO
            elif desvio > 10:
                classificacao = ValuationTag.CARO
            else:
                classificacao = ValuationTag.JUSTO

            valuations.append(ValuationResult(
                property_id=prop.id,
                preco_justo=round(preco_justo, 2),
                preco_justo_por_sqm=round(preco_justo_m2, 2),
                desvio_percentual=round(desvio, 2),
                classificacao=classificacao,
                comparaveis_usados=max(comparaveis_count - 1, 0),
            ))

            logger.debug(
                f"Valuation [{prop.address}]: "
                f"pedido R$ {prop.price:,.0f} vs justo R$ {preco_justo:,.0f} "
                f"(desvio {desvio:+.1f}%, {classificacao.value}) "
                f"[{source}, {comparaveis_count} comparáveis]"
            )

        return ContextPatch(
            agent_id=self.agent_id,
            field="analysis.valuation",
            value=[v.model_dump() for v in valuations],
        )

    def validate_input(self, context: ContextStore) -> bool:
        return len(context.properties) > 0
