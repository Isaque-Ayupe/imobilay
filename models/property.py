"""
IMOBILAY — Models de Propriedades Imobiliárias

Tipos relacionados a imóveis: dados brutos do scraper, imóvel normalizado,
avaliação de preço justo, análise de investimento, oportunidades e ranking.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4


# ── Enums ────────────────────────────────────────────────────


class PropertyType(str, Enum):
    APARTAMENTO = "apartamento"
    STUDIO = "studio"
    COBERTURA = "cobertura"
    KITNET = "kitnet"
    CASA = "casa"
    SOBRADO = "sobrado"
    TERRENO = "terreno"
    COMERCIAL = "comercial"


class PropertySource(str, Enum):
    ZAP = "zap"
    VIVAREAL = "vivareal"
    OLX = "olx"
    OTHER = "other"


class ValuationTag(str, Enum):
    BARATO = "barato"       # desvio < -10%
    JUSTO = "justo"         # -10% a +10%
    CARO = "caro"           # > +10%


class AppreciationPotential(str, Enum):
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"


class OpportunityTag(str, Enum):
    OPPORTUNITY = "opportunity"
    OVERPRICED = "overpriced"
    FAIR = "fair"


# ── Models ───────────────────────────────────────────────────


class RawProperty(BaseModel):
    """Dados brutos retornados pelo WebScraperAgent, antes de normalização."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    raw_title: str                          # título original do anúncio
    raw_price: str                          # ex: "R$ 749.000" — string original
    raw_area: str | None = None             # ex: "68m²"
    raw_rooms: str | None = None            # ex: "2 quartos"
    raw_address: str | None = None
    raw_neighborhood: str | None = None
    raw_city: str | None = None
    url: str | None = None                  # link do anúncio
    source: PropertySource = PropertySource.OTHER
    raw_data: dict | None = None            # payload completo original


class LocationInsights(BaseModel):
    """Dados de enriquecimento geográfico do LocationInsightsAgent."""

    bairro_score: float = Field(ge=0, le=10)            # score geral do bairro
    seguranca_index: float = Field(ge=0, le=10)         # índice de segurança
    liquidez_estimada: str = "media"                     # "baixa", "media", "alta"
    infraestrutura_proxima: list[str] = Field(default_factory=list)  # ex: ["metrô", "parque", "hospital"]


class Property(BaseModel):
    """Imóvel normalizado com todos os campos padronizados."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    address: str
    neighborhood: str
    city: str
    rooms: int = Field(ge=0)
    area: float = Field(gt=0, description="Área em m²")
    parking: int = Field(ge=0, default=0)
    floor: int | None = None
    price: float = Field(gt=0, description="Preço do imóvel em reais")
    price_per_sqm: float = Field(gt=0, description="Preço por m²")
    property_type: PropertyType = PropertyType.APARTAMENTO
    source: PropertySource = PropertySource.OTHER
    url: str | None = None
    location_insights: LocationInsights | None = None

    @field_validator("price_per_sqm", mode="before")
    @classmethod
    def calculate_price_per_sqm(cls, v, info):
        """Calcula preço/m² automaticamente se não fornecido."""
        if v is not None and v > 0:
            return v
        data = info.data
        if "price" in data and "area" in data and data["area"] > 0:
            return data["price"] / data["area"]
        return v


class ValuationResult(BaseModel):
    """Resultado da avaliação de preço justo pelo ValuationAgent."""

    property_id: str
    preco_justo: float = Field(gt=0, description="Preço justo calculado por comparáveis")
    preco_justo_por_sqm: float = Field(gt=0)
    desvio_percentual: float = Field(description="% diferença entre preço pedido e justo. Negativo = abaixo do justo.")
    classificacao: ValuationTag = ValuationTag.JUSTO
    comparaveis_usados: int = Field(ge=0, default=0, description="Quantidade de imóveis comparáveis usados no cálculo")

    @field_validator("classificacao", mode="before")
    @classmethod
    def classify_from_deviation(cls, v, info):
        """Classifica automaticamente baseado no desvio percentual."""
        if v is not None and isinstance(v, ValuationTag):
            return v
        data = info.data
        desvio = data.get("desvio_percentual", 0)
        if desvio < -10:
            return ValuationTag.BARATO
        elif desvio > 10:
            return ValuationTag.CARO
        return ValuationTag.JUSTO


class InvestmentResult(BaseModel):
    """Resultado da análise de investimento pelo InvestmentAnalysisAgent."""

    property_id: str
    aluguel_estimado: float = Field(ge=0, description="Aluguel mensal estimado em reais")
    roi_mensal: float = Field(description="ROI mensal: aluguel / preço × 100")
    roi_anual: float = Field(description="ROI anual estimado em %")
    payback_anos: float = Field(gt=0, description="Anos para recuperar investimento via aluguel")
    potencial_valorizacao: AppreciationPotential = AppreciationPotential.MEDIO


class Opportunity(BaseModel):
    """Oportunidade detectada pelo OpportunityDetectionAgent."""

    property_id: str
    score_composto: float = Field(ge=0, le=10, description="Score: 0.4*desvio + 0.3*liquidez + 0.3*location")
    desvio_percentual: float
    liquidez: str                           # "baixa", "media", "alta"
    location_score: float = Field(ge=0, le=10)
    motivo: str = ""                        # justificativa estruturada


class RankingJustificativa(BaseModel):
    """Justificativa estruturada de por que um imóvel foi ranqueado."""

    property_id: str
    score_total: float = Field(ge=0, le=10)
    score_preco: float = Field(ge=0, le=10)
    score_localizacao: float = Field(ge=0, le=10)
    score_investimento: float = Field(ge=0, le=10)
    score_oportunidade: float = Field(ge=0, le=10)
    resumo: str = ""                        # razão gerada pelo ComparePropertiesAgent


class RankingResult(BaseModel):
    """Ranking final gerado pelo ComparePropertiesAgent."""

    ranking: list[RankingJustificativa] = Field(default_factory=list)
    melhor_opcao: str | None = None         # property_id do melhor imóvel
    total_avaliados: int = 0

    @property
    def has_result(self) -> bool:
        return self.melhor_opcao is not None and len(self.ranking) > 0


# ── Tipos auxiliares para a análise dentro do ContextStore ───


class AnalysisData(BaseModel):
    """Container para os dados de análise no ContextStore."""

    valuation: list[ValuationResult] = Field(default_factory=list)
    investment: list[InvestmentResult] = Field(default_factory=list)
    ranking: RankingResult | None = None
    opportunities: list[Opportunity] = Field(default_factory=list)
