export type PropertyType = 'apartamento' | 'studio' | 'cobertura' | 'kitnet' | 'casa' | 'sobrado' | 'terreno' | 'comercial';
export type PropertySource = 'zap' | 'vivareal' | 'olx' | 'other';
export type ValuationTag = 'barato' | 'justo' | 'caro';
export type AppreciationPotential = 'baixo' | 'medio' | 'alto';

export interface LocationInsights {
  bairro_score: number;
  seguranca_index: number;
  liquidez_estimada: string;
  infraestrutura_proxima: string[];
}

export interface Property {
  id: string;
  address: string;
  neighborhood: string;
  city: string;
  rooms: number;
  area: number;
  parking: number;
  floor: number | null;
  price: number;
  price_per_sqm: number;
  property_type: PropertyType;
  source: PropertySource;
  url: string | null;
  location_insights?: LocationInsights;
}

export interface ValuationResult {
  property_id: string;
  preco_justo: number;
  preco_justo_por_sqm: number;
  desvio_percentual: number;
  classificacao: ValuationTag;
  comparaveis_usados: number;
}

export interface InvestmentResult {
  property_id: string;
  aluguel_estimado: number;
  roi_mensal: number;
  roi_anual: number;
  payback_anos: number;
  potencial_valorizacao: AppreciationPotential;
}

export interface Opportunity {
  property_id: string;
  score_composto: number;
  desvio_percentual: number;
  liquidez: string;
  location_score: number;
  motivo: string;
}

export interface RankingJustificativa {
  property_id: string;
  score_total: number;
  score_preco: number;
  score_localizacao: number;
  score_investimento: number;
  score_oportunidade: number;
  resumo: string;
}

export interface RankingResult {
  ranking: RankingJustificativa[];
  melhor_opcao: string | null;
  total_avaliados: number;
}

export interface AnalysisData {
  valuation: ValuationResult[];
  investment: InvestmentResult[];
  ranking: RankingResult | null;
  opportunities: Opportunity[];
}

export interface ContextData {
  properties: Property[];
  analysis: AnalysisData;
}

export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  contextData?: ContextData; // Dados anexados à mensagem do assistente
  isStream?: boolean; // Se a mensagem ainda está sendo gerada
}

export interface SessionInfo {
  id: string;
  title: string;
  timestamp: Date;
  isToday?: boolean;
  isYesterday?: boolean;
}
