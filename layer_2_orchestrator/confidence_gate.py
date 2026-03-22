"""
IMOBILAY — ConfidenceGate

Validação pré-LLM: verifica se o ContextStore tem dados suficientes
para gerar uma resposta de qualidade antes de acionar o Gemini.

Regras:
  1. Mínimo 1 imóvel após scraping
  2. >= 80% dos imóveis com preco_justo calculado
  3. Ranking presente
  4. Nenhum AgentError com severity="CRITICAL"
"""

from __future__ import annotations

from models.context import (
    ContextStore,
    ErrorSeverity,
    GateRecommendation,
    GateResult,
    LimitationResponse,
)


class ConfidenceGate:
    """Valida completude do ContextStore antes de acionar o LLM."""

    def validate(self, context: ContextStore) -> GateResult:
        """
        Executa a validação de completude.

        Returns:
            GateResult com score, recommendation e missing_fields
        """
        report = context.validate_completeness()

        return GateResult(
            passed=report.recommendation != GateRecommendation.RETURN_LIMITATION,
            score=report.score,
            missing_fields=report.missing_fields,
            recommendation=report.recommendation,
        )

    def build_limitation_response(self, gate: GateResult) -> LimitationResponse:
        """
        Constrói resposta estruturada quando o gate bloqueia o LLM.
        Usada quando recommendation = "return_limitation".
        """
        missing = gate.missing_fields

        if "properties" in missing:
            reason = "Não encontrei imóveis com os critérios informados."
            suggestion = (
                "Tente ampliar a faixa de preço, buscar em bairros vizinhos "
                "ou verificar se o bairro/cidade está correto."
            )
        elif "analysis.valuation" in missing:
            reason = "Consegui encontrar imóveis, mas não foi possível calcular o preço justo."
            suggestion = (
                "Isso pode ocorrer quando há poucos comparáveis na região. "
                "Tente buscar em uma área com mais anúncios."
            )
        elif "analysis.ranking" in missing:
            reason = "Os dados de análise estão incompletos para gerar um ranking."
            suggestion = "Tente uma busca mais simples, como 'apartamento 2 quartos em [bairro]'."
        else:
            reason = "Dados insuficientes para gerar uma análise completa."
            suggestion = "Pode reformular sua pergunta com mais detalhes?"

        return LimitationResponse(
            reason=reason,
            missing_data=missing,
            suggestion=suggestion,
        )
