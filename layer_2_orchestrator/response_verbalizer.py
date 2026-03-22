"""
IMOBILAY — ResponseVerbalizer

ÚNICO ponto de contato com LLM em todo o sistema.
Transforma o ContextStore validado em linguagem natural.

Modelo: Gemini 2.5 Pro via Google GenAI SDK
Temperature: 0.3 (respostas consistentes e factuais)
Max tokens: 1500

Regras:
  - NUNCA inventar dados — apenas verbalizar o que está no context
  - NUNCA acessar campos com valor None sem tratar
  - Tom: consultor imobiliário sênior, direto, fundamentado
"""

from __future__ import annotations

import os
from models.context import ContextStore, GateResult, GateRecommendation


# ── Constantes ───────────────────────────────────────────────

MODEL_NAME = "gemini-2.5-pro"
TEMPERATURE = 0.3
MAX_TOKENS = 1500
MAX_RETRIES = 2


class ResponseVerbalizer:
    """
    Transforma dados estruturados do ContextStore em resposta conversacional.
    Único ponto de contato com LLM no sistema inteiro.
    """

    def __init__(self):
        self._client = None

    async def _get_client(self):
        """Lazy init do cliente Google GenAI."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(
                    api_key=os.environ.get("GEMINI_API_KEY", ""),
                )
            except ImportError:
                self._client = None
        return self._client

    async def verbalize(self, context: ContextStore, gate: GateResult) -> str:
        """
        Gera resposta em linguagem natural a partir do contexto.

        Args:
            context: ContextStore com dados dos agentes
            gate: resultado do ConfidenceGate

        Returns:
            Resposta conversacional em português
        """
        # Se o gate não passou, retornar mensagem estruturada sem LLM
        if gate.recommendation == GateRecommendation.RETURN_LIMITATION:
            return self._build_limitation_message(gate)

        # Construir prompt dinâmico
        prompt = self._build_prompt(context, gate)

        # Tentar chamar o LLM
        for attempt in range(MAX_RETRIES):
            try:
                client = await self._get_client()
                if client is None:
                    return self._build_fallback_response(context)

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config={
                        "temperature": TEMPERATURE,
                        "max_output_tokens": MAX_TOKENS,
                    },
                )

                return response.text or self._build_fallback_response(context)

            except Exception:
                if attempt < MAX_RETRIES - 1:
                    continue
                # Falha definitiva → resposta estruturada sem LLM
                return self._build_fallback_response(context)

    def _build_prompt(self, context: ContextStore, gate: GateResult) -> str:
        """Constrói o prompt dinâmico com dados do context."""
        parts = []

        parts.append(
            "Você é um consultor imobiliário sênior do IMOBILAY. "
            "Responda de forma direta, fundamentada em dados, sem exageros. "
            "NUNCA invente dados. Use apenas as informações fornecidas abaixo.\n"
        )

        # Resumo dos imóveis
        if context.properties:
            parts.append(f"\n## Imóveis encontrados ({len(context.properties)}):\n")
            for i, p in enumerate(context.properties[:10], 1):  # max 10 no prompt
                parts.append(
                    f"{i}. **{p.address}**, {p.neighborhood} — "
                    f"R$ {p.price:,.0f} | {p.area}m² | {p.rooms}q | "
                    f"R$ {p.price_per_sqm:,.0f}/m²"
                )
                if p.location_insights:
                    parts.append(
                        f"   📍 Score bairro: {p.location_insights.bairro_score}/10, "
                        f"Segurança: {p.location_insights.seguranca_index}/10"
                    )

        # Avaliações de preço justo
        if context.analysis.valuation:
            parts.append(f"\n## Avaliação de preço ({len(context.analysis.valuation)} imóveis):\n")
            for v in context.analysis.valuation:
                tag = "🟢" if v.classificacao.value == "barato" else "🟡" if v.classificacao.value == "justo" else "🔴"
                parts.append(
                    f"- Imóvel {v.property_id[:8]}: preço justo R$ {v.preco_justo:,.0f} "
                    f"(desvio {v.desvio_percentual:+.1f}%) {tag} {v.classificacao.value}"
                )

        # Investimento
        if context.analysis.investment:
            parts.append(f"\n## Análise de investimento:\n")
            for inv in context.analysis.investment:
                parts.append(
                    f"- Imóvel {inv.property_id[:8]}: "
                    f"ROI anual {inv.roi_anual:.1f}%, "
                    f"payback {inv.payback_anos:.1f} anos, "
                    f"aluguel estimado R$ {inv.aluguel_estimado:,.0f}/mês"
                )

        # Oportunidades
        if context.analysis.opportunities:
            parts.append(f"\n## Oportunidades detectadas:\n")
            for op in context.analysis.opportunities:
                parts.append(
                    f"- Imóvel {op.property_id[:8]}: score {op.score_composto:.1f}/10 — {op.motivo}"
                )

        # Ranking
        if context.analysis.ranking and context.analysis.ranking.has_result:
            ranking = context.analysis.ranking
            parts.append(f"\n## Ranking final (melhor opção: {ranking.melhor_opcao[:8] if ranking.melhor_opcao else 'N/A'}):\n")
            for r in ranking.ranking[:5]:
                parts.append(
                    f"- {r.property_id[:8]}: score total {r.score_total:.1f}/10 "
                    f"(preço {r.score_preco:.1f}, loc {r.score_localizacao:.1f}, "
                    f"invest {r.score_investimento:.1f})"
                )

        # Warnings
        if gate.recommendation == GateRecommendation.PROCEED_WITH_WARNING:
            parts.append(
                f"\n⚠ Nota: dados parciais. Campos faltantes: {', '.join(gate.missing_fields)}"
            )

        parts.append(
            "\n\nCom base nesses dados, gere uma resposta clara e útil em português "
            "para o usuário. Cite imóveis pelo endereço. Seja direto e fundamentado."
        )

        return "\n".join(parts)

    def _build_fallback_response(self, context: ContextStore) -> str:
        """Resposta estruturada sem LLM — quando Gemini não está disponível."""
        lines = ["📊 **Resultado da análise:**\n"]

        if context.properties:
            lines.append(f"Encontrei **{len(context.properties)} imóveis**:\n")
            for i, p in enumerate(context.properties[:5], 1):
                lines.append(
                    f"{i}. {p.address}, {p.neighborhood} — "
                    f"R$ {p.price:,.0f} ({p.rooms}q, {p.area}m²)"
                )

        if context.analysis.ranking and context.analysis.ranking.melhor_opcao:
            lines.append(f"\n🏆 **Melhor opção:** ID {context.analysis.ranking.melhor_opcao[:8]}")

        if not context.properties:
            lines.append("Não encontrei imóveis com os critérios informados.")

        return "\n".join(lines)

    def _build_limitation_message(self, gate: GateResult) -> str:
        """Mensagem quando o gate bloqueia a resposta."""
        missing = ", ".join(gate.missing_fields) if gate.missing_fields else "dados gerais"
        return (
            f"⚠ Não foi possível gerar uma análise completa. "
            f"Dados faltantes: {missing}. "
            f"Tente reformular sua pergunta com mais detalhes."
        )
