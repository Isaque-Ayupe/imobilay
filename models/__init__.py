"""
IMOBILAY — Models Package

Re-exporta todos os tipos para facilitar importações:
    from models import Property, ContextStore, RoutingResult, FeedbackRecord
"""

# ── Property models ──────────────────────────────────────────
from models.property import (
    AnalysisData,
    AppreciationPotential,
    InvestmentResult,
    LocationInsights,
    Opportunity,
    OpportunityTag,
    Property,
    PropertySource,
    PropertyType,
    RankingJustificativa,
    RankingResult,
    RawProperty,
    ValuationResult,
    ValuationTag,
)

# ── Context models ───────────────────────────────────────────
from models.context import (
    AgentError,
    CompletenessReport,
    ContextPatch,
    ContextStore,
    ErrorSeverity,
    GateRecommendation,
    GateResult,
    LimitationResponse,
    ProcessedInput,
    UserPreferences,
    UserProfile,
    create_initial_context,
)

# ── Routing models ───────────────────────────────────────────
from models.routing import (
    DAGEdge,
    DAGNode,
    EdgeType,
    ExecutionDAG,
    ExecutionGroup,
    ExecutionType,
    IntentType,
    RoutingResult,
)

# ── Feedback models ──────────────────────────────────────────
from models.feedback import (
    AgentExecutionRecord,
    AgentHealthStats,
    AgentStatus,
    CircuitState,
    ExecutionMetrics,
    ExecutionTrace,
    FeedbackRecord,
    ImplicitSignal,
    OrchestratorResult,
)

__all__ = [
    # Property
    "AnalysisData",
    "AppreciationPotential",
    "InvestmentResult",
    "LocationInsights",
    "Opportunity",
    "OpportunityTag",
    "Property",
    "PropertySource",
    "PropertyType",
    "RankingJustificativa",
    "RankingResult",
    "RawProperty",
    "ValuationResult",
    "ValuationTag",
    # Context
    "AgentError",
    "CompletenessReport",
    "ContextPatch",
    "ContextStore",
    "ErrorSeverity",
    "GateRecommendation",
    "GateResult",
    "LimitationResponse",
    "ProcessedInput",
    "UserPreferences",
    "UserProfile",
    "create_initial_context",
    # Routing
    "DAGEdge",
    "DAGNode",
    "EdgeType",
    "ExecutionDAG",
    "ExecutionGroup",
    "ExecutionType",
    "IntentType",
    "RoutingResult",
    # Feedback
    "AgentExecutionRecord",
    "AgentHealthStats",
    "AgentStatus",
    "CircuitState",
    "ExecutionMetrics",
    "ExecutionTrace",
    "FeedbackRecord",
    "ImplicitSignal",
    "OrchestratorResult",
]
