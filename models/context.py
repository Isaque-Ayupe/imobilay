"""
IMOBILAY — Models de Contexto Compartilhado

ContextStore: estado central imutável compartilhado entre todos os agentes.
Usa sistema de patches: apply_patch() retorna NOVA instância, nunca muta.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from models.property import AnalysisData, Property


# ── Enums ────────────────────────────────────────────────────


class ErrorSeverity(str, Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class GateRecommendation(str, Enum):
    PROCEED = "proceed"
    PROCEED_WITH_WARNING = "proceed_with_warning"
    ASK_MORE_INFO = "return_limitation"
    RETURN_LIMITATION = "return_limitation"


# ── Models ───────────────────────────────────────────────────


class UserProfile(BaseModel):
    """Perfil básico do usuário para o pipeline."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "Usuário"
    plan: str = "free"                       # "free" | "pro" | "elite"
    analysis_count: int = 0
    preferences: UserPreferences = Field(default_factory=lambda: UserPreferences())


class UserPreferences(BaseModel):
    """Preferências do usuário para buscas."""

    max_budget: float | None = None
    preferred_areas: list[str] = Field(default_factory=list)
    min_rooms: int | None = None
    investment_goal: str | None = None       # "rental" | "appreciation" | "both"


class ProcessedInput(BaseModel):
    """Entrada processada pelo InputProcessor — ponto de partida do pipeline."""

    message: str
    session_id: str
    user_profile: UserProfile = Field(default_factory=UserProfile)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    trace_id: str = Field(default_factory=lambda: str(uuid4()))


class ContextPatch(BaseModel):
    """Registro imutável de cada escrita no ContextStore."""

    agent_id: str                            # qual agente fez a escrita
    field: str                               # campo alterado (ex: "properties", "analysis.valuation")
    value: Any                               # valor escrito
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: int = 0                         # versão do context após este patch


class AgentError(BaseModel):
    """Erro registrado por um agente durante a execução."""

    agent_id: str
    error_type: str                          # tipo do erro (ex: "TimeoutError", "HTTPError")
    message: str                             # mensagem descritiva
    severity: ErrorSeverity = ErrorSeverity.WARNING
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CompletenessReport(BaseModel):
    """Relatório de completude gerado pelo ConfidenceGate."""

    missing_fields: list[str] = Field(default_factory=list)
    coverage_valuation: float = 0.0          # % de imóveis com preço justo calculado
    total_properties: int = 0
    has_ranking: bool = False
    has_critical_errors: bool = False
    score: float = 0.0                       # 0.0 a 1.0
    recommendation: GateRecommendation = GateRecommendation.RETURN_LIMITATION


class GateResult(BaseModel):
    """Resultado da validação do ConfidenceGate."""

    passed: bool = False
    score: float = Field(ge=0, le=1, default=0.0)
    missing_fields: list[str] = Field(default_factory=list)
    recommendation: GateRecommendation = GateRecommendation.RETURN_LIMITATION


class LimitationResponse(BaseModel):
    """Resposta estruturada quando o ConfidenceGate bloqueia o LLM."""

    reason: str                              # ex: "Dados insuficientes para Pinheiros"
    missing_data: list[str] = Field(default_factory=list)
    suggestion: str = ""                     # ex: "Tente ampliar a faixa de preço ou buscar em bairros vizinhos"


# ── ContextStore ─────────────────────────────────────────────


class ContextStore(BaseModel):
    """
    Estado compartilhado central entre todos os agentes.

    IMUTÁVEL por design: apply_patch() retorna uma NOVA instância.
    Cada escrita gera um ContextPatch registrado no histórico.
    """

    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 0
    input: ProcessedInput | None = None
    raw_properties: list[dict] = Field(default_factory=list)
    properties: list[Property] = Field(default_factory=list)
    analysis: AnalysisData = Field(default_factory=AnalysisData)
    user: UserProfile = Field(default_factory=UserProfile)
    errors: list[AgentError] = Field(default_factory=list)
    patches: list[ContextPatch] = Field(default_factory=list)

    def apply_patch(self, agent_id: str, field: str, value: Any) -> "ContextStore":
        """
        Aplica um patch e retorna uma NOVA instância do ContextStore.
        Nunca muta a instância atual.

        Args:
            agent_id: ID do agente que está escrevendo
            field: Campo a alterar (suporta nested: "analysis.valuation")
            value: Novo valor para o campo

        Returns:
            Nova instância de ContextStore com o patch aplicado
        """
        # Criar cópia profunda do estado atual
        new_data = deepcopy(self.model_dump())
        new_version = self.version + 1

        # Registrar o patch
        patch = ContextPatch(
            agent_id=agent_id,
            field=field,
            value=value,
            version=new_version,
        )
        new_data["patches"].append(patch.model_dump())

        # Aplicar o patch no campo (suporta campos nested com ".")
        parts = field.split(".")
        target = new_data
        for part in parts[:-1]:
            if isinstance(target, dict):
                target = target[part]
            elif isinstance(target, list) and part.isdigit():
                target = target[int(part)]
        
        final_key = parts[-1]
        if isinstance(target, dict):
            # Serializar o valor se for um modelo Pydantic ou lista de modelos
            if isinstance(value, BaseModel):
                target[final_key] = value.model_dump()
            elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
                target[final_key] = [v.model_dump() for v in value]
            else:
                target[final_key] = value

        new_data["version"] = new_version

        return ContextStore.model_validate(new_data)

    def add_error(self, error: AgentError) -> "ContextStore":
        """Adiciona um erro e retorna nova instância."""
        new_data = deepcopy(self.model_dump())
        new_data["errors"].append(error.model_dump())
        return ContextStore.model_validate(new_data)

    def get_snapshot(self, version: int) -> dict:
        """
        Reconstrói o estado em uma versão específica
        re-aplicando patches até a versão desejada.
        """
        if version >= self.version:
            return self.model_dump()

        # Filtrar patches até a versão desejada
        patches_until = [p for p in self.patches if p.version <= version]
        return {
            "version": version,
            "patches_count": len(patches_until),
            "trace_id": self.trace_id,
        }

    def validate_completeness(self) -> CompletenessReport:
        """Valida completude do contexto para o ConfidenceGate."""
        missing = []
        total = len(self.properties)
        valuations = len(self.analysis.valuation)
        has_ranking = self.analysis.ranking is not None
        has_critical = any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)

        if total == 0:
            missing.append("properties")
        if valuations == 0:
            missing.append("analysis.valuation")
        if not has_ranking:
            missing.append("analysis.ranking")

        coverage = valuations / total if total > 0 else 0.0

        # Calcular score de 0 a 1
        score = 0.0
        if total > 0:
            score += 0.3
        if coverage >= 0.8:
            score += 0.3
        if has_ranking:
            score += 0.2
        if not has_critical:
            score += 0.2

        # Determinar recomendação
        if score >= 0.8 and not has_critical:
            recommendation = GateRecommendation.PROCEED
        elif score >= 0.5 and not has_critical:
            recommendation = GateRecommendation.PROCEED_WITH_WARNING
        else:
            recommendation = GateRecommendation.RETURN_LIMITATION

        return CompletenessReport(
            missing_fields=missing,
            coverage_valuation=coverage,
            total_properties=total,
            has_ranking=has_ranking,
            has_critical_errors=has_critical,
            score=score,
            recommendation=recommendation,
        )


def create_initial_context(processed_input: ProcessedInput) -> ContextStore:
    """Factory function para criar um ContextStore inicial a partir do input processado."""
    return ContextStore(
        trace_id=processed_input.trace_id,
        input=processed_input,
        user=processed_input.user_profile,
    )
